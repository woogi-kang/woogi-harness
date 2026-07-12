---
name: ckm:ui-styling
description: "Design Runtime v3의 구현 adapter. 기존 프로젝트의 Web/Flutter stack, token, component system을 보존해 접근 가능한 UI를 구현하고 route/state/viewport evidence를 만든다. shadcn, Tailwind, Motion, Material을 기본값으로 강제하지 않으며 디자인 방향과 최종 평가는 design-harness가 소유한다."
argument-hint: "[surface or component]"
license: MIT
metadata:
  author: claudekit
  version: "2.0.0"
---

# UI Styling Implementation Adapter

이 skill은 “예쁜 UI 추천”이 아니라 `design-harness`가 고정한 contract를 현재 프로젝트 stack으로 구현한다.

## Entry requirements

구현 전에 다음을 확보한다.

- Design Read, register, 5 dials, main slop risk.
- 대상 route/screen, state, viewport.
- 실제 `package.json`/`pubspec.yaml`, theme/token, 대표 component.
- 유지해야 할 design system과 behavior contract.
- evidence manifest 경로 또는 검증 계획.

방향이 정해지지 않았으면 `design-harness shape`; token 구조가 없으면 `design-system`; 한국어 typography 결정이 필요하면 `korean-typography`로 돌아간다.

## Stack detection, not stack invention

```bash
python3 .claude/skills/design-harness/scripts/design-runtime.py plan --root .
```

### Web

- 현재 framework, package manager, rendering mode, CSS/token 방식, component primitives를 유지한다.
- shadcn/Radix/Tailwind/Motion은 이미 설치됐거나 design contract가 선택했을 때만 사용한다.
- component library는 behavior/accessibility를 제공할 수 있지만 프로젝트의 시각 truth를 덮지 않는다.
- semantic HTML, keyboard flow, focus, responsive layout, loading/empty/error를 함께 구현한다.
- 동적 class string, 무분별한 `transition-all`, giant z-index, viewport `100vh`, placeholder label을 피한다.

### Flutter

- 현재 `ThemeData`, Material/Cupertino 선택, localization, router, state-management pattern을 유지한다.
- token을 raw `Color`/spacing 값으로 화면마다 복제하지 않는다.
- `Semantics`, focus order, text scale, safe area, keyboard inset, scroll/overflow, reduced motion을 확인한다.
- loading/empty/error/disabled/focus를 실제 widget state로 만든다.
- 변경 후 `flutter analyze`, relevant test/golden/integration capture를 남긴다.

새 기술을 도입해야 하면 tech-stack registry의 recommended baseline과 migration gate를 확인한다. UI styling이 package upgrade를 몰래 수행하지 않는다.

## Implementation sequence

1. **Map** — 기존 token/component와 contract의 역할을 매핑한다.
2. **Structure** — semantic hierarchy, task order, responsive collapse를 먼저 구현한다.
3. **States** — default만 만들지 말고 scope의 loading/empty/error/disabled/focus를 구현한다.
4. **Style** — register와 dials 안에서 type/color/spacing/radius/elevation/motion을 적용한다.
5. **Content** — 실제 data shape와 구체적 copy를 사용한다. fake metric/logo/screenshot을 만들지 않는다.
6. **Verify** — source scan, build/test, route/state/viewport evidence를 만든다.

## Web component contract

모든 interactive component에서 확인한다.

- 올바른 native element 또는 검증된 accessible primitive.
- visible label, accessible name, focus-visible treatment.
- keyboard operation과 focus return.
- touch target 약 44px, hover-only action 없음.
- async pending/disabled/error feedback.
- mobile overflow와 longest-content behavior.
- theme/dark mode가 존재하면 token parity.

Example은 library 기본 Card grid가 아니라 project component API로 시작한다.

```tsx
type ReviewQueueProps = {
  rows: ReviewRow[]
  status: "loading" | "ready" | "empty" | "error"
  onRetry(): void
}

export function ReviewQueue(props: ReviewQueueProps) {
  if (props.status === "loading") return <QueueSkeleton aria-label="검토 목록 불러오는 중" />
  if (props.status === "error") return <InlineRecovery onRetry={props.onRetry} />
  if (props.status === "empty") return <QueueEmpty />
  return <ReviewTable rows={props.rows} />
}
```

구체 class/token은 프로젝트 truth에서 가져온다. 예제의 시각값을 template처럼 복사하지 않는다.

## Flutter component contract

```dart
sealed class QueueState {
  const QueueState();
}

final class QueueReady extends QueueState {
  const QueueReady(this.rows);
  final List<ReviewRow> rows;
}

Widget buildQueue(QueueState state) => switch (state) {
  QueueLoading() => const QueueSkeleton(),
  QueueEmpty() => const QueueEmpty(),
  QueueFailure(:final retry) => QueueRecovery(onRetry: retry),
  QueueReady(:final rows) => ReviewList(rows: rows),
};
```

Theme와 semantics는 실제 프로젝트 component에서 연결한다. snippet은 상태 완결성의 형태만 보여준다.

## Anti-slop implementation gate

- category가 palette/layout을 자동 결정하지 않는다.
- centered hero + pill + generic CTA + equal card grid를 기본 scaffold로 만들지 않는다.
- shadcn/Material default appearance를 제품 정체성처럼 출하하지 않는다.
- real evidence가 필요한 곳에 div fake UI, abstract blob, empty bento를 넣지 않는다.
- 모든 section에 같은 radius/card/elevation을 반복하지 않는다.
- 실제 상태/데이터 없이 완성도를 주장하지 않는다.

```bash
node .claude/skills/design-harness/scripts/detect-design-slop.mjs \
  --format json --fail-on hard-fail --output <run>/source-scan.json \
  <changed-ui-paths>
```

## Evidence handoff

구현자는 다음 artifact를 만들되 최종 self-approval하지 않는다.

- build/type/analyze/test log.
- planned route/screen의 state별 screenshot.
- Web accessibility tree 또는 Flutter semantics evidence.
- detector JSON.
- 변경된 evidence ID 목록.

`design-harness`가 independent critic과 register eval을 실행한다.

## Reference routing

기존 프로젝트가 해당 stack을 이미 사용하거나 contract가 명시적으로 선택한 경우에만 읽는다.

- `references/shadcn-components.md`
- `references/shadcn-theming.md`
- `references/shadcn-accessibility.md`
- `references/tailwind-utilities.md`
- `references/tailwind-responsive.md`
- `references/tailwind-customization.md`

Canvas/brand visual 방향은 이 skill이 임의로 정하지 않는다. Raster 이미지가 필요하면 `image-prompt`가 prompt를 소유한다.

## Not owned here

- Art direction/register/dials: `design-harness`.
- Token architecture: `design-system`.
- Framework architecture: Flutter/Next project skills.
- Logo/banner/CIP: 해당 asset skill.
- Raster prompt compilation: exact-vendored `image-prompt`.
- Final approval: independent critic + UI eval.
