# Design System Map

Use this when a brief may map to an official design system, component library, or operational UI pattern. Do not invent a fake design system when an official package is the expected foundation.

## Decision Principles

1. **Official beats imitation.** If users expect a known system, use the official package or explicitly explain why the local stack cannot.
2. **One system per surface.** Avoid mixing systems unless one is only an implementation primitive and the visual system remains unified.
3. **Default library state is not a design direction.** shadcn/ui, Radix, Tailwind, Material, and Bootstrap all need project-specific tokens and composition.
4. **Product UI and dashboards prioritize systemness over distinction.** Brand pages can be more authored.
5. **Aesthetic trends are not design systems.** Bento, glass, brutalism, editorial, aurora, and kinetic typography are implementation directions, not official packages.

## Official System Routing

| Brief reads as | Reach for | Notes |
|---|---|---|
| Microsoft / enterprise SaaS / Microsoft ecosystem | `@fluentui/react-components` or Fluent web components | Use Fluent tokens and accessibility patterns. |
| Google-ish product / Material admin | `@material/web` or Material 3 ecosystem | Theme via Material tokens. |
| IBM-style enterprise analytics | `@carbon/react` + `@carbon/styles` | Strong for dense enterprise/data UI. |
| Shopify admin/app surface | Polaris | Required for native Shopify admin fit. |
| Atlassian/Jira/Confluence-like product | Atlaskit + Atlassian tokens | Use for work management/productivity UI. |
| GitHub-like devtool/community/docs | Primer CSS / Primer React / Primer Brand | Primer Brand for marketing, Primer product for UI. |
| UK public-sector service | `govuk-frontend` | Trust and compliance expectations override visual novelty. |
| US public-sector service | `uswds` | Follow USWDS patterns and accessibility. |
| Fast low-risk local business MVP | Bootstrap 5.3 | Boring can be correct when speed and familiarity matter. |
| Accessible React foundation with themed primitives | Radix Themes / Radix primitives | Good when owning composition but needing robust primitives. |
| Owned modern SaaS components | shadcn/ui | Own the code. Never ship default card/button/radius/colors unchanged. |
| Dense data grid/table | TanStack Table, AG Grid, Carbon/Fluent table patterns | Do not hand-roll complex grid behavior. |
| Code editor | Monaco / CodeMirror | Do not fake an editor. |
| Charts/analytics | Recharts, Visx, ECharts, Plot, or product-standard chart library | Use real data structures and axis/legend states. |

## Aesthetic Direction Routing

| Aesthetic | Honest implementation | Guardrail |
|---|---|---|
| Bento | CSS Grid, intentional cell count, real content/assets | No empty decorative cells. |
| Glass/frosted | `backdrop-filter`, layered borders, solid fallback | Do not use as default surface language. |
| Editorial | Typography, asymmetric rhythm, strong art direction | Not for dense operational dashboards. |
| Brutalist | Raw structure, high contrast, strict type | Must still be accessible and usable. |
| Dark tech | Charcoal surfaces, restrained accent, real terminal/code evidence | Avoid neon hacker cliché. |
| Aurora/mesh | SVG or layered gradients | Do not replace product proof. |
| Kinetic typography | CSS/Motion/GSAP where justified | Reduced-motion fallback required. |
| Apple-like spatial/layered UI | Native CSS approximations and platform-aware restraint | Do not claim official Apple Liquid Glass on web. |

## shadcn/ui Customization Gate

If shadcn/ui is used, change at least these project-level choices before ship:

- Radius scale.
- Accent and focus ring tokens.
- Card surface/elevation treatment.
- Button hierarchy and press feedback.
- Typography rhythm.
- Empty/loading/error/focus states.

Detector findings for `default-shadcn-card` are review prompts that usually require customization.

## Package Check

Before recommending imports:

1. Read `package.json`.
2. Prefer existing library conventions if already established.
3. If adding a new system, ensure it does not duplicate an existing one.
4. For official docs/current API, load `official-docs-guide`.
