# Design Harness Migration

Date: 2026-05-29  
Status: active migration applied  
Goal: replace legacy design skills that produce template-like UI with a single modern design harness.

## New Primary Skill

| Skill | Status | Role |
|---|---|---|
| `design-harness` | New primary | UI/UX design, redesign, audit, polish, anti-slop, visual QA, product/brand register, motion/interactions, responsive/state hardening |

## Keep

These remain active because they own specialized implementation or asset workflows.

| Skill | Why keep |
|---|---|
| `ui-styling` | shadcn/ui, Tailwind, component implementation |
| `design-system` | token architecture, CSS variables, component specs |
| `design` | asset/CIP/social/slides orchestration |
| `logo-creator` | logo, brand mark, favicon, app icon generation |
| `banner-design` | banner, cover, header, ad creative generation |
| `brand` | brand voice and messaging |
| `app-store-screenshots` | app store screenshot workflow |
| `slides` / presentation skills | presentation-specific design and export workflows |

## Archived Legacy Entrypoints

These are no longer discoverable as active skills. They were moved to `.claude/archive/skills/design/legacy-entrypoints-260529/` for recovery only.

| Skill | Replacement | Action |
|---|---|---|
| `ui-ux-pro-max` | `design-harness` | Archived with CSV data/scripts. No active routing. |
| `design-craft` | `design-harness` | Archived. Guidance folded into `design-harness`. |

## Archived From Active Skill Tree

These skills are no longer routed or discoverable as active skills. They were moved from `.claude/skills/🎨 디자인/ui-design-agent-skills/` to `.claude/archive/skills/design/ui-design-agent-skills-legacy-260529/` for temporary recovery.

| Path | Problem | Replacement |
|---|---|---|
| `.claude/skills/🎨 디자인/ui-design-agent-skills/1-context` | verbose intake template, duplicated by design read | `design-harness` shape mode |
| `.claude/skills/🎨 디자인/ui-design-agent-skills/2-inspiration` | old trend/moodboard workflow, not tied to implementation QA | `design-harness` + web/image research when needed |
| `.claude/skills/🎨 디자인/ui-design-agent-skills/3-direction` | fixed aesthetic menu encourages category templates | `design-harness` registers + dials |
| `.claude/skills/🎨 디자인/ui-design-agent-skills/4-typography` | static typography recipes | `design-harness` + `design-system` tokens |
| `.claude/skills/🎨 디자인/ui-design-agent-skills/5-color` | preset palettes include old AI defaults | `design-harness` color strategy + `design-system` tokens |
| `.claude/skills/🎨 디자인/ui-design-agent-skills/6-spacing` | narrow token recipe | `design-harness` layout checks + `design-system` |
| `.claude/skills/🎨 디자인/ui-design-agent-skills/7-motion` | old Framer Motion presets, bounce/elastic defaults | `design-harness/references/motion-interaction.md` |
| `.claude/skills/🎨 디자인/ui-design-agent-skills/8-primitives` | component implementation overlaps `ui-styling` | `ui-styling` |
| `.claude/skills/🎨 디자인/ui-design-agent-skills/9-patterns` | atomic pattern catalog encourages generic assembly | `design-harness` + `ui-styling` |
| `.claude/skills/🎨 디자인/ui-design-agent-skills/10-effects` | gradient mesh/glass/neumorphism defaults are AI tells | `design-harness` anti-slop rules |
| `.claude/skills/🎨 디자인/ui-design-agent-skills/11-interactions` | overlaps motion/interaction craft | `design-harness` motion reference |
| `.claude/skills/🎨 디자인/ui-design-agent-skills/12-landing` | centered hero, gradient, badge, trust-in-hero examples are stale | `design-harness` brand register |
| `.claude/skills/🎨 디자인/ui-design-agent-skills/13-dashboard` | dashboard advice should route through product register | `design-harness` product register |
| `.claude/skills/🎨 디자인/ui-design-agent-skills/14-content` | content-page recipes overlap brand/content workflows | `design-harness` brand register + content skills |
| `.claude/skills/🎨 디자인/ui-design-agent-skills/15-mobile` | mobile app rules overlap platform/dev skills | `design-harness` + Flutter/Next.js skills |
| `.claude/skills/🎨 디자인/ui-design-agent-skills/16-accessibility` | keep concepts, but active route should be audit/harden | `design-harness` harden/audit |
| `.claude/skills/🎨 디자인/ui-design-agent-skills/17-responsive` | active route should be harden/adapt | `design-harness` harden/adapt |
| `.claude/skills/🎨 디자인/ui-design-agent-skills/18-performance` | active route should be frontend performance skills | `design-harness` harden + framework performance skill |

## Agent / Routing Changes

| File | Change |
|---|---|
| `.claude/rules/common/agent-orchestration.md` | Design auto-trigger now routes UI/UX, redesign, polish, style/color/type decisions to `design-harness` first. |
| `.claude/skills/design/ROUTING.md` | Design routing matrix now treats `design-harness` as primary and removes `ui-ux-pro-max`/`design-craft` as active options. |
| `.claude/agents/🎨 디자인/ui-design-agent/ui-design-agent-unified.md` | Agent now uses `design-harness` flow instead of old phase skill chain. |

## Follow-Up Cleanup

1. Delete `.claude/archive/skills/design/ui-design-agent-skills-legacy-260529/` after the recovery window if no user asks for those old templates.
2. Delete `.claude/archive/skills/design/legacy-entrypoints-260529/` after the recovery window if the old CSV lookup is not needed.
3. Add more deterministic checks to `design-harness/scripts/detect-design-slop.mjs` as real failures appear.
