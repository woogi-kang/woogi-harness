#!/usr/bin/env bash
# Compatibility wrapper for sync v2. The default is a read-only dry-run.
#
#   bash scripts/sync-to-projects.sh
#   bash scripts/sync-to-projects.sh /path/to/project
#   bash scripts/sync-to-projects.sh --canary --apply --manifest-out /tmp/sync.json

set -euo pipefail

CRAFT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "${CRAFT_DIR}/scripts/harness-sync.py" --root "${CRAFT_DIR}" "$@"
