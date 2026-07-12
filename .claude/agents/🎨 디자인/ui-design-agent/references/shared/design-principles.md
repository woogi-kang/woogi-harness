# Design Principles — Runtime v3

이 문서는 UI agent의 보조 원칙이다. 실행 계약은 `design-harness/SKILL.md`와 `design-run-v3`가 우선한다.

## Context before aesthetics

- 제품 category를 style preset에 매핑하지 않는다.
- 사용자 작업, 장면, 언어, 기존 브랜드/시스템, 실제 evidence가 디자인을 결정한다.
- “minimal/modern/bold”, palette shuffle, template rotation은 독창성 전략이 아니다.
- 한 프로젝트의 최근 결과와 다르게 만들기 위해 임의로 layout/color를 바꾸지 않는다.

## Font decisions

- 특정 font를 무조건 금지하거나 추천 matrix에서 자동 선택하지 않는다.
- Product/operational UI에서 system font나 이미 설치된 neutral sans가 task clarity를 높이면 정당하다.
- Brand/editorial에서 licensed brand font, 언어 glyph coverage, 역할 hierarchy, loading/CLS를 함께 확인한다.
- 한국어 UI는 Latin sample이 아니라 실제 Hangul copy와 `korean-typography` evidence로 평가한다.

## Structure

- 페이지는 사용자의 작업/메시지 순서로 구성한다.
- card는 정보/interaction boundary일 때만 사용한다.
- 같은 section family를 기계적으로 반복하지 않는다.
- Product와 operational surface는 익숙한 control과 상태 완결성을 우선한다.
- Brand/campaign surface는 실제 asset과 한 가지 분명한 시각 관점을 우선한다.

## Accessibility and states

- Native semantic element 또는 검증된 accessible primitive를 사용한다.
- Keyboard, focus-visible, accessible name, contrast, reduced motion을 실제 evidence로 확인한다.
- loading, empty, error, disabled, success/focus 상태는 scope에 맞게 구현하고 캡처한다.
- touch target은 보통 44px 수준을 목표로 하며 hover-only action을 만들지 않는다.
- Form은 visible label, 설명/오류, focus와 recovery를 갖는다.

## Motion

- Motion은 hierarchy, feedback, spatial continuity, narrative 중 하나를 설명해야 한다.
- Product/operational UI는 짧고 interruptible하게 유지한다.
- `transition-all`, broad `will-change`, layout-thrashing animation은 사용하지 않는다.
- Library가 아니라 platform과 project pattern을 기준으로 reduced-motion path를 구현한다.

## Evidence discipline

- fake dashboard, fake terminal, empty bento, fake metric/logo를 제품 증거로 사용하지 않는다.
- screenshot에는 route/screen, state, viewport, platform, command, hash를 남긴다.
- 가장 보기 좋은 화면 한 장으로 모바일/상태/접근성 완료를 주장하지 않는다.
- 구현자는 최종 critic pass를 self-issue하지 않는다.

## Anti-slop test

1. Category만 보고 결과를 예측할 수 있는가?
2. Default library component가 visual identity를 대신하는가?
3. Copy/metric/asset이 검증 가능한가?
4. 필요한 상태와 failure recovery가 실제로 존재하는가?
5. Register에 맞는 평가 축을 사용했는가?

하나라도 실패하면 “더 꾸미기”가 아니라 해당 contract/evidence gate로 돌아간다.
