# Korean Natural Writing Eval

한국어 산문·카피·스토리텔링·실무문을 자연스럽게 고치면서 의미와 고정 요소를 보존하는지 평가한다. 표현 하나의 유무나 AI 탐지기 점수로 합격시키지 않는다.

## 사례 구성

- 산문 3개: 범용 도입, 과도한 교훈, 이미 좋은 원문의 과수정 방지
- 카피 3개: SaaS 히어로, 기한·가격 CTA, 제품 마이크로카피
- 스토리텔링 3개: 감정 설명, 가족 대화의 높임, 결말의 강제 교훈
- 실무문 3개: 기술 번역투, 지원서 근거, 부정문이 많은 요금 안내

각 사례는 `input`, `task`, `required_meaning`, `constraints`, `advisory_focus`를 가진다. 출력 형식은 모든 사례에 공통으로 `## 완성본`, `## 다듬은 기준`을 사용하며 정답 문장 하나를 저장하지 않는다.
최소 글자 수는 핵심 내용이 통째로 빠진 출력을 찾는 안전장치일 뿐이다. 자연스러운 삭제를 막거나 문장을 채우도록 강요하는 기준으로 쓰지 않는다.

## 실행

후보를 파일로 저장한 뒤 deterministic gate를 실행한다.

```bash
python3 .claude/evals/korean-natural-writing/grader.py \
  --case .claude/evals/korean-natural-writing/cases/01-essay-generic-opening.json \
  --candidate /path/to/candidate.md \
  --output /tmp/korean-writing-eval.json
```

비평자 JSON이 있으면 함께 집계한다.

```bash
python3 .claude/evals/korean-natural-writing/grader.py \
  --case <case.json> --candidate <candidate.md> \
  --critic <critic.json> --output <evaluation-result.json>
```

`--critic`이 없으면 deterministic gate가 통과해도 `needs_review`다. 문체 품질은 자동 패턴 수만으로 확정하지 않는다.
CLI 종료 코드는 `pass=0`, `fail=1`, `needs_review=2`다. 검토 대기 결과를 CI 성공으로 취급하지 않는다.

## 비교 실험

각 사례에 같은 task를 사용해 다음을 만든다.

1. `without_skill`: 별도 스킬 없이 작성
2. `with_skill`: `korean-natural-writing`을 읽고 작성. 깊은 윤문은 장르 편집본과 보존 편집본을 서로 보지 않은 문맥에서 만든 뒤, 관점 이름을 숨긴 비평자가 순서를 바꿔 비교하고 검증된 후보 또는 패치만 합친다.

비평자에게는 원문, 제약, 익명 후보의 `## 완성본` 본문만 제공한다. `## 다듬은 기준`, 모델·스킬·반복 횟수, 작성 과정은 블라인드 파일에 넣지 않는다. 먼저 각 후보를 pointwise로 평가한 뒤 A/B/Tie를 판단하고, 후보 위치를 바꿔 다시 판단한다. 두 순서의 승자가 다르거나 pointwise 비평자가 `needs_human_review`를 반환하면 사람 검토로 보낸다.

## 합격 기준

- 12개 사례 모두 deterministic hard gate 통과
- 12개 `with_skill` 후보 모두 독립 비평의 의미 hard gate 통과
- 자연스러움·장르 적합성·담화 리듬이 각 4/5 이상인 사례가 10개 이상
- `with_skill`이 블라인드 비교의 비동률 사례 중 75% 이상 승리
- 순서 교환 결과가 일치하거나 유효한 사람 판정으로 해소된 비동률 사례가 최소 8개이고, 해소되지 않은 순서 불일치가 없음
- 과수정 방지 사례 2개에서 원문 의미, 수치, 부정, 책임 주체의 변화가 없고 `editing_restraint`, `voice_specificity`가 각각 4/5 이상
- 순서 교환 불일치와 사람의 Tie는 판정 파일 없이 억지로 승패에 넣지 않음

순서 불일치가 있더라도 사람 검토로 모두 뒤집었을 때 75% 승률에 도달할 수 없다면 `needs_human_review`로 실패를 미루지 않고 `fail`로 판정한다.

첫 12개 결과는 calibration 결과다. 사용자 블라인드 검토 전에는 capability 상태를 `experimental`로 유지한다.
같은 사례를 보고 구조를 고친 뒤 다시 실행한 결과는 회귀 점검이지 새 holdout이 아니다. `stable` 승격에는 작성 과정에서 사용하지 않은 사례와 실제 사용자 원고의 블라인드 검토가 모두 필요하다.

