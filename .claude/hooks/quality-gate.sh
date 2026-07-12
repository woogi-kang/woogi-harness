#!/usr/bin/env bash
# Claude Code PostToolUse quality feedback.
# Read-only: never installs packages, formats files, or hides failed checks.

set -u

INPUT="$(cat)" || {
  printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"Quality gate could not read hook input. Finalization is blocked until checks run."}}'
  exit 0
}
if ! command -v jq >/dev/null 2>&1; then
  printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"Quality gate dependency jq is missing. This edit is unverified; Design Runtime finalization remains fail-closed."}}'
  exit 0
fi
FILE="$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null)" || exit 0
[[ -n "$FILE" && -f "$FILE" ]] || exit 0

case "$FILE" in
  */node_modules/*|*/.venv/*|*/dist/*|*/build/*|*/coverage/*|*/__pycache__/*|*/third_party/*|*/_vendor/*) exit 0 ;;
esac

PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-$(git -C "$(dirname "$FILE")" rev-parse --show-toplevel 2>/dev/null || pwd)}"
HARNESS_ROOT="$PROJECT_ROOT/.claude"
LOG_DIR="$HARNESS_ROOT/logs"
LOG_FILE="$LOG_DIR/quality-gate.jsonl"
mkdir -p "$LOG_DIR"

EXT="${FILE##*.}"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
FAILURES=()
CHECKS_RUN=0

record_check() {
  local label="$1"
  local status="$2"
  local detail="$3"
  jq -cn \
    --arg ts "$TIMESTAMP" \
    --arg file "$FILE" \
    --arg check "$label" \
    --arg status "$status" \
    --arg detail "$detail" \
    '{schema_version:"harness.quality-gate.v1",timestamp:$ts,file:$file,check:$check,status:$status,detail:$detail}' \
    >> "$LOG_FILE"
}

run_check() {
  local label="$1"
  shift
  local output
  CHECKS_RUN=$((CHECKS_RUN + 1))
  if output="$("$@" 2>&1)"; then
    record_check "$label" "passed" ""
  else
    local summary
    summary="$(printf '%s\n' "$output" | tail -n 20 | head -c 4000)"
    record_check "$label" "failed" "$summary"
    FAILURES+=("[$label] $summary")
  fi
}

case "$EXT" in
  py)
    if [[ -x "$PROJECT_ROOT/.venv/bin/ruff" ]]; then
      run_check "ruff-check" "$PROJECT_ROOT/.venv/bin/ruff" check "$FILE"
      run_check "ruff-format" "$PROJECT_ROOT/.venv/bin/ruff" format --check "$FILE"
    elif command -v ruff >/dev/null 2>&1; then
      run_check "ruff-check" ruff check "$FILE"
      run_check "ruff-format" ruff format --check "$FILE"
    fi
    ;;
  ts|tsx|js|jsx|mjs|cjs)
    if [[ -x "$PROJECT_ROOT/node_modules/.bin/biome" ]]; then
      run_check "biome-check" "$PROJECT_ROOT/node_modules/.bin/biome" check "$FILE"
    elif [[ -x "$PROJECT_ROOT/node_modules/.bin/prettier" ]]; then
      run_check "prettier-check" "$PROJECT_ROOT/node_modules/.bin/prettier" --check "$FILE"
    fi
    ;;
  dart)
    if command -v dart >/dev/null 2>&1; then
      run_check "dart-format" dart format --output=none --set-exit-if-changed "$FILE"
    fi
    ;;
  sh|bash)
    if command -v shellcheck >/dev/null 2>&1; then
      run_check "shellcheck" shellcheck "$FILE"
    else
      run_check "bash-syntax" bash -n "$FILE"
    fi
    ;;
esac

case "$EXT" in
  html|css|scss|sass|js|jsx|ts|tsx|vue|svelte|astro|dart)
    DETECTOR="$HARNESS_ROOT/skills/design-harness/scripts/detect-design-slop.mjs"
    if [[ ! -f "$DETECTOR" ]]; then
      CHECKS_RUN=$((CHECKS_RUN + 1))
      record_check "design-slop-hard-gate" "failed" "detector missing: $DETECTOR"
      FAILURES+=("[design-slop-hard-gate] detector missing: $DETECTOR")
    elif ! command -v node >/dev/null 2>&1; then
      CHECKS_RUN=$((CHECKS_RUN + 1))
      record_check "design-slop-hard-gate" "failed" "node runtime unavailable"
      FAILURES+=("[design-slop-hard-gate] node runtime unavailable")
    else
      run_check "design-slop-hard-gate" node "$DETECTOR" --format text --fail-on hard-fail "$FILE"
    fi
    ;;
esac

if (( ${#FAILURES[@]} > 0 )); then
  MESSAGE="Quality gate found ${#FAILURES[@]} failed check(s) for $FILE. Fix them or record an explicit scoped waiver before completion."
  for failure in "${FAILURES[@]}"; do
    MESSAGE+=$'\n'
    MESSAGE+="$failure"
  done
  jq -cn \
    --arg message "$MESSAGE" \
    '{hookSpecificOutput:{hookEventName:"PostToolUse",additionalContext:$message}}'
elif (( CHECKS_RUN > 0 )); then
  record_check "summary" "passed" "$CHECKS_RUN checks completed"
fi

exit 0
