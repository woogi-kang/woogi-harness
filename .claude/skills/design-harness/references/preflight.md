# Final Design Preflight

Use this before finalizing UI code, a redesign recommendation, or a design review. The work is not done until the relevant gate passes or the remaining risk is stated explicitly.

## 1. Context Gate

- [ ] `design-run-v3` exists for implementation/redesign work and the project fingerprint is current.
- [ ] Design Read is stated.
- [ ] Register is correct: product, brand, operational, editorial, public-sector, or campaign.
- [ ] Dials are explicit: `DISTINCTION`, `MOTION`, `DENSITY`, `EVIDENCE`, `SYSTEMNESS`.
- [ ] Main slop risk is named.
- [ ] Existing project context was inspected when available: tokens, components, package dependencies, representative UI file.
- [ ] For redesigns, mode is declared: greenfield, preserve, evolve, or overhaul.

## 2. System Gate

- [ ] Official design system decision is made when applicable.
- [ ] One design system per surface. Do not mix Fluent, Carbon, Material, Polaris, Atlaskit, shadcn defaults, and bespoke CSS without a reason.
- [ ] Token strategy is clear: CSS variables, Tailwind theme, library tokens, or local component tokens.
- [ ] Page-level theme is locked: light, dark, auto, or explicit dual mode. No random section theme flips.
- [ ] Color roles are semantic: background, surface, elevated, border, text, muted, accent, danger, success, focus.
- [ ] One radius system is applied consistently.

## 3. Slop Gate

- [ ] No category reflex: the product category alone does not predict the look.
- [ ] No default AI hero: centered hero + pill badge + two CTAs + three equal feature cards unless the brief specifically earns it.
- [ ] No repeated section layout family more than twice in a row.
- [ ] No decorative glass, glow, blob, gradient text, or mesh background as substitute for a visual idea.
- [ ] No fake screenshots, fake dashboards, fake terminals, or div rectangles pretending to be product evidence.
- [ ] No empty bento cells or decorative-only grid tiles when the section is supposed to communicate value.
- [ ] No generic names, fake-perfect metrics, or unsupported trust claims.
- [ ] Visible copy avoids vague verbs: elevate, unleash, seamless, revolutionize, next-gen, game-changing, cutting-edge.
- [ ] CTA intents are distinct. Do not duplicate the same action under different labels.

## 4. Layout Gate

- [ ] Hero fits the initial viewport when the surface is a landing/brand page.
- [ ] Primary CTA is visible without scrolling on landing/brand pages.
- [ ] Desktop nav is one line and under 80px tall unless there is a product-specific reason.
- [ ] Body prose is constrained to readable line length.
- [ ] Multi-column layouts have explicit mobile collapse behavior.
- [ ] Text does not overflow cards, buttons, nav, tables, or mobile containers.
- [ ] Long lists use an appropriate component, not lazy repeated `border-t border-b` rows by default.
- [ ] Tables and dense data use tabular numbers and robust overflow behavior.

## 5. Evidence Gate

- [ ] Evidence level matches the `EVIDENCE` dial.
- [ ] Brand/marketing surfaces include real or generated visual proof when visual proof is central to the promise.
- [ ] Product surfaces show actual components, data, charts, maps, screenshots, or states when they claim product capability.
- [ ] External images render and have meaningful alt text when content-bearing.
- [ ] Generated or placeholder assets are clearly appropriate and not misleading.

## 6. Interaction and State Gate

Check every user-facing flow that exists in scope:

- [ ] Loading state.
- [ ] Empty state.
- [ ] Error state.
- [ ] Disabled state.
- [ ] Focus-visible state.
- [ ] Hover and press states where appropriate.
- [ ] Mobile touch targets are normally at least 40x40px, preferably 44x44px.
- [ ] No hover-only affordance on touch-critical surfaces.
- [ ] Forms have labels, helper/error text, and accessible focus treatment.

## 7. Motion Gate

- [ ] Every animation has a purpose: hierarchy, feedback, spatial continuity, or narrative pacing.
- [ ] Motion intensity matches the `MOTION` dial and surface register.
- [ ] Product UI motion is interruptible and not theatrical.
- [ ] Advanced scroll/physics motion is reserved for brand/editorial surfaces that earn it.
- [ ] Reduced-motion fallback exists for meaningful motion.
- [ ] No `transition-all`; transitions target specific properties.
- [ ] `will-change` is rare, specific, and justified.

## 8. Accessibility and Robustness Gate

- [ ] Body text, muted text, buttons, inputs, placeholders, disabled states, and text over images meet contrast expectations.
- [ ] Keyboard navigation is preserved.
- [ ] Images have width/height or sizing strategy to avoid layout shift.
- [ ] Responsive states were checked for realistic breakpoints.
- [ ] Korean UI uses appropriate line breaking, font choice, and avoids awkward English literalism when Korean applies.
- [ ] Dark mode or dual mode was checked if present.

## 9. Mechanical Verification

When code exists locally:

- [ ] `detect-design-slop.mjs` was run on the focused UI paths, or the reason it could not run is stated.
- [ ] Hard-fail detector findings are fixed or explicitly waived with reason.
- [ ] Browser/screenshot QA was run when the project is runnable.
- [ ] Planned route/screen, state, and viewport artifacts are hashed in `evidence-manifest.json`.
- [ ] An external capture authority signed the canonical receipt, source fingerprint, and complete runtime-adapter evidence projection.
- [ ] Web work includes accessibility-tree/equivalent evidence; Flutter work includes analyze/test and semantics-relevant evidence.
- [ ] An independent critic cited evidence IDs and issued a decision.
- [ ] Both capture and critic attestations authenticate against an active host trust-store authority pinned for their purposes.
- [ ] Repair rounds did not exceed two.
- [ ] The register-specific executable UI eval passed; a universal originality score was not substituted.
- [ ] Local completion is reported as `ready_for_external_promotion`; `passed` is used only when an authenticated external provider/orchestrator actually recorded that promotion.
- [ ] Build/type/lint/test commands were run when they are already part of the project workflow and relevant to the change.

## Final Report Format

```markdown
## Design gate result
- Design read:
- Dials:
- Detector:
- Platform build/test:
- Route/state/viewport evidence:
- Independent critic:
- Register eval:
- Local runtime status:
- External promotion (provider/orchestrator ID or not performed):
- Fixed:
- Waivers:
- Remaining risk:
```
