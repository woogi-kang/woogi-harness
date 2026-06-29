#!/usr/bin/env bash
set -euo pipefail

ENDPOINT="${COUPANG_MCP_ENDPOINT:-https://yuju777-coupang-mcp.hf.space/mcp}"
KEYWORD="${1:-생수}"
TIMEOUT_SECONDS="${COUPANG_MCP_TIMEOUT_SECONDS:-40}"

HEADERS_FILE="$(mktemp)"
trap 'rm -f "$HEADERS_FILE"' EXIT

post_mcp() {
  local payload="$1"
  shift

  curl -sS -m "$TIMEOUT_SECONDS" -X POST "$ENDPOINT" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    "$@" \
    -d "$payload"
}

json_payload() {
  python3 - "$@" <<'PY'
import json
import sys

kind = sys.argv[1]

if kind == "initialize":
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "coupang-mcp-diagnostic", "version": "1.0"},
        },
    }
elif kind == "tools_list":
    payload = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
elif kind == "recommendations":
    payload = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "get_coupang_recommendations",
            "arguments": {"category": "전자기기"},
        },
    }
elif kind == "search":
    payload = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "search_coupang_products",
            "arguments": {"keyword": sys.argv[2], "limit": 3},
        },
    }
elif kind == "goldbox":
    payload = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {"name": "get_coupang_goldbox", "arguments": {"limit": 3}},
    }
else:
    raise SystemExit(f"unknown payload kind: {kind}")

print(json.dumps(payload, ensure_ascii=False))
PY
}

extract_data_text() {
  python3 -c '
import json
import sys

raw = sys.stdin.read()
events = []
for line in raw.splitlines():
    if not line.startswith("data:"):
        continue
    data = line.split(":", 1)[1].strip()
    if not data:
        continue
    try:
        events.append(json.loads(data))
    except json.JSONDecodeError:
        events.append({"_raw": data})

if not events:
    print(raw[:1000])
    raise SystemExit(0)

for event in events:
    result = event.get("result")
    if isinstance(result, dict):
        server = result.get("serverInfo")
        if isinstance(server, dict):
            print("server={} version={}".format(server.get("name", "unknown"), server.get("version", "unknown")))
            print("protocol={}".format(result.get("protocolVersion", "unknown")))
            continue
        tools = result.get("tools")
        if isinstance(tools, list):
            print("tools=" + ", ".join(tool.get("name", "unknown") for tool in tools if isinstance(tool, dict)))
            continue
        structured = result.get("structuredContent")
        if isinstance(structured, dict) and "result" in structured:
            print(structured["result"])
            continue
        content = result.get("content")
        if isinstance(content, list) and content:
            first = content[0]
            if isinstance(first, dict) and "text" in first:
                print(first["text"])
                continue
    print(json.dumps(event, ensure_ascii=False)[:1000])
'
}

section() {
  printf '\n== %s ==\n' "$1"
}

quoted_keyword() {
  local escaped="${KEYWORD//\\/\\\\}"
  escaped="${escaped//\"/\\\"}"
  printf '"%s"' "$escaped"
}

print_call_result() {
  local exit_code="$1"
  local body="$2"

  printf 'curl_exit=%s\n' "$exit_code"
  printf '%s\n' "$body" | extract_data_text
}

section "Initialize"
INIT_PAYLOAD="$(json_payload initialize)"
INIT_STATUS=0
INIT_BODY="$(curl -sS -m "$TIMEOUT_SECONDS" -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -D "$HEADERS_FILE" \
  -d "$INIT_PAYLOAD" 2>&1)" || INIT_STATUS=$?
HTTP_CODE="$(awk 'toupper($0) ~ /^HTTP\// {code=$2} END {print code}' "$HEADERS_FILE")"
SESSION_ID="$(awk 'tolower($1)=="mcp-session-id:" {gsub("\r","",$2); print $2}' "$HEADERS_FILE")"

printf 'endpoint=%s\n' "$ENDPOINT"
printf 'http_code=%s\n' "${HTTP_CODE:-unknown}"
printf 'session_present=%s\n' "$([ -n "$SESSION_ID" ] && printf yes || printf no)"
print_call_result "$INIT_STATUS" "$INIT_BODY" | sed -n '1,12p'

if [ -z "$SESSION_ID" ]; then
  printf '\nNo MCP session id was returned; stopping before tool calls.\n' >&2
  exit 1
fi

section "Tools List"
TOOLS_STATUS=0
TOOLS_BODY="$(post_mcp "$(json_payload tools_list)" -H "Mcp-Session-Id: $SESSION_ID" 2>&1)" || TOOLS_STATUS=$?
print_call_result "$TOOLS_STATUS" "$TOOLS_BODY" | sed -n '1,30p'

section "Static Tool"
RECOMMENDATIONS_STATUS=0
RECOMMENDATIONS_BODY="$(post_mcp "$(json_payload recommendations)" -H "Mcp-Session-Id: $SESSION_ID" 2>&1)" || RECOMMENDATIONS_STATUS=$?
print_call_result "$RECOMMENDATIONS_STATUS" "$RECOMMENDATIONS_BODY" | sed -n '1,30p'

section "Live Search Tool"
SEARCH_STATUS=0
SEARCH_BODY="$(post_mcp "$(json_payload search "$KEYWORD")" -H "Mcp-Session-Id: $SESSION_ID" 2>&1)" || SEARCH_STATUS=$?
print_call_result "$SEARCH_STATUS" "$SEARCH_BODY" | sed -n '1,40p'

section "Live Goldbox Tool"
GOLDBOX_STATUS=0
GOLDBOX_BODY="$(post_mcp "$(json_payload goldbox)" -H "Mcp-Session-Id: $SESSION_ID" 2>&1)" || GOLDBOX_STATUS=$?
print_call_result "$GOLDBOX_STATUS" "$GOLDBOX_BODY" | sed -n '1,40p'

section "Interpretation"
if [ "$TOOLS_STATUS" -ne 0 ] || [ "$RECOMMENDATIONS_STATUS" -ne 0 ] || [ "$SEARCH_STATUS" -ne 0 ] || [ "$GOLDBOX_STATUS" -ne 0 ]; then
  cat <<'EOF'
One or more MCP tool calls failed at the HTTP/client layer. Treat this as an
endpoint, network, or remote service availability problem first.
EOF
elif printf '%s\n%s\n' "$SEARCH_BODY" "$GOLDBOX_BODY" | grep -q 'API 오류'; then
  cat <<'EOF'
Live product-data tools returned an API error. If initialize, tools/list, and
the static recommendation tool worked, treat this as remote MCP backend or
data-source failure first, not as proof of local browser automation blocking.
EOF
  printf 'For a non-live fallback, run: python3 scripts/search-coupang-cache.py %s\n' "$(quoted_keyword)"
else
  cat <<'EOF'
No generic API error was detected in the sampled live-data calls. Review the
returned product data manually and keep calls low-volume.
EOF
fi
