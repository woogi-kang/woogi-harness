#!/usr/bin/env bash
# 절대규칙: 생성 이미지 위 글자 후처리(오버레이) 차단 — PreToolUse:Bash 훅
# 텍스트는 프롬프트로 이미지 안에서 렌더한다. 틀리면 프롬프트를 고쳐 재생성.
cmd=$(python3 -c 'import sys,json;print(json.load(sys.stdin).get("tool_input",{}).get("command",""))' 2>/dev/null)
pattern='\-annotate\b|(magick|convert|mogrify)[^|;&]*(caption:|label:|pango:)|\-draw +[^|;&]{0,80}text|ImageDraw|ImageFont|drawtext'
if grep -qE "$pattern" <<<"$cmd"; then
  cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"절대규칙: 생성 이미지 위 글자 후처리 금지(PIL/ImageMagick/ffmpeg drawtext 오버레이 차단) — 프롬프트를 고쳐 이미지 안에서 재렌더할 것 (image-prompt 철칙 9)"}}
JSON
fi
exit 0
