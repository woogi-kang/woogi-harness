#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
VALIDATOR="$ROOT/.claude/skills/💻 개발/remotion-video-production-skill/scripts/validate-product-ui-promo.py"
VALID="$ROOT/.claude/evals/remotion-product-ui-promo/cases/valid"
INVALID="$ROOT/.claude/evals/remotion-product-ui-promo/cases/invalid"
MALFORMED="$ROOT/.claude/evals/remotion-product-ui-promo/cases/malformed"
TRAVERSAL="$ROOT/.claude/evals/remotion-product-ui-promo/cases/traversal"

python3 "$VALIDATOR" \
  --reference "$VALID/reference-analysis.json" \
  --capture "$VALID/capture-manifest.json" \
  --scenes "$VALID/scene-spec.json"

if python3 "$VALIDATOR" \
  --reference "$INVALID/reference-analysis.json" \
  --capture "$INVALID/capture-manifest.json" \
  --scenes "$INVALID/scene-spec.json"; then
  echo "FAIL: invalid fixture unexpectedly passed"
  exit 1
fi

echo "PASS: invalid fixture was rejected"

if python3 "$VALIDATOR" \
  --reference "$MALFORMED/reference-analysis.json" \
  --capture "$MALFORMED/capture-manifest.json" \
  --scenes "$MALFORMED/scene-spec.json"; then
  echo "FAIL: malformed fixture unexpectedly passed"
  exit 1
fi

echo "PASS: malformed fixture was rejected without crashing"

if python3 "$VALIDATOR" \
  --reference "$TRAVERSAL/reference-analysis.json" \
  --capture "$TRAVERSAL/capture-manifest.json" \
  --scenes "$TRAVERSAL/scene-spec.json" \
  --project-root "$TRAVERSAL"; then
  echo "FAIL: traversal fixture unexpectedly passed"
  exit 1
fi

echo "PASS: project-root traversal was rejected"
