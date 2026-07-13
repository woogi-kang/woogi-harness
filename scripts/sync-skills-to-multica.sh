#!/usr/bin/env bash
# Sync Woogi Harness skills to Multica platform
# Usage: bash scripts/sync-skills-to-multica.sh [--dry-run] [--filter pattern]

set -euo pipefail

SKILLS_DIR="$(cd "$(dirname "$0")/../.claude/skills" && pwd)"
DRY_RUN=false
FILTER=""
SUCCESS=0
FAILED=0
SKIPPED=0

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run) DRY_RUN=true; shift ;;
        --filter) FILTER="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

echo "=== Multica Skill Sync ==="
echo "Skills dir: $SKILLS_DIR"
echo "Dry run: $DRY_RUN"
[[ -n "$FILTER" ]] && echo "Filter: $FILTER"
echo ""

# Get existing skills to avoid duplicates
EXISTING_SKILLS=$(multica skill list --output json 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data:
        for s in data:
            print(s.get('name', ''))
except:
    pass
" 2>/dev/null || echo "")

find "$SKILLS_DIR" -name "SKILL.md" -type f | sort | while read -r skill_file; do
    # Skip _template
    if [[ "$skill_file" == *"_template"* ]]; then
        ((SKIPPED++)) || true
        continue
    fi

    # Apply filter
    if [[ -n "$FILTER" ]] && [[ "$skill_file" != *"$FILTER"* ]]; then
        continue
    fi

    # Parse frontmatter
    name=$(python3 -c "
import sys, re
content = open('$skill_file').read()
m = re.search(r'^name:\s*[\"'\'']*([^\"'\''\\n]+)', content, re.MULTILINE)
print(m.group(1).strip() if m else '')
" 2>/dev/null)

    description=$(python3 -c "
import sys, re
content = open('$skill_file').read()
m = re.search(r'^description:\s*[\"'\'']*([^\"'\''\\n]+)', content, re.MULTILINE)
print(m.group(1).strip()[:200] if m else '')
" 2>/dev/null)

    if [[ -z "$name" ]]; then
        rel_path="${skill_file#$SKILLS_DIR/}"
        echo "⚠ SKIP (no name): $rel_path"
        ((SKIPPED++)) || true
        continue
    fi

    # Clean name for Multica (remove prefix like ckm:)
    clean_name="${name#ckm:}"

    # Check duplicate
    if echo "$EXISTING_SKILLS" | grep -qx "$clean_name"; then
        echo "⏭ EXISTS: $clean_name"
        ((SKIPPED++)) || true
        continue
    fi

    # Get content (full file)
    content=$(cat "$skill_file")

    rel_path="${skill_file#$SKILLS_DIR/}"

    if $DRY_RUN; then
        echo "🔍 DRY: $clean_name — ${description:0:60}..."
    else
        result=$(multica skill create \
            --name "$clean_name" \
            --description "${description:-No description}" \
            --content "$content" \
            --output json 2>&1) || true

        if echo "$result" | grep -q '"id"'; then
            echo "✅ $clean_name"
            ((SUCCESS++)) || true
        else
            echo "❌ FAIL: $clean_name — $result"
            ((FAILED++)) || true
        fi
    fi
done

echo ""
echo "=== Done ==="
echo "Success: $SUCCESS | Skipped: $SKIPPED | Failed: $FAILED"
