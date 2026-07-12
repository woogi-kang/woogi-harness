---
name: design-harness
description: "증거 기반 Design Runtime v3. UI/UX 설계·구현·리디자인·감사·폴리시 작업에서 project fingerprint, design contract, 5개 control dial, platform adapter, route/state/viewport evidence, anti-slop detector, 독립 critic, 최대 2회 repair, executable eval을 강제한다. 웹과 Flutter 디자인 변경 또는 AI Slop 위험이 있는 모든 작업에 사용한다."
license: MIT
metadata:
  category: "🎨 디자인"
  version: "0.3.0"
  tags: "design-runtime, frontend-design, flutter-design, anti-slop, visual-qa, evidence, independent-critic, executable-eval"
---

# Design Harness — Runtime v3

좋은 취향을 주장하는 대신, 제품 맥락을 고정하고 실제 화면으로 증명한다.

```text
Project Fingerprint
→ Design Contract
→ Baseline Evidence
→ Platform Execution
→ Source + Visual Gates
→ Independent Critic
→ Bounded Repair (max 2)
→ Register-specific Eval
```

UI 코드, 레이아웃, 스타일, UX, motion, copy, 상태, 접근성, 반응형 결과가 바뀌는 작업은 이 runtime을 먼저 연다. 단순 설명이나 읽기 전용 질문은 run artifact 없이 답할 수 있지만, 구현 완료를 선언하려면 evidence contract를 통과해야 한다.

## Completion contract

다음이 모두 참이어야 로컬 runtime이 `ready_for_external_promotion`을 기록할 수 있다.

1. `design-run-v3`에 Design Read, register, 5 dials, slop risk, 대상 route/state/viewport가 있다.
2. 전체 non-empty project fingerprint가 현재 candidate set과 일치하며 drift bypass가 없다.
3. 플랫폼 adapter가 생성한 capture index와 실제 PNG/접근성/테스트 artifact의 해시가 일치하고, 외부 capture authority가 canonical receipt와 전체 evidence projection을 서명했다.
4. finalizer가 변경 source 전체에 detector를 재실행했고 hard-fail이 0이다. waiver로 승격할 수 없다.
5. 구현 actor와 다른 critic actor가 해시된 context manifest와 trusted evidence ID를 인용해 `pass`했고, 외부 critic/orchestrator trust boundary가 서명한 attestation이 있다.
6. `design-runtime.py finalize`가 register별 grader를 실행해 7.0 이상, 모든 축 5 이상을 확인했다.
7. repair는 최대 2회다. 같은 실패가 반복되면 더 꾸미지 말고 `blocked`/`failed`로 종료한다.

로컬 `design-runtime.py finalize`는 `passed`를 쓰지 않는다. 로컬 최종 상태는 항상 `ready_for_external_promotion`이며, 인증된 외부 provider/orchestrator만 검증된 artifact hash와 attestation을 확인한 뒤 별도 신뢰 경계에서 `passed`로 승격할 수 있다. 외부 승격이 없으면 완료 보고도 로컬 상태 그대로 유지한다.

스크린샷을 보지 않았는데 “시각적으로 검증됨”, 실행하지 않았는데 “반응형 완료”, placeholder를 실제 제품 증거처럼 보고하는 행위는 금지한다.

## 1. Context and fingerprint

먼저 프로젝트 truth를 읽는다.

- 제품/브랜드 문서, route/flow 문서, 대표 화면.
- token/theme, app shell, 공통 component.
- `package.json` 또는 `pubspec.yaml`과 실제 설치된 design system.
- 기존 UI의 유지 대상과 개선 대상.
- redesign이면 SEO, analytics, legal copy, form field, URL contract.

런타임을 시작한다.

```bash
python3 .claude/skills/design-harness/scripts/design-runtime.py init \
  --root . \
  --mode craft \
  --surface "<surface>" \
  --register product \
  --implementation-actor-id "worker:<execution-id>" \
  --critic-public-key "<trusted-ed25519-public-key>" \
  --design-read "Reading this as: <surface> for <audience>, in <scene>, using <register>, with <stance>, avoiding <risk>." \
  --dials 4,2,8,8,9 \
  --slop-risk "<primary risk>" \
  --route /target \
  --state default --state loading --state empty --state error --state focus
```

`references/runtime-v3.md`에 artifact와 명령 계약이 있다.

## 2. Design Read and five dials

