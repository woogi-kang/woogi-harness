# Design Runtime v3 Evaluation

This eval prevents design quality from collapsing into a single taste score. It combines deterministic source checks, route/state/viewport evidence, register-specific scoring, and an independent critic.

## Required packet

1. `design-run.json` from `design-runtime.py init`.
2. `evidence-manifest.json` with adapter provenance, index hash, and artifact hash.
3. A runtime-generated `design-slop-scan-v2` JSON with non-empty `files_scanned`.
4. An actor-separated `design-critic-result-v1` with a hashed context manifest.
5. Register-specific axis scores with evidence IDs and rationale in the critic result.
6. A signed `design-critic-attestation-v1` issued by the authenticated external critic/orchestrator trust boundary.

Screenshots without a route, state, viewport, or content provenance are incomplete evidence. Prompt summaries and implementation claims are not evidence.

## Register-specific meaning of quality

- `product`: task completion, states, accessibility, and repeat-use clarity outrank novelty.
- `operational`: task efficiency, readable density, keyboard/state rigor, and trustworthy data presentation outrank visual drama.
- `brand` and `campaign`: authored point of view, real visual evidence, craft, and message clarity matter; generic novelty alone does not pass.
- `public-sector`: accessibility, official-system fidelity, plain-language usability, and failure recovery dominate.
- `editorial`: typography, pacing, register fit, and source/evidence integrity dominate.
- `design-system`: contract fidelity, states, accessibility, and adoption safety dominate.
- `asset`: brief fidelity, craft, distinction, and technical fitness dominate.

Weights are executable in `grader.py`; there is no universal `Originality 35%` rule.

## Hard gates

- Any detector `hard-fail`; waivers cannot promote a run.
- Placeholder/non-PNG screenshots, manual promotion evidence, or capture-index drift.
- Missing required platform evidence.
- Missing or non-independent critic.
- Critic decision `fail` or `blocked`.
- Any scored axis below 5.
- More than two repair rounds or a round without append-only hash-chained history.
- Fingerprint or evidence hash drift.

Minimum weighted score is 7.0, but a score never overrides a hard gate.

## Commands

```bash
python3 .claude/evals/ui-design/grader.py self-test

python3 .claude/skills/design-harness/scripts/design-runtime.py finalize \
  --run .design-runs/<run>/design-run.json \
  --critic .design-runs/<run>/critic-result.json \
  --attestation .design-runs/<run>/critic-attestation.json \
  --output .design-runs/<run>/finalization-result.json
```

The command's local success status is `ready_for_external_promotion`. It does
not write `passed`; that promotion belongs only to an authenticated external
provider/orchestrator that verifies the same immutable packet and attestation.

## Repair loop

The implementer receives only evidence-backed findings, fixes the smallest coherent issue set, and recaptures affected evidence. A critic who did the implementation cannot self-approve. Stop after two repair rounds; repeated unresolved failures become `blocked` or `failed`, not an endless polish loop.
