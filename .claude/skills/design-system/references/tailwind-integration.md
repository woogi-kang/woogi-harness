# Tailwind CSS 4 Design-token Integration

Use this only when the detected project already uses Tailwind or the design contract explicitly selects it. The recommended version is read from `.claude/registry/tech-stacks/web-nextjs.yaml`; this reference assumes the Tailwind 4 CSS-first model.

## Install adapter

- Vite: `tailwindcss` + `@tailwindcss/vite`.
- PostCSS/Next: `tailwindcss` + `@tailwindcss/postcss` and a PostCSS config.
- Do not add Tailwind to a project that already has a working token/styling system without approval.

## CSS-first token map

```css
@import "tailwindcss";

@custom-variant dark (&:where(.dark, .dark *));

:root {
  --surface-canvas: oklch(0.985 0.004 250);
  --surface-raised: oklch(1 0 0);
  --content-primary: oklch(0.22 0.018 250);
  --content-muted: oklch(0.48 0.02 250);
  --action-primary: oklch(0.56 0.18 250);
  --action-primary-content: oklch(0.99 0.003 250);
  --stroke-subtle: oklch(0.9 0.012 250);
  --focus-ring: oklch(0.65 0.17 250);
  --shape-control: 0.625rem;
  --motion-fast: 140ms;
  --motion-normal: 200ms;
}

.dark {
  --surface-canvas: oklch(0.16 0.014 250);
  --surface-raised: oklch(0.21 0.016 250);
  --content-primary: oklch(0.95 0.008 250);
  --content-muted: oklch(0.72 0.018 250);
  --action-primary: oklch(0.7 0.15 250);
  --action-primary-content: oklch(0.16 0.014 250);
  --stroke-subtle: oklch(0.31 0.018 250);
  --focus-ring: oklch(0.75 0.14 250);
}

@theme inline {
  --color-background: var(--surface-canvas);
  --color-surface: var(--surface-raised);
  --color-foreground: var(--content-primary);
  --color-muted-foreground: var(--content-muted);
  --color-primary: var(--action-primary);
  --color-primary-foreground: var(--action-primary-content);
  --color-border: var(--stroke-subtle);
  --color-ring: var(--focus-ring);
  --radius-control: var(--shape-control);
  --default-transition-duration: var(--motion-normal);
}
```

`@theme inline` is important when one CSS variable references another; generated utilities resolve the current semantic token rather than baking a stale primitive.

## Components

Prefer project components. If a repeated class is truly stable, Tailwind 4 still supports `@utility` and `@apply`.

```css
@utility focus-contract {
  outline: 2px solid transparent;
  outline-offset: 2px;
  &:focus-visible {
    outline-color: var(--focus-ring);
  }
}

.primary-action {
  @apply inline-flex min-h-11 items-center justify-center rounded-control bg-primary px-4 text-primary-foreground;
  transition-property: color, background-color, border-color, opacity, transform;
  transition-duration: var(--motion-fast);
}
```

Do not ship a default card/button grid as a design system. Component roles, state APIs, radius, elevation, and hierarchy still come from the product contract.

## Source detection and legacy config

Tailwind 4 detects source files automatically. Use `@source` only for packages or paths detection cannot see.

```css
@source "../node_modules/@company/ui/src";
```

Keep a JavaScript `tailwind.config.*` only when a required legacy plugin/config cannot migrate yet. Load it explicitly with `@config`; record the compatibility reason and migration gate. Tailwind 3 directives (`@tailwind base/components/utilities`) are not valid generated defaults.

## Plugin migration

CSS plugins use `@plugin` when required.

```css
@plugin "@tailwindcss/typography";
```

Container queries are native in the Tailwind 4 family; do not retain the old container-query plugin by habit. Confirm every plugin's Tailwind 4 compatibility before adding it.

## Migration gates from Tailwind 3

1. Replace three `@tailwind` directives with `@import "tailwindcss"`.
2. Use the correct Vite or PostCSS adapter package.
3. Move theme tokens to CSS-first `@theme` where possible.
4. Review changed border, ring, shadow, transform, gradient, variant, and arbitrary-value behavior.
5. Verify browser floor, build output, dark mode, content detection, and dynamic classes.
6. Run the official upgrade tool only on a clean branch and review every diff.

Do not change version numbers without these gates. See `.claude/registry/tech-stacks/migrations/web-next16-typescript7.md`.
