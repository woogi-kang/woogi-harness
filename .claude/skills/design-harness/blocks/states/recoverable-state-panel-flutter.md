---
name: recoverable-state-panel-flutter
category: states
dial_compatibility:
  distinction: [2, 6]
  motion: [1, 4]
  density: [3, 8]
  evidence: [7, 10]
  systemness: [6, 10]
when_to_use: "A Flutter screen region that can be loading, empty, failed, or ready and must preserve a clear recovery path."
not_for: "A transient toast or validation message local to one field."
stack: ["flutter"]
---

# Recoverable State Panel — Flutter

## Visual sketch

```text
loading  → shape-matched progress
empty    → reason + next valid action
failure  → local message + retry/support action
ready    → content using the same region and hierarchy
```

## Props API

```dart
sealed class PanelState {
  const PanelState();
}

final class PanelLoading extends PanelState { const PanelLoading(); }
final class PanelEmpty extends PanelState { const PanelEmpty(this.message); final String message; }
final class PanelFailure extends PanelState {
  const PanelFailure(this.message, this.onRetry);
  final String message;
  final VoidCallback onRetry;
}
final class PanelReady<T> extends PanelState { const PanelReady(this.value); final T value; }
```

## Code sketch

```dart
Widget buildPanel(PanelState state) => Semantics(
  liveRegion: state is PanelFailure,
  child: switch (state) {
    PanelLoading() => const PanelSkeleton(),
    PanelEmpty(:final message) => EmptyPanel(message: message),
    PanelFailure(:final message, :final onRetry) => FailurePanel(message: message, onRetry: onRetry),
    PanelReady(:final value) => ReadyPanel(value: value),
  },
);
```

## Mobile fallback

This is mobile-first. At large text scale, actions wrap below copy and the panel remains scrollable without clipping. Keyboard insets and SafeArea are handled by the parent screen.

## Motion variants

- `1–3`: progress feedback and short opacity transition only.
- `4–7`: preserve region size between compatible states; no looping illustration.
- `8–10`: incompatible with recovery UI.
- `MediaQuery.disableAnimations` or equivalent removes nonessential motion.

## Dark mode

Resolve all colors from the current `ColorScheme`/theme extension. Error meaning uses icon/text/semantics in addition to color.

## Evidence requirements

- Widget/integration or golden evidence for all four states.
- Text scale and narrow-width capture.
- Semantics/focus order for retry.
- `flutter analyze` and relevant test log.

## Anti-patterns

- Generic illustration replacing the recovery action.
- Error text that exposes raw exception details.
- Empty state that blames the user or offers an invalid action.
- Different panel geometry for each state causing layout jumps.
- Hard-coded colors outside the project theme.

## References

Use the project's Material/Cupertino/component state conventions; this block defines state completeness, not visual branding.
