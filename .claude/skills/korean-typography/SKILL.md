---
name: korean-typography
description: Korean-first typography and webfont system design for Korean products, landing pages, apps, dashboards, portfolios, blogs, slides, and brand surfaces. Use when choosing Korean fonts, font pairing, mood-based Hangul webfont recommendations, commercially safer Korean webfonts, CSS font-family variables, Tailwind or design-token typography mapping, or reviewing Korean UI text readability.
---

# Korean Typography

## Overview

Choose Korean typography by product mood and text role, then turn it into stable implementation tokens. This skill is inspired by the public Korean Vibe Fonts package, but the bundled catalog and recommender are rewritten for Woogi Harness rather than vendored from upstream.

Use this as the typography layer under `design-harness`: design-harness decides the product or brand register, this skill chooses and applies Hangul font roles.

## Quick Start

Run the recommender when the brief is mood-based or broad:

```bash
python3 .claude/skills/korean-typography/scripts/recommend-korean-font.py --theme "AI SaaS 랜딩 페이지"
python3 .claude/skills/korean-typography/scripts/recommend-korean-font.py --theme "차분한 에디토리얼 포트폴리오" --json
```

Then apply the result as a small role system:

```css
:root {
  --font-body: "<body family>";
  --font-heading: "<heading family>";
  --font-code: "<code family>";
}

body {
  font-family: var(--font-body);
}

h1, h2, h3, .display, .headline {
  font-family: var(--font-heading);
}

code, pre, kbd, samp {
  font-family: var(--font-code);
}
```

## Workflow

1. **Read the surface**
   - Product UI, admin, dashboard: prioritize legibility, numbers, labels, repeated scanning.
   - Landing, portfolio, brand story: allow stronger heading personality while keeping body readable.
   - Blog, docs, long-form: prioritize comfortable Korean paragraphs and predictable fallbacks.
   - Campaign, event, commerce: use display fonts for hero or short labels only.

2. **Pick roles, not random families**
   - `body`: paragraphs, UI labels, captions, table cells, forms, card copy.
   - `heading`: page title, section title, hero headline, slide title.
   - `code`: code blocks, terminal UI, CLI examples, developer-product snippets.
   - `accent`: optional only for short notes, stickers, testimonials, or campaign copy.

3. **Keep the system small**
   - Use at most three families: body, heading, code.
   - Do not use handwriting, poster, or display fonts for paragraph text.
   - Keep the same role mapping across screens, pages, and slides.

4. **Load references only when needed**
   - Use `references/presets.md` for fast mood presets.
   - Use `references/font-catalog.json` when applying exact CSS, checking source URLs, or reviewing license status.

5. **Apply through existing project conventions**
   - If the project has design tokens, write font families into tokens.
   - If the project uses Tailwind, map families through CSS variables or `theme.fontFamily`.
   - If the project already uses a framework font loader, preserve that pattern for Google Fonts and use stylesheet imports only where the font requires it.

## Default Pairings

| Situation | Body | Heading | Code |
| --- | --- | --- | --- |
| Korean-first SaaS or app UI | Pretendard Variable | NanumSquare Neo | NanumGothicCoding |
| B2B dashboard or ops tool | IBM Plex Sans KR | IBM Plex Sans KR | NanumGothicCoding |
| Developer portfolio or devtool | Pretendard Variable | Goorm Sans | NanumGothicCoding |
| Editorial brand story | MaruBuri | Hahmlet | none |
| Premium institutional content | Noto Serif KR | Hahmlet | none |
| Friendly community app | NanumSquareRound | Jua | none |
| Campaign or event page | Pretendard Variable | Black Han Sans | none |

## Output Standard

When recommending typography, return:

1. One sentence reading of the mood and surface.
2. Recommended set: body, heading, code, optional accent.
3. Why this pairing fits.
4. Paste-ready stylesheet imports or style block.
5. CSS variables and base selectors.
6. Role mapping for multi-screen or slide work.
7. One or two alternatives only when the decision is genuinely subjective.

## Guardrails

- Treat the bundled catalog as a practical starting point, not legal advice. For a client launch, regulated use, redistribution, or self-hosting, re-open the official license URL before final approval.
- Prefer fonts with official web delivery or stable public CSS. Do not invent CDN URLs.
- For Korean body text, avoid negative letter spacing. Korean UI usually needs normal tracking and careful line-height.
- For dashboards and tables, add `font-variant-numeric: tabular-nums` when supported.
- If the UI mixes Korean and English, test actual mixed strings. Do not choose an English-first font stack that accidentally renders Korean through a weak fallback.
- If the user asks for a specific brand font, verify its license and web delivery instead of silently substituting a similar public font.
- If a screen already has a mature typography system, refine its role mapping before replacing the family.

## Integration With Other Skills

- Use `design-harness` first for full UI design, redesign, visual QA, or register choice.
- Use `design-system` when font choices need to become reusable tokens.
- Use `ui-styling` when applying the chosen system to shadcn, Tailwind, React, Next.js, or static HTML.
