# Design References

Use this file when the user asks to use a known product, brand, website, or "best-in-class" company as visual reference. The goal is reference translation, not cloning.

Research basis: public DESIGN.md-style analyses from getdesign.md and the VoltAgent awesome-design-md collection. Treat those sources as inspiration snapshots, not official design systems.

## Operating Rule

Always separate identity from grammar.

- Identity: logos, marks, exact brand colors, proprietary illustration styles, product screenshots, trademarked UI chrome, copy lines, and recognizable page compositions. Do not borrow these.
- Grammar: density, color role strategy, type hierarchy, radius/shadow discipline, layout rhythm, product evidence strategy, state treatment, component affordances, and motion posture. Borrow and translate these.

When a reference is used, output a short reference stance before design work:

```text
Reference stance:
- Primary reference: <brand/product>
- Secondary reference: <brand/product or none>
- Anti-reference: <style to avoid>
- Borrow: <3-5 transferable grammar traits>
- Do not borrow: <brand-specific traits that must not be copied>
```

If the user names a brand, still decide whether it is suitable for the product, audience, and scene. If it is not, keep it as secondary or anti-reference and explain the mismatch briefly.

## Selection Protocol

1. Pick by job, not taste.
   - Product surfaces need references with repeated-use affordances.
   - Brand surfaces need references with a memorable first impression.
   - Design-system work needs references with token discipline and component rules.
2. Pick one primary reference.
   - More than one primary usually creates a diluted interface.
3. Pick one secondary reference only to solve a missing dimension.
   - Example: Linear for dark product craft plus Stripe for financial form rigor.
4. Pick one anti-reference.
   - This blocks the obvious template path, such as "generic purple AI SaaS".
5. Translate into local tokens.
   - Never paste a brand palette unchanged unless the user owns that brand.
   - Prefer semantic roles: `accent`, `canvas`, `surface`, `hairline`, `ink`, `muted`, `focus`, `danger`.

## Reference Output Checklist

Every reference-driven design decision should leave these notes in the plan or review:

- Surface type: product, brand, design-system, or asset.
- Reference stance.
- Borrowed principles.
- Forbidden traits.
- Token translation.
- Component translation.
- Validation method: screenshot, responsive check, contrast check, interaction-state check.

## Developer Tools And Platforms

Use these for devtools, infrastructure, deployment, CLI, docs, API platforms, issue trackers, and technical dashboards.

### Linear

Best for: issue trackers, planning tools, engineering dashboards, focused SaaS app shells, technical landing pages with high product credibility.

Borrow:

- Near-black craft surface with restrained contrast.
- One chromatic accent used for focus, selection, and high-intent CTAs.
- Hairline borders, charcoal panels, and precise spacing instead of heavy shadows.
- Product screenshots and real interface evidence as the visual proof.
- Dense but calm information hierarchy.

Do not borrow:

- Exact lavender-blue identity color.
- Linear logo geometry, exact dark canvas, or page composition.
- Excessive darkness for non-technical audiences.

Dial suggestion: `DISTINCTION 7`, `MOTION 3`, `DENSITY 7`, `EVIDENCE 9`, `SYSTEMNESS 8`.

### Vercel

Best for: developer platforms, deployment, API docs, build systems, product launches where precision and speed matter.

Borrow:

- Stark black/white precision with a neutral surface ladder.
- Monospace labels for technical metadata.
- Strong typographic hierarchy with minimal decorative chrome.
- Documentation-like structure paired with polished marketing confidence.
- Sparse accent usage for links, status, and focused calls to action.

Do not borrow:

- Triangle mark, exact Geist/brand treatment, or signature gradient system as decoration.
- Overusing gradient bands on pages that do not have launch-stage energy.

Dial suggestion: `DISTINCTION 6`, `MOTION 3`, `DENSITY 6`, `EVIDENCE 9`, `SYSTEMNESS 8`.

### Raycast

Best for: command palettes, launchers, productivity tools, AI command surfaces, extension marketplaces.

Borrow:

- Interface-as-marketing: show real command surfaces instead of abstract art.
- Compact keyboard-first component grammar.
- Dark monochrome chrome with tiny saturated accents only inside product objects.
- Tight radius, thin borders, and fast interaction feedback.
- Feature discovery through tiles, commands, and store-like rows.