항상 한 문장으로 읽기를 고정한다.

```text
Reading this as: <surface> for <audience>, in <scene>, using <register>, with <visual stance>, avoiding <main slop risk>.
```

두 방향이 제품 결과를 실질적으로 바꿀 때만 짧게 질문한다. 나머지는 관찰 가능한 근거와 가정을 기록하고 진행한다.

| Dial | 1–3 | 4–7 | 8–10 |
|---|---|---|---|
| `DISTINCTION` | familiar | context-specific | highly authored |
| `MOTION` | feedback only | subtle choreography | advanced narrative/physics |
| `DENSITY` | sparse | balanced | compact/operational |
| `EVIDENCE` | text-led | mixed proof | proof/state-led |
| `SYSTEMNESS` | bespoke | token-guided | official/strict system |

다이얼은 미학 preset이 아니다. 구현과 evidence 양을 제한하는 계약이다. 예를 들어 `EVIDENCE=9`인데 실제 화면/데이터가 없으면 완료할 수 없다.

## 3. Choose the correct register

`references/registers.md`를 full screen/page/app shell/redesign에서 읽는다.

- `product`: 반복 작업, 예측 가능한 controls, 모든 상태, restrained color.
- `operational`: 비교와 처리 속도, density, keyboard flow, 데이터 신뢰성.
- `brand`/`campaign`: 기억 가능한 관점, 실제 asset, layout variation, 구체적 copy.
- `public-sector`: 공식 시스템, 접근성, plain language, 오류 복구.
- `editorial`: typography, pacing, source integrity.
- `design-system`: token/component contract.
- `asset`: art direction만 이 runtime이 소유하고, image prompt는 `image-prompt`가 소유한다.

Dashboard에 brand-page novelty를 강요하거나 campaign page를 admin UI처럼 채점하지 않는다.

## 4. Mode and reference routing

| Mode | Use | Load |
|---|---|---|
| `shape` | 코드 전 방향/IA | `design-read.md`, `workflows.md` |
| `reference` | 원칙 추출과 anti-imitation | `design-reference-index.md`, `anti-slop.md` |
| `measure` | URL/screenshot에서 측정 가능한 token 추출 | `reference-style-extraction.md` |
| `craft` | 새 surface 구현 | `registers.md`, `anti-slop.md`, `preflight.md` |
| `audit` | 읽기 전용 UX/a11y/visual review | `workflows.md`, `preflight.md` |
| `polish` | 출시 전 교정 | `interface-polish.md`, `motion-interaction.md` |
| `redesign` | 기존 계약을 보존한 현대화 | `redesign-protocol.md`, `anti-slop.md` |
| `typeset` / `colorize` | type/color token | `registers.md`, 필요 시 `korean-typography` |
| `animate` | 목적 있는 motion | `motion-interaction.md` |
| `harden` | state/overflow/mobile/i18n | `preflight.md`, `korean-ui.md` |

## 5. Execute through the detected platform

```bash
python3 .claude/skills/design-harness/scripts/design-runtime.py plan --root .
```

- Web: 기존 framework와 component system을 보존한다. 구현은 `ckm:ui-styling`; 기술 선택은 project profile과 tech-stack registry를 따른다. shadcn/Tailwind/Motion을 기본값으로 가정하지 않는다.
- Flutter: 기존 Theme/Material/Cupertino와 Flutter skills를 따른다. `flutter analyze`, test/golden/integration evidence, 실제 device/simulator state를 사용한다.
- Official system이 맞는 제품은 `design-system-map.md`와 공식 문서를 우선한다.
- Raster image generation은 반드시 exact-vendored `image-prompt`로 compile/validate한 뒤 Codex `$imagegen` host contract(required model `gpt-image-2`)만 사용한다. `full_prompt`는 host tool의 `prompt`로 매핑하며, 이 skill에서 별도 prompt를 만들지 않는다.
- 실제 product screenshot, deterministic SVG/vector, browser/device capture는 이미지 생성이 아니며 그대로 검증한다.

Platform별 evidence와 포착 규칙은 `references/platform-adapters.md`를 읽는다.
Web은 `capture-web-evidence.mjs`, Flutter는 `capture-flutter-evidence.py`로 실제 artifact index를 만들고 `design-runtime.py import-index`로 등록한다.

## 6. Mechanical and visual gates

변경 UI 경로를 scan한다.

