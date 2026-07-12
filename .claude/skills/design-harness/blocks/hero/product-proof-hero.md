---
name: product-proof-hero
category: hero
dial_compatibility:
  distinction: [4, 8]
  motion: [1, 6]
  density: [3, 6]
  evidence: [7, 10]
  systemness: [4, 9]
when_to_use: "A product or brand landing surface where a real workflow capture is the strongest proof."
not_for: "Dashboards, purely editorial campaigns, or products without a truthful capture to show."
stack: ["web"]
---

# Product Proof Hero

## Visual sketch

```text
┌───────────────────────────────────────────────────────────┐
│ brand                 two relevant links        main CTA │
│                                                           │
│ concrete promise        ┌──────────────────────────────┐  │
│ one supporting fact     │ real product capture         │  │
│ main action             │ with one annotated workflow  │  │
│ evidence provenance     └──────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
```

The proof and claim share the first fold. Do not add a decorative pill, second generic CTA, metric row, or equal feature cards.

## Props API

```ts
type ProductProofHeroProps = {
  title: string
  explanation: string
  action: { label: string; href: string }
  proof: { src: string; alt: string; caption: string; width: number; height: number }
}
```

## Code sketch

```tsx
export function ProductProofHero({ title, explanation, action, proof }: ProductProofHeroProps) {
  return (
    <header className="proofHero">
      <div className="proofHero__message">
        <h1>{title}</h1>
        <p>{explanation}</p>
        <a className="proofHero__action" href={action.href}>{action.label}</a>
      </div>
      <figure className="proofHero__proof">
        <img src={proof.src} alt={proof.alt} width={proof.width} height={proof.height} />
        <figcaption>{proof.caption}</figcaption>
      </figure>
    </header>
  )
}
```

Use project tokens/classes; names above express structure only.

## Mobile fallback

- Message precedes proof; no horizontal overflow.
- Keep the primary action visible without forcing fixed viewport height.
- Preserve readable screenshot detail; use a focused real capture rather than shrinking a desktop page into illegibility.

## Motion variants

- `1–3`: no entrance motion; interactive feedback only.
- `4–7`: short opacity/translate reveal after the image is decoded.
- `8–10`: not compatible; choose a narrative block instead.
- Always respect reduced motion and never animate screenshot scale continuously.

## Dark mode

Use project semantic surface/border/text tokens. The screenshot should have a truthful theme, not an automatic invert/filter.

## Evidence requirements

- Source and date/provenance of the capture.
- Mobile and desktop result screenshot.
- Verified image load and meaningful alt.
- Claim must be visible in or supported by the product evidence.

## Anti-patterns

- Fake browser chrome or div-drawn dashboard.
- Generic “everything you need” copy.
- Trust logos or metrics without sources.
- Gradient glow behind the capture to compensate for weak hierarchy.

## References

Use comparable production references only to study proof placement and caption discipline; do not copy their hero composition or brand chrome.
