# Design Runtime v3 artifact contract

Runtime artifacts default to `.design-runs/<run-id>/`. Local `finalize` can
only produce `ready_for_external_promotion`; `validate` is diagnostic and
cannot promote a draft run. The local runtime rejects a forged local `passed`
status. Only an authenticated external provider/orchestrator may promote the
verified artifact set to `passed` across its own trust boundary.

## 1. Initialize an immutable design contract

```bash
RUNTIME=.claude/skills/design-harness/scripts/design-runtime.py
python3 "$RUNTIME" init \
  --root . --mode redesign --surface settings --register product \
  --implementation-actor-id "worker:<execution-id>" \
  --critic-public-key "<trusted-ed25519-public-key>" \
  --design-read "Reading this as: account settings for returning users, in a high-trust maintenance scene, using product register, with calm density, avoiding decorative card sprawl." \
  --dials 4,2,7,8,9 \
  --slop-risk "nested decorative cards" \
  --route /settings \
  --state default --state loading --state error --state focus
```

`--critic-public-key` is only an identifier, not a trust root. A harness
administrator must pin the external provider/orchestrator key in the
runtime-distributed `.claude/registry/design/trusted-authorities.json` before
the project run begins. The CLI does not accept a caller-selected trust-store
path or environment override. The runtime pins that canonical registry,
authority ID, and public-key SHA-256 and revalidates the same binding during
prepare, finalize, and validation. The active authority must explicitly carry
both `capture` and `critic` purposes. The checked-in registry is empty by
default, so unsigned/local-only environments fail closed until an administrator
provisions a real external authority. A key supplied only by the implementer is
rejected.

The fingerprint includes the complete non-empty set of project manifests,
theme/token files, and design documents. A changed candidate set or hash blocks
promotion. `--allow-project-drift` is diagnostic only and always prevents a
passing result.

## 2. Capture through a platform adapter

```bash
python3 "$RUNTIME" capture \
  --run .design-runs/<run>/design-run.json \
  --spec <web-or-flutter-capture.json>
```

Direct adapter execution and `import-index` remain diagnostic-only. The
trusted route copies the spec into a runtime-owned capture directory, executes
the canonical adapter, and emits a receipt whose adapter/spec/index/source and
evidence-projection hashes are exact-bound.

Flutter capture specs declare `generated_artifact_root` and keep non-baseline
artifacts below it. Test targets are confined to `test/` or `integration_test/`;
the adapter validates every path before invoking Flutter and never unlinks a
project artifact as a freshness mechanism.

The import checks adapter identity, project root, capture-spec hash, capture
index hash, artifact hash, real PNG signature/dimensions, and accessibility
tree content. Coverage is the exact `route | state | viewport` cross-product;
three independent set unions are not sufficient.

Every non-default web case declares typed `visible`, `text`, or
`aria_contains` assertions. The adapter records a passing
`state-assertion` artifact, and the runtime rejects states that differ only by
random pixels while sharing identical accessibility semantics. A `redesign`
run additionally declares `phase: baseline` and `phase: result` cases for every
tuple; result-only evidence is never a comparable redesign proof.

`add-evidence` accepts only structurally valid artifacts but marks them
`manual`. Manual evidence is useful for diagnosis and never satisfies a final
hard gate.

## 3. Freeze review evidence and create a critic packet

The external provider/orchestrator must verify that it launched or supervised
that canonical capture, then sign a `design-capture-attestation-v1` artifact.
The signature binds the receipt, canonical adapter, spec, index, source
fingerprint, and complete runtime-adapter evidence projection. A local
self-hash is not a trust proof.

Run the live source gates and freeze the exact review packet before handing
work to a separate critic:

```bash
python3 "$RUNTIME" prepare-review \
  --run .design-runs/<run>/design-run.json \
  --capture-attestation .design-runs/<run>/capture-attestation.json \
  --output .design-runs/<run>/review-packet.json
```

Create a bounded critic context manifest first, using a separate execution
actor. Then create the critic template:

```bash
python3 "$RUNTIME" critic-template \
  --run .design-runs/<run>/design-run.json \
  --critic-id "critic:<separate-execution-id>" \
  --context-manifest <critic-context-manifest.json> \
  --round 0 \
  --out .design-runs/<run>/critic-result.json
```

The critic actor ID must differ from the implementation actor ID. Its context
manifest path and SHA-256 are part of the result. The authenticated external
critic/orchestrator signs a `design-critic-attestation-v1` document defined by
`.claude/registry/design/critic-attestation.schema.json`; the signature binds
the immutable review packet, critic result, evidence manifest, and trusted
public key declared when the run was initialized. A round above zero is valid
only when the run contains an append-only, hash-chained repair record for every
preceding round.

## 4. Finalize

Complete the critic's register-specific `rubric_scores` with evidence IDs that
refer only to trusted capture items, attach the signed attestation, then run:

```bash
python3 "$RUNTIME" finalize \
  --run .design-runs/<run>/design-run.json \
  --critic .design-runs/<run>/critic-result.json \
  --attestation .design-runs/<run>/critic-attestation.json \
  --output .design-runs/<run>/finalization-result.json
```

The finalizer performs one closed sequence:

1. re-run the design-slop detector against current project sources;
2. require at least one scanned UI source and zero hard failures;
3. rebuild the canonical adapter/spec/index projection, verify its external
   capture signature, then verify the complete fingerprint and trusted capture
   tuple coverage;
4. verify critic actor/context/evidence provenance;
5. execute the register-specific grader with a mandatory detector result;
6. hash and register the passing evaluation result;
7. revalidate all evidence, then write `status: ready_for_external_promotion`.

This is the terminal local success state. The local CLI has no authority to
write `passed`. An authenticated external provider/orchestrator must verify the
same immutable hashes and attestation, record its promotion identity, and only
then may publish `passed` outside the local runtime. If that boundary is not
available, report `ready_for_external_promotion`; do not translate it to
`passed` in prose.

Missing targets, placeholder screenshots, hash drift, unsigned capture,
manual evidence, self-authored waivers, missing grader input, incomplete
tuples, or a self critic all fail closed.

## Waivers and approvals

Waivers may record an external decision with approval ID, actor, time, and
scope hash, but Design Runtime never converts a waived hard gate into
`ready_for_external_promotion` or `passed`. The result remains `needs_review`,
`blocked`, or `failed` until evidence is recaptured or the requested scope is
changed through a new run.
