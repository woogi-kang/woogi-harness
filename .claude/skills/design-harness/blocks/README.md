# Design Harness Block Library Contract

Blocks are reusable, reviewed UI patterns. They are not templates to paste blindly. Use them when a surface needs a proven structure and the design read/dials match the block.

## Directory Plan

```text
blocks/
  hero/
  feature/
  social-proof/
  pricing/
  cta/
  navigation/
  footer/
  transition/
  portfolio/
  operational/
  states/
```

## Required Frontmatter

```yaml
---
name: product-proof-hero
category: hero
dial_compatibility:
  distinction: [4, 8]
  motion: [2, 6]
  density: [3, 6]
  evidence: [7, 10]
  systemness: [4, 9]
when_to_use: "Landing pages where the product proof is more persuasive than abstract brand art."
not_for: "Pure editorial campaigns or dashboards where a hero is not the primary task."
stack: ["react", "next", "tailwind"]
---
```

## Required Body Sections

1. **Visual sketch** - short ASCII or layout description.
2. **Props API** - component interface or content contract.
3. **Code sketch** - minimal working implementation, not pseudo-code.
4. **Mobile fallback** - explicit rules for `< 768px`.
5. **Motion variants** - one variant per `MOTION` band: 1-3, 4-7, 8-10. Include reduced-motion fallback.
6. **Dark-mode notes** - token strategy specific to this block.
7. **Evidence requirements** - what image/data/screenshot/proof must be supplied.
8. **Anti-patterns** - common ways the block becomes slop.
9. **References** - real examples in production when available.

## Discipline

- One block per file.
- Every block must work standalone.
- Every block must pass `preflight.md`.
- Blocks depending on an official design system live under `<category>/<name>--<system>.md`.
- Do not add a block that only changes decoration. Blocks must solve layout, comprehension, evidence, or interaction.
- Every active block must name its platform in `stack` and its evidence requirements. Web snippets are not silently translated into Flutter, or vice versa.
- Reviewed starting points currently include `hero/product-proof-hero.md`, `operational/review-queue.md`, and `states/recoverable-state-panel-flutter.md`.
