# GBrain Memory Engine Phase 3 Pilot

Date: 2026-06-10
Status: Pilot Started
Scope: 30-day usefulness review

## Summary

Phase 3 is not a same-day implementation milestone. It is a 30-day evidence loop for deciding whether GBrain should remain, change, or expand beyond the local Claude Craft pilot.

This document starts the pilot by defining the event schema, report command, and Go/No-Go readout.

## Pilot Commands

```bash
scripts/brain-pilot.sh init
scripts/brain-pilot.sh log <event_type> <outcome> <minutes_saved> <citations> <note>
scripts/brain-pilot.sh tasks
scripts/brain-pilot.sh report
```

Metrics are stored in:

```text
/Users/woogi/brain-craft/metrics/gbrain-pilot-events.tsv
```

## Event Schema

| Field | Description |
| --- | --- |
| `date_iso` | UTC event timestamp |
| `event_type` | `lookup`, `context`, `capture`, `resume`, `quality`, or `miss` |
| `outcome` | `useful`, `neutral`, `miss`, `done`, or `blocked` |
| `minutes_saved` | Estimated minutes saved, integer |
| `citations` | Cited memory slug(s), or `-` |
| `note` | Short reason |

## Go Criteria

- At least 10 logged events.
- Useful rate is at least 50%.
- Citation rate is at least 50%.
- At least 5 follow-up tasks materially cite memory.
- Search misses are understandable and fixable.

## No-Go Criteria

- Misses outnumber useful events after enough usage.
- Captures create more noise than recovery value.
- Locking or latency makes memory lookup disruptive.
- Secret/import boundaries are not consistently respected.

## Initial Readout

The pilot starts with Phase 0-2 implementation events, not a full 30-day outcome. The report should remain `collecting data` until enough real follow-up tasks are logged.

Current task backlog:

```bash
scripts/brain-pilot.sh tasks
```

Static task plan:

```text
docs/260611-gbrain-memory-task-backlog.md
```

## Phase 3 Review Questions

- Did context recovery time drop by at least 50%?
- Did the user repeat less project context?
- Were at least 5 follow-up tasks materially helped by memory?
- Were search misses caused by no embeddings, bad capture quality, or wrong trigger rules?
- Should Phase 4 enable embeddings, register direct `docs/` source, or start company-brain scope?
