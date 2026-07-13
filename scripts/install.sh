#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CLAUDE_SRC="$PROJECT_DIR/.claude"
CLAUDE_DEST="${CLAUDE_CRAFT_DEST:-$HOME/.claude}"
SHARED_SKILLS_LINK="${CLAUDE_CRAFT_SHARED_SKILLS_LINK:-$HOME/.agents/skills}"
DIST_DIR="${CLAUDE_CRAFT_DIST_DIR:-$PROJECT_DIR/dist}"
OWNERSHIP_MANIFEST_REL=".claude/.claude-craft-install-manifest.json"
OWNERSHIP_MANIFEST="$CLAUDE_DEST/$OWNERSHIP_MANIFEST_REL"

INSTALL_MODE="link"
ACTION="install"
APPLY=0

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --link, -l    Install runtime paths as symbolic links (default)"
    echo "  --copy, -c    Install runtime paths as copies"
    echo "  --export, -e  Create a distribution zip package"
    echo "  --dry-run     Print the installation/export plan without writing (default)"
    echo "  --apply       Apply the installation/export plan"
    echo "  --help, -h    Show this help message"
}

print_banner() {
    echo ""
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}  ${BOLD}Woogi Harness Runtime Installer${NC}                        ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}     Registry, packs, rules, evals, tools, providers    ${CYAN}║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --link|-l)
            INSTALL_MODE="link"
            ;;
        --copy|-c)
            INSTALL_MODE="copy"
            ;;
        --export|-e)
            ACTION="export"
            ;;
        --dry-run)
            APPLY=0
            ;;
        --apply)
            APPLY=1
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option:${NC} $1" >&2
            usage >&2
            exit 1
            ;;
    esac
    shift
done

if [ ! -d "$CLAUDE_SRC" ]; then
    echo -e "${RED}Error:${NC} $CLAUDE_SRC not found" >&2
    exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
    echo -e "${RED}Error:${NC} python3 is required to resolve the project-pack closure" >&2
    exit 1
fi

validate_destructive_roots() {
    python3 - "$PROJECT_DIR" "$CLAUDE_DEST" "$SHARED_SKILLS_LINK" <<'PY'
import sys
from pathlib import Path

source = Path(sys.argv[1]).resolve()
home = Path.home().resolve()


def resolved_absolute(raw: str, label: str, *, follow_leaf: bool = True) -> Path:
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        raise SystemExit(f"Error: unsafe {label}; path must be absolute: {raw}")
    resolved = (
        candidate.resolve(strict=False)
        if follow_leaf
        else candidate.parent.resolve(strict=False) / candidate.name
    )
    if resolved == Path("/") or resolved == home or len(resolved.parts) < 3:
        raise SystemExit(f"Error: unsafe {label}; destructive root is too broad: {resolved}")
    if resolved == source or resolved in source.parents or source in resolved.parents:
        raise SystemExit(
            f"Error: unsafe {label}; install destination overlaps source repository: {resolved}"
        )
    return resolved


runtime = resolved_absolute(sys.argv[2], "CLAUDE_CRAFT_DEST")
shared = resolved_absolute(
    sys.argv[3], "CLAUDE_CRAFT_SHARED_SKILLS_LINK", follow_leaf=False
)
if runtime == shared:
    raise SystemExit("Error: runtime root and shared skills link must be different paths")
PY
}

validate_destructive_roots

PACK_PATHS=()
PACK_PATH_OUTPUT="$({
    python3 - "$PROJECT_DIR" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()


def safe_relative(raw: object, label: str, *, require_exists: bool = True) -> str:
    value = str(raw).strip()
    relative = Path(value)
    if not value or relative.is_absolute() or ".." in relative.parts:
        raise SystemExit(f"Error: unsafe {label}; expected repository-relative path: {raw}")
    candidate = root / relative
    if require_exists and not (candidate.exists() or candidate.is_symlink()):
        raise SystemExit(f"Error: missing {label}: {value}")
    try:
        candidate.resolve(strict=require_exists).relative_to(root)
    except (OSError, ValueError) as exc:
        raise SystemExit(f"Error: unsafe {label}; path escapes source repository: {value}") from exc
    return relative.as_posix()


