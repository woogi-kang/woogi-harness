#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENDOR="$ROOT/third_party/img2threejs"
LOCK="$VENDOR/UPSTREAM.lock.json"
MANIFEST="$VENDOR/UPSTREAM.manifest"
SKILL_LINK="$ROOT/.claude/skills/img2threejs"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
export PYTHONPYCACHEPREFIX="$TMP/pycache"

for command in git python3; do
  command -v "$command" >/dev/null || {
    echo "ERROR: required command not found: $command" >&2
    exit 1
  }
done

python3 - "$LOCK" <<'PY'
import json
import pathlib
import re
import sys

lock = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
required = {
    "repository",
    "ref",
    "commit",
    "skill_version",
    "license",
    "runtime_paths",
    "archive_sha256",
    "local_patches",
}
missing = sorted(required - lock.keys())
if missing:
    raise SystemExit(f"ERROR: lock fields missing: {', '.join(missing)}")

expected = {
    "repository": "https://github.com/img2threejs/img2threejs",
    "ref": "main",
    "license": "Apache-2.0",
    "runtime_paths": [
        "LICENSE",
        "README.md",
        "CHANGELOG.md",
        "ROADMAP.md",
        "SKILL.md",
        "docs",
        "forge",
        "grimoire",
        "skills",
    ],
    "local_patches": [],
}
for key, value in expected.items():
    if lock.get(key) != value:
        raise SystemExit(f"ERROR: img2threejs lock drift: {key}")
if not re.fullmatch(r"[0-9a-f]{40}", str(lock["commit"])):
    raise SystemExit("ERROR: img2threejs commit must be a full SHA")
if not str(lock["skill_version"]).strip():
    raise SystemExit("ERROR: img2threejs skill_version is empty")
if not re.fullmatch(r"[0-9a-f]{64}", str(lock["archive_sha256"])):
    raise SystemExit("ERROR: img2threejs archive_sha256 is invalid")
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
  printf '%s\n' LICENSE README.md CHANGELOG.md ROADMAP.md SKILL.md
  find "$VENDOR/docs" "$VENDOR/forge" "$VENDOR/grimoire" "$VENDOR/skills" -type f -print |
    sed "s#^$VENDOR/##"
} | LC_ALL=C sort >"$actual_paths"
LC_ALL=C sort -o "$expected_paths" "$expected_paths"

if ! diff -u "$expected_paths" "$actual_paths"; then
  echo "ERROR: vendored runtime file set differs from the upstream manifest" >&2
  exit 1
fi

[[ -L "$SKILL_LINK" ]] || {
  echo "ERROR: .claude/skills/img2threejs must be a symlink to the vendor" >&2
  exit 1
}
[[ "$(readlink "$SKILL_LINK")" == "../../third_party/img2threejs" ]] || {
  echo "ERROR: unexpected img2threejs symlink target" >&2
  exit 1
}

python3 - "$LOCK" "$VENDOR/SKILL.md" <<'PY'
import json
import pathlib
import re
import sys

lock = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
skill = pathlib.Path(sys.argv[2]).read_text(encoding="utf-8")

def field(name: str) -> str:
    match = re.search(rf"^{name}:\s*[\"']?([^\"'\n]+)", skill, re.MULTILINE)
    if not match:
        raise SystemExit(f"ERROR: img2threejs SKILL.md is missing {name}")
    return match.group(1).strip()

if field("name") != "img2threejs":
    raise SystemExit("ERROR: unexpected img2threejs skill name")
if field("version") != lock["skill_version"]:
    raise SystemExit("ERROR: img2threejs skill version differs from lock")
if field("license") != lock["license"]:
    raise SystemExit("ERROR: img2threejs skill license differs from lock")
PY

python3 -m compileall -q "$VENDOR/forge"
python3 "$VENDOR/forge/stage1_intake/probe_image.py" --help >/dev/null
python3 "$VENDOR/forge/stage2_spec/new_pre_spec_assessment.py" --help >/dev/null
python3 "$ROOT/scripts/harness-registry.py" resolve img2threejs >/dev/null

echo "PASS: img2threejs vendor, symlink, Python smoke checks, and registry resolution"
