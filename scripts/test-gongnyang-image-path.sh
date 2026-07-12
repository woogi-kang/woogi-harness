#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
bash "$ROOT/scripts/verify-gongnyang-prompt-kit.sh"

if rg -n -i \
  'gpt-image-1(?:\.5|\b)|dall[ -]?e|google[ -]?imagen|\bimagen\b|gemini|nano banana|midjourney|stable diffusion|\bsdxl\b|\bflux(?:\.2)?\b|leonardo(?:\.ai)?' \
  "$ROOT/.claude/rules/common/imagegen-marketing-assets.md" \
  "$ROOT/.claude/skills/📝 콘텐츠/presentation-agent-skills/7-image-gen/SKILL.md" \
  "$ROOT/.claude/skills/banner-design/SKILL.md" \
  "$ROOT/.claude/skills/logo-creator/SKILL.md"; then
  echo "ERROR: alternate image provider found in a primary route" >&2
  exit 1
fi

blocked_output="$(printf '%s' '{"tool_name":"imagegen","tool_input":{"model":"gpt-image-1.5"}}' | \
  python3 "$ROOT/.claude/hooks/image-generation-guard.py")"
grep -q '"permissionDecision": "deny"' <<<"$blocked_output"

implicit_model_output="$(printf '%s' '{"tool_name":"imagegen","tool_input":{"prompt":"unverified"}}' | \
  python3 "$ROOT/.claude/hooks/image-generation-guard.py")"
grep -q '"permissionDecision": "deny"' <<<"$implicit_model_output"

observable_direct_output="$(printf '%s' '{"tool_name":"imagegen","tool_input":{"model":"gpt-image-2","prompt":"synthetic"}}' | \
  python3 "$ROOT/.claude/hooks/image-generation-guard.py")"
grep -q '"permissionDecision": "deny"' <<<"$observable_direct_output"

skill_blocked_output="$(printf '%s' '{"tool_name":"Skill","tool_input":{"skill":"imagegen","args":"make a generic poster"}}' | \
  python3 "$ROOT/.claude/hooks/image-generation-guard.py")"
grep -q '"permissionDecision": "deny"' <<<"$skill_blocked_output"

skill_claiming_model_output="$(printf '%s' '{"tool_name":"Skill","tool_input":{"skill":"imagegen","model":"gpt-image-2","args":"synthetic"}}' | \
  python3 "$ROOT/.claude/hooks/image-generation-guard.py")"
grep -q '"permissionDecision": "deny"' <<<"$skill_claiming_model_output"

bash_image_api_output="$(printf '%s' '{"tool_name":"Bash","tool_input":{"command":"curl https://api.openai.com/v1/images/generations -d model=gpt-image-2"}}' | \
  python3 "$ROOT/.claude/hooks/image-generation-guard.py")"
grep -q '"permissionDecision": "deny"' <<<"$bash_image_api_output"

compiler_output="$(printf '%s' '{"tool_name":"Skill","tool_input":{"skill":"image-prompt","args":"compile this request"}}' | \
  python3 "$ROOT/.claude/hooks/image-generation-guard.py")"
[[ -z "$compiler_output" ]] || {
  echo "ERROR: Gongnyang image-prompt compiler call was blocked" >&2
  exit 1
}

echo "PASS: local controls enforce exact Gongnyang bytes/validator and deny observable alternate routes"
echo "TRUSTED HOST BOUNDARY: Codex image_gen__imagegen requires gpt-image-2; model identity is not locally observable"
