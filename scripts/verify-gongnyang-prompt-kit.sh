#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENDOR="$ROOT/third_party/gongnyang-prompt-kit"
LOCK="$VENDOR/UPSTREAM.lock.json"
MANIFEST="$VENDOR/UPSTREAM.manifest"
SKILL_LINK="$ROOT/.claude/skills/image-prompt"
HOOK="$VENDOR/hooks/block-text-overlay.sh"
VALIDATOR="$VENDOR/skills/image-prompt/scripts/check_prompt.mjs"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

for command in git node python3; do
  command -v "$command" >/dev/null || {
    echo "ERROR: required command not found: $command" >&2
    exit 1
  }
done

python3 - "$LOCK" <<'PY'
import json
import pathlib
import sys

lock = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
required = {"repository", "ref", "commit", "skill_version", "license", "runtime_paths", "archive_sha256", "local_patches"}
missing = sorted(required - lock.keys())
if missing:
    raise SystemExit(f"ERROR: lock fields missing: {', '.join(missing)}")
if lock["local_patches"] != []:
    raise SystemExit("ERROR: Gongnyang vendor must keep local_patches=[]")
if lock["license"] != "MIT":
    raise SystemExit("ERROR: unexpected Gongnyang license")
expected = {
    "repository": "https://github.com/kimsh-1/gongnyang-prompt-kit",
    "ref": "main",
    "runtime_paths": ["LICENSE", "hooks/block-text-overlay.sh", "skills/image-prompt"],
}
for key, value in expected.items():
    if lock.get(key) != value:
        raise SystemExit(f"ERROR: Gongnyang lock drift: {key}")
if not __import__("re").fullmatch(r"[0-9a-f]{40}", str(lock["commit"])):
    raise SystemExit("ERROR: Gongnyang commit must be a full SHA")
if not str(lock["skill_version"]).strip():
    raise SystemExit("ERROR: Gongnyang skill_version is empty")
if not __import__("re").fullmatch(r"[0-9a-f]{64}", str(lock["archive_sha256"])):
    raise SystemExit("ERROR: Gongnyang archive_sha256 is invalid")
PY

python3 - "$LOCK" "$ROOT/.claude/registry/providers/image-generation.yaml" <<'PY'
import json
import pathlib
import sys

lock = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
policy = json.loads(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"))
compiler = policy.get("prompt_compiler", {})
if compiler.get("vendor_commit") != lock["commit"]:
    raise SystemExit("ERROR: image provider policy commit differs from Gongnyang lock")
if compiler.get("version") != lock["skill_version"]:
    raise SystemExit("ERROR: image provider policy version differs from Gongnyang lock")
if compiler.get("local_patches") != []:
    raise SystemExit("ERROR: image provider policy must keep local_patches=[]")
PY

expected_paths="$TMP/expected-paths"
actual_paths="$TMP/actual-paths"
: >"$expected_paths"

while read -r mode type object path; do
  [[ "$type" == "blob" ]] || {
    echo "ERROR: unsupported manifest object: $type $path" >&2
    exit 1
  }
  actual="$VENDOR/$path"
  [[ -f "$actual" ]] || {
    echo "ERROR: missing vendored file: $path" >&2
    exit 1
  }
  [[ "$(git hash-object "$actual")" == "$object" ]] || {
    echo "ERROR: byte drift in vendored file: $path" >&2
    exit 1
  }
  if [[ "$mode" == "100755" && ! -x "$actual" ]]; then
    echo "ERROR: executable mode drift: $path" >&2
    exit 1
  fi
  if [[ "$mode" == "100644" && -x "$actual" ]]; then
    echo "ERROR: unexpected executable mode: $path" >&2
    exit 1
  fi
  printf '%s\n' "$path" >>"$expected_paths"
done <"$MANIFEST"

{
  printf '%s\n' LICENSE hooks/block-text-overlay.sh
  find "$VENDOR/skills/image-prompt" -type f -print |
    sed "s#^$VENDOR/##"
} | LC_ALL=C sort >"$actual_paths"
LC_ALL=C sort -o "$expected_paths" "$expected_paths"

if ! diff -u "$expected_paths" "$actual_paths"; then
  echo "ERROR: vendored runtime file set differs from the upstream manifest" >&2
  exit 1
fi

[[ -L "$SKILL_LINK" ]] || {
  echo "ERROR: .claude/skills/image-prompt must be a symlink to the vendor" >&2
  exit 1
}
[[ "$(readlink "$SKILL_LINK")" == "../../third_party/gongnyang-prompt-kit/skills/image-prompt" ]] || {
  echo "ERROR: unexpected image-prompt symlink target" >&2
  exit 1
}

node "$VALIDATOR" --test
bash -n "$HOOK"

deny_output="$(printf '%s\n' '{"tool_input":{"command":"python3 -c \"from PIL import ImageDraw\""}}' | bash "$HOOK")"
python3 - "$deny_output" <<'PY'
import json
import sys

payload = json.loads(sys.argv[1])
decision = payload.get("hookSpecificOutput", {}).get("permissionDecision")
if decision != "deny":
    raise SystemExit("ERROR: overlay hook did not deny ImageDraw")
PY

allow_output="$(printf '%s\n' '{"tool_input":{"command":"node check_prompt.mjs --test"}}' | bash "$HOOK")"
[[ -z "$allow_output" ]] || {
  echo "ERROR: overlay hook denied an allowed validator command" >&2
  exit 1
}

python3 - "$ROOT/.claude/settings.json" <<'PY'
import json
import pathlib
import sys

settings = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
commands = []
for matcher in settings.get("hooks", {}).get("PreToolUse", []):
    if matcher.get("matcher") == "Bash":
        commands.extend(hook.get("command", "") for hook in matcher.get("hooks", []))
expected = "$CLAUDE_PROJECT_DIR/third_party/gongnyang-prompt-kit/hooks/block-text-overlay.sh"
if expected not in commands:
    raise SystemExit("ERROR: upstream overlay hook is not registered in .claude/settings.json")
PY

python3 "$ROOT/scripts/verify-image-generation-policy.py"
echo "PASS: Gongnyang Prompt Kit vendor, hook, fixtures, and image-generation policy"