profile_path = root / ".claude/registry/projects/default.json"
profile = json.loads(profile_path.read_text())
pack_files = [
    safe_relative(item, "project pack")
    for item in [profile["pack"], *profile.get("pack_overlays", [])]
]
paths = []
for pack_file in pack_files:
    pack = json.loads((root / pack_file).read_text())
    for raw_path in pack.get("paths", []):
        path = safe_relative(raw_path, f"runtime closure path from {pack_file}")
        if path not in paths:
            paths.append(path)

# A packed directory already carries every nested overlay path. Keeping only
# root-most paths prevents link mode from attempting to write through a linked
# parent directory.
selected = []
for path in paths:
    if any(path.startswith(parent + "/") and (root / parent).is_dir() for parent in selected):
        continue
    selected.append(path)

print("\n".join(selected))
PY
} )"
while IFS= read -r path; do
    [ -n "$path" ] && PACK_PATHS+=("$path")
done <<< "$PACK_PATH_OUTPUT"

RUNTIME_OWNED_PATHS=("${PACK_PATHS[@]}" ".claude/settings.json")
RUNTIME_OWNED_PATHS+=("AGENTS.md" "GEMINI.md" ".agents/skills")
for component in agents skills hooks commands templates rules evals registry project-packs; do
    RUNTIME_OWNED_PATHS+=("$component")
done
RUNTIME_OWNED_PATHS+=("statusline.py")

EXTRA_EXPORT_PATHS=(
    "README.md"
    "docs/CONTRIBUTING.md"
    "docs/260713-harness-runtime-v3.md"
    "docs/260713-design-runtime-v3.md"
    "docs/install.sh"
    "scripts/install.sh"
    ".claude/settings.json"
)

validate_source_closure() {
    local path
    for path in "${PACK_PATHS[@]}" "${EXTRA_EXPORT_PATHS[@]}"; do
        if [ ! -e "$PROJECT_DIR/$path" ] && [ ! -L "$PROJECT_DIR/$path" ]; then
            echo -e "${RED}Error:${NC} runtime closure path is missing: $path" >&2
            exit 1
        fi
    done

    local prompt_link="$CLAUDE_SRC/skills/image-prompt"
    local expected_prompt_target="../../third_party/gongnyang-prompt-kit/skills/image-prompt"
    if [ ! -L "$prompt_link" ] || [ "$(readlink "$prompt_link")" != "$expected_prompt_target" ]; then
        echo -e "${RED}Error:${NC} $prompt_link must link to $expected_prompt_target" >&2
        exit 1
    fi
    if [ ! -f "$prompt_link/SKILL.md" ]; then
        echo -e "${RED}Error:${NC} image-prompt link does not resolve to the vendored Gongnyang skill" >&2
        exit 1
    fi
}

