#!/usr/bin/env bash
set -euo pipefail

INPUT_CASE="${1:-}"
OUTPUT_FILE="${2:-}"
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
VALIDATOR="$ROOT/.claude/skills/korean-typography-quality/scripts/validate_korean_typography.py"

if [[ -z "$OUTPUT_FILE" || ! -f "$OUTPUT_FILE" ]]; then
  echo "FAIL: output file argument missing or not found"
  exit 1
fi

python3 "$VALIDATOR" "$OUTPUT_FILE"
