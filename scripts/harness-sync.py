#!/usr/bin/env python3
"""Non-destructive Claude Craft harness sync with manifest, backup, canary, and rollback."""

from __future__ import annotations

import argparse
import copy
import json
import os
import shutil
import sys
import uuid
from pathlib import Path
from typing import Any, Callable

from harness_runtime_lib import (
    HarnessError,
    load_data,
    path_matches_any,
    project_root_from,
    sha256_bytes,
    sha256_file,
    utc_now,
    write_json,
)


def fingerprint(path: Path) -> dict[str, Any]:
    if path.is_symlink():
        target = os.readlink(path)
        return {
            "kind": "symlink",
            "target": target,
            "sha256": sha256_bytes(target.encode()),
        }
    if path.is_file():
        return {
            "kind": "file",
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
        }
    if path.exists():
        return {"kind": "directory"}
    return {"kind": "absent"}


def safe_project_destination(project_root: Path, raw_path: str | Path) -> Path:
    """Resolve a project-relative destination and reject parent symlink traversal."""
    root = project_root.expanduser().resolve()
    relative = Path(str(raw_path))
    if not relative.parts or relative.is_absolute() or ".." in relative.parts:
        raise HarnessError(f"path must stay project-relative: {raw_path}")
    current = root
    for part in relative.parts[:-1]:
        current = current / part
        if current.is_symlink():
            raise HarnessError(f"destination parent is a symlink: {current}")
    destination = root / relative
    try:
        destination.parent.resolve(strict=False).relative_to(root)
    except ValueError as exc:
        raise HarnessError(f"destination escapes project root: {raw_path}") from exc
    return destination


