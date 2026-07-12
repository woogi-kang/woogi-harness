# Flutter 3.24 to 3.44 migration contract

Verified: 2026-07-13
Registry: `flutter@recommended`

This is a behavioral migration, not a version-string replacement. Preserve the existing project's SDK constraint, platform deployment targets, architecture, generated files, and lockfile as the starting truth.

## Required review

1. SDK and platform templates
   - Move the new-project baseline to Flutter 3.44.6 with bundled Dart 3.12.2.
   - Review every Flutter breaking-change guide from 3.27 through 3.44.
   - Account for Android v1 embedding removal, Plugin DSL and built-in Kotlin changes, Java 17, current AGP, edge-to-edge and predictive back behavior, and the selected packages' Android API 24 floor.
   - Review `.flutter-plugins` removal, generated localization source, iOS `UISceneDelegate`, Swift Package Manager, and current Apple deployment floors.
   - Rebaseline Material 3 token, theme, transition, typography, semantics, and golden-test changes instead of accepting screenshot churn blindly.

2. Dart language and tooling
   - Raise the language constraint only after `dart fix --dry-run`, formatter, analyzer, generator, and test output have been reviewed.
   - Account for language-versioned formatting and analysis, dot shorthands, private named initializing formals, `dart:html` deprecations, and current JS interop guidance.
   - Experimental primary constructors, previews, and agentic tooling never enter a production template by default.

3. Riverpod 2 to 3
   - Decide the retry policy explicitly; failed providers retry by default in Riverpod 3.
   - Test provider pausing below `TickerMode`, `==`-based update filtering, `ProviderObserverContext`, simplified `Ref`, removed Ref subclasses, and `ProviderException` wrapping.
   - Move `StateProvider`, `StateNotifierProvider`, and `ChangeNotifierProvider` consumers to `legacy.dart` or migrate them to Notifier APIs.
   - Keep `flutter_riverpod`, `riverpod_annotation`, and `riverpod_generator` on the registry family and regenerate all providers.

4. GoRouter 14 to 17
   - Test URL case sensitivity, typed route mixins, redirects, browser history, restoration, nested `ShellRoute` stacks, back gestures, and root observer notification changes.
   - Regenerate typed routes with the matching builder before runtime tests.

5. Code generation and storage
   - Freezed 3 classes must use appropriate `abstract` or `sealed` semantics. Do not repeat the stale claim that `when` and `map` are absent; they returned in 3.1.
   - Pigeon 27 removes `PigeonOptions.oneLanguage`. Regenerate and compile Android, iOS, and macOS bindings.
   - Validate Drift schema snapshots and upgrade/downgrade paths before accepting Drift or sqlite3 output changes.
   - Prefer `sqlite3` 3.x over the EOL `sqlite3_flutter_libs` bundling path.

6. Notifications and backend SDKs
   - Local notifications 21+ implies Flutter 3.38.1, Dart 3.10, Android API 24, iOS 13, current compileSdk/AGP, and UIScene-aware setup. Exercise scheduled, foreground, background, permission, and launch-response paths.
   - Resolve FlutterFire as a family and test auth refresh, emulator configuration, Firestore converters/offline behavior, FCM lifecycle states, and release configuration.
   - For Supabase, test auth lifecycle reconnection and use current publishable-key terminology.

## Promotion commands

```bash
flutter --version
flutter pub outdated
dart fix --dry-run
dart format --output=none --set-exit-if-changed .
dart run build_runner build --delete-conflicting-outputs
flutter analyze
flutter test
flutter build apk --release
flutter build ios --no-codesign
```

Run code generation a second time and require an empty diff. Platform builds may be waived only with an explicit reason and an issue that owns the missing evidence.

## Primary sources

- https://docs.flutter.dev/release/release-notes
- https://docs.flutter.dev/release/breaking-changes
- https://dart.dev/changelog
- https://riverpod.dev/docs/3.0_migration
- https://pub.dev/packages/go_router/changelog
- https://pub.dev/packages/freezed/changelog
- https://pub.dev/packages/pigeon/changelog
- https://pub.dev/packages/flutter_local_notifications/changelog
