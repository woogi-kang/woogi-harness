#!/usr/bin/env python3
"""Run local health checks for the cross-provider Claude Craft harness."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

from harness_runtime_lib import (
    HarnessError,
    build_asset_inventory,
    load_data,
    merge_effective_capabilities,
    parse_frontmatter,
    provider_registry_errors,
    project_root_from,
    resolve_provider_quality,
    validate_registry,
)


@dataclass
class Check:
    name: str
    status: str
    message: str


def bounded_process(
    command: list[str], *, cwd: Path, timeout: int = 60
) -> tuple[bool, str]:
    try:
        process = subprocess.run(
            command,
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)
    output = (process.stdout or process.stderr).strip()
    return process.returncode == 0, output[-1000:]


def run_checks(
    root: Path, *, require_host_model_attestation: bool = False
) -> list[Check]:
    checks: list[Check] = []

    for name in ("AGENTS.md", "GEMINI.md"):
        path = root / name
        if path.is_symlink() and os.readlink(path) == "CLAUDE.md":
            checks.append(Check(f"link:{name}", "pass", "links to CLAUDE.md"))
        else:
            checks.append(
                Check(f"link:{name}", "error", "must be a symlink to CLAUDE.md")
            )
    skills_link = root / ".agents" / "skills"
    if skills_link.is_symlink() and os.readlink(skills_link) == "../.claude/skills":
        checks.append(
            Check("link:.agents/skills", "pass", "links to canonical skill root")
        )
    else:
        checks.append(
            Check("link:.agents/skills", "error", "must link to ../.claude/skills")
        )

    common_rules = root / ".claude" / "rules" / "common"
    rule_count = len(list(common_rules.glob("*.md"))) if common_rules.is_dir() else 0
    checks.append(
        Check(
            "rules",
            "pass" if rule_count else "error",
            f"{rule_count} common rule files" if rule_count else "common rules missing",
        )
    )

    try:
        capabilities, issues = validate_registry(root, root / ".claude" / "registry")
        inventory = build_asset_inventory(root)
        effective = merge_effective_capabilities(capabilities, inventory)
        errors = [issue for issue in issues if issue.severity == "error"]
        warnings = [issue for issue in issues if issue.severity == "warning"]
        classified_legacy = warnings and all(
            issue.code == "frontmatter_collision" for issue in warnings
        )
        warning_label = (
            f"{len(warnings)} qualified legacy duplicate groups"
            if classified_legacy
            else f"{len(warnings)} registry warnings"
        )
        checks.append(
            Check(
                "registry",
                "error" if errors else "pass",
                f"{len(capabilities)} static + {inventory['asset_count']} inventoried = "
                f"{len(effective)} resolvable, {len(errors)} errors, {warning_label}",
            )
        )
    except HarnessError as exc:
        checks.append(Check("registry", "error", str(exc)))

    hook_names = ("usage-tracker.sh", "quality-gate.sh", "git-push-guard.sh")
    missing_hooks = []
    non_executable = []
    for name in hook_names:
        path = root / ".claude" / "hooks" / name
        if not path.is_file():
            missing_hooks.append(name)
        elif not os.access(path, os.X_OK):
            non_executable.append(name)
    settings_path = root / ".claude" / "settings.json"
    settings_text = (
        settings_path.read_text(encoding="utf-8") if settings_path.is_file() else ""
    )
    configured = all(name in settings_text for name in hook_names)
    if missing_hooks or non_executable or not configured:
        details = []
        if missing_hooks:
            details.append("missing=" + ",".join(missing_hooks))
        if non_executable:
            details.append("non-executable=" + ",".join(non_executable))
        if not configured:
            details.append("settings hook references incomplete")
        checks.append(Check("hooks", "error", "; ".join(details)))
    else:
        checks.append(
            Check(
                "hooks",
                "pass",
                "required hooks exist, are executable, and are configured",
            )
        )

    provider_path = root / ".claude" / "registry" / "providers" / "core.yaml"
    try:
        provider_data = load_data(provider_path)
        ids = {item.get("id") for item in provider_data.get("providers", [])}
        expected = {"claude", "codex", "gemini", "opencode"}
        policy = provider_data.get("model_policy", {})
        quality_classes = provider_data.get("quality_classes", [])
        class_ids = {item.get("id") for item in quality_classes}
        expected_classes = {
            "reasoning_high",
            "implementation",
            "fast_scan",
            "independent_critic",
        }
        classes_valid = expected_classes <= class_ids and all(
            item.get("required_capabilities") and item.get("required_tools")
            for item in quality_classes
        )
        adapters_cover_classes = all(
            expected_classes <= set(item.get("quality_classes", []))
            for item in provider_data.get("providers", [])
            if item.get("id") in expected
        )
        valid = (
            expected <= ids
            and policy.get("dangerous_permission_defaults") is False
            and policy.get("disallow_hardcoded_general_models") is True
            and classes_valid
            and adapters_cover_classes
            and not provider_registry_errors(provider_data)
        )
        invalid_agent_pins = []
        asset_inventory = build_asset_inventory(root)
        active_assets = [
            item
            for item in asset_inventory.get("entries", [])
            if item.get("status") == "active"
            and item.get("kind") in {"agent", "skill", "command"}
        ]
        for item in active_assets:
            source = item["source"]
            agent_path = root / source
            frontmatter = parse_frontmatter(agent_path)
            model = frontmatter.get("model")
            quality_tier = frontmatter.get("quality_tier")
            if item.get("kind") == "agent" and model != "inherit":
                invalid_agent_pins.append(source)
            if model and model != "inherit":
                invalid_agent_pins.append(source)
            if model and quality_tier not in expected_classes:
                invalid_agent_pins.append(source)
        inventoried_sources = {item["source"] for item in active_assets}
        for command_path in sorted((root / ".claude" / "commands").glob("**/*.md")):
            source = command_path.relative_to(root).as_posix()
            if source in inventoried_sources:
                continue
            frontmatter = parse_frontmatter(command_path)
            model = frontmatter.get("model")
            if model and (
                model != "inherit"
                or frontmatter.get("quality_tier") not in expected_classes
            ):
                invalid_agent_pins.append(source)
        forbidden_model = re.compile(r"\b(?:opus|sonnet|haiku)\b", re.IGNORECASE)
        for asset_root in ("agents", "skills", "commands"):
            for path in sorted((root / ".claude" / asset_root).glob("**/*.md")):
                if {"_vendor", "archive"}.intersection(path.parts):
                    continue
                if forbidden_model.search(
                    path.read_text(encoding="utf-8", errors="replace")
                ):
                    invalid_agent_pins.append(path.relative_to(root).as_posix())
        valid = valid and not invalid_agent_pins
        profile = load_data(root / ".claude" / "registry" / "projects" / "default.json")
        selected_provider = (
            profile.get("selected_provider") if isinstance(profile, dict) else None
        )
        declared_providers = (
            set(profile.get("providers", [])) if isinstance(profile, dict) else set()
        )
        try:
            profile_binding = resolve_provider_quality(
                provider_data,
                str(selected_provider),
                str(profile.get("default_quality_tier", "")),
            )
        except HarnessError:
            profile_binding = None
        valid = (
            valid
            and selected_provider in declared_providers
            and profile_binding is not None
        )
        for active_policy_file in (
            root / "README.md",
            root / "docs" / "CONTRIBUTING.md",
            root / ".claude" / "statusline.py",
        ):
            if active_policy_file.is_file() and forbidden_model.search(
                active_policy_file.read_text(encoding="utf-8", errors="replace")
            ):
                invalid_agent_pins.append(
                    active_policy_file.relative_to(root).as_posix()
                )
        valid = valid and not invalid_agent_pins
        checks.append(
            Check(
                "provider-policy",
                "pass" if valid else "error",
                "four adapters, provider-neutral quality classes, inherited agent models, and safe defaults"
                if valid
                else "provider adapters, agent model pins, quality classes, or safe policy incomplete",
            )
        )
        image_policy_path = (
            root / ".claude" / "registry" / "providers" / "image-generation.yaml"
        )
        image_policy = (
            load_data(image_policy_path) if image_policy_path.is_file() else {}
        )
        image_generation = (
            image_policy.get("generation", {}) if isinstance(image_policy, dict) else {}
        )
        image_prompt_compiler = (
            image_policy.get("prompt_compiler", {})
            if isinstance(image_policy, dict)
            else {}
        )
        assurance = (
            image_policy.get("assurance", {}) if isinstance(image_policy, dict) else {}
        )
        runtime_hooks = (
            image_policy.get("runtime_hooks", [])
            if isinstance(image_policy, dict)
            else []
        )
        codex_provider = next(
            (
                item
                for item in provider_data.get("providers", [])
                if item.get("id") == "codex"
            ),
            {},
        )
        expected_host_contract = {
            "id": "codex.image-generation",
            "tool": "image_gen__imagegen",
            "alias": "$imagegen",
            "schema_model_field": None,
            "model_binding": "trusted-host-fixed",
            "required_model": "gpt-image-2",
            "hook_interception": False,
        }
        image_local_valid = (
            policy.get("image_policy") == "separate-provider-policy"
            and image_policy.get("schema_version")
            == "harness.image-generation-policy.v2"
            and image_prompt_compiler.get("id") == "image-prompt"
            and image_prompt_compiler.get("local_patches") == []
            and image_prompt_compiler.get(
                "upstream_provider_instructions_authoritative"
            )
            is False
            and image_generation.get("provider") == "codex"
            and image_generation.get("tool_alias") == "$imagegen"
            and image_generation.get("host_tool") == "image_gen__imagegen"
            and image_generation.get("required_model") == "gpt-image-2"
            and image_generation.get("input_mapping") == {"full_prompt": "prompt"}
            and image_generation.get("fallback") == []
            and assurance.get("model") == "trusted-host-not-locally-observable"
            and assurance.get("allowed_provenance_claim")
            == "generated_under_trusted_host_contract"
            and all(hook.get("provider") == "claude" for hook in runtime_hooks)
            and codex_provider.get("hook_support") == []
            and expected_host_contract in codex_provider.get("host_tool_contracts", [])
        )
        if image_local_valid:
            checks.append(
                Check(
                    "image-policy-local",
                    "pass",
                    "exact Gongnyang compiler, prompt mapping, route denial, and no fallback",
                )
            )
            checks.append(
                Check(
                    "image-model-boundary",
                    "error" if require_host_model_attestation else "pass",
                    "blocked_imagegen_model_unverifiable: host model attestation is unavailable"
                    if require_host_model_attestation
                    else "Codex host contract requires gpt-image-2; model identity is explicitly not locally observable",
                )
            )
        else:
            checks.append(
                Check(
                    "image-policy-local",
                    "error",
                    "single image provider policy missing or drifted",
                )
            )
            checks.append(
                Check(
                    "image-model-boundary",
                    "error",
                    "Codex trusted-host contract missing or falsely claims local interception",
                )
            )
    except HarnessError as exc:
        checks.append(Check("provider-policy", "error", str(exc)))

    eval_root = root / ".claude" / "evals"
    presets = list(eval_root.glob("presets/*.md")) if eval_root.is_dir() else []
    executable_eval_files = (
        eval_root / "ui-design" / "grader.py",
        eval_root / "ui-design" / "cases" / "detector-regression.json",
        eval_root / "korean-typography" / "grader.sh",
    )
    evals_valid = bool(presets) and all(
        path.is_file() for path in executable_eval_files
    )
    eval_details: list[str] = []
    if evals_valid:
        ui_ok, ui_output = bounded_process(
            [sys.executable, str(executable_eval_files[0]), "self-test"], cwd=root
        )
        if not ui_ok:
            eval_details.append("UI grader self-test failed: " + ui_output)
        korean_grader = executable_eval_files[2]
        if not os.access(korean_grader, os.X_OK):
            korean_ok = False
            korean_output = "Korean grader is not executable"
        else:
            with tempfile.TemporaryDirectory(
                prefix="harness-doctor-korean-"
            ) as temporary:
                artifact = Path(temporary) / "known-good.html"
                artifact.write_text(
                    "<style>body{font-family:Pretendard,sans-serif;word-break: keep-all;"
                    "overflow-wrap: break-word;line-height:1.6}"
                    "code,pre{font-family:ui-monospace,monospace;overflow-wrap:anywhere}"
                    "</style><main>검증 문서</main>\n",
                    encoding="utf-8",
                )
                korean_ok, korean_output = bounded_process(
                    [str(korean_grader), str(executable_eval_files[1]), str(artifact)],
                    cwd=root,
                )
        if not korean_ok:
            eval_details.append(
                "Korean grader known-good case failed: " + korean_output
            )
        evals_valid = ui_ok and korean_ok
    checks.append(
        Check(
            "evals",
            "pass" if evals_valid else "error",
            f"{len(presets)} presets; UI self-test and Korean known-good case passed"
            if evals_valid
            else "; ".join(eval_details)
            or "eval presets or executable graders missing",
        )
    )

    stack_verifier = root / "scripts" / "verify-stack-registry.py"
    stack_registry = root / ".claude" / "registry" / "tech-stacks"
    stack_valid = stack_verifier.is_file() and stack_registry.is_dir()
    stack_output = ""
    if stack_valid:
        stack_valid, stack_output = bounded_process(
            [sys.executable, str(stack_verifier), "--all"], cwd=root, timeout=90
        )
    checks.append(
        Check(
            "tech-stack-registry",
            "pass" if stack_valid else "error",
            "version channels, source lock, generated defaults, and inline pins verified"
            if stack_valid
            else stack_output or "technology stack registry or verifier missing",
        )
    )

    required_pack_runtime = {
        "scripts/brain-memory.sh",
        "scripts/brain-memory-qa.sh",
        "scripts/brain-pilot.sh",
        "scripts/context-pack-gate.py",
        "scripts/harness-provider.py",
        "scripts/orchestrate-worktrees.py",
        "scripts/sprint-reset-loop.sh",
        "scripts/verify-stack-registry.py",
    }
    try:
        default_pack = load_data(
            root / ".claude" / "project-packs" / "default" / "pack.json"
        )
        pack_paths = (
            set(default_pack.get("paths", []))
            if isinstance(default_pack, dict)
            else set()
        )
        missing_pack_runtime = sorted(
            path
            for path in required_pack_runtime
            if path not in pack_paths or not (root / path).is_file()
        )
        checks.append(
            Check(
                "pack-closure",
                "error" if missing_pack_runtime else "pass",
                "missing shared runtime dependencies: "
                + ", ".join(missing_pack_runtime)
                if missing_pack_runtime
                else "shared command, memory, provider, orchestration, and verifier dependencies are packed",
            )
        )
    except HarnessError as exc:
        checks.append(Check("pack-closure", "error", str(exc)))

    quality_gate = root / ".claude" / "hooks" / "quality-gate.sh"
    quality_text = (
        quality_gate.read_text(encoding="utf-8") if quality_gate.is_file() else ""
    )
    quality_safe = (
        "|| true" not in quality_text
        and "npx prettier --write" not in quality_text
        and "design-slop-hard-gate" in quality_text
    )
    checks.append(
        Check(
            "quality-gate",
            "pass" if quality_safe else "error",
            "read-only formatter/linter feedback plus UI hard gate"
            if quality_safe
            else "quality hook hides failures, mutates implicitly, or lacks UI gate",
        )
    )

    orchestrator = root / "scripts" / "orchestrate-worktrees.py"
    orchestrator_text = (
        orchestrator.read_text(encoding="utf-8") if orchestrator.is_file() else ""
    )
    if not orchestrator.is_file():
        checks.append(
            Check("permission-default", "error", "orchestrator runtime missing")
        )
    elif "--dangerously-skip-permissions -p -" in orchestrator_text:
        checks.append(
            Check(
                "permission-default",
                "error",
                "orchestrator still contains a dangerous default launcher",
            )
        )
    else:
        checks.append(
            Check(
                "permission-default",
                "pass",
                "dangerous permissions are not enabled by default",
            )
        )
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, help="Repository root")
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--strict", action="store_true", help="Treat warnings as failures"
    )
    parser.add_argument(
        "--require-host-model-attestation",
        action="store_true",
        help="Fail unless the opaque Codex host reports an attestable image model identity",
    )
    args = parser.parse_args()
    root = (args.root or project_root_from(Path(__file__))).resolve()
    checks = run_checks(
        root,
        require_host_model_attestation=args.require_host_model_attestation,
    )
    if args.json:
        print(
            json.dumps(
                {"root": str(root), "checks": [asdict(check) for check in checks]},
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        for check in checks:
            icon = {"pass": "PASS", "warning": "WARN", "error": "FAIL"}[check.status]
            print(f"{icon:<4} {check.name:<24} {check.message}")
    failed = any(
        check.status == "error" or (args.strict and check.status == "warning")
        for check in checks
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
