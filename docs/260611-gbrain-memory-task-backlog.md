# GBrain Memory Engine Remaining Task Backlog

Date: 2026-06-11
Status: Active
Owner: Woogi
Scope: Finish the GBrain memory-engine rollout by managing Phase 3 and post-pilot decisions to completion.

## Operating Principle

This backlog is outcome-based. A task is complete only when the expected operating result is true and verified by a command, not when a document or feature merely exists.

Primary commands:

```bash
scripts/brain-pilot.sh tasks
scripts/brain-pilot.sh report
scripts/brain-pilot.sh log <event_type> <outcome> <minutes_saved> <citations> <note>
scripts/brain-memory.sh context "<query>"
scripts/brain-memory.sh quality-report
scripts/brain-memory-qa.sh
```

## Outcome Roadmap

| Outcome | Why It Matters | Success Metric |
| --- | --- | --- |
| Claude Craft reliably recovers prior context | Reduces repeated explanation and restart cost | 5+ useful memory-assisted follow-up tasks |
| Memory usage is measurable | Prevents subjective keep/drop decisions | 10+ pilot events by review |
| Search misses are explainable | Separates no-embedding limits from bad capture quality | Every miss has cause and follow-up |
| Memory corpus remains safe and useful | Prevents secret/import noise and stale decisions | Weekly quality checks pass |
| Expansion decisions are evidence-based | Avoids premature embeddings/company-brain work | Keep/change/drop decision after pilot |

## Task Backlog

| ID | Status | Outcome | Completion Criteria | Owner | Target |
| --- | --- | --- | --- | --- | --- |
| GB-P3-01 | Done | Pilot can collect evidence | `scripts/brain-pilot.sh report` works and metrics file exists | Woogi | 2026-06-10 |
| GB-P3-02 | In Progress | Enough real usage is logged | At least 10 pilot events in `brain-craft/metrics/gbrain-pilot-events.tsv` | Woogi + agents | 2026-07-10 |
| GB-P3-03 | In Progress | Memory proves useful in follow-up work | At least 5 `useful` events with citations | Woogi + agents | 2026-07-10 |
| GB-P3-04 | In Progress | Outputs cite memory consistently | Citation rate is at least 50% in `scripts/brain-pilot.sh report` | Agents | 2026-07-10 |
| GB-P3-05 | In Progress | Search misses are explainable | Every `miss` event includes cause and next fix | Agents | Weekly |
| GB-P3-06 | Pending | Weekly quality stays healthy | Weekly `quality` event logged after `scripts/brain-memory.sh quality-report` | Agents | Weekly |
| GB-P3-07 | Pending | Embedding policy is evidence-based | Keep keyword-only or enable embeddings based on miss/usefulness data | Woogi | 2026-07-10 |
| GB-P3-08 | Pending | Import scope remains safe | Decide curated copy vs direct `docs/` source after secret/import review | Woogi | 2026-07-10 |
| GB-P3-09 | Blocked | Company brain expansion has clear scope | Requires keep/change decision and access model | Woogi | After pilot |
| GB-P3-10 | Blocked | Final keep/change/drop decision is made | 30-day review completed with Go/No-Go readout | Woogi | 2026-07-10 |

## How To Log Work

Lookup helped:

```bash
scripts/brain-pilot.sh log lookup useful 10 decisions/260610-gbrain-phase1-harness-wiring "Recovered Phase 1 decision"
```

Context pack helped:

```bash
scripts/brain-pilot.sh log context useful 12 sessions/260610-gbrain-phase2-main-commit "Recovered phase status"
```

Search missed:

```bash
scripts/brain-pilot.sh log miss miss 0 - "Query missed Korean page; retry exact Korean title"
```

Quality review:

```bash
scripts/brain-memory.sh quality-report
scripts/brain-pilot.sh log quality done 0 sources/claude-craft-docs/260610-gbrain-memory-phase2-validation "Weekly quality check"
```

## Review Cadence

| Date | Review |
| --- | --- |
| 2026-06-18 | Week 1 quality and event count review |
| 2026-06-25 | Week 2 miss/citation review |
| 2026-07-02 | Week 3 embedding/import decision prep |
| 2026-07-10 | 30-day keep/change/drop review |

## Completion Rule

Do not mark the GBrain rollout complete until:

- `GB-P3-02`, `GB-P3-03`, and `GB-P3-04` are done.
- `GB-P3-07` and `GB-P3-08` have explicit decisions.
- `GB-P3-10` has a keep/change/drop result.
- The result is captured in `brain-craft` and searchable through GBrain.
