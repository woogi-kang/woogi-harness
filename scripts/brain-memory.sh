#!/usr/bin/env bash
# brain-memory.sh - Claude Craft wrapper for the local GBrain memory engine.

set -euo pipefail

GBRAIN_BIN="${GBRAIN_BIN:-$HOME/.bun/bin/gbrain}"
BRAIN_REPO="${BRAIN_REPO:-$HOME/brain-craft}"
BRAIN_SOURCE="${BRAIN_SOURCE:-brain-craft}"
DEFAULT_TIMEOUT_SECONDS="${BRAIN_TIMEOUT_SECONDS:-30}"
BRAIN_CLEANUP_SERVERS="${BRAIN_CLEANUP_SERVERS:-1}"

usage() {
  cat <<'EOF'
Usage: scripts/brain-memory.sh <command> [args]

Commands:
  status                         Show GBrain identity, stats, sources, and search mode
  search <query>                 Search long-term memory
  context <query>                Build a compact cited context pack
  get <slug>                     Read a memory page
  sync                           Commit-safe sync of brain-craft into GBrain
  secret-scan                    Scan brain-craft for likely secrets
  quality-report                 Print monthly memory quality review checklist
  cleanup                         Stop stale local gbrain serve processes
  capture <type> <slug> <title>  Create a typed memory page from stdin, commit, sync
  capture-decision <slug> <title>
                                 Create decisions/<slug>.md from stdin, commit, sync

Environment:
  GBRAIN_BIN=/path/to/gbrain     Default: $HOME/.bun/bin/gbrain
  BRAIN_REPO=/path/to/brain      Default: $HOME/brain-craft
  BRAIN_SOURCE=source-id         Default: brain-craft
  BRAIN_TIMEOUT_SECONDS=30       Command timeout for status/search/get
  BRAIN_CONTEXT_PAGE_LIMIT=5     Max pages in context pack
  BRAIN_CONTEXT_GET_TIMEOUT=8    Fallback get timeout when local page is missing
  BRAIN_CLEANUP_SERVERS=1        Kill stale gbrain serve before CLI calls
EOF
}

die() {
  printf 'error: %s\n' "$*" >&2
  exit 1
}

require_gbrain() {
  [ -x "$GBRAIN_BIN" ] || die "gbrain not found or not executable: $GBRAIN_BIN"
}

require_brain_repo() {
  [ -d "$BRAIN_REPO/.git" ] || die "brain repo not found or not a git repo: $BRAIN_REPO"
}

require_clean_brain_repo() {
  local status
  status="$(git -C "$BRAIN_REPO" status --porcelain)"
  if [ -n "$status" ]; then
    printf '%s\n' "$status" >&2
    die "brain repo has uncommitted changes; commit intentionally before continuing"
  fi
}

kill_process_tree() {
  local root="$1"
  local signal="${2:-TERM}"
  local child

  while IFS= read -r child; do
    [ -n "$child" ] && kill_process_tree "$child" "$signal"
  done < <(pgrep -P "$root" 2>/dev/null || true)

  kill "-$signal" "$root" 2>/dev/null || true
}

cleanup_gbrain_servers() {
  local pid

  while IFS= read -r pid; do
    [ -n "$pid" ] || continue
    kill -TERM "$pid" 2>/dev/null || true
  done < <(pgrep -f "gbrain serve" 2>/dev/null || true)
}

prepare_gbrain_cli() {
  if [ "$BRAIN_CLEANUP_SERVERS" = "1" ]; then
    cleanup_gbrain_servers
  fi
}

run_timeout() {
  local seconds="$1"
  shift

  "$@" &
  local pid=$!

  (
    sleep "$seconds"
    if kill -0 "$pid" 2>/dev/null; then
      printf 'error: command timed out after %ss: %s\n' "$seconds" "$*" >&2
      kill_process_tree "$pid" TERM
      sleep 1
      if kill -0 "$pid" 2>/dev/null; then
        kill_process_tree "$pid" KILL
      fi
      cleanup_gbrain_servers
    fi
  ) &
  local watcher=$!

  local status=0
  wait "$pid" || status=$?
  kill "$watcher" 2>/dev/null || true
  wait "$watcher" 2>/dev/null || true
  return "$status"
}