Do not borrow:

- Exact red stripe motif, logo shape, or Raycast command palette clone.
- Hover-only discovery for mobile or accessibility-critical flows.

Dial suggestion: `DISTINCTION 6`, `MOTION 4`, `DENSITY 8`, `EVIDENCE 9`, `SYSTEMNESS 8`.

### Warp

Best for: terminals, AI coding tools, developer environments, workflow automation, command runners.

Borrow:

- Warm charcoal rather than cold black.
- Terminal and editor screenshots as primary evidence.
- Understated CTAs and compact geometry.
- Calm technical tone with a small editorial accent when needed.
- Section rhythm that lets code/product surfaces do the work.

Do not borrow:

- Decorative terminal windows without actual product content.
- Serif accents unless the product has an editorial or educational need.

Dial suggestion: `DISTINCTION 5`, `MOTION 3`, `DENSITY 7`, `EVIDENCE 9`, `SYSTEMNESS 8`.

### HashiCorp

Best for: multi-product platforms, enterprise infrastructure, security/devops suites, modular product families.

Borrow:

- Per-product accent taxonomy under one neutral system.
- Enterprise dark surfaces with strict token roles.
- Product cards that make modularity obvious.
- Confident technical hierarchy and structured comparison.
- Accent colors as identity tokens, not random decoration.

Do not borrow:

- Exact product colors or HashiCorp product architecture names.
- Too many accents on one screen without a clear taxonomy.

Dial suggestion: `DISTINCTION 6`, `MOTION 2`, `DENSITY 7`, `EVIDENCE 9`, `SYSTEMNESS 9`.

### ClickHouse

Best for: data infrastructure, analytics engines, database tools, performance dashboards.

Borrow:

- High-contrast black/yellow brand voltage with very scarce accent use.
- Code blocks and product fragments embedded directly in dark surfaces.
- Stat numbers and performance claims with tabular precision.
- Technical documentation density.
- Single-accent confidence.

Do not borrow:

- Hazard-tape yellow/black overload.
- Unsupported performance numbers or fake benchmark visuals.

Dial suggestion: `DISTINCTION 6`, `MOTION 2`, `DENSITY 8`, `EVIDENCE 10`, `SYSTEMNESS 9`.

## AI Products And Creative Tools

Use these for AI assistants, coding copilots, model labs, voice/video generation, creative tooling, and prompt-heavy products.

### Claude

Best for: human-centered AI assistants, writing tools, research copilots, calm productivity agents.

Borrow:

- Warm editorial canvas that rejects cold AI-tech defaults.
- Serif or humanist display type for approachable intelligence.
- Coral/warm accent as a humane primary action.
- Dark product surfaces embedded inside warm content pages.
- Generous explanation and careful information hierarchy.

Do not borrow:

- Anthropic mark, exact coral/cream pairing, or radial logo motifs.
- Warmth that makes a technical product feel slow or soft.

Dial suggestion: `DISTINCTION 7`, `MOTION 3`, `DENSITY 5`, `EVIDENCE 8`, `SYSTEMNESS 6`.

### Cursor

Best for: AI coding tools, code editors, developer workflow agents, task automation.

Borrow:

- Warm cream editorial canvas instead of default dark IDE.
- Code surfaces as major visual anchors.
- One strong CTA accent and a separate status/timeline palette.
- Thin hairlines, minimal shadows, and long-scroll product explanation.
- Task-state color semantics for thinking, reading, editing, searching, done.

Do not borrow:

- Exact orange identity color or code editor chrome.
- Pastel timeline colors without real workflow states.

Dial suggestion: `DISTINCTION 6`, `MOTION 4`, `DENSITY 7`, `EVIDENCE 9`, `SYSTEMNESS 7`.

### Mistral AI

Best for: model labs, frontier AI research, technical AI platforms with institutional confidence.

Borrow:

- Warm scientific palette instead of purple/blue AI defaults.
- Structured bands and section closers that make a long page feel intentional.
- Editorial display paired with technical code surfaces.
- Mature warmth for AI without becoming consumer-soft.

Do not borrow:

- Mountain/sunset imagery unless it belongs to the brand story.
- Warm gradients used as generic AI atmosphere.

