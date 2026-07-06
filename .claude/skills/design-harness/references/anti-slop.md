# Anti-Slop Reference

Use this for implementation, review, redesign, and final QA. Slop is not just "ugly design". It is predictable model behavior: category reflexes, template layouts, generic copy, fake evidence, and missing interface rigor.

## Slop Taxonomy

| Class | Symptom | Fix route |
|---|---|---|
| Category reflex | The product category predicts the design | Design read + anti-reference |
| Layout reflex | Centered hero, pill, three equal cards, repeated splits | Layout family choice + preflight |
| Content slop | Generic verbs, fake metrics, unsupported claims | Copy self-audit |
| Evidence slop | Fake dashboards, blobs, generic avatars, empty bento | Evidence dial + real assets |
| Polish slop | Missing states, bad contrast, transition-all, tiny controls | Interface polish + detector |

## Reflex Rejection

Run both checks:

1. If the category predicts the design, reject it.
   - AI -> purple/blue glow.
   - Fintech -> navy/gold.
   - Healthcare -> white/teal.
   - Developer tool -> dark terminal.
   - Luxury/artisan -> cream/brass/espresso.
   - Korean dating/couple app -> pink hearts and stock couples.
2. If the anti-reference predicts the design, reject it too.
   - "Not purple AI" -> black neon terminal.
   - "Not SaaS cream" -> editorial serif everywhere.
   - "Not fintech navy" -> monochrome cyberpunk.

Pick the scene, audience, and brand truth. Do not pick from training-data reflex.

## Reference Translation

Borrow:

- Color roles, not exact brand palettes.
- Type hierarchy and rhythm, not proprietary font identity unless licensed.
- Density, spacing, radius, shadow discipline, and component affordances.
- Product evidence strategy: real screenshots, charts, photos, maps, command surfaces, or data views.
- Motion posture: causal feedback, editorial pacing, or gallery-like transitions.

Do not borrow:

- Logos, marks, icon silhouettes, mascot characters, proprietary illustrations, or brand photography.
- Exact page compositions, navigation structures, hero layouts, or recognizable product screenshots.
- Trademarked product names, slogans, copied value propositions, or testimonial copy.
- Brand colors in the same roles/proportions when they would read as imitation.
- Trust signals, metrics, compliance claims, or enterprise scale cues the product cannot substantiate.

Before implementation, write:

```text
Borrowed principles:
Forbidden traits:
Local translation:
```

## Hard Bans By Default

These are banned unless the brief explicitly earns them:

- Purple/blue AI gradient as main identity.
- Gradient text as primary emphasis.
- Glassmorphism as default surface language.
- Centered hero + pill badge + two CTAs + three equal feature cards.
- Identical card grids repeated across sections.
- Nested cards without a clear information hierarchy.
- Decorative side-stripe card accents.
- Hero metric template: large number + label + support stats as the main story.
- Fake screenshots made from div rectangles.
- Fake terminal/dashboard/editor UI when real product evidence is needed.
- Placeholder-only form labels.
- Decorative scroll cues.
- Decorative status dots on nav/list/badge items.
- Hero version labels unless launch status is actually the message.
- Section-number eyebrows: `00 / INDEX`, `SECTION 01`, `001 · Capabilities`.
- Generic names: John Doe, Jane Doe, Acme, Nexus, SmartFlow, Cloudly.
- Generic copy: elevate, seamless, unleash, revolutionize, next-gen, game-changing, cutting-edge.
- Fake-perfect metrics: `99.99%`, `1,000,000+`, `50% faster` without source.
- Plain-text fake logo walls.
- Long lists made only from repeated `border-t border-b` rows.
- Default shadcn card/button styling shipped unchanged.

## Layout Checks

- Hero fits the initial viewport; CTA visible without scrolling on brand/landing surfaces.
- Hero stack has at most one small cue, headline, subtext, CTA row, and optional proof element.
- Logo walls and trust strips live below the hero, not inside it.
- Desktop nav is one line and under 80px tall unless product constraints require otherwise.
- Do not repeat the same section layout family more than twice in a row.
- Bento grids have exactly the number of cells needed. No empty decorative cells.
- Multi-column layouts include explicit mobile collapse behavior.
- Use `min-h-[100dvh]`, not `h-screen`, for viewport-height sections.
- Text must not overflow containers on mobile or tablet.
- Product UI should not inherit brand-page bento or scroll-story patterns by default.

## Color Checks

- Choose a color strategy first: restrained, committed, full palette, or drenched.
- Product UI defaults to one accent.
- Brand surfaces can commit to color when identity earns it.
- Tint neutrals toward the brand or scene; do not mix warm and cool gray families randomly.
- Verify contrast for body text, buttons, helper text, placeholders, disabled states, and text over images.
- Keep one page-level theme. Do not randomly alternate light and dark sections.
- Avoid pure black and pure white as large surfaces unless the brand intentionally needs stark contrast.

## Typography Checks

- Body prose: 65-75ch max.
- Display headings: plan words, line length, and image size together.
- Avoid defaulting to Inter, Fraunces, Instrument Serif, Playfair, Space Grotesk, or IBM Plex Mono for brand work without a reason.
- Product UI may use system fonts when that improves native feel.
- Avoid all-caps body copy.
- Preserve italic descenders with line-height or padding.
- Use tabular numbers for prices, metrics, tables, and timers.
- Korean UI needs Korean-first line breaking and font evaluation. Do not judge Hangul rhythm from Latin-only references.

## Assets and Evidence

- Brand/marketing surfaces need visual proof: real or generated images, actual screenshots, component previews, maps, charts, or canvas/WebGL scenes.
- Product surfaces need state proof: real components, real data shape, realistic empty/error/loading states.
- Do not use abstract blobs, hand-rolled SVG illustrations, or fake browser windows as a substitute for a required product/place/person image.
- Verify external image URLs render.
- Give meaningful alt text for content images.
- Invented brands in logo walls need simple marks, not plain text rows.
- Do not invent customer logos, compliance claims, or investor logos.

## Interaction States

Check every user-facing flow:

- Loading: shape-matching skeleton or clear progress.
- Empty: explains the state and next action.
- Error: local, specific, recoverable.
- Disabled: visibly disabled but readable.
- Focus: keyboard-visible and high contrast.
- Mobile: touch targets 44px preferred, no hover-only affordance.
- Forms: label above input, helper text optional, error below input.
- Reduced motion: available for meaningful motion.

## Copy Self-Audit

Read every visible string before delivery. Rewrite anything that is:

- Grammatically broken.
- Cute but unclear.
- Fake-profound.
- Category-generic.
- Filled with unsupported numbers.
- Different in tone from the rest of the page.
- Over-abstract where concrete product nouns would work better.

Prefer concrete claims:

| Slop | Better direction |
|---|---|
| Seamless collaboration | Comment, assign, and resolve changes in one review room |
| Next-gen AI workflows | Turn meeting notes into dated follow-ups with source links |
| Beautiful insights | Cohort retention by signup week, plan, and activation path |
| Trusted by teams worldwide | Name the actual segment or remove the claim |
