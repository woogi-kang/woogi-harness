---
name: design-harness
description: "차세대 프론트엔드 디자인 하네스. UI/UX 디자인, 랜딩/대시보드/앱/포트폴리오/브랜드 페이지, 리디자인, UX 리뷰, visual QA, anti-slop, 스타일/컬러/타이포그래피/레이아웃/모션 의사결정, 접근성/반응형/상태 하드닝에 사용한다. 과거 ui-ux-pro-max, design-craft, ui-design-agent-skills를 대체하는 1차 디자인 진입점이다."
license: MIT
metadata:
  category: "🎨 디자인"
  version: "0.1.1"
  tags: "frontend-design, ui-ux, anti-slop, visual-qa, redesign, design-system, interface-polish"
---

# Design Harness

Use this as the primary UI/UX design entrypoint. It replaces the old split between `ui-ux-pro-max` planning, `design-craft` anti-slop checks, and the granular `🎨 디자인/ui-design-agent-skills/*` template skills.

The job is not to generate a style from a database. The job is to read the product, pick the right register, make explicit design decisions, implement or review the interface, then verify that it does not look like default AI output.

## Core Flow

1. **Load project context**
   - Read `PRODUCT.md` and `DESIGN.md` when present.
   - Inspect at least one representative UI file: tokens/theme CSS, a page, or a component.
   - Check `package.json` before recommending or importing libraries.
   - For redesigns, preserve existing behavior, IA, and brand identity unless the user asks for overhaul.

2. **Write a design read**

   ```text
   Reading this as: <surface> for <audience>, in <scene>, using <brand|product> register, with <visual stance>, avoiding <main slop risk>.
   ```

   Ask one short question only when two plausible reads would materially change the design. Otherwise state assumptions and proceed.

3. **Choose reference stance when useful**

   Read `references/design-reference-index.md` when the user asks for "proven", "best-in-class", big-company, or broad reference options. Read `references/design-references.md` when the user names a company/product/site as inspiration, has already chosen a reference, wants a more mature visual direction, or needs a full-screen/page/app design where reference choice will materially change the output.

   Output:

   ```text
   Reference stance:
   - Primary reference: <brand/product>
   - Secondary reference: <brand/product or none>
   - Anti-reference: <style to avoid>
   - Borrow: <transferable design grammar>
   - Do not borrow: <brand-specific traits>
   ```

   Borrow design grammar, not identity. Do not copy logos, marks, exact brand palettes, proprietary imagery, recognizable page compositions, or trademarked UI chrome.

4. **Set three dials**

   | Dial | 1-3 | 4-7 | 8-10 |
   |---|---|---|---|
   | `DISTINCTION` | familiar | specific | highly authored |
   | `MOTION` | feedback only | subtle choreography | advanced scroll/physics |
   | `DENSITY` | sparse | normal | compact/operational |

   Product UI usually sits at `3-5 / 2-4 / 6-9`. Brand surfaces usually sit at `6-9 / 4-8 / 2-5`. Regulated or public-sector surfaces bias lower distinction and motion.

5. **Pick a mode**

   | Mode | Use when | Required reference |
   |---|---|---|
   | `shape` | UX/UI plan before code | `references/workflows.md` |
   | `reference` | named brand/product/site inspiration, best-in-class reference selection, or DESIGN.md translation | `references/design-reference-index.md`, `references/design-references.md`, `references/anti-slop.md` |
   | `craft` | implement a new UI surface end-to-end | `references/registers.md`, `references/anti-slop.md`, `references/interface-polish.md` |
   | `audit` | review UX, a11y, responsive, visual quality | `references/workflows.md`, `references/anti-slop.md`, `references/interface-polish.md` |
   | `polish` | improve an existing surface before ship | `references/anti-slop.md`, `references/interface-polish.md`, `references/motion-interaction.md` |
   | `redesign` | modernize existing UI | `references/workflows.md` |
   | `typeset` | typography hierarchy/font work | `references/registers.md`, then `korean-typography` when Korean fonts apply |
   | `colorize` | palette/theme work | `references/registers.md`, `references/anti-slop.md` |
   | `animate` | purposeful motion/interactions | `references/motion-interaction.md`, `references/interface-polish.md` |
   | `lottie` | Lottie/Bodymovin JSON motion asset creation or repair | `references/motion-interaction.md`, then `text-to-lottie` |
   | `harden` | states, edge cases, i18n, text overflow | `references/anti-slop.md`, `references/interface-polish.md`, `references/korean-ui.md` when Korean applies |

6. **Use the right downstream skill**
   - Component implementation: `ui-styling`.
   - Token architecture: `design-system`.
   - Korean webfont pairing, Hangul readability, and role-based font tokens: `korean-typography`.
   - Lottie/Bodymovin JSON animation authoring and Skottie preview: `text-to-lottie`.
   - Logos, banners, CIP, social images: `design`, `logo-creator`, `banner-design`.
   - Historical database lookup is archived; do not route new design work to it.

## Register Split

Read `references/registers.md` when the task touches a full screen, page, app shell, landing page, dashboard, or redesign.

- **Product register**: design serves repeated task completion. Favor predictable controls, complete states, restrained color, density, speed, and clarity.
- **Brand register**: design is part of the product. Favor a clear point of view, real assets, committed art direction, layout variation, and strong first impression.

Do not use brand-page tactics on dashboards. Do not use dashboard restraint on portfolio or campaign pages.

## Anti-Slop Defaults

Read `references/anti-slop.md` for implementation or review. The short version:

- Reject category reflexes: AI product does not imply purple glow; finance does not imply navy/gold; luxury does not imply cream/brass.
- Avoid repeated centered heroes, pill badges, equal card grids, gradient text, decorative glass, fake screenshots, generic logo walls, and cliche copy.
- Use actual images, screenshots, generated raster assets, real component previews, charts, maps, or canvas/WebGL scenes when the surface needs visual proof.
- Every interactive flow needs loading, empty, error, disabled, focus, mobile, and reduced-motion behavior when relevant.
- Use `references/interface-polish.md` for micro-details: text wrapping, tabular numbers, optical alignment, concentric radius, subtle press feedback, hit areas, and transition hygiene.

## Mechanical Preflight

When UI code exists locally, run the detector on changed UI files or the focused source directory:

```bash
node .claude/skills/design-harness/scripts/detect-design-slop.mjs src app components pages
```

Use the findings as prompts for inspection, not as a substitute for judgment. After implementation, verify in a browser when the project has a runnable frontend.

## Legacy Policy

- `ui-ux-pro-max` and `design-craft` have been archived outside the active skill tree at `.claude/archive/skills/design/legacy-entrypoints-260529`.
- `🎨 디자인/ui-design-agent-skills/*` has been archived outside the active skill tree at `.claude/archive/skills/design/ui-design-agent-skills-legacy-260529`. Do not use those old template snippets as primary guidance.

## Review Output

For reviews, lead with a table:

| Before | After | Why |
|---|---|---|
| Current pattern or issue | Proposed change | Design reason and risk |

Then list only the highest-impact fixes. Avoid long taste-preference inventories.
