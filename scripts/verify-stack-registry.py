#!/usr/bin/env python3
"""Validate the checked-in technology-stack registry and its consumers.

The verifier is intentionally offline. Network refreshes update sources.lock.json;
this script proves that the lock, registry documents, generated guidance, and
remaining legacy pins agree with one another.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from urllib.parse import urlparse

try:
    import yaml
except ImportError:  # pragma: no cover - actionable failure for minimal runners
    print("FAIL dependency: PyYAML is required (python -m pip install PyYAML)")
    raise SystemExit(2)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_DIR = PROJECT_ROOT / ".claude" / "registry" / "tech-stacks"
SCHEMA_PATH = REGISTRY_DIR / "schema.json"
SOURCE_LOCK_PATH = REGISTRY_DIR / "sources.lock.json"

ROOT_REQUIRED = {
    "schema_version",
    "id",
    "display_name",
    "verified_at",
    "policy",
    "components",
    "migration",
    "promotion_gates",
    "consumers",
}
ROOT_ALLOWED = ROOT_REQUIRED
COMPONENT_REQUIRED = {
    "latest_observed",
    "recommended",
    "compatibility_floor",
    "prerelease",
    "verified_at",
    "source",
    "migration",
    "promotion_gates",
    "consumers",
}
COMPONENT_ALLOWED = COMPONENT_REQUIRED
CHANNEL_REQUIRED = {"version", "channel"}
CHANNEL_ALLOWED = CHANNEL_REQUIRED | {"reason"}
CHANNELS = {"stable", "current", "lts", "beta", "rc", "candidate"}
SOURCE_KINDS = {"official-release", "npm", "pypi", "pub"}
VERSION_SEGMENT_RE = re.compile(
    r"^(?P<core>(?:0|[1-9]\d*)(?:\.(?:0|[1-9]\d*)){1,3})"
    r"(?P<suffix>(?:[-+][0-9A-Za-z][0-9A-Za-z.-]*|(?:a|b|rc|dev)\d[0-9A-Za-z.-]*))?$"
)
SCANNED_SUFFIXES = {
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".txt",
    ".template",
}


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_mapping(
    loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False
):
    loader.flatten_mapping(node)
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_mapping,
)


class Results:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.counts: dict[str, int] = {}

    def error(self, category: str, message: str) -> None:
        self.errors.append(f"{category}: {message}")

    def pass_count(self, category: str, count: int) -> None:
        self.counts[category] = count


def rel(path: Path) -> str:
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def iso_date(value: object) -> str | None:
    if isinstance(value, dt.datetime):
        return value.date().isoformat()
    if isinstance(value, dt.date):
        return value.isoformat()
    if isinstance(value, str):
        try:
            return dt.date.fromisoformat(value).isoformat()
        except ValueError:
            return None
    return None


def parse_version(value: object) -> tuple[tuple[tuple[int, ...], str], ...] | None:
    """Parse bounded semver/PEP-440-like versions, including paired OTel releases."""
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        return None
    parsed: list[tuple[tuple[int, ...], str]] = []
    for segment in value.split("/"):
        match = VERSION_SEGMENT_RE.fullmatch(segment)
        if match is None:
            return None
        numbers = tuple(int(part) for part in match.group("core").split("."))
        parsed.append((numbers, match.group("suffix") or ""))
    return tuple(parsed)


def compare_version_bases(left: object, right: object) -> int | None:
    """Compare release-number bases; suffixes do not promote prereleases over stable."""
    left_parsed = parse_version(left)
    right_parsed = parse_version(right)
    if (
        left_parsed is None
        or right_parsed is None
        or len(left_parsed) != len(right_parsed)
    ):
        return None
    for (left_numbers, _), (right_numbers, _) in zip(
        left_parsed, right_parsed, strict=True
    ):
        width = max(len(left_numbers), len(right_numbers))
        left_key = left_numbers + (0,) * (width - len(left_numbers))
        right_key = right_numbers + (0,) * (width - len(right_numbers))
        if left_key < right_key:
            return -1
        if left_key > right_key:
            return 1
    return 0


def load_json(path: Path, results: Results, category: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        results.error(category, f"missing {rel(path)}")
        return {}
    except (OSError, json.JSONDecodeError) as exc:
        results.error(category, f"cannot read {rel(path)}: {exc}")
        return {}
    if not isinstance(value, dict):
        results.error(category, f"{rel(path)} root must be an object")
        return {}
    return value


def load_registries(results: Results) -> dict[str, dict]:
    registries: dict[str, dict] = {}
    for path in sorted(REGISTRY_DIR.glob("*.yaml")):
        try:
            value = yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
        except (OSError, yaml.YAMLError) as exc:
            results.error("schema", f"cannot read {rel(path)}: {exc}")
            continue
        if not isinstance(value, dict):
            results.error("schema", f"{rel(path)} root must be a mapping")
            continue
        stack_id = value.get("id")
        if not isinstance(stack_id, str):
            results.error("schema", f"{rel(path)} id must be a string")
            continue
        if stack_id in registries:
            results.error("schema", f"duplicate stack id {stack_id!r}")
            continue
        if path.stem != stack_id:
            results.error("schema", f"{rel(path)} filename must match id {stack_id!r}")
        registries[stack_id] = value
    if not registries:
        results.error("schema", "no stack YAML documents found")
    return registries


def require_keys(
    value: object,
    required: set[str],
    allowed: set[str],
    where: str,
    results: Results,
) -> bool:
    if not isinstance(value, Mapping):
        results.error("schema", f"{where} must be a mapping")
        return False
    keys = set(value)
    missing = sorted(required - keys)
    extra = sorted(keys - allowed)
    if missing:
        results.error("schema", f"{where} missing keys: {', '.join(missing)}")
    if extra:
        results.error("schema", f"{where} has unsupported keys: {', '.join(extra)}")
    return not missing and not extra


def require_nonempty_strings(value: object, where: str, results: Results) -> bool:
    if (
        not isinstance(value, Sequence)
        or isinstance(value, (str, bytes))
        or not value
        or any(not isinstance(item, str) or not item.strip() for item in value)
    ):
        results.error("schema", f"{where} must be a non-empty list of strings")
        return False
    if len(value) != len(set(value)):
        results.error("schema", f"{where} contains duplicates")
        return False
    return True


def validate_channel(value: object, where: str, results: Results) -> None:
    if not require_keys(value, CHANNEL_REQUIRED, CHANNEL_ALLOWED, where, results):
        return
    assert isinstance(value, Mapping)
    version = value.get("version")
    channel = value.get("channel")
    reason = value.get("reason")
    if not isinstance(version, str) or not version.strip():
        results.error("schema", f"{where}.version must be a non-empty string")
    elif parse_version(version) is None:
        results.error("schema", f"{where}.version is malformed: {version!r}")
    if channel not in CHANNELS:
        results.error("schema", f"{where}.channel must be one of {sorted(CHANNELS)}")
    if reason is not None and (not isinstance(reason, str) or not reason.strip()):
        results.error("schema", f"{where}.reason must be a non-empty string")


def validate_component_version_semantics(
    component: Mapping[str, object], where: str, results: Results
) -> None:
    channels = {
        name: component.get(name)
        for name in ("latest_observed", "recommended", "compatibility_floor")
    }
    for channel_value in channels.values():
        if not isinstance(channel_value, Mapping):
            return
        parsed = parse_version(channel_value.get("version"))
        if parsed is None:
            return

    latest = channels["latest_observed"]
    recommended = channels["recommended"]
    floor = channels["compatibility_floor"]
    assert (
        isinstance(latest, Mapping)
        and isinstance(recommended, Mapping)
        and isinstance(floor, Mapping)
    )
    floor_cmp = compare_version_bases(floor.get("version"), recommended.get("version"))
    recommended_cmp = compare_version_bases(
        recommended.get("version"), latest.get("version")
    )
    if floor_cmp is None or recommended_cmp is None:
        results.error(
            "schema",
            f"{where} stable version channels must use matching version shapes",
        )
    elif floor_cmp > 0:
        results.error(
            "schema", f"{where}.compatibility_floor cannot exceed recommended"
        )
    if recommended_cmp is not None and recommended_cmp > 0:
        results.error("schema", f"{where}.recommended cannot exceed latest_observed")

    prerelease = component.get("prerelease")
    if prerelease is None or not isinstance(prerelease, Mapping):
        return
    parsed_prerelease = parse_version(prerelease.get("version"))
    if parsed_prerelease is None:
        return
    if prerelease.get("channel") not in {"beta", "rc", "candidate"}:
        results.error(
            "schema", f"{where}.prerelease must use beta, rc, or candidate channel"
        )
    if not any(
        suffix and not suffix.startswith("+") for _, suffix in parsed_prerelease
    ):
        results.error(
            "schema", f"{where}.prerelease version must include a prerelease suffix"
        )
    prerelease_cmp = compare_version_bases(
        prerelease.get("version"), latest.get("version")
    )
    if prerelease_cmp is None:
        results.error(
            "schema",
            f"{where}.prerelease must use the same version shape as latest_observed",
        )
    elif prerelease_cmp < 0:
        results.error(
            "schema", f"{where}.prerelease base cannot be older than latest_observed"
        )


def validate_schema(registries: dict[str, dict], results: Results) -> None:
    schema = load_json(SCHEMA_PATH, results, "schema")
    if schema:
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            results.error("schema", "schema.json must use JSON Schema draft 2020-12")
        if set(schema.get("required", [])) != ROOT_REQUIRED:
            results.error(
                "schema", "schema.json root required keys drifted from verifier"
            )
        component_schema = schema.get("$defs", {}).get("component", {})
        if set(component_schema.get("required", [])) != COMPONENT_REQUIRED:
            results.error(
                "schema", "schema.json component required keys drifted from verifier"
            )

    component_count = 0
    for stack_id, stack in registries.items():
        where = f"{stack_id}.yaml"
        if not require_keys(stack, ROOT_REQUIRED, ROOT_ALLOWED, where, results):
            continue
        if stack.get("schema_version") != 1:
            results.error("schema", f"{where}.schema_version must be 1")
        if (
            not isinstance(stack.get("display_name"), str)
            or not stack["display_name"].strip()
        ):
            results.error("schema", f"{where}.display_name must be a non-empty string")
        if iso_date(stack.get("verified_at")) is None:
            results.error("schema", f"{where}.verified_at must be an ISO date")

        policy = stack.get("policy")
        if require_keys(
            policy,
            {"default_channel", "upgrade_rule"},
            {"default_channel", "upgrade_rule"},
            f"{where}.policy",
            results,
        ):
            assert isinstance(policy, Mapping)
            if policy.get("default_channel") != "recommended":
                results.error(
                    "schema", f"{where}.policy.default_channel must be recommended"
                )
            if (
                not isinstance(policy.get("upgrade_rule"), str)
                or not policy["upgrade_rule"].strip()
            ):
                results.error(
                    "schema", f"{where}.policy.upgrade_rule must be non-empty"
                )

        migration = stack.get("migration")
        if require_keys(
            migration,
            {"guide", "summary"},
            {"guide", "summary"},
            f"{where}.migration",
            results,
        ):
            assert isinstance(migration, Mapping)
            validate_migration_path(
                migration.get("guide"), f"{where}.migration.guide", results
            )
            if (
                not isinstance(migration.get("summary"), str)
                or not migration["summary"].strip()
            ):
                results.error("schema", f"{where}.migration.summary must be non-empty")

        require_nonempty_strings(
            stack.get("promotion_gates"), f"{where}.promotion_gates", results
        )
        require_nonempty_strings(stack.get("consumers"), f"{where}.consumers", results)

        components = stack.get("components")
        if not isinstance(components, Mapping) or not components:
            results.error("schema", f"{where}.components must be a non-empty mapping")
            continue
        for component_id, component in components.items():
            component_count += 1
            cwhere = f"{where}.components.{component_id}"
            if not isinstance(component_id, str) or not component_id:
                results.error("schema", f"{where} has an invalid component id")
                continue
            if not require_keys(
                component, COMPONENT_REQUIRED, COMPONENT_ALLOWED, cwhere, results
            ):
                continue
            assert isinstance(component, Mapping)
            for channel_name in (
                "latest_observed",
                "recommended",
                "compatibility_floor",
            ):
                validate_channel(
                    component.get(channel_name), f"{cwhere}.{channel_name}", results
                )
            prerelease = component.get("prerelease")
            if prerelease is not None:
                validate_channel(prerelease, f"{cwhere}.prerelease", results)
            validate_component_version_semantics(component, cwhere, results)
            if iso_date(component.get("verified_at")) is None:
                results.error("schema", f"{cwhere}.verified_at must be an ISO date")

            source = component.get("source")
            if require_keys(
                source, {"kind", "url"}, {"kind", "url"}, f"{cwhere}.source", results
            ):
                assert isinstance(source, Mapping)
                if source.get("kind") not in SOURCE_KINDS:
                    results.error("schema", f"{cwhere}.source.kind is unsupported")
                parsed = urlparse(str(source.get("url", "")))
                if parsed.scheme != "https" or not parsed.hostname:
                    results.error("schema", f"{cwhere}.source.url must be an HTTPS URL")

            cmigration = component.get("migration")
            if require_keys(
                cmigration,
                {"guide", "note"},
                {"guide", "note"},
                f"{cwhere}.migration",
                results,
            ):
                assert isinstance(cmigration, Mapping)
                validate_migration_path(
                    cmigration.get("guide"), f"{cwhere}.migration.guide", results
                )
                if (
                    not isinstance(cmigration.get("note"), str)
                    or not cmigration["note"].strip()
                ):
                    results.error(
                        "schema", f"{cwhere}.migration.note must be non-empty"
                    )
            require_nonempty_strings(
                component.get("promotion_gates"), f"{cwhere}.promotion_gates", results
            )
            require_nonempty_strings(
                component.get("consumers"), f"{cwhere}.consumers", results
            )

    results.pass_count("schema", len(registries) + component_count)


def validate_migration_path(value: object, where: str, results: Results) -> None:
    if not isinstance(value, str) or not re.fullmatch(r"migrations/.+\.md", value):
        results.error("schema", f"{where} must match migrations/*.md")
        return
    path = REGISTRY_DIR / value
    if not path.is_file():
        results.error("schema", f"{where} points to missing {rel(path)}")


def validate_source_lock(
    registries: dict[str, dict], lock: dict, results: Results
) -> None:
    required = {
        "schema_version",
        "verified_at",
        "official_source_hosts",
        "stacks",
        "managed_consumers",
        "inline_pin_policy",
    }
    if set(lock) != required:
        results.error("source-lock", f"root keys must be exactly {sorted(required)}")
        return
    if lock.get("schema_version") != 1:
        results.error("source-lock", "schema_version must be 1")
    if iso_date(lock.get("verified_at")) is None:
        results.error("source-lock", "verified_at must be an ISO date")
    hosts = lock.get("official_source_hosts")
    if (
        not isinstance(hosts, list)
        or not hosts
        or any(not isinstance(host, str) for host in hosts)
    ):
        results.error(
            "source-lock", "official_source_hosts must be a non-empty string list"
        )
        hosts = []
    allowed_hosts = set(hosts)
    stacks = lock.get("stacks")
    if not isinstance(stacks, Mapping):
        results.error("source-lock", "stacks must be a mapping")
        return
    if set(stacks) != set(registries):
        results.error(
            "source-lock",
            f"stack ids differ: lock={sorted(stacks)} registry={sorted(registries)}",
        )

    checked = 0
    for stack_id, stack in registries.items():
        locked = stacks.get(stack_id)
        if not isinstance(locked, Mapping):
            results.error("source-lock", f"missing stack {stack_id}")
            continue
        if set(locked) != {"verified_at", "components", "prereleases"}:
            results.error(
                "source-lock",
                f"{stack_id} lock keys must be verified_at, components, and prereleases",
            )
        if iso_date(locked.get("verified_at")) != iso_date(stack.get("verified_at")):
            results.error(
                "source-lock", f"{stack_id}.verified_at differs from registry"
            )
        locked_components = locked.get("components")
        registry_components = stack.get("components", {})
        if not isinstance(locked_components, Mapping):
            results.error("source-lock", f"{stack_id}.components must be a mapping")
            continue
        if set(locked_components) != set(registry_components):
            results.error(
                "source-lock",
                f"{stack_id} component ids differ: lock={sorted(locked_components)} registry={sorted(registry_components)}",
            )
        for component_id, component in registry_components.items():
            checked += 1
            expected = component.get("latest_observed", {}).get("version")
            if locked_components.get(component_id) != expected:
                results.error(
                    "source-lock",
                    f"{stack_id}.{component_id} lock={locked_components.get(component_id)!r} latest_observed={expected!r}",
                )
            source_url = component.get("source", {}).get("url", "")
            hostname = urlparse(source_url).hostname
            if hostname not in allowed_hosts:
                results.error(
                    "source-lock",
                    f"{stack_id}.{component_id} source host {hostname!r} is not allowlisted",
                )
        locked_prereleases = locked.get("prereleases")
        expected_prereleases = {
            component_id: {
                "version": component["prerelease"]["version"],
                "channel": component["prerelease"]["channel"],
            }
            for component_id, component in registry_components.items()
            if component.get("prerelease") is not None
        }
        if locked_prereleases != expected_prereleases:
            results.error(
                "source-lock",
                f"{stack_id}.prereleases differ: lock={locked_prereleases!r} registry={expected_prereleases!r}",
            )
    results.pass_count("source-lock", checked)


def validate_consumers(
    registries: dict[str, dict], lock: dict, results: Results
) -> None:
    managed = lock.get("managed_consumers")
    if not isinstance(managed, list):
        results.error("generated", "managed_consumers must be a list")
        return
    actual_by_stack: dict[str, set[str]] = {stack_id: set() for stack_id in registries}
    seen_paths: set[tuple[str, str]] = set()
    for index, item in enumerate(managed):
        where = f"managed_consumers[{index}]"
        if not isinstance(item, Mapping):
            results.error("generated", f"{where} must be an object")
            continue
        if set(item) != {"path", "stack", "required_markers"}:
            results.error("generated", f"{where} has invalid keys")
            continue
        path_value = item.get("path")
        stack_id = item.get("stack")
        markers = item.get("required_markers")
        if not isinstance(path_value, str) or not path_value:
            results.error("generated", f"{where}.path must be a string")
            continue
        if stack_id not in registries:
            results.error("generated", f"{path_value} has unknown stack {stack_id!r}")
            continue
        identity = (path_value, str(stack_id))
        if identity in seen_paths:
            results.error(
                "generated", f"duplicate managed path/stack {path_value} / {stack_id}"
            )
        seen_paths.add(identity)
        if (
            not isinstance(markers, list)
            or not markers
            or any(not isinstance(marker, str) or not marker for marker in markers)
        ):
            results.error(
                "generated", f"{path_value} required_markers must be non-empty strings"
            )
            continue
        path = PROJECT_ROOT / path_value
        try:
            content = path.read_text(encoding="utf-8")
        except (FileNotFoundError, OSError, UnicodeDecodeError) as exc:
            results.error("generated", f"cannot read {path_value}: {exc}")
            continue
        for marker in markers:
            if marker not in content:
                results.error("generated", f"{path_value} missing marker {marker!r}")
        actual_by_stack[stack_id].add(path_value)

    for stack_id, stack in registries.items():
        registry_consumers = set(stack.get("consumers", []))
        if registry_consumers != actual_by_stack[stack_id]:
            results.error(
                "generated",
                f"{stack_id} consumers differ: registry={sorted(registry_consumers)} managed={sorted(actual_by_stack[stack_id])}",
            )
        for component_id, component in stack.get("components", {}).items():
            if set(component.get("consumers", [])) != registry_consumers:
                results.error(
                    "generated",
                    f"{stack_id}.{component_id} consumers drifted from stack consumers",
                )
        for consumer in registry_consumers:
            if not (PROJECT_ROOT / consumer).is_file():
                results.error(
                    "generated", f"{stack_id} points to missing consumer {consumer}"
                )
    results.pass_count("generated", len(managed))


def validate_inline_pins(lock: dict, results: Results) -> None:
    policy = lock.get("inline_pin_policy")
    if not isinstance(policy, Mapping):
        results.error("inline-pins", "inline_pin_policy must be an object")
        return
    if set(policy) != {
        "scan_roots",
        "excluded_path_fragments",
        "patterns",
        "allowlist",
    }:
        results.error("inline-pins", "inline_pin_policy has invalid keys")
        return
    patterns_raw = policy.get("patterns")
    allowlist_raw = policy.get("allowlist")
    if not isinstance(patterns_raw, list) or not isinstance(allowlist_raw, list):
        results.error("inline-pins", "patterns and allowlist must be lists")
        return

    patterns: dict[str, re.Pattern[str]] = {}
    for item in patterns_raw:
        if not isinstance(item, Mapping) or set(item) != {"id", "regex"}:
            results.error("inline-pins", f"invalid pattern entry {item!r}")
            continue
        pattern_id = item.get("id")
        regex = item.get("regex")
        if not isinstance(pattern_id, str) or not isinstance(regex, str):
            results.error("inline-pins", f"invalid pattern entry {item!r}")
            continue
        if pattern_id in patterns:
            results.error("inline-pins", f"duplicate pattern id {pattern_id}")
            continue
        try:
            patterns[pattern_id] = re.compile(regex)
        except re.error as exc:
            results.error("inline-pins", f"invalid regex for {pattern_id}: {exc}")

    allowed: dict[tuple[str, str], str] = {}
    for item in allowlist_raw:
        if not isinstance(item, Mapping) or set(item) != {
            "path",
            "pattern_ids",
            "reason",
        }:
            results.error("inline-pins", f"invalid allowlist entry {item!r}")
            continue
        path_value = item.get("path")
        pattern_ids = item.get("pattern_ids")
        reason = item.get("reason")
        if (
            not isinstance(path_value, str)
            or not isinstance(pattern_ids, list)
            or not isinstance(reason, str)
            or not reason.strip()
        ):
            results.error("inline-pins", f"invalid allowlist entry {item!r}")
            continue
        if not (PROJECT_ROOT / path_value).is_file():
            results.error(
                "inline-pins", f"allowlisted path does not exist: {path_value}"
            )
        for pattern_id in pattern_ids:
            key = (path_value, pattern_id)
            if pattern_id not in patterns:
                results.error(
                    "inline-pins",
                    f"{path_value} references unknown pattern {pattern_id}",
                )
            if key in allowed:
                results.error(
                    "inline-pins",
                    f"duplicate allowlist pair {path_value} / {pattern_id}",
                )
            allowed[key] = reason

    roots = policy.get("scan_roots")
    exclusions = policy.get("excluded_path_fragments")
    if not isinstance(roots, list) or not isinstance(exclusions, list):
        results.error(
            "inline-pins", "scan_roots and excluded_path_fragments must be lists"
        )
        return
    seen_allowed: set[tuple[str, str]] = set()
    scanned = 0
    for root_value in roots:
        root = PROJECT_ROOT / str(root_value)
        if not root.is_dir():
            results.error("inline-pins", f"scan root does not exist: {root_value}")
            continue
        for path in sorted(file for file in root.rglob("*") if file.is_file()):
            path_value = rel(path)
            normalized = f"/{path_value}"
            if path.suffix not in SCANNED_SUFFIXES:
                continue
            if any(fragment in normalized for fragment in exclusions):
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            scanned += 1
            for pattern_id, pattern in patterns.items():
                if not pattern.search(content):
                    continue
                key = (path_value, pattern_id)
                if key in allowed:
                    seen_allowed.add(key)
                else:
                    results.error(
                        "inline-pins", f"unexpected {pattern_id} in {path_value}"
                    )

    for path_value, pattern_id in sorted(set(allowed) - seen_allowed):
        results.error(
            "inline-pins", f"stale allowlist entry {path_value} / {pattern_id}"
        )
    results.pass_count("inline-pins", scanned)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--schema", action="store_true", help="validate schema and stack YAML"
    )
    parser.add_argument(
        "--source-lock", action="store_true", help="validate locked source versions"
    )
    parser.add_argument(
        "--generated", action="store_true", help="validate managed consumer markers"
    )
    parser.add_argument(
        "--inline-pins", action="store_true", help="scan for stale inline defaults"
    )
    parser.add_argument(
        "--all", action="store_true", help="run every validation (default)"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_all = args.all or not any(
        (args.schema, args.source_lock, args.generated, args.inline_pins)
    )
    selected = {
        "schema": run_all or args.schema,
        "source-lock": run_all or args.source_lock,
        "generated": run_all or args.generated,
        "inline-pins": run_all or args.inline_pins,
    }

    results = Results()
    registries = load_registries(results)
    lock = (
        load_json(SOURCE_LOCK_PATH, results, "source-lock")
        if any(selected[name] for name in ("source-lock", "generated", "inline-pins"))
        else {}
    )

    if selected["schema"]:
        validate_schema(registries, results)
    if selected["source-lock"] and lock:
        validate_source_lock(registries, lock, results)
    if selected["generated"] and lock:
        validate_consumers(registries, lock, results)
    if selected["inline-pins"] and lock:
        validate_inline_pins(lock, results)

    if results.errors:
        print(f"FAIL stack-registry: {len(results.errors)} error(s)")
        for error in results.errors:
            print(f"  - {error}")
        return 1

    details = ", ".join(
        f"{name}={results.counts.get(name, 0)}"
        for name, enabled in selected.items()
        if enabled
    )
    print(f"PASS stack-registry: {details}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
