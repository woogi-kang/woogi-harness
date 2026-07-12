# Design Routing Guide

When to use each design sub-skill.

## Skill Overview

| Skill | Purpose | Key Files |
|-------|---------|-----------|
| design-harness | UI/UX direction, redesign, audit, polish, anti-slop, visual QA | SKILL.md + references + detector script |
| brand | Brand identity, voice, assets | SKILL.md + 10 references + 3 scripts |
| design-system | Token architecture, specs | SKILL.md + 7 references + 2 scripts |
| ui-styling | Component implementation | SKILL.md + 7 references + 2 scripts |
| logo-design | AI logo generation (55 styles, 30 palettes) | SKILL.md + 4 references + 2 scripts |
| cip-design | Corporate Identity Program (50 deliverables) | SKILL.md + 3 references + 3 scripts |
| slides | HTML presentations with Chart.js | SKILL.md + 4 references |
| banner-design | Banners for social, ads, web, print (22 styles) | SKILL.md + 1 reference |
| icon-design | Gongnyang C9 raster 또는 deterministic SVG artifact | SKILL.md + 1 reference + 1 script |

## Routing by Task Type

### Brand Identity Tasks
**→ brand**

- Define brand colors and typography
- Create logo usage guidelines
- Establish brand voice and tone
- Organize and validate assets
- Create messaging frameworks
- Audit brand consistency

### Token System Tasks
**→ design-system**

- Create design tokens JSON
- Generate CSS variables
- Define component specifications
- Map tokens to Tailwind config
- Validate token usage in code
- Document state and variants

### Implementation Tasks
**→ ui-styling**

- Add shadcn/ui components
- Style with Tailwind classes
- Implement dark mode
- Create responsive layouts
- Build accessible components

### UI/UX Direction And Review Tasks
**→ design-harness**

- Decide UI/UX direction for pages, dashboards, apps, portfolios
- Review UX, accessibility, responsive behavior, and visual quality
- Redesign or polish existing interfaces
- Select product vs brand register
- Run anti-slop and mechanical preflight before implementation

### Logo Design Tasks
**→ logo-design**

- Compile logo concepts with `image-prompt`, then generate with Codex `gpt-image-2`
- Search logo styles, color palettes, industry guidelines
- Generate design briefs
- Explore 55+ styles (minimalist, vintage, luxury, geometric, etc.)

### Corporate Identity Program Tasks
**→ cip-design**

- Generate CIP deliverables (business cards, letterheads, signage, vehicles, apparel)
- Create CIP briefs with industry/style analysis
- Compile mockup plans with `image-prompt`, then generate with Codex `gpt-image-2`
- Render HTML presentations from CIP mockups

### Presentation Tasks
**→ slides**

- Create strategic HTML presentations
- Data visualization with Chart.js
- Apply copywriting formulas to slide content
- Use layout patterns and design tokens

### Banner Design Tasks
**→ banner-design**

- Design banners for social media (Facebook, Twitter, LinkedIn, YouTube, Instagram)
- Create ad banners (Google Ads, Meta Ads)
- Website hero banners and headers
- Print banners and covers
- 22 art direction styles (minimalist, bold typography, gradient, glassmorphism, etc.)

### Icon Design Tasks
**→ icon-design**

- Generate raster concepts through `image-prompt` or normalize existing deterministic SVG
- Batch icon variations in multiple styles
- Multi-size export (16px, 24px, 32px, 48px)
- 15 styles: outlined, filled, duotone, rounded, sharp, gradient, etc.
- 12 categories: navigation, action, communication, media, commerce, data

## Routing by Question Type

| Question | Skill |
|----------|-------|
| "What color should this be?" | brand |
| "What should this interface feel like?" | design-harness |
| "Review this landing page" | design-harness |
| "This looks AI-generated" | design-harness |
| "How do I create a token for X?" | design-system |
| "How do I build a button component?" | ui-styling |
| "Is this on-brand?" | brand |
| "Should I use a CSS variable here?" | design-system |
| "How do I add dark mode?" | ui-styling |
| "Create a logo for my brand" | logo-design |
| "Generate business card mockups" | cip-design |
| "Create a pitch deck" | slides |
| "Design brand identity package" | cip-design |
| "What logo style fits my industry?" | logo-design |
| "Design a Facebook cover" | banner-design |
| "Create ad banners for Google" | banner-design |
| "Make a website hero banner" | banner-design |
| "Generate a settings icon" | icon-design |
| "Create SVG icons for my app" | icon-design |
| "Design an icon set" | icon-design |

## Multi-Skill Workflows

### New Project Setup

```
1. design-harness → Define UI register and direction
   - Product vs brand, dials, anti-slop risks

2. brand → Define identity
   - Colors, typography, voice

3. design-system → Create tokens
   - Primitive, semantic, component

4. ui-styling → Implement
   - Configure Tailwind, add components
```

### Design System Migration

```
1. brand → Audit existing
   - Extract brand colors, fonts

2. design-system → Formalize tokens
   - Create three-layer architecture

3. ui-styling → Update code
   - Replace hardcoded values
```

### Component Creation

```
1. design-system → Reference specs
   - Button states, sizes, variants

2. ui-styling → Implement
   - Build with shadcn/ui + Tailwind
```

## Skill Dependencies

```
brand
    ↓ (colors, typography)
design-system
    ↓ (tokens, specs)
ui-styling
    ↓ (components)
Application Code
```

## Quick Commands

**Brand:**
```bash
node .claude/skills/brand/scripts/inject-brand-context.cjs
node .claude/skills/brand/scripts/validate-asset.cjs <path>
```

**Tokens:**
```bash
node .claude/skills/design-system/scripts/generate-tokens.cjs -c tokens.json
node .claude/skills/design-system/scripts/validate-tokens.cjs -d src/
```

**Components:**
```bash
npx shadcn@latest add button card input
```

## When to Use Multiple Skills

Use **all eight** when:
- Complete brand package from scratch (logo → CIP → presentation)

Use **design-harness + brand + design-system + ui-styling** when:
- Design direction, design system setup, and implementation

Use **logo-design + cip-design** when:
- Complete brand identity package with deliverable mockups

Use **logo-design + cip-design + slides** when:
- Brand pitch: generate logo, create CIP mockups, build pitch deck

Use **banner-design + brand** when:
- Social media presence: branded banners across all platforms

Use **icon-design + design-system** when:
- Custom icon set matching design tokens and component specs

Use **design-harness + brand + design-system** when:
- Defining design language without implementation

Use **design-system + ui-styling** when:
- Implementing existing brand in code
- Building component library
