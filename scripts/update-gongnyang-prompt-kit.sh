#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENDOR="$ROOT/third_party/gongnyang-prompt-kit"
POLICY="$ROOT/.claude/registry/providers/image-generation.yaml"
REPOSITORY="https://github.com/kimsh-1/gongnyang-prompt-kit"
COMMIT=""
APPLY=0
APPLIED=0
TMP=""

usage() {
  echo "Usage: $0 --commit <full-sha> [--apply]"
  echo "Without --apply, fetch, validate, and show the exact staged diff only."
}

rollback() {
  [[ "$APPLIED" -eq 1 ]] || return 0
  rm -rf "$VENDOR"
  mv "$TMP/backup/vendor" "$VENDOR"
  rm -f "$POLICY"
  mv "$TMP/backup/image-generation.yaml" "$POLICY"
  APPLIED=0
  echo "ROLLBACK: restored previous Gongnyang vendor and provider policy" >&2
}

cleanup() {
  local status=$?
  trap - EXIT
  if [[ "$status" -ne 0 ]]; then
    rollback
  fi
  [[ -z "$TMP" ]] || rm -rf "$TMP"
  exit "$status"
}
trap cleanup EXIT

while [[ $# -gt 0 ]]; do
  case "$1" in
    --commit) COMMIT="${2:-}"; shift 2 ;;
    --apply) APPLY=1; shift ;;
    --help|-h) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
  esac
done

[[ "$COMMIT" =~ ^[0-9a-f]{40}$ ]] || {
  echo "ERROR: --commit must be an explicit full SHA; floating updates are forbidden" >&2
  exit 2
}

TMP="$(mktemp -d "$ROOT/.gongnyang-update.XXXXXX")"
UPSTREAM="$TMP/upstream"
STAGED_VENDOR="$TMP/vendor"
STAGED_POLICY="$TMP/image-generation.yaml"
mkdir -p "$UPSTREAM" "$STAGED_VENDOR"

git -C "$UPSTREAM" init -q
git -C "$UPSTREAM" remote add origin "$REPOSITORY"
git -C "$UPSTREAM" fetch -q --depth 1 origin "$COMMIT"
[[ "$(git -C "$UPSTREAM" rev-parse FETCH_HEAD)" == "$COMMIT" ]] || {
  echo "ERROR: fetched commit does not match requested SHA" >&2
  exit 1
}

git -C "$UPSTREAM" archive --format=tar "$COMMIT" \
  LICENSE hooks/block-text-overlay.sh skills/image-prompt |
  tar -xf - -C "$STAGED_VENDOR"
cp "$VENDOR/UPSTREAM.md" "$STAGED_VENDOR/UPSTREAM.md"

git -C "$UPSTREAM" ls-tree -r "$COMMIT" -- \
  LICENSE hooks/block-text-overlay.sh skills/image-prompt >"$STAGED_VENDOR/UPSTREAM.manifest"

archive_sha="$(git -C "$UPSTREAM" archive --format=tar "$COMMIT" \
  LICENSE hooks/block-text-overlay.sh skills/image-prompt | shasum -a 256 | awk '{print $1}')"
skill_version="$(python3 - "$STAGED_VENDOR/skills/image-prompt/SKILL.md" <<'PY'
import re
import sys
from pathlib import Path

text = Path(sys.argv[1]).read_text(encoding="utf-8")
match = re.search(r'^version:\s*["\x27]?([^"\x27\n]+)', text, re.MULTILINE)
if not match:
    raise SystemExit("version missing from upstream SKILL.md")
print(match.group(1).strip())
PY
)"

python3 - "$STAGED_VENDOR/UPSTREAM.lock.json" "$COMMIT" "$skill_version" "$archive_sha" <<'PY'
import json
import sys
from pathlib import Path

payload = {
    "repository": "https://github.com/kimsh-1/gongnyang-prompt-kit",
    "ref": "main",
    "commit": sys.argv[2],
    "skill_version": sys.argv[3],
    "license": "MIT",
    "runtime_paths": ["LICENSE", "hooks/block-text-overlay.sh", "skills/image-prompt"],
    "archive_sha256": sys.argv[4],
    "local_patches": [],
}
Path(sys.argv[1]).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY

python3 - "$POLICY" "$STAGED_POLICY" "$COMMIT" "$skill_version" <<'PY'
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
compiler = payload["prompt_compiler"]
compiler["vendor_commit"] = sys.argv[3]
compiler["version"] = sys.argv[4]
compiler["local_patches"] = []
Path(sys.argv[2]).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY

grep -q '^MIT License$' "$STAGED_VENDOR/LICENSE"
grep -q 'gpt-image-2' "$STAGED_VENDOR/skills/image-prompt/SKILL.md"
node "$STAGED_VENDOR/skills/image-prompt/scripts/check_prompt.mjs" --test
bash -n "$STAGED_VENDOR/hooks/block-text-overlay.sh"
python3 -m json.tool "$STAGED_VENDOR/UPSTREAM.lock.json" >/dev/null
python3 -m json.tool "$STAGED_POLICY" >/dev/null

echo "Staged upstream diff for $COMMIT:"
diff -ruN "$VENDOR" "$STAGED_VENDOR" || true

if [[ "$APPLY" -ne 1 ]]; then
  echo "CHECK ONLY: rerun with --apply after reviewing the staged diff."
  exit 0
fi

mkdir -p "$TMP/backup"
mv "$VENDOR" "$TMP/backup/vendor"
mv "$POLICY" "$TMP/backup/image-generation.yaml"
mv "$STAGED_VENDOR" "$VENDOR"
mv "$STAGED_POLICY" "$POLICY"
APPLIED=1

bash "$ROOT/scripts/verify-gongnyang-prompt-kit.sh"
APPLIED=0
rm -rf "$TMP/backup"
echo "UPDATED: Gongnyang Prompt Kit -> $COMMIT"
