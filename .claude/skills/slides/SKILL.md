---
name: ckm:slides
description: "전략적 HTML 프레젠테이션 — Chart.js, 디자인 토큰, 반응형 레이아웃 기반 슬라이드"
argument-hint: "[topic] [slide-count]"
metadata:
  author: claudekit
  version: "1.0.0"
---

# Slides

Strategic HTML presentation design with data visualization.

<args>$ARGUMENTS</args>

## When to Use

- Marketing presentations and pitch decks
- Data-driven slides with Chart.js
- Strategic slide design with layout patterns
- Copywriting-optimized presentation content

## Subcommands

| Subcommand | Description | Reference |
|------------|-------------|-----------|
| `create` | Create strategic presentation slides | `references/create.md` |

## References (Knowledge Base)

| Topic | File |
|-------|------|
| Layout Patterns | `references/layout-patterns.md` |
| HTML Template | `references/html-template.md` |
| Copywriting Formulas | `references/copywriting-formulas.md` |
| Slide Strategies | `references/slide-strategies.md` |

## Routing

1. Parse subcommand from `$ARGUMENTS` (first word)
2. Load corresponding `references/{subcommand}.md`
3. Execute with remaining arguments

## Presentation Quality Gate

For Korean information decks, training decks, and strategic explanation decks, apply the same
quality gate used by the PPT/Future Slide harness before final delivery:

- Keep title, lede/key sentence, and first content block spacing consistent across slides.
- Do not use decorative divider lines, number underlines, or shadows unless they explain flow.
- Keep same-level boxes symmetric in width, height, baseline, and left/right edges.
- Use accent color only for a meaningful state or emphasis; do not highlight one process card by accident.
- Use left alignment for sentence-style Korean explanations; reserve center alignment for labels or short titles.
- Replace abstract claims with concrete examples: input/question, natural-language answer, structured output, and validation/fallback reason.
- Regenerate PDF and review a contact sheet or screenshots after visual changes.
