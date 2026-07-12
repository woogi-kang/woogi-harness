#!/bin/bash
# Claude Code Hook: Usage Tracker
# Logs Agent/Skill tool invocations as normalized, one-object-per-line JSONL.
#
# Triggered by PostToolUse events (configured in settings.json)
# Reads JSON from stdin per Claude Code hooks spec

INPUT=$(cat) || exit 0

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
TOOL_NAME=$(printf '%s' "$INPUT" | jq -r '.tool_name // "unknown"' 2>/dev/null) || exit 0
SESSION_ID=$(printf '%s' "$INPUT" | jq -r '.session_id // .sessionId // "unknown"' 2>/dev/null) || SESSION_ID="unknown"

LOG_DIR="$(cd "$(dirname "$0")/.." && pwd)/logs"
LOG_FILE="$LOG_DIR/usage.jsonl"
mkdir -p "$LOG_DIR"

case "$TOOL_NAME" in
  Agent)
    NAME=$(printf '%s' "$INPUT" | jq -r '.tool_input.description // .tool_input.subagent_type // "unknown"')
    TYPE=$(printf '%s' "$INPUT" | jq -r '.tool_input.subagent_type // "general-purpose"')
    jq -cn \
      --arg ts "$TIMESTAMP" \
      --arg sid "$SESSION_ID" \
      --arg name "$NAME" \
      --arg subtype "$TYPE" \
      '{schema_version:"harness.telemetry.v1",timestamp:$ts,session_id:$sid,provider:"claude",event_type:"invocation",subject_type:"agent",subject_id:$name,status:"observed",duration_ms:null,context_bytes:null,metadata:{subagent_type:$subtype}}' \
      >> "$LOG_FILE"
    ;;
  Skill)
    NAME=$(printf '%s' "$INPUT" | jq -r '.tool_input.skill // "unknown"')
    ARGS=$(printf '%s' "$INPUT" | jq -r '.tool_input.args // ""')
    jq -cn \
      --arg ts "$TIMESTAMP" \
      --arg sid "$SESSION_ID" \
      --arg name "$NAME" \
      --arg args "$ARGS" \
      '{schema_version:"harness.telemetry.v1",timestamp:$ts,session_id:$sid,provider:"claude",event_type:"invocation",subject_type:"skill",subject_id:$name,status:"observed",duration_ms:null,context_bytes:null,metadata:{args:$args}}' \
      >> "$LOG_FILE"
    ;;
esac

exit 0
