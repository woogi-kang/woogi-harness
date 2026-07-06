---
name: design-harness
description: "차세대 프론트엔드 디자인 실행 하네스 v2. UI/UX 디자인, 랜딩/대시보드/앱/포트폴리오/브랜드 페이지, 리디자인, UX 리뷰, visual QA, anti-slop, reference translation, 디자인 시스템 선택, 접근성/반응형/상태 하드닝에 사용한다. AI Slop이 의심되는 모든 프론트엔드 산출물에는 반드시 이 스킬을 사용하고, design read → control dials → anti-slop gate → detector/preflight 검증까지 수행한다."
license: MIT
metadata:
  category: "🎨 디자인"
  version: "0.2.0"
  tags: "frontend-design, ui-ux, anti-slop, visual-qa, redesign, design-system, interface-polish, preflight"
---

# Design Harness v2

Use this as the primary UI/UX design execution harness. The goal is not to make a page look "designed". The goal is to read the product, choose the right design register, block predictable AI slop, implement or review with evidence, and verify the result before handoff.

This harness replaces loose taste advice with an execution contract:

```text
Design Read → Control Dials → Mode + References → Execute → Detector → Final Preflight
```

If a frontend task can affect layout, styling, UX, motion, copy, accessibility, responsive behavior, or visual QA, use this skill.

## Non-Negotiable Operating Rules

1. **Do not start from style. Start from the product scene.**
   A medical workflow, Korean dating recommendation app, developer tool, public-sector service, and campaign page must not share the same visual reflex.
2. **Name the main slop risk before acting.**
   Examples: category reflex, centered hero reflex, shadcn default state, fake dashboard evidence, generic AI copy, missing product states.
3. **Use evidence, not decoration.**
   Prefer real screenshots, generated raster assets, actual component previews, charts, maps, photos, or data views. Do not substitute abstract blobs or div-based fake UIs when proof is needed.
4. **Official systems beat imitation.**
   If the brief maps to Material, Fluent, Carbon, Polaris, Atlassian, Primer, GOV.UK, USWDS, or another official system, use the official package or explain why not.
5. **The task is not complete until the gate passes.**
   Run the detector when code is available. Run browser/screenshot QA when the project is runnable. Use `references/preflight.md` before finalizing.

## Core Flow

### 1. Load project context

- Read `PRODUCT.md`, `DESIGN.md`, brand docs, route docs, or local planning files when present.
- Inspect at least one representative UI file: tokens/theme CSS, app shell, page, or component.
- Check `package.json` before recommending or importing libraries.
- For redesigns, inspect current IA, brand tokens, SEO-sensitive routes, analytics hooks, forms, and legal copy before proposing changes.

### 2. Write the Design Read

Always produce a compact design read before implementation or review:

```text
Reading this as: <surface> for <audience>, in <scene>, using <product|brand|operational> register, with <visual stance>, avoiding <main slop risk>.
```

Ask one short question only when two plausible reads would materially change the work. Otherwise state assumptions and proceed.

Read `references/design-read.md` when the direction is ambiguous, broad, or likely to suffer from category reflex.

### 3. Set five control dials

| Dial | 1-3 | 4-7 | 8-10 |
|---|---|---|---|
| `DISTINCTION` | familiar | specific | highly authored |
| `MOTION` | feedback only | subtle choreography | advanced scroll/physics |
| `DENSITY` | sparse | normal | compact/operational |
| `EVIDENCE` | mostly text | some proof | proof-led: screenshots/data/assets |
| `SYSTEMNESS` | bespoke | token-guided | official DS / strict component system |

Defaults by surface:

| Surface | DISTINCTION | MOTION | DENSITY | EVIDENCE | SYSTEMNESS |
|---|---:|---:|---:|---:|---:|
| Product UI / dashboard | 3-5 | 2-4 | 6-9 | 6-9 | 7-10 |
| Brand / landing | 6-9 | 4-8 | 2-5 | 7-10 | 4-8 |
| Portfolio / editorial | 6-9 | 3-7 | 2-5 | 5-9 | 3-7 |
| Public-sector / regulated | 2-4 | 1-3 | 5-8 | 6-9 | 8-10 |
| Redesign preserve | match existing + small lift | +0-1 | match | +1 | +1 |

### 4. Pick a mode and required references

