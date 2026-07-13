#!/usr/bin/env bash
# brain-memory-qa.sh - Routing and memory-engine smoke checks.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BRAIN_MEMORY="${BRAIN_MEMORY:-$ROOT_DIR/scripts/brain-memory.sh}"
BRAIN_PILOT="${BRAIN_PILOT:-$ROOT_DIR/scripts/brain-pilot.sh}"

pass_count=0
fail_count=0

pass() {
  pass_count=$((pass_count + 1))
  printf 'ok: %s\n' "$*"
}

fail() {
  fail_count=$((fail_count + 1))
  printf 'fail: %s\n' "$*" >&2
}

needs_memory_lookup() {
  local prompt="$1"

  case "$prompt" in
    *지난번*|*전에*|*이어*|*다시*|*왜\ 이렇게\ 했지*|*왜\ 하기로\ 했지*|*왜\ 정했지*|*이\ 프로젝트*|*결정*|*실패*|*다음\ 액션*|*관련\ 문서*|*GTM*|*PRD*|*마이그레이션*|*resume*|*previous*|*decision*)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

assert_route() {
  local prompt="$1"
  local expected="$2"
  local actual="skip"

  if needs_memory_lookup "$prompt"; then
    actual="lookup"
  fi

  if [ "$actual" = "$expected" ]; then
    pass "route [$expected] $prompt"
  else
    fail "route expected [$expected], got [$actual]: $prompt"
  fi
}

assert_command() {
  local description="$1"
  shift

  if "$@" >/tmp/brain-memory-qa.out 2>/tmp/brain-memory-qa.err; then
    pass "$description"
  else
    fail "$description"
    sed -n '1,80p' /tmp/brain-memory-qa.err >&2 || true
  fi
}

assert_search_contains() {
  local query="$1"
  local expected="$2"
  local output

  output="$("$BRAIN_MEMORY" search "$query")"
  if printf '%s\n' "$output" | rg -q "$expected"; then
    pass "search [$query] contains [$expected]"
  else
    fail "search [$query] missing [$expected]"
    printf '%s\n' "$output" >&2
  fi
}

assert_context_pack() {
  local query="$1"
  local output
  local words

  if ! output="$(BRAIN_TIMEOUT_SECONDS="${BRAIN_QA_CONTEXT_TIMEOUT:-45}" "$BRAIN_MEMORY" context "$query")"; then
    fail "context pack [$query]"
    printf '%s\n' "$output" >&2
    return
  fi

  words="$(printf '%s\n' "$output" | wc -w | tr -d ' ')"
  if [ "$words" -gt 1500 ]; then
    fail "context pack word limit [$query]: $words words"
    return
  fi

  for required in "## Retrieved Context" "### Citations" "### Stale And Gap Notes" "Gap:"; do
    if ! printf '%s\n' "$output" | rg -q "$required"; then
      fail "context pack [$query] missing [$required]"
      return
    fi
  done

  pass "context pack [$query] ${words} words"
}

main() {
  [ -x "$BRAIN_MEMORY" ] || {
    printf 'error: brain wrapper is not executable: %s\n' "$BRAIN_MEMORY" >&2
    exit 1
  }

  assert_route "GBrain 도입 왜 하기로 했지?" lookup
  assert_route "웨딩 SaaS GTM 이어서 해줘" lookup
  assert_route "design-harness 마이그레이션 이유" lookup
  assert_route "전에 실패한 접근 뭐였지?" lookup
  assert_route "이 프로젝트 다음 액션 정리해줘" lookup
  assert_route "지난번 Woogi Harness 결정 다시 보여줘" lookup
  assert_route "관련 문서 찾아서 이어서 작성해줘" lookup
  assert_route "previous decision on memory engine" lookup
  assert_route "README 오타 하나 고쳐줘" skip
  assert_route "scripts/brain-memory.sh 문법 검사해줘" skip

  assert_command "wrapper status" "$BRAIN_MEMORY" status
  assert_command "secret scan" "$BRAIN_MEMORY" secret-scan
  assert_command "quality report" "$BRAIN_MEMORY" quality-report
  assert_command "pilot report" "$BRAIN_PILOT" report
  assert_command "pilot tasks" "$BRAIN_PILOT" tasks
  assert_search_contains "GBrain 도입" "260610-gbrain-memory-engine-prd"
  assert_search_contains "Phase 0 도입" "260610-gbrain-phase0-implementation"
  assert_context_pack "Phase 1 complete"

  printf '\nSummary: %s passed, %s failed\n' "$pass_count" "$fail_count"
  [ "$fail_count" -eq 0 ]
}

main "$@"