Dial suggestion: `DISTINCTION 7`, `MOTION 3`, `DENSITY 5`, `EVIDENCE 8`, `SYSTEMNESS 6`.

### xAI

Best for: research labs, frontier AI, high-authority announcements, minimal technical brands.

Borrow:

- Strict near-black canvas with high restraint.
- White outline/pill controls and sparse warm accent moments.
- Monospace captions for technical legitimacy.
- Large, quiet type and negative space.

Do not borrow:

- Empty black hero with no product proof.
- Cosmic gradients or "frontier" language without substance.

Dial suggestion: `DISTINCTION 6`, `MOTION 2`, `DENSITY 4`, `EVIDENCE 8`, `SYSTEMNESS 6`.

### Runway

Best for: creative AI, video tools, media platforms, galleries, creator portfolios.

Borrow:

- Cinematic photographic evidence as the core visual asset.
- Editorial gallery pacing with generous air.
- Monochrome chrome so media carries the color.
- Hairline dividers and program-like typography.
- Primary actions that do not compete with visuals.

Do not borrow:

- Stock-like atmosphere without actual work examples.
- Film-festival pacing for operational tools.

Dial suggestion: `DISTINCTION 8`, `MOTION 5`, `DENSITY 3`, `EVIDENCE 9`, `SYSTEMNESS 5`.

### ElevenLabs

Best for: voice AI, audio tools, narrative media, creator products that need calm trust.

Borrow:

- Print-magazine posture with light display weights.
- Photographic or atmospheric proof rather than saturated CTA color.
- Quiet off-white surfaces and subtle dark pills.
- Audio/storytelling examples as the asset layer.
- Low-chrome navigation.

Do not borrow:

- Decorative orbs as generic AI color moments.
- Thin typography where readability is already difficult.

Dial suggestion: `DISTINCTION 7`, `MOTION 4`, `DENSITY 4`, `EVIDENCE 9`, `SYSTEMNESS 6`.

## Fintech, Trust, And Commerce

Use these for payments, pricing, checkout, banking, marketplaces, B2B finance, and trust-critical conversion.

### Stripe

Best for: B2B payments, financial infrastructure, pricing, checkout, billing, API-first products.

Borrow:

- Financial form rigor and clear hierarchy around money.
- Tabular numerals for pricing, rates, usage, and invoices.
- Light marketing canvas with a dark app/dashboard polarity when needed.
- Tight pill buttons and disciplined card surfaces.
- Technical copy that connects product capability to business outcomes.

Do not borrow:

- Signature gradient mesh as a shortcut.
- Exact indigo palette, angled gradient bands, or Stripe-like dashboard clone.

Dial suggestion: `DISTINCTION 6`, `MOTION 3`, `DENSITY 7`, `EVIDENCE 10`, `SYSTEMNESS 9`.

### Wise

Best for: consumer fintech, international money, pricing transparency, comparison tools.

Borrow:

- Friendly high-contrast display typography.
- Vivid accent used for confidence and clarity.
- Plain-language fee and comparison modules.
- Rounded cards on lightly tinted surfaces.
- Consumer trust without bank-like stiffness.

Do not borrow:

- Exact lime identity.
- Oversized type where users need dense financial comparison.

Dial suggestion: `DISTINCTION 7`, `MOTION 3`, `DENSITY 5`, `EVIDENCE 9`, `SYSTEMNESS 9`.

### Revolut

Best for: consumer finance apps, cards, accounts, mobile-first financial products.

Borrow:

- Product objects as hero evidence: cards, phones, terminals, app views.
- Strong black/off-white polarity with consumer-grade polish.
- Rounded product cards and pill CTAs.
- Accent colors tied to product categories.
- App-store-like clarity for features and plans.

Do not borrow:

- Over-saturated product palette without category rules.
- Black luxury treatment that hides trust and fee details.

Dial suggestion: `DISTINCTION 6`, `MOTION 4`, `DENSITY 5`, `EVIDENCE 9`, `SYSTEMNESS 8`.

### Mastercard

Best for: enterprise commerce, partner ecosystems, trust networks, multi-stakeholder services.

Borrow:

- Warm annual-report canvas.
- Oversized radius and circular relationship diagrams.
- Orbit/trajectory metaphors for networks and ecosystem flows.
- Editorial trust language instead of aggressive fintech conversion.
- Strong but warm footer and institutional sections.

