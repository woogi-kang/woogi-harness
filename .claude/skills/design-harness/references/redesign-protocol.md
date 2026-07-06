# Redesign Protocol

Use this for existing projects, pages, apps, or components. Misclassifying redesign mode is the fastest way to create damage: broken IA, SEO loss, analytics regressions, inaccessible replacements, or brand drift.

## 1. Detect Mode First

| Mode | Meaning | Design behavior |
|---|---|---|
| `greenfield` | No meaningful existing UI, or explicit fresh start | Start from design read and dials. |
| `preserve` | Keep brand/IA, modernize lightly | Audit first, improve low-risk layers. |
| `evolve` | Keep product structure, improve visual language materially | Preserve IA/content contracts, change tokens/layout selectively. |
| `overhaul` | New visual language approved | Treat visuals as greenfield, but preserve content/data/legal/SEO contracts unless approved. |

If ambiguous, ask one question:

```text
Should this preserve the current brand and IA, or are we allowed to overhaul the visual language?
```

## 2. Audit Before Touching

Capture:

- **Brand tokens** - colors, fonts, logo/wordmark treatment, radius, shadows, icons.
- **Information architecture** - routes, nav labels, anchor IDs, key conversion paths.
- **Content blocks** - what is doing work, what is filler, what is legally/SEO sensitive.
- **Product behavior** - forms, filters, tables, dialogs, keyboard flows, state handling.
- **Analytics and data contracts** - event names, button labels used downstream, form field names, API payload assumptions.
- **Accessibility wins** - focus states, ARIA, landmarks, labels, contrast that must not regress.
- **Slop signatures** - top 5 visible AI/default/generic patterns.
- **Trust/usability issues** - top 5 issues affecting comprehension or task completion.

## 3. Preservation Rules

Never change silently:

- URL structure or route slugs.
- Primary nav labels.
- Form field names, order, labels, required/optional semantics.
- Legal, consent, cookie, privacy, or compliance copy.
- Brand logo or wordmark.
- Analytics event hooks and data attributes.
- Product behavior, keyboard shortcuts, permissions, or destructive action flow.
- SEO titles, meta descriptions, structured data, canonical tags, and OG cards unless the task includes SEO migration.

## 4. Modernization Levers

Apply in this order and stop when the brief is satisfied:

1. **Typography refresh** - hierarchy, line length, font pairing, tabular numbers.
2. **Spacing and rhythm** - section cadence, container widths, alignment, mobile collapse.
3. **Color recalibration** - semantic tokens, contrast, neutral family, accent consistency.
4. **Component states** - loading, empty, error, disabled, focus, hover, active.
5. **Surface geometry** - radius system, borders, shadows, image edges.
6. **Key-section recomposition** - hero, pricing, proof, feature, CTA only when structure is weak.
7. **Evidence upgrade** - replace fake/mock visuals with actual screenshots, data, maps, images, or generated assets.
8. **Motion layer** - only after structure and states are correct.
9. **Full block replacement** - only when existing block is unsalvageable.

## 5. Redesign Report Template

```markdown
## Redesign read
- Mode:
- Register:
- Dials:
- Main slop risk:

## Preserve
- IA/routes:
- Brand assets:
- Legal/SEO/analytics/forms:

## Retire
1.
2.
3.

## Change plan
| Lever | Change | Risk |
|---|---|---|

## Verification
- Detector:
- Browser/screenshot QA:
- Preflight:
```

## 6. Failure Patterns

- Replacing a working product UI with a brand landing pattern.
- Changing nav labels because the new wording sounds cleaner.
- Removing dense information that operators need every day.
- Introducing motion before fixing states and contrast.
- Copying a reference page identity instead of translating grammar.
- Hiding legal or pricing details to make the layout cleaner.
- Using new screenshots or claims that the product cannot substantiate.
