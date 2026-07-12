# Independent Critic and Bounded Repair

The critic is an evaluator, not a second art director.

## Independence

- The implementer may run mechanical checks but cannot issue the final critic pass.
- Before critic work, a separate external authority signs the canonical capture receipt and complete evidence projection; a local self-hash cannot establish capture provenance.
- The critic uses a separate execution actor ID and a `context-pack-gate` manifest whose SHA-256 is recorded in the critic result.
- The authenticated external critic/orchestrator signs an attestation bound to the immutable review packet, critic result, evidence manifest, and run trust policy.
- Give the critic the design run, evidence manifest, actual artifacts, and source-scan result.
- Do not lead with the implementer's preferred aesthetic or ask the critic to validate a conclusion.
- If a separate reviewer or signed attestation is unavailable, status is `needs_review`, not `ready_for_external_promotion` or `passed`.

An independent critic decision of `pass` is necessary but is not itself a runtime status promotion. Local `finalize` stops at `ready_for_external_promotion`; only an authenticated external provider/orchestrator may promote the verified result to `passed`.

## Finding contract

Each finding contains severity, axis, observation, evidence IDs, and the smallest repair. “Feels generic” is invalid unless the critic points to a specific composition/copy/evidence pattern.

## Repair policy

1. Round 0 reviews the first evidence-complete implementation.
2. Round 1 repairs critical/major issues and recaptures affected artifacts.
3. Round 2 is the final bounded repair.
4. A third aesthetic rewrite is forbidden. Mark unresolved material failure `failed` or a real dependency/tool gap `blocked`.

Each completed repair round is appended to `repair_history` with the prior
record hash, affected critic hash, changed files, and verification evidence.
Changing only the critic's `round` integer cannot advance the loop.

Do not fix suggestions while critical usability, state, accessibility, or evidence failures remain. Do not recompose unrelated screens to satisfy a narrow finding.
