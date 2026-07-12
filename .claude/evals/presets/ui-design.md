# UI/Design Eval Preset v3

UI 평가는 취향 점수 하나로 통과시키지 않는다. `design-harness`의 `design-run-v3`, 해시된 evidence manifest, 기계적 source scan, 실제 화면/상태 증거, 독립 critic을 먼저 확인한 뒤 register별 축을 채점한다.

실행 가능한 기준과 가중치는 `.claude/evals/ui-design/eval.md`와 `.claude/evals/ui-design/grader.py`가 source of truth다.

## Evidence packet

필수 근거:

- `design-run.json`: Design Read, register, 5 dials, project fingerprint, 대상 route/state/viewport.
- `evidence-manifest.json`: baseline/result screenshot, source scan, accessibility 또는 Flutter test evidence.
- `source-scan.json`: `design-slop-scan-v2` 결과.
- `critic-result.json`: 구현자와 독립된 reviewer가 evidence ID를 인용한 결과.
- register별 scores: 각 점수에 evidence ID와 rationale 포함.

다음은 점수 근거가 아니다.

- 개인 취향이나 유행 선호.
- 브랜드·회사·작성자 인지도.
- 실제 캡처되지 않은 화면/상태 추측.
- “프로덕션급”, “고급스럽다”, “독창적이다” 같은 자기평가.
- prompt 또는 구현 설명만 있고 artifact가 없는 주장.

## Register별 평가 축

### Product

| Axis | Weight | 보는 것 |
|---|---:|---|
| Usability | 25% | 핵심 작업의 발견성, 순서, 피드백, 복구 |
| State completeness | 20% | loading/empty/error/disabled/focus와 edge state |
| Craft | 20% | 위계, spacing, contrast, responsive, component rigor |
| Accessibility | 15% | keyboard, semantics, focus, contrast, reduced motion |
| Evidence truth | 10% | 실제 데이터/컴포넌트/스크린샷, 허위 주장 부재 |
| Distinction | 10% | 제품 맥락에 맞는 authored decision; novelty 자체가 목적은 아님 |

### Operational

| Axis | Weight | 보는 것 |
|---|---:|---|
| Task efficiency | 25% | 반복 업무 속도, 비교, keyboard path, action proximity |
| Density readability | 20% | 정보 밀도와 scanability의 균형 |
| State completeness | 20% | 실패/빈 상태/권한/대량 처리/부분 성공 |
| Craft | 15% | 정렬, 숫자, table/list overflow, token 일관성 |
| Accessibility | 10% | keyboard, focus, semantics, contrast |
| Evidence truth | 10% | 실제 data shape와 검증 가능한 상태 |

### Brand

| Axis | Weight | 보는 것 |
|---|---:|---|
| Register fit | 15% | audience, scene, brand promise와 시각 문법의 일치 |
| Distinction | 25% | category reflex가 아닌 기억 가능한 authored stance |
| Evidence truth | 20% | 실제/정당한 visual asset과 검증 가능한 claim |
| Craft | 20% | typography, composition, color, responsive, motion 완성도 |
| Accessibility | 10% | contrast, keyboard, semantics, reduced motion |
| Narrative | 10% | fold/section 간 메시지 진행과 CTA 명확성 |

`campaign`, `public-sector`, `editorial`은 실행 grader의 별도 가중치를 사용한다. 공공 surface에서 originality를 35%로 두거나 운영 화면에 brand-page novelty를 강요하지 않는다.

## Hard gates

- 미해결 detector `hard-fail`.
- 플랫폼 필수 evidence 누락.
- 독립 critic 누락 또는 독립성 불명.
- critic `fail`/`blocked`.
- 어떤 축이든 5점 미만.
- weighted score 7.0 미만.
- project fingerprint/evidence hash drift.
- repair 2회 초과.

점수가 높아도 hard gate를 덮을 수 없다. 근거가 일부면 `needs_review`; 완료로 보고하지 않는다.

## 출력

`.claude/evals/presets/evaluation-result-schema.md`의 `evaluation-result-v1`을 사용한다. `included_signals`에는 실제 파일/명령/스크린샷만 넣고, 각 축은 반드시 해당 evidence ID를 인용한다.

```bash
python3 .claude/evals/ui-design/grader.py self-test
python3 .claude/evals/ui-design/grader.py grade \
  --run <run.json> --evidence <manifest.json> --critic <critic.json> \
  --detector <source-scan.json> --scores <scores.json> --output <result.json>
```
