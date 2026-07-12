# Design Runtime v3 Migration

## Why this replaces Design Harness v2

V2 had useful design language but completion was still prose-driven. Five dials existed in the skill while the UI agent exposed three, the implementation owner assumed shadcn/Tailwind/Framer, positive blocks were empty, the detector ignored Dart, and the eval assigned universal 35% originality weight without executable evidence.

V3 makes the design path operational:

```text
project truth → typed run → platform capture index → trusted hashed evidence
→ live source/visual gates → actor-separated critic → hash-chained repair
→ register eval → local finalizer (`ready_for_external_promotion`)
→ authenticated external provider/orchestrator promotion (`passed`)
```

## Source of truth

| Contract | Path |
|---|---|
| Runtime entrypoint | `.claude/skills/design-harness/SKILL.md` |
| Run/evidence/critic schemas | `.claude/registry/design/` |
| Runtime CLI | `.claude/skills/design-harness/scripts/design-runtime.py` |
| Source detector | `.claude/skills/design-harness/scripts/detect-design-slop.mjs` |
| Executable eval | `.claude/evals/ui-design/` |
| Implementation adapter | `.claude/skills/ui-styling/SKILL.md` (`ckm:ui-styling`) |
| Positive blocks | `.claude/skills/design-harness/blocks/` |

## Behavioral changes

- UI work no longer starts by choosing minimal/modern/bold or a font matrix.
- `DISTINCTION`, `MOTION`, `DENSITY`, `EVIDENCE`, and `SYSTEMNESS` are all required.
- Web and Flutter share the artifact contract but use different platform evidence.
- `shell/build success` and a best-looking screenshot cannot establish design completion.
- The implementer can collect evidence but cannot issue the final critic pass.
- Placeholder files and manual evidence cannot satisfy promotion gates.
- Coverage is verified as route/state/viewport tuples, not three unrelated sets.
- `design-runtime.py prepare-review` requires an external capture-authority signature over the canonical adapter/spec/index/source/evidence projection; local self-hashes alone are diagnostic.
- `design-runtime.py finalize` reruns the detector and grader, authenticates both the capture and critic attestations, and writes only `ready_for_external_promotion`.
- The local runtime rejects a locally asserted `passed`; only an authenticated external provider/orchestrator may verify the immutable hashes and promote the result to `passed` across its own trust boundary.
- Repair is bounded at two rounds.
- Product, operational, brand, campaign, public-sector, and editorial surfaces use different weights.
- Raster image prompt ownership is removed from design skills and delegated to exact-vendored Gongnyang `image-prompt`; execution uses only the Codex `$imagegen` host contract whose required model is `gpt-image-2`. The opaque host does not expose per-call model identity, so local provenance records a trusted-host contract rather than a locally verified model.

## Rollout

1. Run `grader.py self-test` in the harness.
2. Canary on one Web product surface and one Flutter surface.
3. Compare v2 handoff claims with v3 evidence completeness.
4. Fix adapter/tool gaps; do not weaken evidence gates to force a pass.
5. Confirm local results stop at `ready_for_external_promotion` and that an authenticated external provider/orchestrator is the only actor that can record `passed`.
6. Promote the runtime through project packs and sync v2 after canary approval.

Existing projects can use the runtime without adopting a new UI library. The first action is detection and fingerprinting, not package installation.

## Known boundary

Static detector hits are heuristics. Warnings require contextual review; they are not automatic aesthetic failures. Visual quality beyond deterministic checks remains a critic responsibility, but the critic must cite actual evidence and cannot override hard functional/accessibility failures with taste scores.

`ready_for_external_promotion` is the strongest local claim, not a synonym for `passed`. If the authenticated external promotion boundary is unavailable, the handoff must retain that local status and name external promotion as not performed.