ownership_preflight() {
    python3 - "$CLAUDE_DEST" "$SHARED_SKILLS_LINK" "$OWNERSHIP_MANIFEST" "${RUNTIME_OWNED_PATHS[@]}" <<'PY'
import hashlib
import json
import os
import sys
from pathlib import Path

runtime = Path(sys.argv[1]).expanduser().absolute()
shared = Path(sys.argv[2]).expanduser().absolute()
manifest_path = Path(sys.argv[3]).expanduser().absolute()
planned = list(dict.fromkeys(sys.argv[4:]))
schema = "claude-craft.install-ownership.v1"


def lexists(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def safe_relative(raw: str) -> Path:
    relative = Path(raw)
    if not raw or relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"unsafe ownership path: {raw}")
    return relative


def fingerprint(path: Path) -> dict[str, object]:
    mode = path.lstat().st_mode & 0o7777
    if path.is_symlink():
        target = os.readlink(path)
        return {
            "kind": "symlink",
            "target": target,
            "sha256": hashlib.sha256(target.encode("utf-8")).hexdigest(),
            "mode": mode,
        }
    if path.is_file():
        digest = hashlib.sha256()
        size = 0
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
                size += len(chunk)
        return {
            "kind": "file",
            "sha256": digest.hexdigest(),
            "bytes": size,
            "mode": mode,
        }
    if path.is_dir():
        digest = hashlib.sha256()
        entries = 0
        size = 0
        for child in sorted(path.rglob("*"), key=lambda item: item.relative_to(path).as_posix()):
            relative = child.relative_to(path).as_posix()
            if child.is_symlink():
                kind = "symlink"
                payload = os.readlink(child).encode("utf-8")
            elif child.is_file():
                kind = "file"
                file_digest = hashlib.sha256()
                file_size = 0
                with child.open("rb") as handle:
                    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                        file_digest.update(chunk)
                        file_size += len(chunk)
                payload = file_digest.hexdigest().encode("ascii")
                size += file_size
            elif child.is_dir():
                kind = "directory"
                payload = b""
            else:
                raise ValueError(f"unsupported installed path type: {child}")
            child_mode = child.lstat().st_mode & 0o7777
            digest.update(
                kind.encode("ascii")
                + b"\0"
                + relative.encode("utf-8")
                + b"\0"
                + str(child_mode).encode("ascii")
                + b"\0"
                + payload
                + b"\n"
            )
            entries += 1
        return {
            "kind": "directory",
            "sha256": digest.hexdigest(),
            "entries": entries,
            "bytes": size,
            "mode": mode,
        }
    raise ValueError(f"unsupported installed path type: {path}")


def validate_parent_chain(base: Path, relative: Path, errors: list[str]) -> None:
    current = base
    for part in relative.parts[:-1]:
        current /= part
        if not lexists(current):
            continue
        if current.is_symlink():
            errors.append(f"parent path is an unowned symlink: {current}")
            return
        if not current.is_dir():
            errors.append(f"parent path is not a directory: {current}")
            return


errors: list[str] = []
owned_runtime: dict[str, object] = {}
owned_external: dict[str, object] = {}
if lexists(manifest_path):
    if not manifest_path.is_file() or manifest_path.is_symlink():
        errors.append(f"ownership manifest is not a regular file: {manifest_path}")
    else:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"ownership manifest is unreadable: {exc}")
        else:
            if manifest.get("schema_version") != schema:
                errors.append("ownership manifest schema is unsupported")
            recorded_root = Path(str(manifest.get("runtime_root", ""))).expanduser().absolute()
            if recorded_root != runtime:
                errors.append(
                    f"ownership manifest runtime root mismatch: {recorded_root} != {runtime}"
                )
            paths = manifest.get("owned_paths", {})
            if not isinstance(paths, dict):
                errors.append("ownership manifest owned_paths must be an object")
            else:
                owned_runtime = paths.get("runtime", {})
                owned_external = paths.get("external", {})
                if not isinstance(owned_runtime, dict) or not isinstance(owned_external, dict):
                    errors.append("ownership manifest path maps must be objects")
                    owned_runtime = {}
                    owned_external = {}

manifest_exists = bool(owned_runtime or owned_external or manifest_path.is_file())
for raw in planned:
    try:
        relative = safe_relative(raw)
    except ValueError as exc:
        errors.append(str(exc))
        continue
    validate_parent_chain(runtime, relative, errors)
    destination = runtime / relative
    if not lexists(destination):
        continue
    expected = owned_runtime.get(relative.as_posix()) if manifest_exists else None
    if expected is None:
        errors.append(f"refusing to replace path not owned by this installer: {destination}")
        continue
    try:
        actual = fingerprint(destination)
    except (OSError, ValueError) as exc:
        errors.append(f"cannot fingerprint owned path {destination}: {exc}")
        continue
    if actual != expected:
        errors.append(f"owned path changed since installation; refusing update: {destination}")

# Previously installed paths remain owned even if a later pack stops updating
# them. Verify their bytes so a future installer cannot silently absorb edits.
for raw, expected in owned_runtime.items():
    try:
        relative = safe_relative(raw)
    except ValueError as exc:
        errors.append(str(exc))
        continue
    destination = runtime / relative
    if lexists(destination):
        try:
            actual = fingerprint(destination)
        except (OSError, ValueError) as exc:
            errors.append(f"cannot fingerprint owned path {destination}: {exc}")
            continue
        if actual != expected:
            message = f"owned path changed since installation; refusing update: {destination}"
            if message not in errors:
                errors.append(message)

