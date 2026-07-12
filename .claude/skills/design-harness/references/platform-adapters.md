# Design Runtime Platform Adapters

Adapters create evidence; they do not redefine design quality.

An adapter result with `status: passed` means only that capture operation succeeded. It never promotes the Design Runtime run. A trusted review also requires an external capture-authority signature over the canonical receipt and evidence projection. Local `finalize` stops at `ready_for_external_promotion`; only an authenticated external provider/orchestrator may promote the verified run to `passed`.

## Web

Detect from `package.json` and framework config. Preserve the project's package manager, rendering mode, component system, token model, and test commands.

Evidence minimum:

- Build/type/lint evidence relevant to the changed surface.
- JSON source scan.
- Fixed viewport screenshots for each planned viewport.
- Default plus in-scope loading/empty/error/focus states.
- Typed assertions proving every non-default state actually exists.
- Accessibility tree or equivalent automated/manual audit artifact.
- Console/network failures captured when they affect the flow.

Use a real browser session. DOM snippets, static HTML, or a screenshot of a loading crash do not prove the intended page.

The target app must already be running. The adapter uses the target project's installed Playwright and never installs a browser package or silently changes tools.

Use `assertions` with `visible`, `text`, or `aria_contains` for each
non-default case. The adapter stores the evaluated values and pass/fail result;
state labels alone do not count. For `redesign`, capture comparable
`phase: baseline` and `phase: result` cases at every route/state/viewport tuple.

```bash
node .claude/skills/design-harness/scripts/capture-web-evidence.mjs \
  --root . --spec <web-capture.json> --out <run>/web
```

## Flutter

Detect from `pubspec.yaml`. Preserve the current Theme, Material/Cupertino choice, navigation, localization, and state-management patterns.

Evidence minimum:

- `flutter analyze` and relevant tests.
- JSON source scan over changed `.dart` files.
- Simulator/device, golden, or integration screenshots at declared logical size.
- In-scope loading/empty/error/focus or semantics states.
- Semantics/accessibility evidence when the surface contains interactive controls.

Do not treat a widget-test pump as visual proof unless a captured artifact is attached. Golden evidence must state platform/font/device assumptions.

The Flutter adapter runs `flutter analyze`, declared `flutter test` targets, then copies and hashes declared golden/integration/semantics artifacts. `test_targets` must stay under `test/` or `integration_test/`; every non-baseline artifact must stay under the spec's project-relative `generated_artifact_root` (normally `build/design-evidence`). The adapter never deletes a declared project artifact before testing. A missing Flutter SDK, failed test, stale artifact, unsafe path, or missing artifact is a failure.

```bash
python3 .claude/skills/design-harness/scripts/capture-flutter-evidence.py \
  --root . --spec <flutter-capture.json> --out <run>/flutter
```

## Capture discipline

- Keep route/screen, state, viewport, platform, command, and timestamp with every artifact.
- Use deterministic data where visual diffs matter.
- Do not crop away overflow, browser errors, system bars, or broken controls merely to improve the review image.
- Baseline and result must use comparable conditions.
- Redact private data before sharing; do not fabricate replacement evidence.
