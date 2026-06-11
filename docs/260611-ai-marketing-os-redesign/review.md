# AI Marketing OS Redesign Review

## Design Read

Reading this as: product operations console for 1인 창업자와 소규모 마케팅 운영자, in a weekly content planning, approval, manual publishing, and performance-learning scene, using an Account Control Room register, with dense editorial operations and evidence-first workflow UI, avoiding generic purple AI SaaS, monochrome wireframe admin, and landing-page hero/card repetition.

## Reference Stance

- Primary reference: Airtable
- Secondary reference: Raycast / Linear
- Anti-reference: generic purple AI SaaS, black-and-white wireframe admin
- Borrow: grid/card hybrid workflow, dense operational controls, source/evidence drawers, restrained single-accent discipline, command-like quick actions
- Do not borrow: Airtable's exact color identity, Raycast command-palette clone, Linear's exact dark canvas or lavender accent

## Dials

| Dial | Value | Reason |
|---|---:|---|
| DISTINCTION | 6 | More authored than admin UI, but not a brand page |
| MOTION | 3 | State continuity and view switching only |
| DENSITY | 8 | Repeated weekly operations need scanning, comparison, and queue handling |

## Current Surface Map

| PRD screen | Redesign placement | Key components |
|---|---|---|
| Account Dashboard | Dashboard view | Operating signals, priority queue, cost meter |
| Knowledge Base | Knowledge view | Knowledge table, source grade, review date |
| Content Import | Knowledge view | CSV/URL/manual import zone |
| Content DNA Report | Knowledge view | Voice, topic, hook, CTA pattern tiles |
| Hook Library | Hooks view | Hook template table, score, risk |
| Research Run | Hooks view | Weekly pattern, candidate, risk summary |
| Content Calendar | Calendar view | Week board, channel/status scheduling |
| Content Editor | Editor view | Split editor, channel preview, source drawer |
| Review Queue | Review view | Blocker table and owner action |
| Manual Publish Checklist | Review view | Approved manual publishing row |
| Performance Log | Performance view | Reaction chart, learning insights |

## Visual System

| Token role | Value | Use |
|---|---|---|
| Canvas | `#f5f6f2` | App background |
| Sidebar | `#202820` | Persistent navigation and cost context |
| Surface | `#ffffff` | Tables, panels, editor work areas |
| Line | `#d8ded0` | Hairline separation |
| Accent | `#2f674e` | Approved state and primary actions |
| Research | `#335c8a` | Research and hook discovery |
| Review | `#a35b18` | Needs review, fact check, rewrite |
| Danger | `#9f2f25` | Blocked, never publish, sensitive |

## Component Rules

- Navigation is workflow based, not marketing-section based.
- Cards are reserved for individual queue items and compact data summaries.
- Tables are the default for source, hook, review, and performance comparison.
- Every generated content surface must show source evidence and safety state next to the draft.
- `never_publish`, `sensitive`, price checks, and similarity warnings must be visible before approval.
- Manual publishing remains a first-class flow, not a fallback hidden behind automation.

## Implementation Notes

- Prototype path: `docs/260611-ai-marketing-os-redesign/index.html`
- No frontend app code exists for this project in the current repo snapshot, so the redesign is delivered as a static product prototype.
- The prototype keeps PRD behavior and IA intact while replacing the visual concept and screen composition.
- If this moves into Next.js later, split the prototype into `AppShell`, `SidebarNav`, `SignalGrid`, `QueueBoard`, `KnowledgeTable`, `HookLibraryTable`, `ContentEditor`, `ReviewRail`, and `PerformanceInsights`.

## Validation Method

- Browser QA at desktop and mobile widths.
- Responsive collapse check for sidebar, queue board, calendar, editor, and performance rows.
- Slop check against design-harness anti-patterns: no purple AI glow, no fake SaaS hero, no repeated equal-card marketing grid, no nested cards, no generic claims.
