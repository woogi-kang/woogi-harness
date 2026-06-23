# Interface Polish

Use this for the last layer of product feel after the surface already has the right structure, copy, states, and responsive behavior.

This reference is adapted from Jakub Krehel's "Make Interfaces Feel Better" skill and article: https://jakub.kr/skills/make-interfaces-feel-better and https://jakub.kr/writing/details-that-make-interfaces-feel-better. Treat the rules as review prompts, not universal style law. Existing product tokens, accessibility, density, platform conventions, and Korean UI constraints still win.

## Text Rendering

- Use `text-wrap: balance` for short headings and titles where line balance matters.
- Use `text-wrap: pretty` for short-to-medium descriptions, captions, and card copy.
- Skip custom wrapping on long prose, code blocks, and preformatted text.
- Apply macOS font smoothing once at the root when the stack already supports it.
- Use `font-variant-numeric: tabular-nums` for changing numbers: counters, timers, prices, metrics, scoreboards, and numeric table columns.
- Verify tabular numerals in the actual font. Some fonts change numeral shape when tabular figures are enabled.

## Surface Geometry

- For tightly nested rounded surfaces, calculate radius from the inside out: outer radius should roughly equal inner radius plus the padding between them.
- Do not force concentric math when the gap is large enough that the layers read as separate surfaces.
- Align icons optically when geometric centering looks wrong. Play triangles, carets, arrows, and asymmetric icons often need a small visual correction.
- Prefer fixing icon geometry in the SVG when the correction is reusable; use local margin or padding only when it is component-specific.
- Use shadows as a depth/ring substitute for cards, buttons, popovers, menus, and other raised surfaces when it adapts better than a solid border.
- Keep real separators as borders: table grid lines, list dividers, form outlines, and dense operational boundaries.
- Add an inset 1px neutral outline to images when the edge needs definition. Use black at low opacity in light mode and white at low opacity in dark mode; do not tint image outlines with the brand accent.

## Interaction Feel

- Interactive state changes should be interruptible. Prefer transitions for hover, press, toggle, open, close, and drag states.
- Use keyframes for one-shot staged sequences, not for UI that users can reverse mid-animation.
- Split enter animation by semantic chunks when the reveal matters: title, body, actions, then optional child items.
- Make exit animation quieter than enter animation. Shorter duration, opacity, and a small fixed movement usually feel better than a dramatic full-distance exit.
- Animate contextual icon swaps with opacity, scale, and a light blur when the project already has the motion posture for it.
- If the project already uses Motion or Framer Motion, reuse it. If it does not, prefer CSS cross-fades and transitions over adding a dependency for one icon swap.
- Press feedback should be subtle. A scale around `0.96` to `0.98` or `translateY(1px)` is enough for most buttons; avoid press scales below `0.95` unless the brief is deliberately playful.
- For default-state React transitions, consider skipping first-render entrance with `initial={false}`. Do not use this when the page intentionally depends on an initial staged reveal.

## Performance And Robustness

- Do not use `transition: all` or `transition-all`. Transition only the properties that actually change.
- Animate compositor-friendly properties first: `transform`, `opacity`, and sometimes `filter`.
- Avoid animating layout properties such as `width`, `height`, `padding`, `margin`, `top`, and `left` unless there is a clear reason and the browser test confirms it feels stable.
- Use `will-change` only after seeing first-frame stutter. Limit it to properties that benefit from compositing; never use `will-change: all`.
- Respect reduced-motion settings for anything beyond small hover or press feedback.

## Hit Areas

- Visible controls can be compact, but their hit area should normally be at least 40x40px and preferably 44x44px on touch surfaces.
- Extend tiny controls with padding or pseudo-elements only when the extended area will not overlap another control.
- Do not rely on hover-only affordances on mobile or touch-heavy product surfaces.

## Review Checklist

- Headings and short copy wrap intentionally.
- Dynamic numbers do not shift when values change.
- Nested rounded surfaces look concentric where they visually touch.
- Icon buttons look optically centered, not only mathematically centered.
- Raised surfaces use depth, rings, or borders according to purpose.
- Images have defined edges when they sit on mixed or busy backgrounds.
- Interactive animations can be interrupted.
- Enter and exit motion have different intensity.
- Press feedback is present but not exaggerated.
- Transitions are property-specific.
- `will-change` is rare, specific, and justified.
- Small controls have enough hit area without colliding.
