# Design Runtime Registry

This directory is the machine-readable contract for Design Runtime v3.

- `design-run.schema.json`: context, register, five dials, project fingerprint, gates, and bounded repair policy.
- `evidence-manifest.schema.json`: immutable source, screenshot, state, accessibility, and critic evidence.
- `critic-result.schema.json`: independent critic findings tied to evidence IDs.
- `platforms.json`: web and Flutter detection, capture adapter CLI, and evidence requirements.
- `web-capture.schema.json` / `flutter-capture.schema.json`: stateful capture input contracts.
- `capture-index.schema.json`: hashed adapter output imported into the evidence manifest.
- `capture-attestation.schema.json`: external signature over the canonical capture receipt and evidence projection.
- `critic-trust-store.schema.json`: host-owned authority pins with separate capture/critic purposes.

Prompt prose and local self-hashes are not trust evidence. When required evidence exists, hashes match, the capture and critic attestations authenticate against the external trust store, the source scan has no hard failures, and route/state/viewport coverage is complete, local `finalize` records `ready_for_external_promotion`. The local runtime never writes `passed`; only an authenticated external provider/orchestrator may promote that immutable result across its own trust boundary.
