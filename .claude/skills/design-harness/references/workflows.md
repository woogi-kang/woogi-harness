# Workflows

Use this file to choose the right operating mode. Implementation workflows create a `design-run-v3`, start with a project fingerprint and Design Read, then end with hashed evidence, an independent critic, and the relevant gate from `preflight.md`.

## Shape

Use before code when direction or scope is unclear.

Output:

- Design read.
- Register and five dial values.
- Main slop risk and anti-reference.
- Reference stance when a brand, product, site, or proven design direction is relevant.
- Surface map: sections/screens/components.
- Visual stance and anti-goals.
- Key assets/evidence needed.
- System decision: official DS, local tokens, or bespoke.
- Open questions limited to blockers.
- Validation method.

Do not create a long generic design brief when a compact plan is enough.

## Craft

Use when building a page/screen/component.

Steps:

1. Inspect existing stack, tokens, components, package dependencies, and representative surfaces.
2. Create a design run with fingerprint, Design Read, five dials, routes/states/viewports, and main slop risk.
3. Read `design-system-map.md` when an official system may apply.
4. Translate borrowed reference grammar into local tokens, components, and layout rules.
5. Identify the one visual idea or product usability goal.
6. Implement with the detected Web/Flutter adapter and existing primitives.
7. Add necessary states, accessibility, and responsive behavior.
8. Run the JSON detector and project build/analyze/test.
9. Capture and hash route/state/viewport evidence.
10. Obtain an independent evidence-linked critic result; repair at most twice.
11. Run the register-specific executable eval and final preflight.
12. Report local `ready_for_external_promotion`; use `passed` only after an authenticated external provider/orchestrator records the promotion.

## Measure

Use when a concrete URL, screenshot, or product reference should inform local tokens or styling.

Steps:

1. Read `references/reference-style-extraction.md`.
2. Capture source evidence: CSS, computed styles, screenshots, or clearly marked visual estimates.
3. Produce a compact `design.md` with token roles, provenance, transfer rules, and do-not-borrow guardrails.
4. Choose apply level:
   - `L1 tokens`: typography scale, spacing, color roles, radius, shadows.
   - `L2 style`: tokens plus component treatment and state styling.
   - `L3 redesign`: layout/IA changes only with explicit approval.
5. Map reference grammar into the current project's tokens/components.
6. Verify the result does not copy brand identity, proprietary art, exact layout, or trademarked chrome.

## Audit

Use for review without immediately rewriting.

Lead with:

| Before | After | Why |
|---|---|---|

Prioritize:

1. Broken usability or accessibility.
2. Layout/responsive failures.
3. Missing states.
4. AI slop signatures.
5. Evidence gaps.
6. Visual polish.

Include gate status:

- Detector run or not applicable.
- Screenshot/browser QA if performed.
- Highest-risk preflight failures.

## Polish

Use after a surface exists and mostly works.

Order of operations:

1. Fix readability and contrast.
2. Fix spacing rhythm and hierarchy.
3. Remove generic filler elements.
4. Replace fake evidence with real screenshots/data/assets or remove the claim.
5. Add or correct interaction states.
6. Apply interface polish: text wrapping, dynamic numerals, optical alignment, radius math, image edges, hit areas, and transition specificity.
7. Improve assets and copy.
8. Tune motion only where it communicates.
9. Run detector and preflight.

## Redesign

Use for existing projects. Read `redesign-protocol.md` first.

1. Detect mode: greenfield, preserve, evolve, or overhaul.
2. Inventory current font, palette, radius, shadows, spacing, icon set, section patterns, routes, forms, legal/SEO/analytics-sensitive elements.
3. Pick primary, secondary, and anti-reference if outside direction is needed.
4. List top 5 slop signatures and top 5 trust/usability issues.
5. Fix in low-risk order: typography, spacing, color tokens, component states, surface geometry, key-section recomposition, evidence, motion.
6. Preserve URL structure, form field names, legal copy, analytics hooks, and product behavior unless explicitly requested.
7. Run detector, browser QA when possible, and final preflight.
8. Register comparable baseline/result artifacts, obtain an independent critic result, and run the register-specific eval.

## Harden

Use before ship.

- Text overflow and longest words.
- Empty/loading/error/disabled/focus states.
- Keyboard and screen-reader access.
- Reduced motion.
- Mobile nav and touch targets.
- Image dimensions and CLS.
- Transition hygiene and `will-change` usage.
- Dynamic numeric alignment.
- i18n and Korean line breaking where relevant.
- Dark/dual-mode parity where relevant.
- Detector and final preflight.