Do not borrow:

- Mastercard red/yellow circles, orbital paths too close to the brand mark, or exact nav shape.
- Extreme radius on dense operational UI.

Dial suggestion: `DISTINCTION 8`, `MOTION 4`, `DENSITY 4`, `EVIDENCE 9`, `SYSTEMNESS 8`.

### Apple

Best for: hardware, polished product launches, app showcases, object-focused marketing, visual inspection.

Borrow:

- Product-first layout where chrome recedes.
- Large photography or real screenshots as the main proof.
- Alternating light/dark product tiles when each tile has a real subject.
- Single blue interaction color and clean copy hierarchy.
- Museum-like spacing around hero objects.

Do not borrow:

- SF Pro + Apple blue + tile layout as a direct clone.
- Minimalism that leaves the product value unexplained.

Dial suggestion: `DISTINCTION 7`, `MOTION 4`, `DENSITY 3`, `EVIDENCE 10`, `SYSTEMNESS 8`.

### Airbnb

Best for: marketplaces, travel, local services, booking/search, human-centered commerce.

Borrow:

- Photography-first cards and friendly search/filter affordances.
- Soft radius and human spacing.
- One confident brand accent for primary search/booking action.
- Marketplace taxonomy with clear tabs and badges.
- Trust through real listings, ratings, and availability states.

Do not borrow:

- Exact pink/red accent or Airbnb search bar shape.
- Friendly marketplace chrome for serious enterprise workflows.

Dial suggestion: `DISTINCTION 6`, `MOTION 4`, `DENSITY 6`, `EVIDENCE 10`, `SYSTEMNESS 8`.

## Productivity, Collaboration, And SaaS Workflows

Use these for documents, databases, scheduling, collaboration, analytics, email, design tools, and work operating systems.

### Notion

Best for: docs, notes, knowledge bases, lightweight workspaces, editable content systems.

Borrow:

- Paper-calm canvas and low chrome.
- Page-like hierarchy with clear blocks and quiet controls.
- Playful illustration or sticker palette only as personality accents.
- Strong empty states and content-first affordances.
- Simple blue action/link semantics.

Do not borrow:

- Exact Notion page chrome, emoji-heavy identity, or black-on-white clone.
- Over-minimal UI where workflow needs explicit controls.

Dial suggestion: `DISTINCTION 5`, `MOTION 2`, `DENSITY 6`, `EVIDENCE 9`, `SYSTEMNESS 8`.

### Airtable

Best for: workflow builders, databases, spreadsheet hybrids, no-code operations tools.

Borrow:

- Sober white workspace with editorial explainer sections.
- Grid/card hybrid thinking.
- Signature color blocks to separate major workflow concepts.
- Near-black primary actions and outlined secondary actions.
- Modest typography that supports repeated work.

Do not borrow:

- Random coral/green/navy blocks without information architecture.
- Spreadsheet UI that hides object relationships.

Dial suggestion: `DISTINCTION 6`, `MOTION 3`, `DENSITY 8`, `EVIDENCE 10`, `SYSTEMNESS 9`.

### Superhuman

Best for: email, inboxes, speed-focused productivity, premium workflow tools.

Borrow:

- Speed as the core story, proven through UI moments.
- Premium editorial dark hero paired with sober white product/pricing sections.
- Dense settings, shortcuts, and workflow proof.
- Tight rectangular buttons and clean pricing modules.
- High-performance tone without noisy effects.

Do not borrow:

- Luxury newsletter feel for collaborative admin products.
- Atmospheric hero if the speed workflow is not demonstrated.

Dial suggestion: `DISTINCTION 6`, `MOTION 5`, `DENSITY 7`, `EVIDENCE 9`, `SYSTEMNESS 8`.

### Figma

Best for: design tools, collaborative creation, canvases, visual editors, plugin ecosystems.

Borrow:

- Black/white structural frame with color reserved for collaboration or creation states.
- Large color blocks as functional stage-setting, not decoration.
- Canvas/tooling metaphors and visible artifacts of work.
- Flexible section rhythm that avoids equal-card monotony.
- Joyful technical tone.

Do not borrow:

