#!/usr/bin/env python3
"""Compile a bounded context manifest from a project profile and capabilities."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from harness_runtime_lib import (
    HarnessError,
    build_asset_inventory,
    ensure_unique_selected_frontmatter,
    load_data,
    merge_effective_capabilities,
    project_root_from,
    resolve_provider_quality,
    resolve_capabilities,
    sha256_file,
    utc_now,
    validate_registry,
    write_json,
)


def compile_manifest(
    root: Path,
    profile_path: Path,
    requested: list[str],
    budget_override: int | None = None,
    provider_override: str | None = None,
    quality_tier_override: str | None = None,
) -> dict[str, Any]:
    profile = load_data(profile_path)
    if (
        not isinstance(profile, dict)
        or profile.get("schema_version") != "harness.project-profile.v1"
    ):
        raise HarnessError(f"invalid project profile: {profile_path}")
    provider_registry = load_data(
        root / ".claude" / "registry" / "providers" / "core.yaml"
    )
    declared_providers = profile.get("providers", [])
    selected_provider = provider_override or profile.get("selected_provider")
    if (
        not isinstance(declared_providers, list)
        or selected_provider not in declared_providers
    ):
        raise HarnessError(
            "project profile selected_provider must be present in providers"
        )
    selected_quality_tier = quality_tier_override or profile.get(
        "default_quality_tier", ""
    )
    provider_binding = resolve_provider_quality(
        provider_registry,
        str(selected_provider),
        str(selected_quality_tier),
    )
    static_capabilities, issues = validate_registry(root, root / ".claude" / "registry")
    errors = [issue for issue in issues if issue.severity == "error"]
    if errors:
        raise HarnessError(
            "registry errors: " + "; ".join(issue.message for issue in errors)
        )
    inventory = build_asset_inventory(root)
    capabilities = merge_effective_capabilities(static_capabilities, inventory)

    names = list(profile.get("capabilities", []))
    names.extend(requested)
    selected_capabilities = resolve_capabilities(capabilities, names)
    ensure_unique_selected_frontmatter(root, selected_capabilities)

    budget = (
        budget_override
        if budget_override is not None
        else int(profile.get("context_budget_bytes", 0))
    )
    if budget <= 0:
        raise HarnessError("context budget must be positive")

    candidates: list[tuple[str, str, bool]] = []
    seen_paths: set[str] = set()
    for capability in selected_capabilities:
        paths = [(capability.get("source"), True)]
        paths.extend(
            (context_path, bool(capability.get("required_context")))
            for context_path in capability.get("context_files", [])
        )
        for raw_path, required in paths:
            relative = str(raw_path or "").strip()
            if not relative or relative in seen_paths:
                continue
            seen_paths.add(relative)
            candidates.append((relative, str(capability["id"]), required))
    for raw_path in profile.get("overlays", []):
        relative = str(raw_path).strip()
        if relative and relative not in seen_paths:
            seen_paths.add(relative)
            candidates.append((relative, "project-overlay", True))

    selected: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    total = 0
    root_resolved = root.resolve()
    for relative, owner, required in candidates:
        path = (root / relative).resolve()
        try:
            path.relative_to(root_resolved)
        except ValueError as exc:
            raise HarnessError(f"context path escapes repository: {relative}") from exc
        if not path.is_file():
            message = {
                "path": relative,
                "capability": owner,
                "reason": "not-a-file",
                "required": required,
            }
            if required:
                raise HarnessError(f"required context file missing: {relative}")
            skipped.append(message)
            continue
        size = path.stat().st_size
        if total + size > budget:
            message = {
                "path": relative,
                "capability": owner,
                "bytes": size,
                "reason": "budget-exceeded",
                "required": required,
            }
            if required:
                raise HarnessError(
                    f"required context exceeds budget at {relative}: {total + size} > {budget} bytes"
                )
            skipped.append(message)
            continue
        selected.append(
            {
                "path": relative,
                "capability": owner,
                "bytes": size,
                "sha256": sha256_file(path),
                "required": required,
            }
        )
        total += size

    return {
        "schema_version": "harness.context-manifest.v1",
        "generated_at": utc_now(),
        "repository": str(root),
        "profile": str(profile.get("id")),
        "profile_path": profile_path.relative_to(root).as_posix()
        if profile_path.is_relative_to(root)
        else str(profile_path),
        "provider_binding": provider_binding,
        "capabilities": [item["id"] for item in selected_capabilities],
        "inventory_hash": inventory["inventory_hash"],
        "budget_bytes": budget,
        "total_bytes": total,
        "selected": selected,
        "skipped": skipped,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, help="Repository root")
    parser.add_argument("--project-profile", type=Path, help="Profile JSON path")
    parser.add_argument(
        "--capability",
        action="append",
        default=[],
        help="Additional capability id or alias",
    )
    parser.add_argument("--max-bytes", type=int, help="Override profile context budget")
    parser.add_argument(
        "--provider",
        help="Override the profile provider with another declared provider",
    )
    parser.add_argument(
        "--quality-tier", help="Override the profile quality tier for this manifest"
    )
    parser.add_argument("--output", type=Path, help="Write manifest to this path")
    args = parser.parse_args()

    root = (args.root or project_root_from(Path(__file__))).resolve()
    profile = (
        args.project_profile
        or root / ".claude" / "registry" / "projects" / "default.json"
    )
    if not profile.is_absolute():
        profile = root / profile
    try:
        manifest = compile_manifest(
            root,
            profile.resolve(),
            args.capability,
            args.max_bytes,
            args.provider,
            args.quality_tier,
        )
    except HarnessError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.output:
        output = args.output if args.output.is_absolute() else root / args.output
        write_json(output, manifest)
        print(output)
    else:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