secret_scan() {
  require_brain_repo

  local hits
  hits="$(
    rg -n \
      '(sk-[A-Za-z0-9]{20,}|sk-ant-[A-Za-z0-9_-]{20,}|gbrain_[A-Za-z0-9_-]{16,}|api[_-]?key\s*[:=]\s*["'\'']?[A-Za-z0-9_-]{16,}|secret\s*[:=]\s*["'\'']?[A-Za-z0-9_-]{16,}|password\s*[:=]\s*["'\'']?[^"'\''[:space:]]{12,}|BEGIN (RSA|OPENSSH|PRIVATE) KEY)' \
      "$BRAIN_REPO" \
      | rg -v 'api_key="\\.\\.\\."|api_key="\\.\\.\\."|process\\.env\\.|example|placeholder' \
      || true
  )"

  if [ -n "$hits" ]; then
    printf '%s\n' "$hits" >&2
    die "possible secret(s) found in $BRAIN_REPO; refusing to continue"
  fi

  printf 'secret-scan: ok\n'
}

status() {
  require_gbrain
  prepare_gbrain_cli
  printf '== gbrain ==\n'
  "$GBRAIN_BIN" --version
  printf '\n== identity ==\n'
  run_timeout "$DEFAULT_TIMEOUT_SECONDS" "$GBRAIN_BIN" call get_brain_identity '{}'
  printf '\n== stats ==\n'
  run_timeout "$DEFAULT_TIMEOUT_SECONDS" "$GBRAIN_BIN" stats
  printf '\n== sources ==\n'
  run_timeout "$DEFAULT_TIMEOUT_SECONDS" "$GBRAIN_BIN" sources list
  printf '\n== search mode ==\n'
  run_timeout "$DEFAULT_TIMEOUT_SECONDS" "$GBRAIN_BIN" search modes
}

search_memory() {
  require_gbrain
  [ "$#" -gt 0 ] || die "missing search query"
  prepare_gbrain_cli

  local output
  local status=0
  output="$(run_timeout "$DEFAULT_TIMEOUT_SECONDS" "$GBRAIN_BIN" search "$*" 2>&1)" || status=$?
  printf '%s\n' "$output"

  if [ "$status" -ne 0 ]; then
    return "$status"
  fi

  if [ "$output" = "No results." ]; then
    printf 'hint: Phase 0 has embeddings disabled; retry with exact Korean terms, source title words, or slug fragments.\n'
  fi
}

get_page() {
  require_gbrain
  [ "$#" -eq 1 ] || die "usage: get <slug>"
  prepare_gbrain_cli
  run_timeout "$DEFAULT_TIMEOUT_SECONDS" "$GBRAIN_BIN" get "$1"
}

first_heading() {
  awk '
    /^# / {
      sub(/^# /, "")
      print
      exit
    }
  '
}

section_preview() {
  local section="$1"
  awk -v section="$section" '
    BEGIN { found = 0; count = 0 }
    /^## / {
      if (found) exit
      found = ($0 == "## " section)
      next
    }
    found && NF {
      gsub(/^[ \t]+|[ \t]+$/, "")
      print
      count++
      if (count >= 3) exit
    }
  '
}

fallback_preview() {
  awk '
    NF && $0 !~ /^---$/ && $0 !~ /^type:/ && $0 !~ /^title:/ && $0 !~ /^#/ {
      gsub(/^[ \t]+|[ \t]+$/, "")
      print
      count++
      if (count >= 3) exit
    }
  '
}

compact_line() {
  tr '\n' ' ' | sed 's/[[:space:]][[:space:]]*/ /g' | cut -c 1-500
}

page_preview() {
  local page="$1"
  local preview

  preview="$(printf '%s\n' "$page" | section_preview "Summary" | compact_line)"
  if [ -z "$preview" ]; then
    preview="$(printf '%s\n' "$page" | section_preview "Context" | compact_line)"
  fi
  if [ -z "$preview" ]; then
    preview="$(printf '%s\n' "$page" | fallback_preview | compact_line)"
  fi

  printf '%s\n' "$preview"
}

