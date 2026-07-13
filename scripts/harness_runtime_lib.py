#!/usr/bin/env python3
"""Shared, dependency-free primitives for the Woogi Harness runtime."""

from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import re
import tempfile
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


EXECUTION_STATES = frozenset(
    {"pending", "running", "succeeded", "failed", "blocked", "needs_approval"}
)
EXECUTION_ARTIFACT_ROOT = "artifacts"
TERMINAL_STATES = frozenset({"succeeded", "failed"})
ALLOWED_TRANSITIONS = {
    "pending": {"running", "blocked", "needs_approval", "failed"},
    "running": {"succeeded", "failed", "blocked", "needs_approval"},
    "blocked": {"running", "failed", "needs_approval"},
    "needs_approval": {"running", "failed", "blocked"},
    "succeeded": set(),
    "failed": set(),
}


class HarnessError(RuntimeError):
    """A deterministic harness validation or runtime error."""


@dataclass(frozen=True)
class RegistryIssue:
    severity: str
    code: str
    message: str
    paths: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "paths": list(self.paths),
        }


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_data(path: Path) -> Any:
    """Load JSON or JSON-compatible YAML without optional dependencies.

    Registry ``.yaml`` files intentionally use JSON syntax. JSON is a valid YAML
    subset, which keeps every harness CLI stdlib-only and deterministic.
    """
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise HarnessError(f"file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise HarnessError(f"invalid JSON-compatible data in {path}: {exc}") from exc


def provider_registry_errors(data: Any) -> list[str]:
    """Validate executable provider-to-quality-class capability bindings."""
    if (
        not isinstance(data, dict)
        or data.get("schema_version") != "harness.providers.v1"
    ):
        return ["provider registry schema_version must be harness.providers.v1"]
    raw_classes = data.get("quality_classes")
    raw_providers = data.get("providers")
    if not isinstance(raw_classes, list) or not isinstance(raw_providers, list):
        return ["provider registry requires quality_classes and providers arrays"]

    errors: list[str] = []
    classes: dict[str, dict[str, Any]] = {}
    for item in raw_classes:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("id"), str)
            or not item.get("id", "").strip()
        ):
            errors.append("quality class entries require string ids")
            continue
        class_id = item["id"]
        if class_id in classes:
            errors.append(f"duplicate quality class: {class_id}")
        classes[class_id] = item
        for field in ("required_capabilities", "required_tools"):
            value = item.get(field)
            if (
                not isinstance(value, list)
                or not value
                or any(not isinstance(v, str) for v in value)
            ):
                errors.append(f"quality class {class_id} requires non-empty {field}")
        if item.get("context_policy") not in {"isolated", "fresh_required"}:
            errors.append(f"quality class {class_id} requires a valid context_policy")

    provider_ids: set[str] = set()
    for provider in raw_providers:
        if (
            not isinstance(provider, dict)
            or not isinstance(provider.get("id"), str)
            or not provider.get("id", "").strip()
        ):
            errors.append("provider entries require string ids")
            continue
        provider_id = provider["id"]
        if provider_id in provider_ids:
            errors.append(f"duplicate provider: {provider_id}")
        provider_ids.add(provider_id)
        supported = provider.get("quality_classes")
        capabilities = set(provider.get("quality_capabilities", []))
        tools = set(provider.get("tools", []))
        adapter = provider.get("quality_adapter")
        bindings = adapter.get("bindings", {}) if isinstance(adapter, dict) else {}
        tool_adapter = provider.get("tool_adapter")
        execution_adapter = provider.get("execution_adapter")
        execution_kind: str | None = None
        if tool_adapter != "native":
            errors.append(f"provider {provider_id} tool_adapter must be native")
        if not isinstance(execution_adapter, dict):
            errors.append(f"provider {provider_id} requires execution_adapter")
        else:
            execution_kind = execution_adapter.get("kind")
            if execution_kind == "cli":
                executable = execution_adapter.get("executable")
                args = execution_adapter.get("args")
                if not isinstance(executable, str) or not executable.strip():
                    errors.append(
                        f"provider {provider_id} cli adapter requires executable"
                    )
                if not isinstance(args, list) or any(
                    not isinstance(value, str) for value in args
                ):
                    errors.append(
                        f"provider {provider_id} cli adapter requires string args"
                    )
                if execution_adapter.get("input") != "stdin":
                    errors.append(
                        f"provider {provider_id} cli adapter input must be stdin"
                    )
            elif execution_kind == "host-native":
                if execution_adapter.get("profile") != f"{provider_id}-native":
                    errors.append(
                        f"provider {provider_id} host-native profile must be {provider_id}-native"
                    )
            else:
                errors.append(
                    f"provider {provider_id} execution_adapter kind is invalid"
                )
        # Host boundary for the image-prompt -> validator -> Codex image tool route.
        expected_codex_host_contracts = [
            {
                "id": "codex.image-generation",
                "tool": "image_gen__imagegen",
                "alias": "$imagegen",
                "schema_model_field": None,
                "model_binding": "trusted-host-fixed",
                "required_model": "gpt-image-2",
                "hook_interception": False,
            }
        ]
        host_tool_contracts = provider.get("host_tool_contracts")
        if provider_id == "codex":
            if host_tool_contracts != expected_codex_host_contracts:
                errors.append(
                    "provider codex host_tool_contracts must declare the exact image generation host binding"
                )
        elif host_tool_contracts is not None:
            errors.append(
                f"provider {provider_id} must not declare Codex host tool contracts"
            )
        if not isinstance(supported, list) or not supported:
            errors.append(f"provider {provider_id} requires quality_classes")
            continue
        if (
            not isinstance(adapter, dict)
            or not isinstance(bindings, dict)
            or adapter.get("strategy") != "provider-native"
        ):
            errors.append(
                f"provider {provider_id} requires a provider-native quality_adapter"
            )
            bindings = {}
        if isinstance(supported, list) and set(bindings) != set(supported):
            errors.append(
                f"provider {provider_id} quality bindings must exactly match supported classes"
            )
        seen_execution_profiles: set[str] = set()
        for class_id in supported:
            quality_class = classes.get(class_id)
            if quality_class is None:
                errors.append(
                    f"provider {provider_id} references unknown quality class {class_id}"
                )
                continue
            missing_capabilities = (
                set(quality_class.get("required_capabilities", [])) - capabilities
            )
            missing_tools = set(quality_class.get("required_tools", [])) - tools
            if missing_capabilities:
                errors.append(
                    f"provider {provider_id}/{class_id} missing capabilities: "
                    + ", ".join(sorted(missing_capabilities))
                )
            if missing_tools:
                errors.append(
                    f"provider {provider_id}/{class_id} missing tools: "
                    + ", ".join(sorted(missing_tools))
                )
            binding = bindings.get(class_id)
            if not isinstance(binding, dict) or binding.get("selection") != class_id:
                errors.append(
                    f"provider {provider_id}/{class_id} missing executable selection binding"
                )
            elif binding.get("context_policy") != quality_class.get("context_policy"):
                errors.append(
                    f"provider {provider_id}/{class_id} context policy does not match the quality class"
                )
            if not isinstance(binding, dict):
                continue
            execution_profile = binding.get("execution_profile")
            if not isinstance(execution_profile, dict):
                errors.append(
                    f"provider {provider_id}/{class_id} requires execution_profile"
                )
                continue
            if execution_kind == "cli":
                if execution_profile.get("kind") != "cli-args":
                    errors.append(
                        f"provider {provider_id}/{class_id} execution profile must use cli-args"
                    )
                    continue
                profile_args = execution_profile.get("args")
                if (
                    not isinstance(profile_args, list)
                    or not profile_args
                    or any(
                        not isinstance(value, str) or not value.strip()
                        for value in profile_args
                    )
                ):
                    errors.append(
                        f"provider {provider_id}/{class_id} cli execution profile requires args"
                    )
                    continue
                forbidden_flags = {
                    "--model",
                    "--fallback-model",
                    "--continue",
                    "--resume",
                    "-c",
                    "-r",
                }
                if forbidden_flags.intersection(profile_args):
                    errors.append(
                        f"provider {provider_id}/{class_id} cli execution profile must stay model-neutral and fresh"
                    )
                profile_identity = json.dumps(profile_args, separators=(",", ":"))
            else:
                expected_profile = f"{provider_id}-native:{class_id}"
                if execution_profile != {
                    "kind": "host-native",
                    "profile": expected_profile,
                }:
                    errors.append(
                        f"provider {provider_id}/{class_id} host-native profile must be {expected_profile}"
                    )
                profile_identity = str(execution_profile.get("profile", ""))
            if profile_identity in seen_execution_profiles:
                errors.append(
                    f"provider {provider_id} quality classes must use distinct execution profiles"
                )
            seen_execution_profiles.add(profile_identity)
    return errors


