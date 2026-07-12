---
name: operational-review-queue
category: operational
dial_compatibility:
  distinction: [2, 5]
  motion: [1, 3]
  density: [7, 10]
  evidence: [8, 10]
  systemness: [7, 10]
when_to_use: "A repeated review/triage workflow where users compare records and take bulk or row actions."
not_for: "A marketing comparison table or a short settings list."
stack: ["web"]
---

# Operational Review Queue

## Visual sketch

```text
title + saved view                          primary bulk action
filters / search / result count
┌───────────────────────────────────────────────────────────┐
│ □ record     owner      changed       status      action │
│ □ …          …          …             …           …      │
│ □ …          …          …             …           …      │
└───────────────────────────────────────────────────────────┘
selection summary / pagination or continuation
```

## Props API

```ts
type ReviewQueueProps = {
  rows: ReviewRow[]
  status: "loading" | "ready" | "empty" | "error"
  selectedIds: Set<string>
  onSelectionChange(ids: Set<string>): void
  onRetry(): void
}
```

## Code sketch

```tsx
export function ReviewQueue(props: ReviewQueueProps) {
  if (props.status === "loading") return <QueueSkeleton columns={5} rows={8} />
  if (props.status === "error") return <QueueRecovery onRetry={props.onRetry} />
  if (props.status === "empty") return <QueueEmpty filtersCanReset />
  return (
    <ReviewTable
      rows={props.rows}
      selectedIds={props.selectedIds}
      onSelectionChange={props.onSelectionChange}
    />
  )
}
```

## Mobile fallback

- Preserve task priority, not every desktop column.
- Keep record identity, status, and primary action visible; move secondary metadata to disclosure.
- Bulk selection must remain operable by keyboard and touch.

## Motion variants

- `1–3`: row feedback and progress only.
- `4–7`: outside compatibility; do not animate sorting/reordering theatrically.
- `8–10`: incompatible.
- Reduced motion removes spatial row transitions.

## Dark mode

Use semantic table/header/selection/focus tokens. Status must not rely on color alone.

## Evidence requirements

- Realistic longest identifiers, partial/failed data, and permission states.
- Keyboard flow for filters, selection, row action, and recovery.
- Dense desktop and constrained mobile screenshots.
- Loading/empty/error evidence.

## Anti-patterns

- One decorative card per row.
- Hidden actions available only on hover.
- Plain color dots without labels.
- Fake-perfect metrics above the table.
- Pagination or selection state that disappears after an error.

## References

Prefer the official design system already used by the project for table, filter, focus, and bulk-action behavior.
