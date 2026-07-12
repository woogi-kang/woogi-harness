# UI Agent Platform and Stack Policy

UI agent는 고정 stack을 소유하지 않는다. 현재 프로젝트 profile과 `.claude/registry/tech-stacks/`의 recommended baseline이 source of truth다.

## Detection

```bash
python3 .claude/skills/design-harness/scripts/design-runtime.py plan --root .
```

그다음 실제 manifest를 읽는다.

- Web: `package.json`, lockfile, framework config, CSS/token files, component registry.
- Flutter: `pubspec.yaml`, `analysis_options.yaml`, Theme/ColorScheme, navigation/state/localization pattern.
- 새 dependency가 필요하면 tech-stack registry의 source, migration note, promotion gate를 확인한다.

## Web policy

- 현재 framework/rendering mode/package manager를 유지한다.
- 이미 설치된 component primitive와 token model을 우선한다.
- Tailwind, shadcn/Radix, Motion, CSS Modules, styled system 중 하나를 하네스 기본값으로 강제하지 않는다.
- Official design system이 제품 맥락에 맞으면 공식 package/docs를 우선한다.
- Build/type/lint/test와 실제 browser evidence로 검증한다.

## Flutter policy

- Flutter/Dart와 package 권장은 `tech-stacks/flutter.yaml`을 따른다.
- 기존 Material/Cupertino/brand Theme를 보존하며 raw token 복제를 피한다.
- Responsive, text scale, SafeArea, keyboard inset, semantics, state, golden/integration evidence를 확인한다.
- package major migration은 UI 작업 안에서 몰래 수행하지 않는다.

## Typography

- 설치/라이선스/언어 glyph/brand role을 먼저 확인한다.
- font name matrix와 category 추천표를 사용하지 않는다.
- Korean surface는 `korean-typography`; project font asset이 있으면 그것이 우선한다.

## Animation

- project가 이미 채택한 API를 사용한다.
- Web은 CSS/Web Animations/framework library, Flutter는 implicit/explicit animation 중 목적과 기존 pattern에 맞는 것을 선택한다.
- reduced motion과 interruption을 evidence로 확인한다.

## Components

- Library component는 behavior/accessibility 시작점이지 visual truth가 아니다.
- Default Card/Button styling, equal card grid, decorative status dot를 그대로 출하하지 않는다.
- 필요한 state API부터 설계한 뒤 project tokens를 적용한다.

## Version policy

문서에 떠다니는 `latest`나 임의 버전 번호를 복사하지 않는다. 다음을 분리한다.

- `latest_observed`: 공식 registry에서 관찰한 최신값.
- `recommended`: 현재 toolchain과 fixture를 통과한 생성 기본값.
- `compatibility_floor`: 기존 프로젝트 지원 하한.
- `candidate`: migration 검증 중인 major.

구체 값과 차이는 `.claude/registry/tech-stacks/`와 해당 `migrations/` 문서를 읽는다.
