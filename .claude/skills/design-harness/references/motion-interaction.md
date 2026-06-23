# Motion And Interaction

Use this for `animate`, `polish`, interactions, overlays, and perceived quality.

## Animation Decision

Ask in order:

1. How often will users see this?
   - Hundreds of times/day: no animation.
   - Tens of times/day: minimal feedback only.
   - Occasional: standard transition.
   - Rare or celebratory: delight is allowed.

2. What does it communicate?
   - Feedback.
   - State change.
   - Spatial continuity.
   - Hierarchy.
   - Narrative reveal.

If the answer is only "it looks cool", remove it.

## Timing

- Button press: 100-160ms.
- Tooltip/popover/menu: 125-220ms.
- Dropdown/select: 150-250ms.
- Modal/drawer: 180-320ms.
- Marketing narrative: can be longer when it explains something.

## Easing

- Entering UI: strong ease-out.
- Moving or morphing on screen: ease-in-out or spring.
- Hover/color changes: ease.
- Constant motion: linear.
- Avoid ease-in for user-triggered entry; it feels delayed.
- Avoid bounce/elastic unless the brief is playful and low-risk.

Useful CSS curves:

```css
--ease-out-strong: cubic-bezier(0.23, 1, 0.32, 1);
--ease-in-out-strong: cubic-bezier(0.77, 0, 0.175, 1);
--ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);
```

## Component Craft

- Pressable elements need subtle active feedback: `scale(0.96)` to `scale(0.98)` or `translateY(1px)`.
- Avoid press scales below `0.95` unless the product is intentionally playful.
- Never animate from `scale(0)`. Start from `scale(0.95)` plus opacity.
- Popovers scale from their trigger. Modals stay centered.
- Tooltips should delay initially, then open instantly when moving across adjacent tools.
- Use transitions for interruptible UI. Keyframes are fine for predetermined decorative loops.
- For contextual icon swaps, animate opacity, scale, and light blur when the motion posture supports it. Reuse Motion/Framer Motion only when the project already has it; otherwise use CSS transitions.
- Skip first-render animation for default-state controls when using React presence utilities, but keep intentional page entrance sequences intact.
- Use blur sparingly to soften crossfades. Heavy blur is expensive, especially in Safari.

## Gestures

- Drag interactions need pointer capture and boundary damping.
- Swipe dismiss should consider velocity, not only distance.
- Gesture-only actions need visible alternatives.
- Multi-touch should not cause element jumps.

## Performance

- Animate `transform` and `opacity`.
- Avoid animating width, height, margin, padding, top, left.
- Avoid `transition: all` and `transition-all`; specify the properties that change.
- Use `will-change` only for observed first-frame stutter, and never as `will-change: all`.
- Avoid scroll listeners that set React state every frame.
- Use Motion values, IntersectionObserver, CSS scroll timelines, WAAPI, or GSAP ScrollTrigger when the dependency exists.
- Check `package.json` before importing Motion, GSAP, Lenis, Three.js, or any animation library.
- Provide `prefers-reduced-motion` behavior for anything more than simple hover/active feedback.

## Lottie Outputs

Use `text-to-lottie` when the deliverable is a Lottie/Bodymovin JSON file, not just an in-app transition.

- Decide the motion intent here first: feedback, state change, hierarchy, or narrative reveal.
- Then hand off mechanics to `text-to-lottie`: official `diffusionstudio/lottie` player, `public/lottie.json`, optional `public/controls.json`, Skottie slots, validation, and pinned-frame screenshots.
- Prefer concrete source geometry such as SVG paths or existing icons. Lottie generation from vague prompts tends to become generic.
- Keep Lottie assets small and purposeful. For repeated product UI, use Lottie mainly for loaders, empty states, onboarding details, or compact brand moments.
- Do not verify Lottie output only with `lottie-web` if the target harness is Skottie; Skottie support and blank-canvas failure modes differ.
