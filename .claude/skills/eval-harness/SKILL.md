---
name: eval-harness
description: "Evidence-backed Eval Harness v2. 행동/산출물 품질을 executable cases, deterministic checks, 독립 model/human critic, typed outcome, 회귀 결과로 검증한다. shell exit 0이나 자기평가만으로 성공 처리하지 않으며 UI/디자인은 Design Runtime v3 evidence contract를 사용한다."
metadata:
  category: "standalone"
  version: "2.0.0"
  tags: "eval, evidence, testing, grader, regression, quality, typed-outcome"
  author: "woogi"
---

# Eval Harness v2

Eval은 “좋아 보인다”는 의견을 자동화하는 도구가 아니다. 성공 기준을 관찰 가능한 evidence와 실행 가능한 grader로 바꾸고, 주관 판단은 evidence ID를 인용하는 독립 평가로 분리한다.

## Contract

```text
Objective + cases
→ evidence packet
→ deterministic grader
→ independent model/human grader when needed
→ hard gates + weighted result
→ typed execution outcome
→ regression record
```

다음은 성공 증거가 아니다.

- process exit code 0만 존재.
- 구현자의 “완료”, “프로덕션급” 주장.
- 실행하지 않은 test/build/browser flow.
- 실제 입력·출력·화면 없이 작성한 점수.
- 개인정보, 브랜드 인지도, 작성자 prestige.

## Eval package

```text
.claude/evals/<name>/
├── eval.md
├── grader.py | grader.sh
├── cases/
├── fixtures/          # optional deterministic inputs
└── results/           # optional append-only run records
```

최소 요구:

1. Case ID와 목적.
2. 입력/환경 조건.
3. expected invariant 또는 rubric axis.
4. hard failure.
5. 실제 실행 명령.
6. machine-readable 결과.
7. 재현에 필요한 seed/version/platform 정보.

## Grader order

1. **Deterministic** — schema, exact invariant, build/test, detector, browser/device assertion.
2. **Model-based** — 의미/명료성/시각 품질처럼 deterministic하게 완결할 수 없는 축.
3. **Human** — 사용자 취향, 승인, 법적/브랜드 판단처럼 권한자가 필요한 축.

하위 단계가 상위 hard failure를 덮을 수 없다. 예를 들어 visual score가 높아도 기능 불능이나 접근성 hard gate는 fail이다.

## Evidence packet

`.claude/evals/presets/evaluation-result-schema.md`를 사용한다.

- `included_signals`: 실제 파일, 명령, test log, browser/device flow, screenshot, 사용자 제공 artifact.
- `excluded_signals`: identity, prestige, private data, unsupported context, scope 밖 정보.
- `missing_evidence`: 채점에 필요하지만 확인하지 못한 것.
- 모든 score/finding은 evidence ID를 인용한다.

근거가 부족하면 점수를 추정해 pass시키지 않고 `needs_review`로 둔다.

## Typed outcome integration

Harness execution state는 `pending | running | succeeded | failed | blocked | needs_approval`이다. `succeeded`에는 다음이 필요하다.

- 하나 이상의 success criterion.
- 각 criterion의 passed check.
- 하나 이상의 evidence item.
- 재현 가능한 final outcome document.

```bash
python3 scripts/harness-execution.py validate --file <outcome.json> --final
python3 scripts/harness-execution.py from-exit --exit-code 0 --outcome-file <outcome.json>
```

Outcome file이 없으면 exit 0도 실패다.

## UI/Design

UI는 실제 executable eval이 있다.

```bash
python3 .claude/evals/ui-design/grader.py self-test
python3 .claude/evals/ui-design/grader.py grade \
  --run <design-run.json> --evidence <evidence-manifest.json> \
  --critic <critic-result.json> --detector <source-scan.json> \
  --scores <scores.json> --output <evaluation-result.json>
```

`product`, `operational`, `brand`, `campaign`, `public-sector`, `editorial`은 서로 다른 weight를 사용한다. universal originality score는 사용하지 않는다. Web/Flutter platform evidence와 independent critic이 없으면 pass할 수 없다.

## Other presets

| Preset | Source | Status |
|---|---|---|
| Evaluation result | `.claude/evals/presets/evaluation-result-schema.md` | standard schema |
| UI/Design | `.claude/evals/ui-design/` | executable regression + evidence grader |
| Korean typography | `.claude/evals/korean-typography/` | executable source validator |
| API backend | `.claude/evals/presets/api-backend.md` | rubric; add project-specific executable cases |
| Content | `.claude/evals/presets/content-quality.md` | rubric; add source/fact cases |

Markdown rubric만 있는 preset은 실행 완료 증거가 아니다. 프로젝트별 cases/grader를 추가하거나 상태를 `needs_review`로 둔다.

## Repeated-run metrics

`pass@k = 1 - C(n-c, k) / C(n, k)`는 stochastic generation을 동일 조건에서 여러 번 실행할 때만 사용한다. 한 번 실행한 deterministic build나 UI QA를 pass@k로 포장하지 않는다.

기록에는 model/provider, prompt/skill version, seed 가능 여부, case set hash, 성공 수 `c`, 전체 시도 `n`, `k`를 남긴다. Sample이 작으면 과도한 readiness 결론을 내리지 않는다.

## Workflow

1. 구현 전에 success criteria와 hard gates를 정한다.
2. normal/edge/failure/adversarial cases를 작성한다.
3. 실제 evidence source와 excluded signal을 정한다.
4. deterministic grader를 먼저 작성·실행한다.
5. 주관 축만 독립 model/human grader로 보완한다.
6. `evaluation-result-v1`과 typed execution outcome을 남긴다.
7. 실패 원인을 수정하고 동일 cases로 재실행한다.
8. 안정된 eval을 CI/doctor/project pack에 연결한다.

같은 실패를 점수 조정으로 숨기거나 test fixture를 구현에 맞춰 약화하지 않는다.