| Mode | Use when | Required references |
|---|---|---|
| `shape` | UX/UI plan before code | `references/workflows.md`, `references/design-read.md` |
| `reference` | named brand/product/site inspiration or best-in-class comparison | `references/design-reference-index.md`, `references/design-references.md`, `references/anti-slop.md` |
| `measure` | concrete URL/screenshot should become measured tokens or `design.md` | `references/reference-style-extraction.md`, then `web-access-ladder` if fetching is hard |
| `craft` | implement a new UI surface end-to-end | `references/registers.md`, `references/anti-slop.md`, `references/preflight.md`, `references/interface-polish.md` |
| `audit` | review UX, a11y, responsive, visual quality | `references/workflows.md`, `references/anti-slop.md`, `references/preflight.md`, `references/interface-polish.md` |
| `polish` | improve an existing surface before ship | `references/anti-slop.md`, `references/preflight.md`, `references/interface-polish.md`, `references/motion-interaction.md` |
| `redesign` | modernize existing UI | `references/redesign-protocol.md`, `references/workflows.md`, `references/anti-slop.md`, `references/preflight.md` |
| `typeset` | typography hierarchy/font work | `references/registers.md`, then `korean-typography` when Korean fonts apply |
| `colorize` | palette/theme work | `references/registers.md`, `references/anti-slop.md`, `references/preflight.md` |
| `animate` | purposeful motion/interactions | `references/motion-interaction.md`, `references/interface-polish.md`, `references/preflight.md` |
| `harden` | states, edge cases, i18n, text overflow | `references/preflight.md`, `references/interface-polish.md`, `references/korean-ui.md` when Korean applies |

Use `references/design-system-map.md` whenever the surface is product UI, dashboard/admin, public-sector, enterprise, commerce/admin, devtool, or any interface where official systems may apply.

### 5. Execute with the right downstream skill

- Component implementation: `ui-styling`.
- Token architecture: `design-system`.
- Korean webfont pairing, Hangul readability, and role-based font tokens: `korean-typography`.
- Public reference URL retrieval: `web-access-ladder`.
- Official design system docs for a library or SDK: `official-docs-guide`.
- Lottie/Bodymovin JSON animation authoring and Skottie preview: `text-to-lottie`.
- Logos, banners, CIP, social images: `design`, `logo-creator`, `banner-design`.
- Historical database lookup is archived; do not route new design work to it.

### 6. Mandatory gate before finalizing

When UI code exists locally, run the detector on changed UI files or the focused source directory:

```bash
node .claude/skills/design-harness/scripts/detect-design-slop.mjs src app components pages
```

If the script exits non-zero, inspect findings. Hard-fail findings require a fix or an explicit reason they are acceptable. Warnings are review prompts.

When the project is runnable, verify in a browser or screenshot. Check desktop and mobile-relevant widths when feasible.

Before final response, use `references/preflight.md`. State what was verified and what remains unverified.

## Register Split

Read `references/registers.md` when the task touches a full screen, page, app shell, landing page, dashboard, or redesign.

- **Product register**: repeated task completion. Favor predictable controls, complete states, restrained color, density, speed, and clarity.
- **Brand register**: design is part of the product. Favor a clear point of view, real assets, committed art direction, layout variation, and strong first impression.
- **Operational register**: internal tools, dashboards, admin, data workflows. Favor data density, keyboard flow, robust states, low motion, and official system patterns.

Do not use brand-page tactics on dashboards. Do not use dashboard restraint on campaign pages. Do not use aesthetic references to override regulatory, accessibility, or product constraints.

## Anti-Slop Model

Read `references/anti-slop.md` for implementation or review. Treat slop as five failure classes:

1. **Category reflex** - the category predicts the look.
2. **Layout reflex** - centered hero, pill, equal cards, repeated split sections.
3. **Content slop** - vague verbs, fake-perfect metrics, unsupported trust claims.
4. **Evidence slop** - fake dashboards, abstract blobs, empty bento cells, generic avatars.
5. **Polish slop** - bad contrast, missing states, `transition-all`, tiny hit areas, broken mobile.

The default response to slop is not "make it prettier". It is to identify the failure class and route it to the right gate: reference, official system, evidence, detector, polish, or preflight.

## Review Output

For reviews, lead with a table:

| Before | After | Why |
|---|---|---|
| Current pattern or issue | Proposed change | Design reason and risk |

Then list only the highest-impact fixes. Avoid long taste-preference inventories.

For implementation handoff, include:

- Design read.
- Dials.
- Key decisions.
- Gate results: detector, browser/screenshot QA, preflight notes.
- Remaining risks or assumptions.

## Legacy Policy

- `ui-ux-pro-max` and `design-craft` have been archived outside the active skill tree at `.claude/archive/skills/design/legacy-entrypoints-260529`.
- `🎨 디자인/ui-design-agent-skills/*` has been archived outside the active skill tree at `.claude/archive/skills/design/ui-design-agent-skills-legacy-260529`. Do not use those old template snippets as primary guidance.