```bash
node .claude/skills/design-harness/scripts/detect-design-slop.mjs \
  --format json --fail-on hard-fail \
  --output .design-runs/<run>/source-scan.json \
  src app components lib
```

Detector는 `.dart`를 포함하고 JSON/SARIF를 출력한다. 존재하지 않는 target과 scan 대상 0개는 실패다. warning은 맥락 검토 항목이지만 hard-fail은 수정 전에 승격할 수 없다. 정적 scan 통과는 시각 품질 통과가 아니다.

각 대상 route/screen에서 최소한 다음을 포착한다.

- 계획된 viewport별 default state.
- scope에 있는 loading, empty, error, disabled/focus 상태.
- Web은 접근성 tree 또는 동등한 audit evidence.
- Flutter는 analyze/test log와 screenshot/golden 또는 integration capture.
- redesign은 비교 가능한 baseline.

Promotion artifact는 `design-runtime.py capture`가 canonical adapter를 직접 실행해 등록한다. 직접 adapter 실행 뒤 `import-index`를 호출하거나 `add-evidence`를 사용하는 경로는 manual/diagnostic로 표시되며 hard gate를 충족하지 못한다. 외부 trust-store authority의 `design-capture-attestation-v1`도 없으면 review packet을 만들 수 없다. 자세한 예시는 `runtime-v3.md`를 따른다.

## 7. Independent critic and bounded repair

구현자는 자기 결과를 최종 승인할 수 없다. critic에게 implementation rationale 대신 run, screenshots, state coverage, detector output을 제공한다. 외부/병렬 worker로 repo context를 보낼 때는 `context-pack-gate`를 먼저 통과한다.

critic에게 넘기기 전에 외부 authority가 canonical capture를 서명하고, `design-runtime.py prepare-review --capture-attestation ...`로 live detector 결과와 evidence hash를 묶은 immutable review packet을 만든다. critic 결과는 그 packet hash를 인용해야 하며, 외부 critic/orchestrator는 같은 trust-store authority로 검증할 수 있는 별도 critic attestation을 발급한다.

Critic은 다음만 보고한다.

- evidence에 보이는 구체적 observation.
- severity와 평가 axis.
- 영향을 받는 evidence ID.
- 가장 작은 coherent repair.
- `pass | repair | fail | blocked`.

Repair는 최대 2회다. 전체를 취향대로 다시 디자인하는 open-ended loop는 금지한다. `references/critic-loop.md`를 따른다.

## 8. Final executable evaluation

```bash
python3 .claude/evals/ui-design/grader.py self-test
python3 .claude/skills/design-harness/scripts/design-runtime.py finalize \
  --run <design-run.json> \
  --critic <critic-result.json> \
  --attestation <critic-attestation.json> \
  --output <finalization-result.json>
```

평가 가중치는 register마다 다르다. `Originality 35%` 같은 단일 보편 기준을 사용하지 않는다.
이 명령의 성공 결과는 `ready_for_external_promotion`이다. 로컬 명령 성공을 `passed`로 바꾸어 말하지 않는다.

## Anti-slop failure classes

`references/anti-slop.md`를 구현/리뷰에서 읽는다.

1. Category reflex.
2. Layout reflex.
3. Content slop.
4. Evidence slop.
5. Polish/state slop.
6. Evaluation slop — screenshot/flow 없이 “좋다”고 채점.

기본 대응은 “더 예쁘게”가 아니다. register, evidence, official system, source detector, state coverage 중 실패한 gate로 되돌린다.

## Handoff

최종 보고에는 다음만 포함한다.

- Design Read와 5 dials.
- 바뀐 핵심 결정.
- 실행한 플랫폼 검증.
- detector/evidence/critic/eval 결과 경로.
- 로컬 상태(`ready_for_external_promotion`까지)와 외부 promotion 여부.
- diagnostic approval과 남은 위험. waiver가 남아 있으면 `passed`가 아니다.

완료되지 않은 evidence를 완료처럼 표현하지 않는다.

## Legacy policy

- `ui-ux-pro-max`, `design-craft`, `ui-design-agent-skills/*`는 archive이며 활성 지침이 아니다.
- UI agent의 `minimal/modern/bold` template strategy는 비활성 legacy 참고자료다. category-to-style routing에 사용하지 않는다.
- active implementation owner는 `ckm:ui-styling`이고, 방향과 검증 owner는 `design-harness`다.