def resolve_provider_quality(
    data: Any, provider_id: str, quality_tier: str
) -> dict[str, Any]:
    """Resolve and enforce one provider-native quality-class adapter binding."""
    errors = provider_registry_errors(data)
    if errors:
        raise HarnessError("invalid provider registry: " + "; ".join(errors))
    classes = {item["id"]: item for item in data["quality_classes"]}
    providers = {item["id"]: item for item in data["providers"]}
    provider = providers.get(provider_id)
    if provider is None:
        raise HarnessError(f"unknown provider: {provider_id}")
    if quality_tier not in classes:
        raise HarnessError(f"unknown quality tier: {quality_tier}")
    if quality_tier not in provider["quality_classes"]:
        raise HarnessError(
            f"provider {provider_id} does not support quality tier {quality_tier}"
        )
    quality_class = classes[quality_tier]
    binding = provider["quality_adapter"]["bindings"][quality_tier]
    payload = {
        "schema_version": "harness.provider-binding.v1",
        "provider": provider_id,
        "quality_tier": quality_tier,
        "selection": binding["selection"],
        "context_policy": binding["context_policy"],
        "required_capabilities": list(quality_class["required_capabilities"]),
        "required_tools": list(quality_class["required_tools"]),
        "adapter": provider["tool_adapter"],
        "execution_adapter": provider["execution_adapter"],
        "execution_profile": binding["execution_profile"],
        "host_tool_contracts": list(provider.get("host_tool_contracts", [])),
        "status": "supported",
    }
    payload["binding_hash"] = sha256_bytes(
        json.dumps(
            payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    )
    return payload


def write_json(path: Path, value: Any) -> None:
    """Atomically write formatted JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def project_root_from(script_path: Path) -> Path:
    return script_path.resolve().parent.parent


def parse_frontmatter(path: Path) -> dict[str, Any]:
    """Parse only the bounded frontmatter prefix, never the Markdown body."""
    try:
        lines: list[str] = []
        total_bytes = 0
        closed = False
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for index, line in enumerate(handle):
                if index >= 512:
                    break
                total_bytes += len(line.encode("utf-8"))
                if total_bytes > 65536:
                    break
                lines.append(line.rstrip("\r\n"))
                if index > 0 and line.strip() == "---":
                    closed = True
                    break
    except (OSError, UnicodeDecodeError):
        return {}
    if not lines or lines[0].strip() != "---" or not closed:
        return {}

    result: dict[str, Any] = {}
    current_list: str | None = None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indented = line[:1].isspace()
        if indented and stripped.startswith("-") and current_list:
            result.setdefault(current_list, []).append(_unquote(stripped[1:].strip()))
            continue
        if indented:
            continue
        if ":" not in line:
            current_list = None
            continue
        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if not key:
            continue
        if not value:
            result[key] = []
            current_list = key
        elif value.startswith("[") and value.endswith("]"):
            try:
                result[key] = json.loads(value.replace("'", '"'))
            except json.JSONDecodeError:
                result[key] = [
                    _unquote(item.strip())
                    for item in value[1:-1].split(",")
                    if item.strip()
                ]
            current_list = None
        else:
            result[key] = _unquote(value)
            current_list = None
    return result


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def scan_frontmatter_catalog(repo_root: Path) -> dict[str, list[str]]:
    """Return frontmatter names mapped to repo-relative source paths."""
    paths = list((repo_root / ".claude" / "skills").glob("**/SKILL.md"))
    paths.extend(_safe_vendored_skill_entrypoints(repo_root))
    paths.extend((repo_root / ".claude" / "agents").glob("**/*.md"))
    paths.extend((repo_root / ".claude" / "commands").glob("**/*.md"))
    catalog: dict[str, list[str]] = {}
    for path in sorted(set(paths)):
        name = str(parse_frontmatter(path).get("name", "")).strip()
        if not name:
            continue
        relative = path.relative_to(repo_root).as_posix()
        catalog.setdefault(name, []).append(relative)
    return catalog


def _safe_vendored_skill_entrypoints(repo_root: Path) -> list[Path]:
    """Return top-level linked skills only when their real target stays in third_party.

    ``Path.glob('**/SKILL.md')`` deliberately does not recurse through linked
    directories.  A small number of exact-vendored skills are linked into the
    canonical skill root, so inspect only those top-level links and reject
    missing targets, nested link traversal, and targets outside this repository's
    ``third_party`` tree.
    """
    skill_root = repo_root / ".claude" / "skills"
    vendor_root = repo_root / "third_party"
    if not skill_root.is_dir() or not vendor_root.is_dir():
        return []
    try:
        trusted_root = vendor_root.resolve(strict=True)
    except OSError:
        return []
    entrypoints: list[Path] = []
    for linked_skill in sorted(skill_root.iterdir()):
        if not linked_skill.is_symlink():
            continue
        try:
            resolved = linked_skill.resolve(strict=True)
            resolved.relative_to(trusted_root)
        except (OSError, RuntimeError, ValueError):
            continue
        entrypoint = linked_skill / "SKILL.md"
        if resolved.is_dir() and entrypoint.is_file() and not entrypoint.is_symlink():
            entrypoints.append(entrypoint)
    return entrypoints


def _inventory_asset_id(kind: str, source: str, name: str) -> str:
    ascii_name = (
        unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    )
    readable = re.sub(r"[^a-z0-9]+", "-", ascii_name.lower()).strip("-") or "asset"
    path_hash = hashlib.sha256(source.encode("utf-8")).hexdigest()[:12]
    return f"{kind}.path.{readable}.{path_hash}"


def _qualified_inventory_alias(kind: str, root: Path, path: Path, name: str) -> str:
    if kind == "skill":
        relative = path.relative_to(root / ".claude" / "skills")
        parents = relative.parent.parts
        scope = parents[-2] if len(parents) >= 2 else "root"
    elif kind == "agent":
        relative = path.relative_to(root / ".claude" / "agents")
        scope = relative.parent.parts[-1] if relative.parent.parts else "root"
    else:
        relative = path.relative_to(root / ".claude" / "commands")
        scope = relative.parent.parts[-1] if relative.parent.parts else "root"
    return f"{kind}:{scope}/{name}"


SUPPORTING_AGENT_DIRS = frozenset(
    {
        "contracts",
        "examples",
        "initialization",
        "mcp",
        "phases",
        "references",
        "shared",
        "skills",
        "state",
        "templates",
        "verification",
    }
)


def is_supporting_agent_path(path: Path, agent_root: Path) -> bool:
    """Classify agent documentation that must never become a callable agent."""
    relative = path.relative_to(agent_root)
    directory_parts = set(relative.parts[:-1])
    filename = relative.name.lower()
    return (
        bool(directory_parts & SUPPORTING_AGENT_DIRS)
        or filename in {"readme.md", "usage-guide.md"}
        or relative.stem.lower().endswith("-flow")
    )


def build_asset_inventory(repo_root: Path) -> dict[str, Any]:
    """Build a bounded identity inventory for every frontmatter skill/agent asset."""
    raw_assets: list[dict[str, Any]] = []
    roots = (
        ("skill", repo_root / ".claude" / "skills", "**/SKILL.md"),
        ("agent", repo_root / ".claude" / "agents", "**/*.md"),
        ("command", repo_root / ".claude" / "commands", "**/*.md"),
    )
    for kind, asset_root, pattern in roots:
        if not asset_root.is_dir():
            continue
        paths = list(asset_root.glob(pattern))
        if kind == "skill":
            paths.extend(_safe_vendored_skill_entrypoints(repo_root))
        for path in sorted(set(paths)):
            name = str(parse_frontmatter(path).get("name", "")).strip()
            if not name:
                continue
            source = path.relative_to(repo_root).as_posix()
            supporting = kind == "agent" and is_supporting_agent_path(path, asset_root)
            raw_assets.append(
                {
                    "id": _inventory_asset_id(kind, source, name),
                    "kind": kind,
                    "source": source,
                    "frontmatter_name": name,
                    "qualified_alias": _qualified_inventory_alias(
                        kind, repo_root, path, name
                    ),
                    "status": "supporting" if supporting else "active",
                }
            )

    name_counts: dict[str, int] = {}
    qualified_counts: dict[str, int] = {}
    for asset in raw_assets:
        name_counts[asset["frontmatter_name"]] = (
            name_counts.get(asset["frontmatter_name"], 0) + 1
        )
        qualified_counts[asset["qualified_alias"]] = (
            qualified_counts.get(asset["qualified_alias"], 0) + 1
        )

    entries: list[dict[str, Any]] = []
    ids: set[str] = set()
    for asset in raw_assets:
        if asset["id"] in ids:
            raise HarnessError(f"generated inventory id collision: {asset['id']}")
        ids.add(asset["id"])
        name = asset["frontmatter_name"]
        aliases: list[str] = []
        if name_counts[name] == 1:
            aliases.append(name)
        if qualified_counts[asset["qualified_alias"]] == 1:
            aliases.append(asset["qualified_alias"])
        entries.append(
            {
                "id": asset["id"],
                "kind": asset["kind"],
                "source": asset["source"],
                "frontmatter_name": name,
                "aliases": aliases,
                "duplicate_group": f"frontmatter:{name}"
                if name_counts[name] > 1
                else None,
                "duplicate_count": name_counts[name],
                "status": asset["status"],
                "qualified": True,
                "allow_duplicate_frontmatter": name_counts[name] > 1,
                "context_files": [],
                "required_context": False,
                "_generated": True,
            }
        )
    entries.sort(key=lambda item: item["id"])
    fingerprint_payload = json.dumps(
        entries, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    duplicate_groups = {
        name: count for name, count in sorted(name_counts.items()) if count > 1
    }
    return {
        "schema_version": "harness.asset-inventory.v1",
        "generated_at": utc_now(),
        "inventory_hash": hashlib.sha256(
            fingerprint_payload.encode("utf-8")
        ).hexdigest(),
        "asset_count": len(entries),
        "duplicate_groups": duplicate_groups,
        "entries": entries,
    }


def merge_effective_capabilities(
    static_capabilities: list[dict[str, Any]],
    inventory: dict[str, Any],
) -> list[dict[str, Any]]:
    """Merge generated assets without shadowing explicit canonical records."""
    effective = [dict(item) for item in static_capabilities]
    static_sources = {str(item.get("source", "")) for item in static_capabilities}
    used_names = set(capability_index(static_capabilities))
    for raw_entry in inventory.get("entries", []):
        if raw_entry.get("status") != "active":
            continue
        if raw_entry.get("source") in static_sources:
            continue
        entry = dict(raw_entry)
        if entry["id"] in used_names:
            raise HarnessError(
                f"generated id collides with canonical registry: {entry['id']}"
            )
        entry["aliases"] = [
            alias for alias in entry.get("aliases", []) if alias not in used_names
        ]
        effective.append(entry)
        used_names.add(entry["id"])
        used_names.update(entry["aliases"])
    return effective


def load_capabilities(registry_root: Path) -> list[dict[str, Any]]:
    capability_dir = registry_root / "capabilities"
    if not capability_dir.is_dir():
        raise HarnessError(f"capability registry missing: {capability_dir}")
    capabilities: list[dict[str, Any]] = []
    collections = (
        ("capabilities", "capabilities", None),
        ("agents", "agents", "agent"),
        ("skills", "skills", "skill"),
    )
    for directory_name, collection_key, default_kind in collections:
        directory = registry_root / directory_name
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.json")):
            data = load_data(path)
            entries = data.get(collection_key, []) if isinstance(data, dict) else data
            if not isinstance(entries, list):
                raise HarnessError(f"{collection_key} must be a list: {path}")
            for entry in entries:
                if not isinstance(entry, dict):
                    raise HarnessError(
                        f"{collection_key} entry must be an object: {path}"
                    )
                item = dict(entry)
                if default_kind:
                    item.setdefault("kind", default_kind)
                item["_registry_file"] = path.as_posix()
                capabilities.append(item)
    return capabilities


def validate_registry(
    repo_root: Path,
    registry_root: Path,
    *,
    strict_legacy: bool = False,
) -> tuple[list[dict[str, Any]], list[RegistryIssue]]:
    capabilities = load_capabilities(registry_root)
    issues: list[RegistryIssue] = []
    ids: dict[str, str] = {}
    names: dict[str, dict[str, str]] = {}

    for capability in capabilities:
        capability_id = str(capability.get("id", "")).strip()
        registry_file = str(capability.get("_registry_file", ""))
        if not capability_id:
            issues.append(
                RegistryIssue(
                    "error", "missing_id", "capability has no id", (registry_file,)
                )
            )
            continue
        if capability_id in ids:
            issues.append(
                RegistryIssue(
                    "error",
                    "duplicate_id",
                    f"duplicate capability id: {capability_id}",
                    (ids[capability_id], registry_file),
                )
            )
        ids[capability_id] = registry_file

        aliases = capability.get("aliases", [])
        if not isinstance(aliases, list):
            issues.append(
                RegistryIssue(
                    "error",
                    "invalid_aliases",
                    f"aliases must be a list: {capability_id}",
                )
            )
            aliases = []
        current_identity = {
            "id": capability_id,
            "kind": str(capability.get("kind", "capability")),
            "status": str(capability.get("status", "stable")),
            "file": registry_file,
        }
        for name in [capability_id, *[str(alias).strip() for alias in aliases]]:
            if not name:
                issues.append(
                    RegistryIssue(
                        "error", "empty_alias", f"empty alias: {capability_id}"
                    )
                )
                continue
            owner = names.get(name)
            if owner and owner["id"] != capability_id:
                owner_active = owner["status"] not in {"disabled", "deprecated"}
                current_active = current_identity["status"] not in {
                    "disabled",
                    "deprecated",
                }
                active_collision = owner_active and current_active
                issues.append(
                    RegistryIssue(
                        "error" if active_collision else "warning",
                        "active_name_collision"
                        if active_collision
                        else "inactive_name_collision",
                        f"canonical name '{name}' resolves to both "
                        f"{owner['id']} ({owner['kind']}) and "
                        f"{capability_id} ({current_identity['kind']})",
                        (owner["file"], registry_file),
                    )
                )
                continue
            names[name] = current_identity

        source = str(capability.get("source", "")).strip()
        if source:
            source_path = (repo_root / source).resolve()
            try:
                source_path.relative_to(repo_root.resolve())
            except ValueError:
                issues.append(
                    RegistryIssue(
                        "error", "source_escape", f"source escapes repository: {source}"
                    )
                )
            else:
                if not source_path.exists():
                    issues.append(
                        RegistryIssue(
                            "error", "missing_source", f"source not found: {source}"
                        )
                    )

    catalog = scan_frontmatter_catalog(repo_root)
    for name, paths in sorted(catalog.items()):
        if len(paths) > 1:
            severity = "error" if strict_legacy else "warning"
            issues.append(
                RegistryIssue(
                    severity,
                    "frontmatter_collision",
                    f"frontmatter name '{name}' appears {len(paths)} times",
                    tuple(paths),
                )
            )

    for capability in capabilities:
        expected = str(capability.get("frontmatter_name", "")).strip()
        source = str(capability.get("source", "")).strip()
        if not expected:
            continue
        actual = str(parse_frontmatter(repo_root / source).get("name", "")).strip()
        if actual != expected:
            issues.append(
                RegistryIssue(
                    "error",
                    "frontmatter_mismatch",
                    f"{capability.get('id')} expects name '{expected}', found '{actual or '<missing>'}'",
                    (source,),
                )
            )
        matches = catalog.get(expected, [])
        if len(matches) != 1 or (matches and matches[0] != source):
            issues.append(
                RegistryIssue(
                    "error",
                    "registered_name_collision",
                    f"registered frontmatter name '{expected}' is not unique to {source}",
                    tuple(matches),
                )
            )

    return capabilities, issues


def capability_index(
    capabilities: Iterable[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for capability in capabilities:
        for name in [capability.get("id"), *capability.get("aliases", [])]:
            if name:
                index[str(name)] = capability
    return index


def resolve_capabilities(
    capabilities: list[dict[str, Any]], requested: Iterable[str]
) -> list[dict[str, Any]]:
    index = capability_index(capabilities)
    resolved: list[dict[str, Any]] = []
    seen: set[str] = set()
    for name in requested:
        if name not in index:
            raise HarnessError(f"unknown capability: {name}")
        item = index[name]
        capability_id = str(item["id"])
        if capability_id not in seen:
            resolved.append(item)
            seen.add(capability_id)
    return resolved


def ensure_unique_selected_frontmatter(
    repo_root: Path, capabilities: Iterable[dict[str, Any]]
) -> None:
    catalog = scan_frontmatter_catalog(repo_root)
    for capability in capabilities:
        expected = str(capability.get("frontmatter_name", "")).strip()
        if not expected:
            continue
        source = str(capability.get("source", ""))
        matches = catalog.get(expected, [])
        if capability.get("allow_duplicate_frontmatter"):
            if source not in matches:
                raise HarnessError(
                    f"qualified frontmatter source mismatch for '{expected}': {source} not in {matches or 'none'}"
                )
            continue
        if matches != [source]:
            raise HarnessError(
                f"frontmatter name collision for '{expected}': expected {source}, found {matches or 'none'}"
            )


def read_json_stream(path: Path) -> list[dict[str, Any]]:
    """Read JSONL and legacy concatenated objects without skipping corruption."""
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    decoder = json.JSONDecoder()
    entries: list[dict[str, Any]] = []
    cursor = 0
    while cursor < len(text):
        while cursor < len(text) and text[cursor].isspace():
            cursor += 1
        if cursor >= len(text):
            break
        try:
            value, end = decoder.raw_decode(text, cursor)
        except json.JSONDecodeError as exc:
            raise HarnessError(
                f"invalid JSON stream in {path} at line {exc.lineno}, "
                f"column {exc.colno}: {exc.msg}"
            ) from exc
        if not isinstance(value, dict):
            line = text.count("\n", 0, cursor) + 1
            raise HarnessError(
                f"invalid JSON stream in {path} at line {line}: "
                "top-level values must be objects"
            )
        entries.append(value)
        cursor = end
    return entries


def normalize_telemetry_event(event: dict[str, Any]) -> dict[str, Any]:
    """Convert v0 usage records and v1 events into the normalized event shape."""
    if event.get("schema_version") == "harness.telemetry.v1":
        normalized = dict(event)
        normalized.setdefault("metadata", {})
        return normalized
    tool = str(event.get("tool", event.get("subject_type", "unknown")))
    name = str(event.get("name", event.get("subject_id", "unknown")))
    metadata = {
        key: value
        for key, value in event.items()
        if key not in {"timestamp", "session_id", "tool", "name"}
    }
    return {
        "schema_version": "harness.telemetry.v1",
        "timestamp": event.get("timestamp", utc_now()),
        "session_id": event.get("session_id", "unknown"),
        "provider": event.get("provider", "claude"),
        "event_type": event.get("event_type", "invocation"),
        "subject_type": tool,
        "subject_id": name,
        "status": event.get("status", "observed"),
        "duration_ms": event.get("duration_ms"),
        "context_bytes": event.get("context_bytes"),
        "metadata": metadata,
    }


def new_execution_record(
    execution_id: str,
    objective: str,
    success_criteria: list[str],
) -> dict[str, Any]:
    now = utc_now()
    return {
        "schema_version": "harness.execution.v1",
        "execution_id": execution_id,
        "objective": objective,
        "state": "pending",
        "attempt": 0,
        "success_criteria": success_criteria,
        "artifact_root": EXECUTION_ARTIFACT_ROOT,
        "evidence": [],
        "checks": [],
        "stop_reason": None,
        "created_at": now,
        "updated_at": now,
        "history": [
            {"from": None, "to": "pending", "at": now, "reason": "initialized"}
        ],
    }


def _execution_artifact_path(raw_path: str, artifact_root: Path) -> Path:
    relative = Path(raw_path)
    if (
        relative.is_absolute()
        or ".." in relative.parts
        or relative in {Path(""), Path(".")}
    ):
        raise HarnessError(
            f"artifact path must be relative to {EXECUTION_ARTIFACT_ROOT}: {raw_path}"
        )
    if artifact_root.is_symlink() or not artifact_root.is_dir():
        raise HarnessError(
            f"artifact root is missing, symlinked, or not a directory: {artifact_root}"
        )
    root = artifact_root.resolve(strict=True)
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise HarnessError(
                f"artifact path contains a symlink component: {raw_path}"
            )
    try:
        artifact = current.resolve(strict=True)
        artifact.relative_to(root)
    except (OSError, ValueError) as exc:
        raise HarnessError(
            f"artifact is missing or escapes artifact root: {raw_path}"
        ) from exc
    if not artifact.is_file():
        raise HarnessError(f"artifact is not a regular file: {raw_path}")
    return artifact


def validate_execution_record(
    record: dict[str, Any],
    *,
    final: bool = False,
    artifact_root: Path | None = None,
) -> list[str]:
    errors: list[str] = []
    state = record.get("state")
    if record.get("schema_version") != "harness.execution.v1":
        errors.append("schema_version must be harness.execution.v1")
    if not str(record.get("execution_id", "")).strip():
        errors.append("execution_id is required")
    if not str(record.get("objective", "")).strip():
        errors.append("objective is required")
    if record.get("artifact_root") != EXECUTION_ARTIFACT_ROOT:
        errors.append(f"artifact_root must be {EXECUTION_ARTIFACT_ROOT!r}")
    if state not in EXECUTION_STATES:
        errors.append(f"invalid state: {state}")
    attempt = record.get("attempt")
    if not isinstance(attempt, int) or attempt < 0:
        errors.append("attempt must be a non-negative integer")
    criteria = record.get("success_criteria")
    if not isinstance(criteria, list):
        errors.append("success_criteria must be a list")
        criteria = []
    elif any(
        not isinstance(criterion, str) or not criterion.strip()
        for criterion in criteria
    ):
        errors.append("success_criteria must contain non-empty strings")
    elif len(criteria) != len(set(criteria)):
        errors.append("success_criteria must not contain duplicates")
    evidence = record.get("evidence")
    if not isinstance(evidence, list):
        errors.append("evidence must be a list")
        evidence = []
    checks = record.get("checks")
    if not isinstance(checks, list):
        errors.append("checks must be a list")
        checks = []
    history = record.get("history")
    if not isinstance(history, list) or not history:
        errors.append("history must be a non-empty transition list")
        history = []
    else:
        previous: str | None = None
        running_transitions = 0
        for index, event in enumerate(history):
            if not isinstance(event, dict):
                errors.append(f"history[{index}] must be an object")
                continue
            source = event.get("from")
            target = event.get("to")
            if source != previous:
                errors.append(
                    f"history[{index}] transition source {source!r} does not match {previous!r}"
                )
            if target not in EXECUTION_STATES:
                errors.append(f"history[{index}] has invalid target state: {target}")
                continue
            if index == 0:
                if source is not None or target != "pending":
                    errors.append("history must begin with None -> pending")
            elif target not in ALLOWED_TRANSITIONS.get(str(source), set()):
                errors.append(
                    f"history[{index}] transition is not allowed: {source} -> {target}"
                )
            if not isinstance(event.get("at"), str) or not event.get("at", "").strip():
                errors.append(f"history[{index}] requires a timestamp")
            if target == "running":
                running_transitions += 1
            previous = str(target)
        if previous != state:
            errors.append(
                f"history terminal state {previous!r} does not match record state {state!r}"
            )
        if isinstance(attempt, int) and running_transitions != attempt:
            errors.append(
                f"attempt {attempt} does not match {running_transitions} running transition(s)"
            )
    if state == "succeeded" or final:
        if state != "succeeded" and final:
            errors.append(f"final outcome is not succeeded: {state}")
        if not criteria:
            errors.append("succeeded requires at least one success criterion")
        if not isinstance(attempt, int) or attempt < 1:
            errors.append("succeeded requires attempt >= 1")
        if not evidence:
            errors.append("succeeded requires at least one evidence item")
        for index, item in enumerate(evidence):
            if not isinstance(item, dict):
                errors.append(f"evidence[{index}] must be an object")
                continue
            if (
                not isinstance(item.get("type"), str)
                or not item.get("type", "").strip()
            ):
                errors.append(f"evidence[{index}] requires a non-empty type")
            if (
                not isinstance(item.get("description"), str)
                or not item.get("description", "").strip()
            ):
                errors.append(f"evidence[{index}] requires a non-empty description")
            if (
                not isinstance(item.get("producer"), str)
                or not item.get("producer", "").strip()
            ):
                errors.append(f"evidence[{index}] requires a non-empty producer")
            command = item.get("command")
            if (
                not isinstance(command, list)
                or not command
                or any(
                    not isinstance(part, str) or not part.strip() for part in command
                )
            ):
                errors.append(
                    f"evidence[{index}] command must be a non-empty string array"
                )
            exit_code = item.get("exit_code")
            if not isinstance(exit_code, int) or isinstance(exit_code, bool):
                errors.append(f"evidence[{index}] requires an integer exit_code")
            evidence_status = item.get("status")
            if evidence_status not in {"passed", "failed"}:
                errors.append(f"evidence[{index}] status must be passed or failed")
            elif evidence_status == "passed" and exit_code != 0:
                errors.append(f"evidence[{index}] passed evidence requires exit_code=0")
            if evidence_status != "passed":
                errors.append(
                    f"evidence[{index}] must have status=passed for succeeded"
                )
            raw_path = item.get("path")
            expected_sha = item.get("sha256")
            expected_bytes = item.get("bytes")
            if not isinstance(raw_path, str) or not raw_path.strip():
                errors.append(f"evidence[{index}] requires an artifact path")
                continue
            if (
                not isinstance(expected_sha, str)
                or re.fullmatch(r"[0-9a-f]{64}", expected_sha) is None
            ):
                errors.append(f"evidence[{index}] requires a lowercase SHA-256")
                continue
            if (
                not isinstance(expected_bytes, int)
                or isinstance(expected_bytes, bool)
                or expected_bytes < 0
            ):
                errors.append(f"evidence[{index}] requires non-negative bytes")
                continue
            if artifact_root is not None:
                try:
                    artifact = _execution_artifact_path(raw_path, artifact_root)
                except HarnessError as exc:
                    errors.append(f"evidence[{index}] {exc}")
                else:
                    if artifact.stat().st_size != expected_bytes:
                        errors.append(
                            f"evidence[{index}] artifact byte size changed: {raw_path}"
                        )
                    if sha256_file(artifact) != expected_sha:
                        errors.append(
                            f"evidence[{index}] artifact SHA-256 changed: {raw_path}"
                        )
        if not checks:
            errors.append("succeeded requires criterion checks")
        elif any(
            not isinstance(check, dict) or check.get("status") != "passed"
            for check in checks
        ):
            errors.append("all success checks must have status=passed")
        else:
            checked = [str(check.get("criterion", "")) for check in checks]
            missing_checks = [
                str(criterion)
                for criterion in criteria
                if str(criterion) not in checked
            ]
            if missing_checks:
                errors.append("missing passed checks for: " + ", ".join(missing_checks))
            if len(checked) != len(set(checked)):
                errors.append("success checks must not contain duplicate criteria")
            unexpected_checks = sorted(
                set(checked) - set(str(criterion) for criterion in criteria)
            )
            if unexpected_checks:
                errors.append(
                    "unexpected success checks for: " + ", ".join(unexpected_checks)
                )
    if (
        state in {"failed", "blocked", "needs_approval"}
        and not str(record.get("stop_reason") or "").strip()
    ):
        errors.append(f"{state} requires stop_reason")
    return errors


def transition_execution(
    record: dict[str, Any],
    target: str,
    *,
    reason: str = "",
    stop_reason: str | None = None,
    evidence: list[dict[str, Any]] | None = None,
    checks: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    current = str(record.get("state", ""))
    if current not in EXECUTION_STATES:
        raise HarnessError(f"invalid current execution state: {current}")
    if target not in EXECUTION_STATES:
        raise HarnessError(f"invalid target execution state: {target}")
    if target not in ALLOWED_TRANSITIONS[current]:
        raise HarnessError(f"transition not allowed: {current} -> {target}")
    updated = json.loads(json.dumps(record))
    now = utc_now()
    if target == "running":
        updated["attempt"] = int(updated.get("attempt", 0)) + 1
        updated["stop_reason"] = None
    if evidence:
        updated.setdefault("evidence", []).extend(evidence)
    if checks is not None:
        updated["checks"] = checks
    if target in {"failed", "blocked", "needs_approval"}:
        updated["stop_reason"] = stop_reason or reason
    elif stop_reason is not None:
        updated["stop_reason"] = stop_reason
    updated["state"] = target
    updated["updated_at"] = now
    updated.setdefault("history", []).append(
        {"from": current, "to": target, "at": now, "reason": reason or None}
    )
    errors = validate_execution_record(updated)
    if errors:
        raise HarnessError("; ".join(errors))
    return updated


def validate_process_outcome(
    exit_code: int, outcome_path: Path | None
) -> tuple[str, str, dict[str, Any] | None]:
    """Resolve a process exit into a typed outcome.

    Exit 0 is only a transport-level signal. A valid, evidence-bearing outcome
    document is required to produce ``succeeded``.
    """
    if exit_code != 0:
        return "failed", f"process exited with code {exit_code}", None
    if outcome_path is None or outcome_path.is_symlink() or not outcome_path.is_file():
        return "failed", "process exited 0 but no outcome file was produced", None
    try:
        outcome = load_data(outcome_path)
    except HarnessError as exc:
        return "failed", f"invalid outcome file: {exc}", None
    if not isinstance(outcome, dict):
        return "failed", "outcome file must contain an object", None
    artifact_root = outcome_path.resolve().parent / EXECUTION_ARTIFACT_ROOT
    errors = validate_execution_record(outcome, artifact_root=artifact_root)
    if errors:
        return "failed", "invalid typed outcome: " + "; ".join(errors), outcome
    state = str(outcome.get("state"))
    if state == "succeeded":
        return "succeeded", "validated evidence-bearing outcome", outcome
    if state in {"failed", "blocked", "needs_approval"}:
        return state, str(outcome.get("stop_reason")), outcome
    return (
        "failed",
        f"process exited 0 with non-terminal outcome state: {state}",
        outcome,
    )


def path_matches_any(path: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)
