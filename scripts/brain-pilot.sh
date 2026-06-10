#!/usr/bin/env bash
# brain-pilot.sh - GBrain Phase 3 pilot metrics logger and report generator.

set -euo pipefail

BRAIN_REPO="${BRAIN_REPO:-$HOME/brain-craft}"
PILOT_EVENTS="${PILOT_EVENTS:-$BRAIN_REPO/metrics/gbrain-pilot-events.tsv}"
PILOT_START_DATE="${PILOT_START_DATE:-2026-06-10}"
PILOT_REVIEW_DATE="${PILOT_REVIEW_DATE:-2026-07-10}"

usage() {
  cat <<'EOF'
Usage: scripts/brain-pilot.sh <command> [args]

Commands:
  init
      Create the pilot metrics file if missing.
  log <event_type> <outcome> <minutes_saved> <citations> <note>
      Append one pilot event.
  report
      Print a Markdown pilot metrics report.
  tasks
      Print the remaining Phase 3+ task backlog with dynamic metric status.

Event types:
  lookup, context, capture, resume, quality, miss

Outcomes:
  useful, neutral, miss, done, blocked

Examples:
  scripts/brain-pilot.sh init
  scripts/brain-pilot.sh log lookup useful 10 decisions/260610-gbrain-phase1-harness-wiring "Recovered Phase 1 decision"
  scripts/brain-pilot.sh report
  scripts/brain-pilot.sh tasks
EOF
}

die() {
  printf 'error: %s\n' "$*" >&2
  exit 1
}

require_brain_repo() {
  [ -d "$BRAIN_REPO/.git" ] || die "brain repo not found or not a git repo: $BRAIN_REPO"
}

sanitize_field() {
  printf '%s' "$1" | tr '\t\n\r' '   ' | sed 's/[[:space:]][[:space:]]*/ /g; s/^ //; s/ $//'
}

init_pilot() {
  require_brain_repo
  mkdir -p "$(dirname "$PILOT_EVENTS")"

  if [ ! -f "$PILOT_EVENTS" ]; then
    printf 'date_iso\tevent_type\toutcome\tminutes_saved\tcitations\tnote\n' > "$PILOT_EVENTS"
  fi

  printf 'pilot metrics: %s\n' "$PILOT_EVENTS"
}

log_event() {
  require_brain_repo
  [ "$#" -ge 5 ] || die "usage: log <event_type> <outcome> <minutes_saved> <citations> <note>"

  local event_type="$1"
  local outcome="$2"
  local minutes_saved="$3"
  local citations="$4"
  shift 4
  local note="$*"

  case "$event_type" in
    lookup|context|capture|resume|quality|miss) ;;
    *) die "unknown event_type: $event_type" ;;
  esac

  case "$outcome" in
    useful|neutral|miss|done|blocked) ;;
    *) die "unknown outcome: $outcome" ;;
  esac

  [[ "$minutes_saved" =~ ^-?[0-9]+$ ]] || die "minutes_saved must be an integer"

  init_pilot >/dev/null
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" \
    "$(sanitize_field "$event_type")" \
    "$(sanitize_field "$outcome")" \
    "$minutes_saved" \
    "$(sanitize_field "$citations")" \
    "$(sanitize_field "$note")" >> "$PILOT_EVENTS"

  printf 'pilot event logged: %s %s %s\n' "$event_type" "$outcome" "$minutes_saved"
}

report_pilot() {
  require_brain_repo
  [ -f "$PILOT_EVENTS" ] || die "pilot metrics file not found; run init first"

  awk -F '\t' -v metrics_file="$PILOT_EVENTS" '
    NR == 1 { next }
    {
      total++
      type[$2]++
      outcome[$3]++
      minutes += $4
      if ($5 != "" && $5 != "-") cited++
      if ($3 == "useful") useful++
      if ($3 == "miss") misses++
      if ($2 == "capture") captures++
      if ($2 == "resume") resumes++
    }
    END {
      useful_rate = total ? useful * 100 / total : 0
      citation_rate = total ? cited * 100 / total : 0
      printf "# GBrain Phase 3 Pilot Metrics\n\n"
      printf "Metrics file: `%s`\n\n", metrics_file
      printf "## Summary\n\n"
      printf "- Total events: %d\n", total
      printf "- Useful events: %d (%.0f%%)\n", useful, useful_rate
      printf "- Misses: %d\n", misses
      printf "- Capture events: %d\n", captures
      printf "- Resume events: %d\n", resumes
      printf "- Cited events: %d (%.0f%%)\n", cited, citation_rate
      printf "- Estimated minutes saved: %d\n\n", minutes
      printf "## Event Types\n\n"
      for (key in type) {
        printf "- %s: %d\n", key, type[key]
      }
      printf "\n## Outcomes\n\n"
      for (key in outcome) {
        printf "- %s: %d\n", key, outcome[key]
      }
      printf "\n## Go / No-Go Readout\n\n"
      if (total < 10) {
        printf "- Status: collecting data\n"
        printf "- Reason: fewer than 10 events logged.\n"
      } else if (useful_rate >= 50 && misses <= useful && citation_rate >= 50) {
        printf "- Status: go\n"
        printf "- Reason: useful rate and citation rate meet the pilot bar.\n"
      } else {
        printf "- Status: change\n"
        printf "- Reason: usefulness, misses, or citation rate need improvement before expansion.\n"
      }
      printf "\n## Required 30-Day Review Questions\n\n"
      printf "- Did context recovery time drop by at least 50%%?\n"
      printf "- Did the user repeat less project context?\n"
      printf "- Were at least 5 follow-up tasks materially helped by memory?\n"
      printf "- Were search misses caused by no embeddings, bad capture quality, or wrong trigger rules?\n"
      printf "- Keep, change, or drop the current setup?\n"
    }
  ' "$PILOT_EVENTS"
}