12개 결과와 순서 교환 비교를 한 번에 집계한다.

```bash
python3 .claude/evals/korean-natural-writing/aggregate.py \
  --cases-dir .claude/evals/korean-natural-writing/cases \
  --run-dir /path/to/iteration \
  --mapping /path/to/blind-mapping.json \
  --metadata /path/to/experiment-metadata.json \
  --human-review /path/to/human-review.json \
  --output /path/to/benchmark.json
```

사람 검토가 아직 없으면 `--human-review`를 생략한다.

각 실행 디렉터리는 `<case-id>/<variant>/evaluation-result-deterministic.json`, `<case-id>/<variant>/evaluation-result.json`을 가진다. 익명 디렉터리는 `blind/<case-id>/A.md`, `B.md`, `comparison-first.json`, `comparison-swapped.json`을 가진다. `A.md`와 `B.md`에는 원본 `candidate.md`에서 추출한 `## 완성본` 본문만 저장한다. 제목과 `## 다듬은 기준`은 제외하며, 후보 해시·인용·사람 검토도 이 본문만 기준으로 삼는다. 두 비교 파일의 `winner`는 화면 위치가 아니라 익명 후보 ID `A`, `B`, `Tie` 중 하나로 기록한다.

비교 JSON에는 `decisive_axes`, 후보 A/B의 실제 인용과 독자 효과를 담은 `candidate_evidence`, 두 pointwise critic의 SHA-256을 담은 `pointwise_critic_sha256`이 필요하다. 집계기는 인용이 실제 후보에 있는지, critic hash가 맞는지, 의미 hard gate를 실패한 후보가 승자로 선택되지 않았는지 확인한다. 한 후보만 의미 gate를 통과하면 그 후보만 비교 적격이며, 둘 다 실패하면 사례 전체가 실패한다.

후보 생성을 시작하기 전에 다음 명령의 일곱 해시를 실행 메타데이터에 그대로 고정한다.

```bash
python3 .claude/evals/korean-natural-writing/aggregate.py --print-provenance
```

메타데이터에는 `provider`, `model`, `created_at`, `iteration`, `critic_protocol`, `token_usage`, `latency`, `skill_sha256`, `grader_sha256`, `analyzer_sha256`, `critic_instructions_sha256`, `eval_protocol_sha256`, `aggregate_sha256`, `case_set_sha256`을 기록한다. 호스트가 토큰이나 지연 시간을 노출하지 않으면 값을 추정하지 말고 `{ "status": "unavailable", "reason": "..." }`로 남긴다. 집계기는 생성 시 해시와 현재 스킬·평가기·비평 지침·비교 프로토콜·집계기·사례 해시가 같은지 확인하고, 다르면 과거 후보를 현재 버전의 결과로 인정하지 않는다. `evaluation-result.json`의 후보 경로도 실제 실행 디렉터리의 `candidate.md` 경로와 일치해야 한다.

순서 불일치, Tie, pointwise `needs_human_review`를 사람이 판정했다면 `--human-review <json>`을 추가한다. 파일은 `schema: korean-natural-writing.human-review.v2`, `reviewer`, `reviewer_type: human`, `attestation: human_direct_review`, `created_at`, `cases`를 가진다. 에이전트나 모델은 이 파일을 사람 검토로 대신 작성하지 않는다. 각 사례에는 `winner`, `rationale`, `case_sha256`, A/B `candidate_sha256`, `pointwise_critic_sha256`, `decisive_axes`, 실제 완성본을 인용한 `candidate_evidence`를 기록한다. 집계기는 모델의 두 비교를 보존한 채 reviewable 사례에만 사람 판정을 적용하고, 사례·후보·비평 해시가 다르거나 의미 gate를 실패한 후보를 고르면 중단한다.

## 기록

결과는 `evaluation-result-v1`을 사용한다. 모델/provider, 스킬 SHA, case set SHA, 출력 토큰, 지연, 반복 횟수, 원문·후보 경로를 함께 기록한다. 공개 저장소에는 비공개 사용자 원문을 커밋하지 않는다.
각 평가 결과에는 canonical case, 후보 원문, 독립 비평 JSON의 SHA-256을 저장한다. 집계기는 현재 파일과 해시·case ID·rubric·schema가 모두 일치하는지 확인하고, 다른 사례나 이전 후보의 결과 JSON을 재사용하면 중단한다.