shared_key = str(shared)
if lexists(shared):
    expected = owned_external.get(shared_key) if manifest_exists else None
    if expected is None:
        errors.append(f"refusing to replace path not owned by this installer: {shared}")
    else:
        try:
            actual = fingerprint(shared)
        except (OSError, ValueError) as exc:
            errors.append(f"cannot fingerprint owned path {shared}: {exc}")
        else:
            if actual != expected:
                errors.append(f"owned path changed since installation; refusing update: {shared}")

for raw, expected in owned_external.items():
    path = Path(raw).expanduser().absolute()
    if lexists(path):
        try:
            actual = fingerprint(path)
        except (OSError, ValueError) as exc:
            errors.append(f"cannot fingerprint owned path {path}: {exc}")
            continue
        if actual != expected:
            message = f"owned path changed since installation; refusing update: {path}"
            if message not in errors:
                errors.append(message)

preserved_settings = runtime / "settings.json"
if lexists(preserved_settings) and not preserved_settings.is_file():
    errors.append(f"preserved settings path must be a regular file: {preserved_settings}")

if errors:
    print("Error: install ownership preflight failed:", file=sys.stderr)
    for error in errors:
        print(f"  - {error}", file=sys.stderr)
    raise SystemExit(1)
PY
}

write_ownership_manifest() {
    local output="$1"
    python3 - "$PROJECT_DIR" "$CLAUDE_DEST" "$SHARED_SKILLS_LINK" "$OWNERSHIP_MANIFEST" "$INSTALL_MODE" "$output" "${RUNTIME_OWNED_PATHS[@]}" <<'PY'
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

source = Path(sys.argv[1]).resolve()
runtime = Path(sys.argv[2]).expanduser().absolute()
shared = Path(sys.argv[3]).expanduser().absolute()
previous_path = Path(sys.argv[4]).expanduser().absolute()
install_mode = sys.argv[5]
output = Path(sys.argv[6])
planned = list(dict.fromkeys(sys.argv[7:]))


def lexists(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def fingerprint(path: Path) -> dict[str, object]:
    mode = path.lstat().st_mode & 0o7777
    if path.is_symlink():
        target = os.readlink(path)
        return {
            "kind": "symlink",
            "target": target,
            "sha256": hashlib.sha256(target.encode("utf-8")).hexdigest(),
            "mode": mode,
        }
    if path.is_file():
        digest = hashlib.sha256()
        size = 0
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
                size += len(chunk)
        return {
            "kind": "file",
            "sha256": digest.hexdigest(),
            "bytes": size,
            "mode": mode,
        }
    if path.is_dir():
        digest = hashlib.sha256()
        entries = 0
        size = 0
        for child in sorted(path.rglob("*"), key=lambda item: item.relative_to(path).as_posix()):
            relative = child.relative_to(path).as_posix()
            if child.is_symlink():
                kind = "symlink"
                payload = os.readlink(child).encode("utf-8")
            elif child.is_file():
                kind = "file"
                file_digest = hashlib.sha256()
                file_size = 0
                with child.open("rb") as handle:
                    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                        file_digest.update(chunk)
                        file_size += len(chunk)
                payload = file_digest.hexdigest().encode("ascii")
                size += file_size
            elif child.is_dir():
                kind = "directory"
                payload = b""
            else:
                raise SystemExit(f"Error: unsupported installed path type: {child}")
            child_mode = child.lstat().st_mode & 0o7777
            digest.update(
                kind.encode("ascii")
                + b"\0"
                + relative.encode("utf-8")
                + b"\0"
                + str(child_mode).encode("ascii")
                + b"\0"
                + payload
                + b"\n"
            )
            entries += 1
        return {
            "kind": "directory",
            "sha256": digest.hexdigest(),
            "entries": entries,
            "bytes": size,
            "mode": mode,
        }
    raise SystemExit(f"Error: installed path is missing or unsupported: {path}")


owned_runtime: dict[str, object] = {}
owned_external: dict[str, object] = {}
if previous_path.is_file() and not previous_path.is_symlink():
    previous = json.loads(previous_path.read_text(encoding="utf-8"))
    previous_owned = previous.get("owned_paths", {})
    if isinstance(previous_owned, dict):
        old_runtime = previous_owned.get("runtime", {})
        old_external = previous_owned.get("external", {})
        if isinstance(old_runtime, dict):
            for raw, value in old_runtime.items():
                path = runtime / Path(raw)
                if lexists(path):
                    owned_runtime[raw] = value
        if isinstance(old_external, dict):
            for raw, value in old_external.items():
                if lexists(Path(raw).expanduser().absolute()):
                    owned_external[raw] = value

for raw in planned:
    path = runtime / Path(raw)
    owned_runtime[Path(raw).as_posix()] = fingerprint(path)
owned_external[str(shared)] = fingerprint(shared)

payload = {
    "schema_version": "claude-craft.install-ownership.v1",
    "installed_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "source_root": str(source),
    "runtime_root": str(runtime),
    "install_mode": install_mode,
    "owned_paths": {
        "runtime": dict(sorted(owned_runtime.items())),
        "external": dict(sorted(owned_external.items())),
    },
    "preserved_paths": ["settings.json"],
}
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
os.chmod(output, 0o644)
PY
}

print_install_plan() {
    local path
    echo "Mode: dry-run"
    echo "Install mode: $INSTALL_MODE"
    echo "Runtime root: $CLAUDE_DEST"
    echo "Canonical project-pack closure:"
    for path in "${PACK_PATHS[@]}"; do
        echo "  - $path"
    done
    echo "  - .claude/settings.json (canonical doctor configuration)"
    echo "Compatibility links:"
    echo "  - $CLAUDE_DEST/{agents,skills,hooks,commands,templates,rules,evals,registry,project-packs,statusline.py}"
    echo "  - $CLAUDE_DEST/{AGENTS.md,GEMINI.md,.agents/skills}"
    echo "  - $SHARED_SKILLS_LINK"
    echo "Ownership manifest: $OWNERSHIP_MANIFEST"
    echo "Existing targets must match a prior ownership fingerprint."
    echo ""
    echo -e "${YELLOW}Dry-run only.${NC} Re-run with --apply to write changes."
}

stage_path() {
    local relative="$1"
    local src="$PROJECT_DIR/$relative"
    local dest="$STAGE_RUNTIME/$relative"

    mkdir -p "$(dirname "$dest")"
    if [ "$INSTALL_MODE" = "copy" ]; then
        cp -R "$src" "$dest"
    else
        ln -s "$src" "$dest"
    fi
}

stage_link() {
    local target="$1"
    local relative="$2"
    local dest="$STAGE_RUNTIME/$relative"

    mkdir -p "$(dirname "$dest")"
    ln -s "$target" "$dest"
}

stage_canonical_settings() {
    local dest="$STAGE_RUNTIME/.claude/settings.json"
    mkdir -p "$(dirname "$dest")"
    cp "$CLAUDE_SRC/settings.json" "$dest"
}

validate_staged_runtime() {
    local prompt_link="$STAGE_RUNTIME/.claude/skills/image-prompt"
    if [ ! -L "$prompt_link" ] || [ ! -f "$prompt_link/SKILL.md" ]; then
        echo -e "${RED}Error:${NC} staged image-prompt symlink is unresolved" >&2
        exit 1
    fi
}

stage_default_settings() {
    cat > "$STAGE_RUNTIME/settings.json" <<'EOF'
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/statusline.py"
  }
}
EOF
}

