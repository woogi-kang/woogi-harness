# Tailwind CSS 4 Customization

This is an implementation reference, not an art-direction preset. Read project tokens and the Design Runtime contract first.

## CSS-first theme

```css
@import "tailwindcss";

@theme {
  --color-brand-50: oklch(0.97 0.02 250);
  --color-brand-500: oklch(0.58 0.18 250);
  --color-brand-900: oklch(0.28 0.10 250);
  --font-product: var(--project-font-sans);
  --spacing-workspace: 1.125rem;
  --breakpoint-wide: 90rem;
  --radius-control: 0.625rem;
}
```

Use semantic project variables with `@theme inline` when utilities should follow runtime theme changes.

```css
:root {
  --surface: oklch(0.99 0.003 250);
  --content: oklch(0.22 0.018 250);
}

.dark {
  --surface: oklch(0.17 0.014 250);
  --content: oklch(0.95 0.008 250);
}

@theme inline {
  --color-background: var(--surface);
  --color-foreground: var(--content);
}
```

## Utilities and variants

```css
@utility content-auto {
  content-visibility: auto;
}

@custom-variant busy (&[aria-busy="true"]);
@custom-variant dark (&:where(.dark, .dark *));
```

Avoid decorative glass/glow utilities, broad transitions, and default Card compositions. A utility should encode a repeated behavior/token, not a style reflex.

## Plugins and sources

```css
@plugin "@tailwindcss/typography";
@source "../node_modules/@company/ui/src";
```

- Add plugins only when the current project requires them and Tailwind 4 compatibility is verified.
- Tailwind 4 handles container queries without the retired plugin.
- Automatic source detection is the default; `@source` is for missed external packages or explicit exclusions.

## Dark mode

Use the project's existing strategy. For class-driven dark mode:

```css
@custom-variant dark (&:where(.dark, .dark *));
```

Verify every semantic role, focus, disabled, chart, and image treatment. Do not invert raster evidence with CSS filters.

## When JavaScript config remains

Tailwind 4 can load a legacy config explicitly:

```css
@config "../../tailwind.config.js";
```

This is a compatibility lane, not the generated default. Record why the plugin/theme cannot migrate, keep the scope small, and add a removal gate.

## Tailwind 3 → 4 checklist

- Replace `@tailwind base/components/utilities` with `@import "tailwindcss"`.
- Use `@tailwindcss/vite` or `@tailwindcss/postcss` instead of the legacy PostCSS plugin shape.
- Move theme values into `@theme`; keep runtime semantic variables separate.
- Review borders, rings, shadows, transforms, gradients, important modifier placement, and arbitrary variables.
- Ensure target browsers meet Tailwind 4 requirements.
- Run build, responsive/state screenshots, dark mode, and design-slop checks.

The recommended version and promotion gates live in `.claude/registry/tech-stacks/web-nextjs.yaml`.
