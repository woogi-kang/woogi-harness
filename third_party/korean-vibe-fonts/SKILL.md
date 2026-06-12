---
name: korean-vibe-fonts
description: Recommend and apply commercially usable Korean webfonts for vibe-coded frontends, landing pages, portfolios, dashboards, editorial pages, campaign microsites, and developer UIs. Use when Codex needs to choose Korean typography by mood or tone and manner, explain why a font fits a concept, verify that the font is safe for commercial use from the bundled catalog, or inject paste-ready stylesheet imports and font-family CSS into HTML, CSS, React, Next.js, or design-token files.
---

# Korean Vibe Fonts

## Overview

Choose a Korean webfont by product mood, not by alphabetical list. Start from the page's tone and manner, pick a readable body font, add a stronger heading font only when it helps, and keep the final set small and paste-ready.

Prefer fonts that are already verified in the bundled catalog. Do not claim commercial safety for fonts that are not in `references/font_catalog.json` unless the user explicitly asks you to research and verify new sources.

## Quick Start

1. Read the user's theme, product type, and desired mood.
2. Run the recommender:

```bash
python3 scripts/recommend_font.py --theme "AI SaaS 랜딩 페이지"
python3 scripts/recommend_font.py --theme "차분한 에디토리얼 포트폴리오" --json
```

3. Use the selected body and heading fonts unless the codebase already has a strong typography system that should be preserved.
4. Keep the role mapping stable across every screen, section, or slide: once `body`, `heading`, and `code` are chosen, do not swap them around per page.
5. Paste the emitted stylesheet tags or inline style block, plus the CSS variables, into the project.
6. If the page contains code blocks, terminal UI, CLI examples, or developer-product sections, add `NanumGothicCoding` for code.

## Workflow

### 1. Decode the vibe first

- Extract the visual brief from the user's words: modern, editorial, premium, playful, cozy, technical, poster-like, etc.
- Infer the page type: landing, dashboard, portfolio, blog, campaign, docs, commerce banner.
- Choose the typography profile before choosing the exact family.

Default profile heuristics:

- Product UI: `Pretendard Variable`, `Spoqa Han Sans Neo`, `Goorm Sans`, `IBM Plex Sans KR`, `NanumSquare Neo`
- Editorial / brand story: `MaruBuri`, `Hahmlet`, `Noto Serif KR`, `Gowun Batang`
- Playful / community / cozy: `NanumSquareRound`, `Gowun Dodum`, `Jua`, `Single Day`
- Impact / campaign / promo: `Black Han Sans`, `Do Hyeon`, `여기어때 잘난체`, `Gmarket Sans`, `NanumSquare Neo`

### 2. Keep the font system small

Use at most 3 families:

- `body`
- `heading`
- `code` when needed

Do not use a handwriting or display font for paragraph text unless the user explicitly wants a deliberately unconventional result.

### 3. Prefer readable body text

Even if the vibe is cute or bold, keep paragraphs readable.

Recommended pattern:

- Strong display font for hero only
- Neutral or soft body font for paragraphs
- Monospace only for code, terminals, tables, or metric-heavy snippets

### 3.5. Keep element roles consistent across screens and slides

If the project has multiple screens, sections, or slides, keep typography consistent by element role even when layouts or moods vary slightly.

Recommended role map:

- `heading`: page title, slide title, section heading, hero headline
- `body`: paragraph, bullet, subtitle, description, caption, label, table cell, card copy
- `code`: code block, terminal, CLI snippet, monospace metric line

Do not reassign fonts per slide just because the composition changes. A title should still look like the same title system, and body text should still look like the same body system.

If one slide or section needs stronger personality, change size, weight, spacing, color, or layout first. Change the font family only when the user explicitly wants a deliberate break.

### 4. Apply fonts in the fastest project-safe way

For quick vibe-coding prototypes:

- Use the bundled `html_link`, `style_tag`, or setup note from the catalog
- Emit CSS custom properties such as `--font-body`, `--font-heading`, and `--font-code`

If the repo already uses a framework-specific loader:

- Preserve it
- For Google Fonts in Next.js, translate the chosen family into `next/font/google` only when that clearly matches the repo's existing pattern
- For NAVER fonts and Pretendard, use the catalog stylesheet URL unless the user explicitly asks for self-hosting
- In multi-screen or slide-like work, define typography tokens once and reuse them everywhere instead of picking new font families per frame

## Output Format

When recommending fonts to the user, prefer this structure:

1. One-sentence vibe summary
2. Recommended set: body, heading, code
3. Why the set matches the tone
4. Paste-ready `<link>` or `@import`
5. Paste-ready CSS variables and base selectors
6. Role mapping when the work spans multiple screens or slides
7. Optional 1-2 alternatives when the choice is subjective

Keep the explanation short and opinionated. Do not overwhelm the user with the entire catalog unless they ask for a list.

## Application Patterns

### Generic HTML or static site

Emit:

```html
<link href="..." rel="stylesheet">
```

and:

```css
:root {
  --font-body: ...;
  --font-heading: ...;
  --font-code: ...;
}

body { font-family: var(--font-body); }
h1, h2, h3, h4, .display, .headline { font-family: var(--font-heading); }
code, pre, kbd, samp { font-family: var(--font-code); }
```

### Existing CSS or Tailwind project

- Put the stylesheet import in the global stylesheet or layout head
- Map the chosen families to CSS variables
- If the project uses design tokens, store the families in tokens instead of hard-coding them on individual components

### React, Vite, or small frontend app

- Add the stylesheet once at app root
- Apply font tokens at `:root` or `body`
- Avoid sprinkling per-component imports

## Guardrails

- Use only fonts in `references/font_catalog.json` when the user asks for commercially safe Korean webfonts and does not ask for extra research.
- Treat the catalog as the source of truth for integration snippets, family names, and commercial-use notes.
- If a catalog entry is marked as not suitable for automatic webfont recommendation, do not recommend it by default for paste-ready web use.
- Prefer exact paste-ready snippets over vague advice.
- Do not mix too many expressive fonts on a single page.
- Even when screens or slides differ visually, keep font-family assignments consistent by role.
- If the user wants "retro", "street", or "poster", push the energy into headings first and keep the body clean.
- If the user wants "cozy" or "handmade", keep the body readable and use handwriting fonts as accents.
- If the user wants "developer", "AI", "dashboard", or "tooling", include `NanumGothicCoding` for code areas.
- If no clear vibe is provided, default to `Pretendard Variable` for body and `NanumSquare Neo` or `Pretendard Variable` for headings.

## Resources

### `scripts/recommend_font.py`

Run this first when the vibe is ambiguous or when you want a paste-ready starter set.

Example:

```bash
python3 scripts/recommend_font.py --theme "테크 감성의 개발자 포트폴리오"
```

### `references/font_catalog.json`

Use this for verified font metadata:

- official source page
- official or documented stylesheet URL, inline snippet, or self-hosting note
- recommended body and heading family strings
- tone tags
- best-fit and avoid-fit notes

### `references/vibe_presets.md`

Use this when the user gives a common theme and speed matters more than exhaustive exploration.

Examples:

- AI SaaS landing
- quiet editorial portfolio
- cozy lifestyle brand
- bold campaign page

## Final reminder

Recommend fonts like a design partner, not like a font directory. Pick the smallest viable set, explain the mood match in one or two sharp sentences, and leave the user with code they can paste immediately.