- Figma logo colors, exact pill CTAs, or sticky-note panels as a gimmick.
- Color blocks without interaction or creation meaning.

Dial suggestion: `DISTINCTION 8`, `MOTION 5`, `DENSITY 6`, `EVIDENCE 10`, `SYSTEMNESS 8`.

### PostHog

Best for: open-source devtools, analytics, docs-heavy products, playful but technical SaaS.

Borrow:

- Friendly cream canvas with technical data embedded in credible UI cards.
- Mascot/illustration as marginalia, not the main product.
- Docs and analytics surfaces coexisting on one page.
- Yellow-orange CTA accent with restrained usage.
- Hand-drawn warmth around serious engineering content.

Do not borrow:

- Mascot insertion when the product has no illustrated brand system.
- Cream/yellow developer-tool cliche without real personality.

Dial suggestion: `DISTINCTION 7`, `MOTION 3`, `DENSITY 7`, `EVIDENCE 10`, `SYSTEMNESS 8`.

### Sentry

Best for: monitoring, debugging, observability, reliability tooling, incident workflows.

Borrow:

- Severity-aware dark/light polarity.
- Chunky display personality balanced by readable UI copy.
- Lime/pink/violet accents tied to state, alert, and illustration systems.
- Pricing and docs surfaces with strong contrast.
- Slightly subversive developer tone when brand permits it.

Do not borrow:

- Purple dark mode as generic devtool styling.
- Sticker/mascot attitude for regulated or enterprise-conservative buyers.

Dial suggestion: `DISTINCTION 7`, `MOTION 3`, `DENSITY 8`, `EVIDENCE 10`, `SYSTEMNESS 9`.

## Common Reference Bundles

Use these bundles as starting points, then adjust to the product.

| Job | Primary | Secondary | Anti-reference |
|---|---|---|---|
| AI coding assistant | Cursor | Raycast | Generic purple AI SaaS |
| AI writing/research assistant | Claude | Notion | Cold dark terminal AI |
| Developer dashboard | Linear | Vercel | Decorative cyberpunk console |
| Infrastructure landing page | HashiCorp | ClickHouse | Cloud-blue enterprise template |
| API/payment platform | Stripe | Vercel | Finance navy/gold brochure |
| Consumer fintech | Wise | Revolut | Bank-like formality |
| Marketplace/search | Airbnb | Apple | Generic ecommerce grid |
| Knowledge workspace | Notion | Airtable | Overdesigned productivity hero |
| Analytics/observability | Sentry | PostHog | Plain admin dashboard |
| Creative AI/video | Runway | ElevenLabs | Purple AI gradient deck |
| Product launch page | Apple | Vercel | Centered SaaS hero with cards |
| Multi-product suite | HashiCorp | Airtable | Unstructured color buffet |

## Translation Examples

### From Brand Reference To Local System

Bad:

```text
Use Stripe's gradient, Stripe-like buttons, and a dashboard like Stripe.
```

Good:

```text
Use Stripe as a financial-infrastructure reference. Borrow tabular numeric rigor, light marketing surfaces, tight pill CTAs, and dark dashboard polarity. Translate the accent into our existing primary token and avoid Stripe's exact gradient treatment.
```

### From Product Reference To Component Rules

Bad:

```text
Make it like Linear.
```

Good:

```text
Use Linear for product craft: dense charcoal panels, thin borders, one accent for selection/focus, screenshot-led proof, and muted supporting copy. Keep our brand color and do not recreate Linear's navigation or issue list composition.
```

### From AI Reference To Anti-Slop

Bad:

```text
Make it feel like an AI product.
```

Good:

```text
Use Claude and Cursor as anti-purple AI references. Borrow warm editorial surfaces, product/code evidence, and workflow-state colors. Avoid purple glow, glass cards, fake prompt boxes, and unsupported automation claims.
```

## When Not To Use A Big-Company Reference

Do not force these references when:

- The product is early and needs clarity more than style.
- The user has an existing brand system with stronger constraints.
- The reference would imply scale, trust, or compliance the product does not yet have.
- The target audience would read the style as imitation rather than maturity.
- The implementation cannot supply the required assets, screenshots, or data.

In those cases, use the reference as an anti-reference or reduce it to one specific rule, such as "tabular numerals like Stripe" or "single-accent discipline like Linear".