page_signal() {
  local page="$1"
  local primary="$2"
  local secondary="${3:-}"
  local signal

  signal="$(printf '%s\n' "$page" | section_preview "$primary" | compact_line)"
  if [ -z "$signal" ] && [ -n "$secondary" ]; then
    signal="$(printf '%s\n' "$page" | section_preview "$secondary" | compact_line)"
  fi
  printf '%s\n' "$signal"
}

append_context_item() {
  local slug="$1"
  local page="$2"
  local title
  local preview

  title="$(printf '%s\n' "$page" | first_heading)"
  preview="$(page_preview "$page")"
  [ -n "$title" ] || title="$slug"
  [ -n "$preview" ] || preview="Gap: no concise summary section found."

  printf -- '- `%s`: %s. %s\n' "$slug" "$title" "$preview"
}

context_pack() {
  require_gbrain
  require_brain_repo
  [ "$#" -gt 0 ] || die "missing context query"
  prepare_gbrain_cli

  local query="$*"
  local limit="${BRAIN_CONTEXT_PAGE_LIMIT:-5}"
  local search_output
  local search_status=0
  local slugs
  local slug
  local page
  local page_file
  local pages_file
  local found_count=0
  local decisions=0
  local docs=0
  local constraints=0
  local failures=0
  local questions=0

  pages_file="$(mktemp)"
  trap 'rm -f "${pages_file:-}"' RETURN

  search_output="$(run_timeout "$DEFAULT_TIMEOUT_SECONDS" "$GBRAIN_BIN" search "$query" 2>&1)" || search_status=$?
  slugs="$(printf '%s\n' "$search_output" | sed -nE 's/^\[[^]]+\] ([^ ]+) --.*/\1/p' | head -n "$limit")"

  printf '## Retrieved Context\n\n'
  printf 'Query: `%s`\n' "$query"
  printf 'Source: `%s`\n' "$BRAIN_SOURCE"
  printf 'Mode: conservative keyword search; embeddings disabled in current pilot.\n\n'

  if [ "$search_status" -ne 0 ]; then
    printf '### Search Status\n\n'
    printf -- '- Gap: search command failed or timed out.\n'
    printf -- '- Detail: `%s`\n\n' "$(printf '%s\n' "$search_output" | head -n 1)"
    printf '### Citations\n\n'
    printf -- '- Gap: no citations available because search did not complete.\n'
    return "$search_status"
  fi

  if [ -z "$slugs" ]; then
    printf '### Search Status\n\n'
    printf -- '- Gap: no search results. Retry with exact Korean terms, source title words, or slug fragments.\n\n'
    printf '### Citations\n\n'
    printf -- '- Gap: no citations available.\n'
    return 0
  fi

  while IFS= read -r slug; do
    [ -n "$slug" ] || continue
    page_file="$BRAIN_REPO/$slug.md"
    if [ ! -f "$page_file" ]; then
      page_file="$BRAIN_REPO/$slug"
    fi
    if [ -f "$page_file" ]; then
      page="$(sed -n '1,240p' "$page_file")"
    else
      page="$(run_timeout "${BRAIN_CONTEXT_GET_TIMEOUT:-8}" "$GBRAIN_BIN" get "$slug" 2>/dev/null || true)"
    fi
    [ -n "$page" ] || continue
    found_count=$((found_count + 1))
    {
      printf '<<<SLUG:%s>>>\n' "$slug"
      printf '%s\n' "$page"
      printf '<<<END>>>\n'
    } >> "$pages_file"
  done <<EOF_SLUGS
$slugs
EOF_SLUGS

  printf '### Relevant Decisions\n\n'
  while IFS= read -r slug; do
    [ -n "$slug" ] || continue
    case "$slug" in
      decisions/*)
        page="$(awk -v slug="$slug" '
          $0 == "<<<SLUG:" slug ">>>" { found = 1; next }
          $0 == "<<<END>>>" && found { exit }
          found { print }
        ' "$pages_file")"
        append_context_item "$slug" "$page"
        decisions=$((decisions + 1))
        ;;
    esac
  done <<EOF_DECISIONS
$slugs
EOF_DECISIONS
  [ "$decisions" -gt 0 ] || printf -- '- Gap: no decision page appeared in the top results.\n'
  printf '\n'

  printf '### Relevant Project Docs\n\n'
  while IFS= read -r slug; do
    [ -n "$slug" ] || continue
    case "$slug" in
      projects/*|sources/*|sessions/*|patterns/*)
        page="$(awk -v slug="$slug" '
          $0 == "<<<SLUG:" slug ">>>" { found = 1; next }
          $0 == "<<<END>>>" && found { exit }
          found { print }
        ' "$pages_file")"
        append_context_item "$slug" "$page"
        docs=$((docs + 1))
        ;;
    esac
  done <<EOF_DOCS
$slugs
EOF_DOCS
  [ "$docs" -gt 0 ] || printf -- '- Gap: no project/source/session/pattern page appeared in the top results.\n'
  printf '\n'

  printf '### Known Constraints\n\n'
  while IFS= read -r slug; do
    [ -n "$slug" ] || continue
    page="$(awk -v slug="$slug" '
      $0 == "<<<SLUG:" slug ">>>" { found = 1; next }
      $0 == "<<<END>>>" && found { exit }
      found { print }
    ' "$pages_file")"
    signal="$(page_signal "$page" "Impact" "Import Policy")"
    if [ -n "$signal" ]; then
      printf -- '- `%s`: %s\n' "$slug" "$signal"
      constraints=$((constraints + 1))
    fi
  done <<EOF_CONSTRAINTS
$slugs
EOF_CONSTRAINTS
  [ "$constraints" -gt 0 ] || printf -- '- Gap: no explicit constraint or impact section found in retrieved pages.\n'
  printf '\n'

  printf '### Failed Approaches\n\n'
  while IFS= read -r slug; do
    [ -n "$slug" ] || continue
    page="$(awk -v slug="$slug" '
      $0 == "<<<SLUG:" slug ">>>" { found = 1; next }
      $0 == "<<<END>>>" && found { exit }
      found { print }
    ' "$pages_file")"
    signal="$(page_signal "$page" "Alternatives Considered" "Failure Modes")"
    if [ -n "$signal" ]; then
      printf -- '- `%s`: %s\n' "$slug" "$signal"
      failures=$((failures + 1))
    fi
  done <<EOF_FAILURES
$slugs
EOF_FAILURES
  [ "$failures" -gt 0 ] || printf -- '- Gap: no rejected alternative or failure mode found in retrieved pages.\n'
  printf '\n'

  printf '### Open Questions\n\n'
  while IFS= read -r slug; do
    [ -n "$slug" ] || continue
    page="$(awk -v slug="$slug" '
      $0 == "<<<SLUG:" slug ">>>" { found = 1; next }
      $0 == "<<<END>>>" && found { exit }
      found { print }
    ' "$pages_file")"
    signal="$(page_signal "$page" "Open Questions" "Next Actions")"
    if [ -n "$signal" ]; then
      printf -- '- `%s`: %s\n' "$slug" "$signal"
      questions=$((questions + 1))
    fi
  done <<EOF_QUESTIONS
$slugs
EOF_QUESTIONS
  [ "$questions" -gt 0 ] || printf -- '- Gap: no open question or next action section found in retrieved pages.\n'
  printf '\n'

  printf '### Stale And Gap Notes\n\n'
  printf -- '- Stale check: verify dates inside cited pages before treating old strategy, pricing, legal, or market facts as current.\n'
  if [ "$found_count" -lt "$limit" ]; then
    printf -- '- Gap: only %s readable page(s) were available from the top results.\n' "$found_count"
  fi
  printf -- '- Gap policy: do not infer missing decisions, owners, or metrics without another source.\n\n'

  printf '### Citations\n\n'
  while IFS= read -r slug; do
    [ -n "$slug" ] && printf -- '- `%s`\n' "$slug"
  done <<EOF_CITATIONS
$slugs
EOF_CITATIONS
  rm -f "$pages_file"
  trap - RETURN
}

quality_report() {
  require_brain_repo

  local dirty="no"
  local file_count
  local decision_count
  local project_count
  local pattern_count
  local session_count

  if [ -n "$(git -C "$BRAIN_REPO" status --porcelain)" ]; then
    dirty="yes"
  fi

  file_count="$(find "$BRAIN_REPO" -path "$BRAIN_REPO/.git" -prune -o -type f -name '*.md' -print | wc -l | tr -d ' ')"
  decision_count="$(find "$BRAIN_REPO/decisions" -type f -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"
  project_count="$(find "$BRAIN_REPO/projects" -type f -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"
  pattern_count="$(find "$BRAIN_REPO/patterns" -type f -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"
  session_count="$(find "$BRAIN_REPO/sessions" -type f -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"

  printf '# Monthly Memory Quality Review\n\n'
  printf 'Brain repo: `%s`\n' "$BRAIN_REPO"
  printf 'Source: `%s`\n' "$BRAIN_SOURCE"
  printf 'Dirty repo: `%s`\n\n' "$dirty"

  printf '## Inventory\n\n'
  printf -- '- Markdown pages: %s\n' "$file_count"
  printf -- '- Decisions: %s\n' "$decision_count"
  printf -- '- Projects: %s\n' "$project_count"
  printf -- '- Patterns: %s\n' "$pattern_count"
  printf -- '- Sessions: %s\n\n' "$session_count"

  printf '## Required Checks\n\n'
  printf -- '- [ ] `scripts/brain-memory.sh secret-scan` passes.\n'
  printf -- '- [ ] `scripts/brain-memory-qa.sh` passes.\n'
  printf -- '- [ ] Top 10 newest pages have useful Summary sections.\n'
  printf -- '- [ ] No raw logs, secrets, screenshots, or source dumps were imported.\n'
  printf -- '- [ ] No duplicate decisions should be merged or retired.\n'
  printf -- '- [ ] At least 5 real follow-up tasks cited memory slugs.\n'
  printf -- '- [ ] Stale strategy, pricing, legal, and market facts are marked or refreshed.\n\n'

  printf '## Review Queries\n\n'
  printf -- '- `scripts/brain-memory.sh context \"GBrain Phase 1\"`\n'
  printf -- '- `scripts/brain-memory.sh context \"전에 실패한 접근\"`\n'
  printf -- '- `scripts/brain-memory.sh context \"이 프로젝트 다음 액션\"`\n\n'

  printf '## Decision\n\n'
  printf -- '- Keep / Change / Drop:\n'
  printf -- '- Follow-up actions:\n'
}

sync_memory() {
  require_gbrain
  require_brain_repo
  secret_scan >/dev/null
  require_clean_brain_repo
  prepare_gbrain_cli

  "$GBRAIN_BIN" sync \
    --source "$BRAIN_SOURCE" \
    --repo "$BRAIN_REPO" \
    --no-embed \
    --no-pull \
    --yes
  "$GBRAIN_BIN" extract all --source db
}

capture_memory() {
  require_brain_repo
  require_clean_brain_repo
  [ "$#" -ge 3 ] || die "usage: capture <type> <slug> <title> < stdin"

  local type="$1"
  local slug="$2"
  shift 2
  local title="$*"
  local directory
  local heading

  case "$type" in
    decision|decisions)
      directory="decisions"
      heading="Decision"
      [[ "$slug" =~ ^[0-9]{6}-[a-z0-9][a-z0-9-]*$ ]] || die "decision slug must look like YYMMDD-kebab-title"
      ;;
    project|projects)
      directory="projects"
      heading="Project"
      [[ "$slug" =~ ^[a-z0-9][a-z0-9-]*$ ]] || die "project slug must be kebab-case"
      ;;
    idea|ideas)
      directory="ideas"
      heading="Idea"
      [[ "$slug" =~ ^[a-z0-9][a-z0-9-]*$ ]] || die "idea slug must be kebab-case"
      ;;
    pattern|patterns)
      directory="patterns"
      heading="Pattern"
      [[ "$slug" =~ ^[a-z0-9][a-z0-9-]*$ ]] || die "pattern slug must be kebab-case"
      ;;
    session|sessions)
      directory="sessions"
      heading="Session"
      [[ "$slug" =~ ^[0-9]{6}-[a-z0-9][a-z0-9-]*$ ]] || die "session slug must look like YYMMDD-kebab-title"
      ;;
    *)
      die "unknown memory type: $type"
      ;;
  esac

  local file="$BRAIN_REPO/$directory/$slug.md"
  [ ! -e "$file" ] || die "file already exists: $file"

  local body
  body="$(cat)"
  [ -n "$body" ] || die "stdin body is empty"

  mkdir -p "$BRAIN_REPO/$directory"

  {
    printf '# %s: %s\n\n' "$heading" "$title"
    printf '## Summary\n\n'
    printf '%s\n\n' "$body"
    case "$directory" in
      decisions)
        printf '## Context\n\n'
        printf '## Decision\n\n'
        printf '## Alternatives Considered\n\n'
        printf '## Why Now\n\n'
        printf '## Impact\n\n'
        ;;
      projects)
        printf '## Current Status\n\n'
        printf '## Key Decisions\n\n'
        printf '## Open Questions\n\n'
        printf '## Next Actions\n\n'
        ;;
      ideas)
        printf '## Problem\n\n'
        printf '## Hypothesis\n\n'
        printf '## Evidence\n\n'
        printf '## Next Test\n\n'
        ;;
      patterns)
        printf '## Trigger\n\n'
        printf '## Workflow\n\n'
        printf '## Quality Bar\n\n'
        printf '## Failure Modes\n\n'
        ;;
      sessions)
        printf '## Completed\n\n'
        printf '## Decisions\n\n'
        printf '## Open Questions\n\n'
        printf '## Next Actions\n\n'
        ;;
    esac
    printf '## Related\n\n'
    printf '## Timeline\n\n'
  } > "$file"

  secret_scan >/dev/null
  git -C "$BRAIN_REPO" add "$file"
  git -C "$BRAIN_REPO" commit -m "docs: capture ${directory%?} ${slug#??????-}"
  local commit
  commit="$(git -C "$BRAIN_REPO" rev-parse --short HEAD)"
  sync_memory
  printf 'Capture receipt:\n'
  printf '%s\n' "- slug: $directory/$slug"
  printf '%s\n' "- file: $file"
  printf '%s\n' "- commit: $commit"
  printf '%s\n' "- source: $BRAIN_SOURCE"
  printf '%s\n' "- synced: yes"
}

capture_decision() {
  [ "$#" -ge 2 ] || die "usage: capture-decision <slug> <title> < stdin"

  local slug="$1"
  shift
  local title="$*"
  capture_memory decision "$slug" "$title"
}

main() {
  local command="${1:-}"
  case "$command" in
    status)
      shift
      [ "$#" -eq 0 ] || die "status takes no arguments"
      status
      ;;
    search)
      shift
      search_memory "$@"
      ;;
    context)
      shift
      context_pack "$@"
      ;;
    get)
      shift
      get_page "$@"
      ;;
    sync)
      shift
      [ "$#" -eq 0 ] || die "sync takes no arguments"
      sync_memory
      ;;
    secret-scan)
      shift
      [ "$#" -eq 0 ] || die "secret-scan takes no arguments"
      secret_scan
      ;;
    quality-report)
      shift
      [ "$#" -eq 0 ] || die "quality-report takes no arguments"
      quality_report
      ;;
    cleanup)
      shift
      [ "$#" -eq 0 ] || die "cleanup takes no arguments"
      cleanup_gbrain_servers
      ;;
    capture)
      shift
      capture_memory "$@"
      ;;
    capture-decision)
      shift
      capture_decision "$@"
      ;;
    -h|--help|help|'')
      usage
      ;;
    *)
      usage >&2
      die "unknown command: $command"
      ;;
  esac
}

main "$@"