def sanitized_actions(actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = copy.deepcopy(actions)
    for action in result:
        if action.get("desired", {}).get("kind") == "json-merge":
            action["desired"].pop("content", None)
    return result


def sync_plan_digest(actions: list[dict[str, Any]], run_id: str) -> str:
    immutable = []
    for action in sanitized_actions(actions):
        immutable.append(
            {
                key: action.get(key)
                for key in (
                    "project_id",
                    "project_path",
                    "path",
                    "operation",
                    "before",
                    "desired",
                )
            }
        )
    payload = json.dumps(
        {"run_id": run_id, "actions": immutable},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return sha256_bytes(payload)


def receipt_path(project_root: Path, run_id: str) -> Path:
    return safe_project_destination(
        project_root, Path(".claude") / "harness-backups" / run_id / "receipt.json"
    )


def desired_assets(root: Path, pack: dict[str, Any]) -> list[dict[str, Any]]:
    excludes = list(pack.get("exclude", []))
    assets: dict[str, dict[str, Any]] = {}
    for raw in pack.get("paths", []):
        relative = Path(str(raw))
        if relative.is_absolute() or ".." in relative.parts:
            raise HarnessError(f"pack path must stay repository-relative: {relative}")
        source = root / relative
        if not source.exists() and not source.is_symlink():
            raise HarnessError(f"pack source missing: {relative.as_posix()}")
        candidates = (
            [source]
            if source.is_file() or source.is_symlink()
            else list(source.rglob("*"))
        )
        for candidate in candidates:
            if not (candidate.is_file() or candidate.is_symlink()):
                continue
            rel = candidate.relative_to(root).as_posix()
            if path_matches_any(rel, excludes):
                continue
            if candidate.is_symlink():
                assets[rel] = {
                    "path": rel,
                    "kind": "symlink",
                    "target": os.readlink(candidate),
                    "pack_id": str(pack.get("id", "unknown")),
                }
            else:
                assets[rel] = {
                    "path": rel,
                    "kind": "file",
                    "source": str(candidate),
                    "sha256": sha256_file(candidate),
                    "bytes": candidate.stat().st_size,
                    "pack_id": str(pack.get("id", "unknown")),
                }
    for rel, target in pack.get("links", {}).items():
        link_path = Path(str(rel))
        if link_path.is_absolute() or ".." in link_path.parts:
            raise HarnessError(f"link path must stay project-relative: {rel}")
        if not path_matches_any(rel, excludes):
            assets[str(rel)] = {
                "path": str(rel),
                "kind": "symlink",
                "target": str(target),
                "pack_id": str(pack.get("id", "unknown")),
            }
    return [assets[key] for key in sorted(assets)]


def load_profile_packs(root: Path, profile: dict[str, Any]) -> list[dict[str, Any]]:
    """Load the base pack followed by explicit project-pack overlays."""
    raw_paths = [profile["pack"], *profile.get("pack_overlays", [])]
    packs = []
    for raw_path in raw_paths:
        pack_path = Path(str(raw_path))
        if not pack_path.is_absolute():
            pack_path = root / pack_path
        pack = load_data(pack_path)
        if (
            not isinstance(pack, dict)
            or pack.get("schema_version") != "harness.project-pack.v1"
        ):
            raise HarnessError(f"invalid project pack: {pack_path}")
        packs.append(pack)
    return packs


def combine_pack_assets(
    root: Path, packs: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    assets: dict[str, dict[str, Any]] = {}
    for pack in packs:
        for asset in desired_assets(root, pack):
            existing = assets.get(asset["path"])
            if existing and {
                key: value for key, value in existing.items() if key != "pack_id"
            } != {key: value for key, value in asset.items() if key != "pack_id"}:
                raise HarnessError(
                    f"pack asset conflict for {asset['path']}: "
                    f"{existing.get('pack_id')} vs {asset.get('pack_id')}"
                )
            assets[asset["path"]] = asset
    return [assets[key] for key in sorted(assets)]


def _ensure_list_path(document: dict[str, Any], path: list[str]) -> list[Any]:
    if not path or any(not isinstance(key, str) or not key for key in path):
        raise HarnessError("settings merge path must be a non-empty string list")
    current: dict[str, Any] = document
    for key in path[:-1]:
        value = current.setdefault(key, {})
        if not isinstance(value, dict):
            raise HarnessError(f"settings merge path is not an object at: {key}")
        current = value
    leaf = current.setdefault(path[-1], [])
    if not isinstance(leaf, list):
        raise HarnessError(f"settings merge target is not a list: {'.'.join(path)}")
    return leaf


def apply_append_if_missing(document: dict[str, Any], spec: dict[str, Any]) -> bool:
    """Materialize one append-if-missing spec, preserving unrelated settings."""
    if spec.get("format") != "json" or spec.get("operation") != "append-if-missing":
        raise HarnessError("only json append-if-missing settings merges are supported")
    target_list = _ensure_list_path(document, list(spec.get("path", [])))
    match = spec.get("match", {})
    if not isinstance(match, dict) or not match:
        raise HarnessError("settings merge match must be a non-empty object")
    matched_items = [
        item
        for item in target_list
        if isinstance(item, dict)
        and all(item.get(key) == value for key, value in match.items())
    ]
    append_path = list(spec.get("append_path", []))
    value = copy.deepcopy(spec.get("value"))
    if not isinstance(value, dict) or not value:
        raise HarnessError("settings merge value must be a non-empty object")
    for item in matched_items:
        current: Any = item
        for key in append_path:
            if not isinstance(current, dict) or key not in current:
                current = None
                break
            current = current[key]
        if isinstance(current, list) and value in current:
            return False

    matched = matched_items[0] if matched_items else None
    if matched is None:
        matched = copy.deepcopy(match)
        target_list.append(matched)
    append_list = _ensure_list_path(matched, append_path)
    append_list.append(value)
    return True


def plan_settings_merges(
    project: dict[str, Any],
    packs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Combine all pack settings merges into one idempotent action per target."""
    target_root = Path(project["path"]).expanduser().resolve()
    grouped: dict[str, list[tuple[str, dict[str, Any]]]] = {}
    for pack in packs:
        for spec in pack.get("settings_merges", []):
            relative = Path(str(spec.get("target", "")))
            if not relative.parts or relative.is_absolute() or ".." in relative.parts:
                raise HarnessError(
                    f"settings merge target must stay project-relative: {relative}"
                )
            grouped.setdefault(relative.as_posix(), []).append(
                (str(pack.get("id", "unknown")), spec)
            )

    actions = []
    for relative, specs in sorted(grouped.items()):
        destination = safe_project_destination(target_root, relative)
        before = fingerprint(destination)
        base_action = {
            "project_id": project["id"],
            "project_path": str(target_root),
            "path": relative,
            "before": before,
            "applied": False,
            "merge_packs": [pack_id for pack_id, _ in specs],
        }
        if before["kind"] in {"directory", "symlink"}:
            base_action["operation"] = f"conflict-settings-{before['kind']}"
            base_action["desired"] = {"kind": "json-merge"}
            actions.append(base_action)
            continue
        try:
            document = load_data(destination) if before["kind"] == "file" else {}
        except (HarnessError, OSError) as exc:
            base_action["operation"] = "conflict-invalid-json"
            base_action["conflict_reason"] = str(exc)
            base_action["desired"] = {"kind": "json-merge"}
            actions.append(base_action)
            continue
        if not isinstance(document, dict):
            base_action["operation"] = "conflict-invalid-json"
            base_action["conflict_reason"] = "settings root must be an object"
            base_action["desired"] = {"kind": "json-merge"}
            actions.append(base_action)
            continue
        merged = copy.deepcopy(document)
        changed = False
        for _, spec in specs:
            changed = apply_append_if_missing(merged, spec) or changed
        payload = (
            json.dumps(merged, ensure_ascii=False, indent=2, sort_keys=True).encode()
            + b"\n"
        )
        base_action["desired"] = {
            "kind": "json-merge",
            "content": merged,
            "sha256": sha256_bytes(payload),
            "bytes": len(payload),
        }
        if not changed:
            base_action["operation"] = "unchanged-merge"
        elif before["kind"] == "absent":
            base_action["operation"] = "create-json"
        else:
            base_action["operation"] = "merge-json"
        actions.append(base_action)
    return actions


def protected_patterns(profile: dict[str, Any], target: Path) -> list[str]:
    patterns = list(profile.get("protected_paths", []))
    overlay_path = target / ".claude" / "harness-overlay.json"
    if overlay_path.is_file():
        overlay = load_data(overlay_path)
        if isinstance(overlay, dict):
            patterns.extend(str(item) for item in overlay.get("protected_paths", []))
    return patterns


def plan_project(
    root: Path,
    project: dict[str, Any],
    assets: list[dict[str, Any]],
    profile: dict[str, Any],
) -> list[dict[str, Any]]:
    target = Path(project["path"]).expanduser().resolve()
    patterns = protected_patterns(profile, target)
    actions: list[dict[str, Any]] = []
    for asset in assets:
        relative = asset["path"]
        destination = safe_project_destination(target, relative)
        before = fingerprint(destination)
        action = {
            "project_id": project["id"],
            "project_path": str(target),
            "path": relative,
            "desired": {key: value for key, value in asset.items() if key != "source"},
            "before": before,
            "operation": "unchanged",
            "applied": False,
        }
        parent_conflict = None
        parent = destination.parent
        while parent != target and parent != parent.parent:
            if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
                parent_conflict = parent
                break
            parent = parent.parent
        if path_matches_any(relative, patterns):
            action["operation"] = "skip-protected"
        elif parent_conflict is not None:
            action["operation"] = "conflict-parent"
            action["conflict_path"] = str(parent_conflict)
        elif before["kind"] == "directory":
            action["operation"] = "conflict-directory"
        elif (
            asset["kind"] == "file"
            and before.get("kind") == "file"
            and before.get("sha256") == asset["sha256"]
        ):
            action["operation"] = "unchanged"
        elif (
            asset["kind"] == "symlink"
            and before.get("kind") == "symlink"
            and before.get("target") == asset["target"]
        ):
            action["operation"] = "unchanged"
        elif before["kind"] == "absent":
            action["operation"] = "create"
        else:
            action["operation"] = "update"
        actions.append(action)
    return actions


def backup_existing(
    destination: Path, backup_root: Path, action: dict[str, Any]
) -> None:
    before = action["before"]
    if before["kind"] == "absent":
        return
    backup = backup_root / action["path"]
    backup.parent.mkdir(parents=True, exist_ok=True)
    if before["kind"] == "file":
        shutil.copy2(destination, backup)
        action["backup"] = str(backup)
    elif before["kind"] == "symlink":
        action["backup_symlink_target"] = before["target"]


def desired_matches_fingerprint(
    desired: dict[str, Any], actual: dict[str, Any]
) -> bool:
    kind = desired.get("kind")
    if kind == "file":
        return (
            actual.get("kind") == "file"
            and actual.get("sha256") == desired.get("sha256")
            and actual.get("bytes") == desired.get("bytes")
        )
    if kind == "symlink":
        return actual.get("kind") == "symlink" and actual.get("target") == desired.get(
            "target"
        )
    if kind == "json-merge":
        return (
            actual.get("kind") == "file"
            and actual.get("sha256") == desired.get("sha256")
            and actual.get("bytes") == desired.get("bytes")
        )
    return False


def validate_source_precondition(root: Path, action: dict[str, Any]) -> None:
    desired = action["desired"]
    if desired.get("kind") != "file":
        return
    source = root / action["path"]
    actual = fingerprint(source)
    if not desired_matches_fingerprint(desired, actual):
        raise HarnessError(
            f"pack source changed after planning: {action['path']} "
            f"desired={desired.get('sha256')} actual={actual.get('sha256')}"
        )


def apply_actions(
    root: Path,
    actions: list[dict[str, Any]],
    run_id: str,
    checkpoint: Callable[[], None] | None = None,
) -> None:
    for action in actions:
        if action["operation"] not in {"create", "update", "create-json", "merge-json"}:
            continue
        project_root = Path(action["project_path"]).expanduser().resolve()
        destination = safe_project_destination(project_root, action["path"])
        current = fingerprint(destination)
        if current != action["before"]:
            raise HarnessError(
                f"destination changed after planning: {destination} "
                f"before={action['before']} current={current}"
            )
        validate_source_precondition(root, action)
        backup_root = safe_project_destination(
            project_root, Path(".claude") / "harness-backups" / run_id / "payload"
        )
        backup_existing(destination, backup_root, action)
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.is_symlink() or destination.is_file():
                destination.unlink()
            desired = action["desired"]
            if desired["kind"] == "file":
                source = root / action["path"]
                shutil.copy2(source, destination)
            elif desired["kind"] == "symlink":
                destination.symlink_to(desired["target"])
            elif desired["kind"] == "json-merge":
                write_json(destination, desired["content"])
            else:
                raise HarnessError(f"unsupported desired asset kind: {desired['kind']}")
            action["after"] = fingerprint(destination)
            if not desired_matches_fingerprint(desired, action["after"]):
                raise HarnessError(
                    f"sync postcondition failed for {destination}: "
                    f"desired={desired} actual={action['after']}"
                )
            action["applied"] = True
            if checkpoint:
                checkpoint()
        except (HarnessError, OSError):
            restore_action(action, require_after_match=False)
            action["applied"] = False
            raise


def restore_action(action: dict[str, Any], *, require_after_match: bool) -> bool:
    project_root = Path(action["project_path"]).expanduser().resolve()
    destination = safe_project_destination(project_root, action["path"])
    if require_after_match and fingerprint(destination) != action.get("after"):
        return False
    before = action["before"]
    backup: Path | None = None
    if before["kind"] == "file":
        backup = Path(action.get("backup", ""))
        backup_fingerprint = fingerprint(backup)
        if (
            backup.is_symlink()
            or not backup.is_file()
            or backup_fingerprint.get("sha256") != before.get("sha256")
            or backup_fingerprint.get("bytes") != before.get("bytes")
        ):
            return False
    elif before["kind"] == "symlink":
        if action.get("backup_symlink_target") != before.get("target"):
            return False
    elif before["kind"] != "absent":
        return False
    if destination.is_symlink() or destination.is_file():
        destination.unlink()
    if before["kind"] == "file":
        assert backup is not None
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(backup, destination)
    elif before["kind"] == "symlink":
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.symlink_to(action["backup_symlink_target"])
    return True


def rollback_actions(actions: list[dict[str, Any]]) -> tuple[int, int]:
    restored = 0
    skipped = 0
    for action in reversed(actions):
        if not action.get("applied"):
            continue
        destination = safe_project_destination(
            Path(action["project_path"]).expanduser().resolve(), action["path"]
        )
        if not restore_action(action, require_after_match=True):
            print(f"SKIP changed or missing backup: {destination}", file=sys.stderr)
            skipped += 1
            continue
        restored += 1
    return restored, skipped


def validate_rollback_manifest(
    manifest: Any, manifest_path: Path
) -> tuple[list[dict[str, Any]], str]:
    if not isinstance(manifest, dict):
        raise HarnessError("sync manifest root must be an object")
    if manifest.get("schema_version") != "harness.sync-manifest.v1":
        raise HarnessError("unsupported sync manifest schema_version")
    if manifest.get("mode") != "apply":
        raise HarnessError("only apply manifests can be rolled back")
    run_id = manifest.get("run_id")
    actions = manifest.get("actions")
    if not isinstance(run_id, str) or not run_id or not isinstance(actions, list):
        raise HarnessError("sync manifest requires run_id and actions")

    required = {
        "project_id",
        "project_path",
        "path",
        "before",
        "desired",
        "operation",
        "applied",
    }
    for index, action in enumerate(actions):
        if not isinstance(action, dict) or not required <= set(action):
            raise HarnessError(f"invalid sync action at index {index}")
        if (
            not isinstance(action["project_path"], str)
            or not Path(action["project_path"]).is_absolute()
        ):
            raise HarnessError(f"action[{index}] project_path must be absolute")
        if not isinstance(action["path"], str) or not isinstance(
            action["applied"], bool
        ):
            raise HarnessError(f"action[{index}] path/applied fields are invalid")
        project_root = Path(action["project_path"]).expanduser().resolve()
        safe_project_destination(project_root, action["path"])
        if action["applied"] and not isinstance(action.get("after"), dict):
            raise HarnessError(
                f"action[{index}] applied action is missing after fingerprint"
            )
        backup = action.get("backup")
        if backup:
            backup_path = Path(str(backup)).expanduser().resolve()
            allowed_backup = receipt_path(project_root, run_id).parent / "payload"
            try:
                backup_path.relative_to(allowed_backup)
            except ValueError as exc:
                raise HarnessError(
                    f"action[{index}] backup escapes run backup root"
                ) from exc

    digest = sync_plan_digest(actions, run_id)
    project_roots = {
        Path(action["project_path"]).expanduser().resolve() for action in actions
    }
    for project_root in project_roots:
        receipt = load_data(receipt_path(project_root, run_id))
        expected = {
            "schema_version": "harness.sync-receipt.v1",
            "run_id": run_id,
            "project_path": str(project_root),
            "plan_sha256": digest,
        }
        if not isinstance(receipt, dict) or any(
            receipt.get(key) != value for key, value in expected.items()
        ):
            raise HarnessError(
                f"sync receipt does not authorize manifest {manifest_path} for {project_root}"
            )
    return list(actions), run_id


def rollback_manifest(manifest_path: Path) -> tuple[int, int]:
    manifest = load_data(manifest_path)
    actions, run_id = validate_rollback_manifest(manifest, manifest_path)
    result = rollback_actions(actions)
    if result[1] == 0:
        for project_root in {
            Path(action["project_path"]).resolve() for action in actions
        }:
            receipt = receipt_path(project_root, run_id)
            value = load_data(receipt)
            value["rolled_back_at"] = utc_now()
            write_json(receipt, value)
    return result


def select_projects(
    root: Path,
    registry_path: Path,
    selectors: list[str],
    canary: bool,
) -> list[dict[str, Any]]:
    registry = load_data(registry_path)
    entries = [
        dict(item) for item in registry.get("projects", []) if item.get("enabled", True)
    ]
    by_id = {item["id"]: item for item in entries}
    by_path = {str(Path(item["path"]).expanduser().resolve()): item for item in entries}
    if selectors:
        selected = []
        for index, selector in enumerate(selectors):
            resolved = (
                str(Path(selector).expanduser().resolve())
                if "/" in selector or selector.startswith(".")
                else ""
            )
            item = by_id.get(selector) or by_path.get(resolved)
            if item is None:
                item = {
                    "id": f"adhoc-{index + 1}",
                    "path": resolved or str((Path.cwd() / selector).resolve()),
                    "profile": ".claude/registry/projects/default.json",
                    "enabled": True,
                    "canary": index == 0,
                }
            selected.append(dict(item))
    else:
        selected = entries
    if canary:
        marked = [item for item in selected if item.get("canary")]
        selected = marked[:1] if marked else selected[:1]
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "targets", nargs="*", help="Backward-compatible project ids or paths"
    )
    parser.add_argument("--root", type=Path, help="Harness source root")
    parser.add_argument("--registry", type=Path, help="Project registry JSON")
    parser.add_argument(
        "--project", action="append", default=[], help="Project id or path; repeatable"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply planned changes (default is dry-run)",
    )
    parser.add_argument(
        "--canary", action="store_true", help="Limit to the first canary project"
    )
    parser.add_argument(
        "--manifest-out", type=Path, help="Write the plan/apply manifest"
    )
    parser.add_argument("--rollback", type=Path, help="Rollback a prior apply manifest")
    args = parser.parse_args()

    if args.rollback:
        try:
            restored, skipped = rollback_manifest(args.rollback.resolve())
        except HarnessError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
        print(f"Rollback: {restored} restored, {skipped} skipped")
        return 1 if skipped else 0

    root = (args.root or project_root_from(Path(__file__))).resolve()
    registry_path = (
        args.registry or root / ".claude" / "registry" / "projects" / "projects.json"
    )
    if not registry_path.is_absolute():
        registry_path = root / registry_path
    selectors = [*args.project, *args.targets]
    try:
        projects = select_projects(root, registry_path, selectors, args.canary)
        if not projects:
            raise HarnessError("no projects selected")
        all_actions: list[dict[str, Any]] = []
        used_pack_ids: set[str] = set()
        for project in projects:
            target = Path(project["path"]).expanduser().resolve()
            if not target.is_dir():
                print(f"SKIP missing project: {target}", file=sys.stderr)
                continue
            profile_path = Path(
                project.get("profile", ".claude/registry/projects/default.json")
            )
            if not profile_path.is_absolute():
                profile_path = root / profile_path
            profile = load_data(profile_path)
            packs = load_profile_packs(root, profile)
            used_pack_ids.update(str(pack.get("id", "unknown")) for pack in packs)
            assets = combine_pack_assets(root, packs)
            all_actions.extend(plan_project(root, project, assets, profile))
            all_actions.extend(plan_settings_merges(project, packs))
    except (HarnessError, KeyError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    conflicts = [
        action for action in all_actions if action["operation"].startswith("conflict-")
    ]
    run_id = f"{utc_now().replace(':', '').replace('-', '')}-{uuid.uuid4().hex[:8]}"
    counts: dict[str, int] = {}
    for action in all_actions:
        counts[action["operation"]] = counts.get(action["operation"], 0) + 1
    manifest = {
        "schema_version": "harness.sync-manifest.v1",
        "run_id": run_id,
        "generated_at": utc_now(),
        "source_root": str(root),
        "mode": "apply" if args.apply else "dry-run",
        "canary": args.canary,
        "packs": sorted(used_pack_ids),
        "actions": sanitized_actions(all_actions),
        "summary": counts,
    }
    output = None
    if args.manifest_out:
        output = (
            args.manifest_out
            if args.manifest_out.is_absolute()
            else root / args.manifest_out
        )
    elif args.apply:
        output = root / ".claude" / "sync-manifests" / f"{run_id}.json"

    def checkpoint() -> None:
        if output is None:
            return
        manifest["actions"] = sanitized_actions(all_actions)
        write_json(output, manifest)

    if args.apply:
        if conflicts:
            for action in conflicts:
                print(
                    f"ERROR {action['operation']}: {action['project_path']}/{action['path']}",
                    file=sys.stderr,
                )
            return 2
        project_roots = {
            Path(action["project_path"]).expanduser().resolve()
            for action in all_actions
        }
        plan_sha256 = sync_plan_digest(all_actions, run_id)
        try:
            manifest["journal_state"] = "planned"
            checkpoint()
            for project_root in project_roots:
                write_json(
                    receipt_path(project_root, run_id),
                    {
                        "schema_version": "harness.sync-receipt.v1",
                        "run_id": run_id,
                        "project_path": str(project_root),
                        "plan_sha256": plan_sha256,
                        "created_at": utc_now(),
                    },
                )
            manifest["journal_state"] = "applying"
            checkpoint()
            apply_actions(root, all_actions, run_id, checkpoint)
            manifest["journal_state"] = "applied"
            manifest["applied_at"] = utc_now()
            checkpoint()
        except (HarnessError, OSError) as exc:
            restored, skipped = rollback_actions(all_actions)
            manifest["journal_state"] = (
                "rolled-back" if skipped == 0 else "rollback-incomplete"
            )
            manifest["rollback"] = {
                "restored": restored,
                "skipped": skipped,
                "at": utc_now(),
            }
            try:
                checkpoint()
            except (HarnessError, OSError):
                pass
            print(
                f"ERROR during apply: {exc}; automatic rollback restored={restored} skipped={skipped}",
                file=sys.stderr,
            )
            return 2
    elif output is not None:
        checkpoint()

    if output is not None:
        print(f"Manifest: {output}")
    print(
        json.dumps(
            {"mode": manifest["mode"], "projects": len(projects), "summary": counts},
            ensure_ascii=False,
        )
    )
    if not args.apply:
        print("Dry-run only. Re-run with --apply to write changes.")
    return 1 if conflicts else 0


if __name__ == "__main__":
    raise SystemExit(main())