task_backlog() {
  require_brain_repo
  [ -f "$PILOT_EVENTS" ] || die "pilot metrics file not found; run init first"

  awk -F '\t' -v metrics_file="$PILOT_EVENTS" -v start_date="$PILOT_START_DATE" -v review_date="$PILOT_REVIEW_DATE" '
    NR == 1 { next }
    {
      total++
      if ($3 == "useful") useful++
      if ($3 == "miss") misses++
      if ($5 != "" && $5 != "-") cited++
      if ($2 == "quality") quality++
      if ($2 == "resume" && $3 == "useful") resume_useful++
    }
    END {
      remaining_events = 10 - total
      if (remaining_events < 0) remaining_events = 0
      remaining_useful = 5 - useful
      if (remaining_useful < 0) remaining_useful = 0
      citation_rate = total ? cited * 100 / total : 0
      useful_rate = total ? useful * 100 / total : 0
      event_status = remaining_events == 0 ? "Done" : "In Progress"
      useful_status = remaining_useful == 0 ? "Done" : "In Progress"
      citation_status = citation_rate >= 50 ? "Done" : "At Risk"

      printf "# GBrain Remaining Task Backlog\n\n"
      printf "Pilot start: `%s`\n", start_date
      printf "Pilot review target: `%s`\n", review_date
      printf "Metrics file: `%s`\n\n", metrics_file

      printf "## Current Counters\n\n"
      printf "- Total events: %d / 10 minimum\n", total
      printf "- Useful events: %d / 5 target\n", useful
      printf "- Cited events: %d (%.0f%%)\n", cited, citation_rate
      printf "- Miss events: %d\n", misses
      printf "- Quality reviews logged: %d\n\n", quality

      printf "## Tasks\n\n"
      printf "| ID | Status | Outcome | Completion Criteria | Next Command |\n"
      printf "| --- | --- | --- | --- | --- |\n"
      printf "| GB-P3-01 | Done | Pilot can collect evidence | Metrics file exists and report runs | `scripts/brain-pilot.sh report` |\n"
      printf "| GB-P3-02 | %s | Enough real usage is logged | 10+ events logged; %d remaining | `scripts/brain-pilot.sh log ...` |\n", event_status, remaining_events
      printf "| GB-P3-03 | %s | Memory proves useful in follow-up work | 5 useful events; %d remaining | `scripts/brain-pilot.sh log lookup useful ...` |\n", useful_status, remaining_useful
      printf "| GB-P3-04 | %s | Outputs cite memory consistently | Citation rate >= 50%%; current %.0f%% | `scripts/brain-memory.sh context \"...\"` |\n", citation_status, citation_rate
      printf "| GB-P3-05 | In Progress | Search misses are explainable | Every miss has a logged cause and follow-up | `scripts/brain-pilot.sh log miss miss 0 - \"...\"` |\n"
      printf "| GB-P3-06 | Pending | Weekly memory quality stays healthy | Weekly `quality` event through review date | `scripts/brain-memory.sh quality-report` |\n"
      printf "| GB-P3-07 | Pending | Embedding policy is evidence-based | Decide after miss/usefulness review | `scripts/brain-pilot.sh report` |\n"
      printf "| GB-P3-08 | Pending | Import scope remains safe | Decide curated copy vs direct docs source | `scripts/brain-memory.sh secret-scan` |\n"
      printf "| GB-P3-09 | Blocked | Company brain expansion has clear scope | Requires keep/change decision | `scripts/brain-pilot.sh report` |\n"
      printf "| GB-P3-10 | Blocked | Final keep/change/drop decision | Requires enough events and review date | `scripts/brain-pilot.sh report` |\n\n"

      printf "## Operating Rule\n\n"
      printf "- Log one pilot event whenever memory lookup, context pack, capture, resume, quality review, or miss materially affects a task.\n"
      printf "- Do not mark Phase 3 complete until GB-P3-02, GB-P3-03, GB-P3-04, and GB-P3-10 are done.\n"
    }
  ' "$PILOT_EVENTS"
}

main() {
  local command="${1:-}"

  case "$command" in
    init)
      shift
      [ "$#" -eq 0 ] || die "init takes no arguments"
      init_pilot
      ;;
    log)
      shift
      log_event "$@"
      ;;
    report)
      shift
      [ "$#" -eq 0 ] || die "report takes no arguments"
      report_pilot
      ;;
    tasks)
      shift
      [ "$#" -eq 0 ] || die "tasks takes no arguments"
      task_backlog
      ;;
    -h|--help|help|"")
      usage
      ;;
    *)
      usage >&2
      die "unknown command: $command"
      ;;
  esac
}

main "$@"
