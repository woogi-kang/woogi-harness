---
name: korean-typography-quality
description: Use this whenever generating, reviewing, or evaluating Korean-language UI, landing pages, dashboards, slides, documents, or HTML/CSS. It prevents Korean AI slop by enforcing Korean-safe font choices, word breaking, line-height, role-based typography consistency, and commercial-use caution based on the pinned korean-vibe-fonts catalog.
metadata:
  category: design
  version: "1.0.0"
  tags: "korean, typography, fonts, css, word-break, eval, ui, slides"
  author: "woogi"
---

# Korean Typography Quality Layer

Most generated artifacts in this workspace are Korean. Treat Korean typography as a quality gate, not decoration. The common AI-slop failure modes are broken Korean word wrapping, random font swaps between sections, English-first SaaS font stacks, and over-tight letter spacing that makes Hangul look mechanical.

## Core workflow

1. Detect whether the artifact is Korean-first or contains meaningful Korean text.
2. Pick a small role-based font system using the pinned catalog at `third_party/korean-vibe-fonts/`.
3. Apply the Korean CSS baseline from `references/korean-default.css`.
4. Keep font families stable by text role across screens/slides/pages.
5. Run `scripts/validate_korean_typography.py` on generated HTML/CSS/TSX/MD artifacts before considering the output done.

## Default Korean font system

Use this when the user does not provide a stronger art direction:

- `body`: Pretendard Variable
- `heading`: NanumSquare Neo or Pretendard Variable
- `code`: NanumGothicCoding

Use at most 3 families in normal work: body, heading, code. Add an accent/display font only for deliberate campaign or poster-style emphasis, never for paragraphs.

## Korean wrapping policy

For Korean text containers, prefer:

```css
word-break: keep-all;
overflow-wrap: break-word;
line-break: strict;
```

For code, URLs, CLI commands, and long unbroken tokens, override with:

```css
word-break: normal;
overflow-wrap: anywhere;
```

This prevents awkward syllable-level line breaks while still avoiding layout overflow from URLs or code.

## Role map

- `heading`: page title, slide title, section heading, hero headline
- `body`: paragraph, bullet, subtitle, description, caption, label, table cell, card copy
- `code`: code block, terminal, CLI snippet, monospace metrics
- `accent`: short point labels only

Do not change font family per section just because the layout changes. Change size, weight, spacing, color, or composition first.

## Vibe-based selection

Use `third_party/korean-vibe-fonts/scripts/recommend_font.py` when mood matters:

```bash
python3 third_party/korean-vibe-fonts/scripts/recommend_font.py --theme "AI SaaS 랜딩 페이지" --json
python3 third_party/korean-vibe-fonts/scripts/recommend_font.py --theme "차분한 에디토리얼 포트폴리오"
```

Recommended defaults by artifact type:

| Artifact | Body | Heading | Notes |
|---|---|---|---|
| AI/SaaS landing | Pretendard Variable | NanumSquare Neo | Safe product default |
| Dashboard/admin | Spoqa Han Sans Neo or Pretendard | Pretendard | Numeric/data readability |
| Developer docs | Noto Sans KR or Pretendard | IBM Plex Sans KR | Include code font |
| Editorial/brand story | Gowun Batang or Noto Serif KR | MaruBuri or Hahmlet | Long-form Korean mood |
| Playful community | Gowun Dodum or NanumSquareRound | Jua or NanumSquareRound | Keep body readable |
| Campaign/event | Pretendard or Gmarket Sans | Black Han Sans or Do Hyeon | Display font only for headings |

## CSS baseline

Read and reuse `references/korean-default.css`. Important invariants:

- `html[lang="ko"]` or Korean content gets `word-break: keep-all`.
- body text uses line-height around `1.55-1.75`.
- headings use tighter line-height around `1.12-1.25`, not cramped body defaults.
- Korean text avoids aggressive letter spacing. Body should usually stay between `0` and `-0.015em`; headings can go to about `-0.03em`.
- code/pre/kbd/samp use a code-capable font and `overflow-wrap: anywhere`.

## Quality checks

Before shipping a Korean artifact, verify:

- Korean glyph-capable font stack exists.
- `word-break: keep-all` is applied to Korean text contexts.
- `overflow-wrap` fallback exists to prevent overflow.
- code/URL contexts have separate wrapping rules.
- heading/body/code role mapping is stable.
- no more than 3 normal font families are used.
- font license notes are not phrased as legal guarantees.

Run:

```bash
python3 .claude/skills/korean-typography-quality/scripts/validate_korean_typography.py path/to/artifact.html
```

The validator is a fast static guard. Passing it does not replace visual QA, but failing it is a strong signal that the artifact will look like Korean AI slop.

## License and delivery caution

The pinned `korean-vibe-fonts` catalog prioritizes commercially usable fonts, but catalog notes are not legal advice. For final commercial deployment, verify official font licenses and choose CDN vs self-hosting based on privacy, CSP, PDF rendering, and customer requirements.