path_exists() {
    [ -e "$1" ] || [ -L "$1" ]
}

TRANSACTION_ACTIVE=0
TRANSACTION_ROOT=""
TRANSACTION_DESTINATIONS=()
TRANSACTION_BACKUPS=()
COMMIT_COUNT=0

remove_owned_path() {
    local path="$1"
    if [ -L "$path" ] || [ -f "$path" ]; then
        rm -f "$path"
    elif [ -d "$path" ]; then
        rm -rf "$path"
    fi
}

rollback_install() {
    local index dest backup
    set +e
    for ((index=${#TRANSACTION_DESTINATIONS[@]} - 1; index >= 0; index--)); do
        dest="${TRANSACTION_DESTINATIONS[$index]}"
        backup="${TRANSACTION_BACKUPS[$index]}"
        remove_owned_path "$dest"
        if [ "$backup" != "-" ] && path_exists "$backup"; then
            mkdir -p "$(dirname "$dest")"
            mv "$backup" "$dest"
        fi
    done
    if [ -n "$TRANSACTION_ROOT" ] && [ -d "$TRANSACTION_ROOT" ]; then
        rm -rf "$TRANSACTION_ROOT"
    fi
    set -e
}

transaction_exit() {
    local status=$?
    if [ "$TRANSACTION_ACTIVE" -eq 1 ]; then
        echo -e "${RED}Error:${NC} installation failed; rolling back owned paths" >&2
        rollback_install
    fi
    exit "$status"
}

maybe_inject_test_failure() {
    local fail_after="${CLAUDE_CRAFT_TEST_FAIL_AFTER_COMMIT:-}"
    if [ -z "$fail_after" ]; then
        return
    fi
    if [ "${CLAUDE_CRAFT_TESTING:-}" != "1" ]; then
        echo -e "${RED}Error:${NC} CLAUDE_CRAFT_TEST_FAIL_AFTER_COMMIT is test-only" >&2
        return 2
    fi
    if ! [[ "$fail_after" =~ ^[0-9]+$ ]]; then
        echo -e "${RED}Error:${NC} invalid test failpoint" >&2
        return 2
    fi
    if [ "$COMMIT_COUNT" -eq "$fail_after" ]; then
        echo -e "${RED}Error:${NC} injected installer transaction failure" >&2
        return 97
    fi
}

commit_staged_path() {
    local staged="$1"
    local dest="$2"
    local backup="$3"

    mkdir -p "$(dirname "$dest")" "$(dirname "$backup")"
    if path_exists "$dest"; then
        mv "$dest" "$backup"
        TRANSACTION_BACKUPS+=("$backup")
    else
        TRANSACTION_BACKUPS+=("-")
    fi
    TRANSACTION_DESTINATIONS+=("$dest")
    mv "$staged" "$dest"
    COMMIT_COUNT=$((COMMIT_COUNT + 1))
    maybe_inject_test_failure
}

install_runtime() {
    local path component
    local components=(agents skills hooks commands templates rules evals registry project-packs)

    mkdir -p "$CLAUDE_DEST"
    TRANSACTION_ROOT="$(mktemp -d "$CLAUDE_DEST/.claude-craft-install.XXXXXX")"
    local stage_root="$TRANSACTION_ROOT/stage"
    local backup_root="$TRANSACTION_ROOT/backup"
    STAGE_RUNTIME="$stage_root/runtime"
    mkdir -p "$STAGE_RUNTIME" "$backup_root/runtime"

    echo "Staging canonical runtime closure..."
    for path in "${PACK_PATHS[@]}"; do
        stage_path "$path"
    done
    stage_canonical_settings
    stage_link "CLAUDE.md" "AGENTS.md"
    stage_link "CLAUDE.md" "GEMINI.md"
    stage_link "../.claude/skills" ".agents/skills"
    for component in "${components[@]}"; do
        stage_link ".claude/$component" "$component"
    done
    stage_link ".claude/statusline.py" "statusline.py"
    local shared_target
    if [ "$CLAUDE_DEST" = "$HOME/.claude" ]; then
        shared_target="../.claude/skills"
    else
        shared_target="$CLAUDE_DEST/skills"
    fi
    ln -s "$shared_target" "$stage_root/shared-skills"
    local install_default_settings=0
    if ! path_exists "$CLAUDE_DEST/settings.json"; then
        stage_default_settings
        install_default_settings=1
    fi
    validate_staged_runtime

    TRANSACTION_ACTIVE=1
    trap transaction_exit EXIT
    trap 'exit 130' INT
    trap 'exit 129' HUP
    trap 'exit 143' TERM

    echo "Committing owned runtime paths..."
    for path in "${PACK_PATHS[@]}"; do
        commit_staged_path \
            "$STAGE_RUNTIME/$path" \
            "$CLAUDE_DEST/$path" \
            "$backup_root/runtime/$path"
    done
    commit_staged_path \
        "$STAGE_RUNTIME/.claude/settings.json" \
        "$CLAUDE_DEST/.claude/settings.json" \
        "$backup_root/runtime/.claude/settings.json"
    commit_staged_path "$STAGE_RUNTIME/AGENTS.md" "$CLAUDE_DEST/AGENTS.md" "$backup_root/runtime/AGENTS.md"
    commit_staged_path "$STAGE_RUNTIME/GEMINI.md" "$CLAUDE_DEST/GEMINI.md" "$backup_root/runtime/GEMINI.md"
    commit_staged_path "$STAGE_RUNTIME/.agents/skills" "$CLAUDE_DEST/.agents/skills" "$backup_root/runtime/.agents/skills"
    for component in "${components[@]}"; do
        commit_staged_path \
            "$STAGE_RUNTIME/$component" \
            "$CLAUDE_DEST/$component" \
            "$backup_root/runtime/$component"
    done
    commit_staged_path \
        "$STAGE_RUNTIME/statusline.py" \
        "$CLAUDE_DEST/statusline.py" \
        "$backup_root/runtime/statusline.py"
    if [ "$install_default_settings" -eq 1 ]; then
        commit_staged_path \
            "$STAGE_RUNTIME/settings.json" \
            "$CLAUDE_DEST/settings.json" \
            "$backup_root/runtime/settings.json"
    fi

    local external_backup="$SHARED_SKILLS_LINK.claude-craft-backup.$(basename "$TRANSACTION_ROOT")"
    if path_exists "$external_backup"; then
        echo -e "${RED}Error:${NC} external transaction backup already exists: $external_backup" >&2
        return 1
    fi
    commit_staged_path "$stage_root/shared-skills" "$SHARED_SKILLS_LINK" "$external_backup"

    local staged_manifest="$stage_root/ownership-manifest.json"
    write_ownership_manifest "$staged_manifest"
    commit_staged_path "$staged_manifest" "$OWNERSHIP_MANIFEST" "$backup_root/ownership-manifest.json"

    TRANSACTION_ACTIVE=0
    trap - EXIT INT HUP TERM
    remove_owned_path "$external_backup"
    rm -rf "$TRANSACTION_ROOT"
    TRANSACTION_ROOT=""

    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC}  ${BOLD}✓ Runtime installation complete${NC}                       ${GREEN}║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Verify:"
    echo "  python3 \"$CLAUDE_DEST/scripts/harness-doctor.py\" --root \"$CLAUDE_DEST\""
    echo ""
    echo "Restart the active CLI so it reloads instructions and skills."
}

export_package() {
    local package_name="woogi-harness-${WOOGI_HARNESS_PACKAGE_DATE:-${CLAUDE_CRAFT_PACKAGE_DATE:-$(date +%Y%m%d)}}.zip"
    local package_path="$DIST_DIR/$package_name"
    local files=("${PACK_PATHS[@]}" "${EXTRA_EXPORT_PATHS[@]}" "AGENTS.md" "GEMINI.md" ".agents/skills")

    echo "Mode: $([ "$APPLY" -eq 1 ] && echo apply || echo dry-run)"
    echo "Export: $package_path"
    echo "Symlinks are stored as symlinks, including .claude/skills/image-prompt."
    if [ "$APPLY" -ne 1 ]; then
        echo ""
        echo -e "${YELLOW}Dry-run only.${NC} Re-run with --export --apply to create the package."
        return
    fi
    if ! command -v zip >/dev/null 2>&1; then
        echo -e "${RED}Error:${NC} zip is required for --export" >&2
        exit 1
    fi

    mkdir -p "$DIST_DIR"
    rm -f "$package_path"
    (
        cd "$PROJECT_DIR"
        zip -qry "$package_path" "${files[@]}" \
            -x "*.DS_Store" \
            -x "*/__pycache__/*" \
            -x "*.pyc" \
            -x ".claude/logs/*" \
            -x ".claude/settings.local.json"
    )

    echo -e "${GREEN}Package created:${NC} $package_path"
}

print_banner
validate_source_closure

if [ "$ACTION" = "export" ]; then
    export_package
else
    ownership_preflight
    if [ "$APPLY" -eq 1 ]; then
        install_runtime
    else
        print_install_plan
    fi
fi
