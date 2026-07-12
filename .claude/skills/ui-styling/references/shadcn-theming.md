# shadcn/ui + Tailwind 4 Theming

Use this only when shadcn/ui is already present or the design contract selects it. shadcn components are source code and accessible primitives; their default appearance is not the project's design identity.

## Theme ownership

1. Keep product semantic variables independent from Tailwind utility names.
2. Map them with Tailwind 4 `@theme inline`.
3. Customize copied component source against the Design Read and project tokens.
4. Verify every state and dark/light mode with actual screenshots.

```css
@import "tailwindcss";
@custom-variant dark (&:where(.dark, .dark *));

:root {
  --surface-canvas: oklch(0.985 0.004 250);
  --surface-control: oklch(1 0 0);
  --content-primary: oklch(0.22 0.018 250);
  --content-secondary: oklch(0.49 0.018 250);
  --action-primary: oklch(0.56 0.16 250);
  --action-primary-content: oklch(0.99 0.003 250);
  --stroke-control: oklch(0.88 0.012 250);
  --focus-ring: oklch(0.67 0.15 250);
  --shape-control: 0.625rem;
}

.dark {
  --surface-canvas: oklch(0.16 0.014 250);
  --surface-control: oklch(0.21 0.016 250);
  --content-primary: oklch(0.95 0.008 250);
  --content-secondary: oklch(0.72 0.018 250);
  --action-primary: oklch(0.7 0.14 250);
  --action-primary-content: oklch(0.16 0.014 250);
  --stroke-control: oklch(0.32 0.018 250);
  --focus-ring: oklch(0.76 0.13 250);
}

@theme inline {
  --color-background: var(--surface-canvas);
  --color-card: var(--surface-control);
  --color-foreground: var(--content-primary);
  --color-muted-foreground: var(--content-secondary);
  --color-primary: var(--action-primary);
  --color-primary-foreground: var(--action-primary-content);
  --color-border: var(--stroke-control);
  --color-ring: var(--focus-ring);
  --radius-control: var(--shape-control);
}
```

The values are structural examples, not a palette preset. Replace them with measured project tokens.

## Theme provider

If the project already uses `next-themes`, keep its established provider and hydration strategy. For a new class-driven setup, ensure the server-rendered root, stored preference, and system preference do not flash contradictory themes. A toggle needs an accessible name, visible focus, and deterministic state after hydration.

```tsx
<button
  type="button"
  aria-label="색상 모드 전환"
  aria-pressed={resolvedTheme === "dark"}
  onClick={toggleTheme}
  className="min-h-11 min-w-11 rounded-control focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
>
  <ThemeIcon aria-hidden="true" />
</button>
```

Do not animate icons with broad `transition-all`; target opacity/transform and respect reduced motion.

## Component variants

Keep behavior states explicit.

```tsx
const actionVariants = cva(
  "inline-flex min-h-11 items-center justify-center rounded-control px-4 text-sm font-medium focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      intent: {
        primary: "bg-primary text-primary-foreground hover:opacity-92",
        secondary: "border border-border bg-card text-foreground",
        danger: "bg-destructive text-destructive-foreground",
      },
      pending: { true: "cursor-wait" },
    },
  },
)
```

Default shadcn Card/Button radius, border, and shadow must be reviewed rather than shipped unchanged. Avoid nesting cards without an information boundary.

## Multiple themes

Additional themes must represent a real brand/product mode, not palette shuffle.

```css
[data-theme="partner"] {
  --action-primary: var(--partner-action-primary);
  --focus-ring: var(--partner-focus-ring);
}
```

Every theme must pass contrast, focus, disabled, destructive, charts, images, and state screenshots. If only light/dark is required, do not add a theme framework.

## Verification

- Tailwind 4 build and source detection.
- No Tailwind 3 directives or implicit JavaScript config dependency.
- Keyboard/focus, hydration, stored/system preference.
- Default/loading/error/disabled states.
- Light/dark screenshots at planned viewports.
- `detect-design-slop.mjs` on changed UI source.
