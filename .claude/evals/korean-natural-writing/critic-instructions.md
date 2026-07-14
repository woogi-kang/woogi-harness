# Independent Korean Writing Critic

원문과 편집 계약을 기준으로 익명 후보 하나를 평가한다. 후보 입력에는 `## 완성본`에서 추출한 본문만 사용한다. 후보를 만든 모델, 스킬 사용 여부, 작성 횟수, `## 다듬은 기준`을 비롯한 작성자의 설명은 보지 않는다.

## 평가 순서

1. 사실, 조건, 부정, 책임 주체, 고유명사, 수치, 날짜, 링크, 인용, 코드 식별자의 변화를 찾는다.
2. 원문에 없던 통계, 성과, 후기, 감정, 장면이 추가됐는지 찾고 모든 의미 변화를 `semantic_deltas`에 기록한다.
3. `required_meaning`을 항목별로 대조하고 후보의 실제 구간을 `required_meaning_coverage`에 인용한다. task, genre, register도 `contract_checks`에서 각각 확인한다.
4. `semantic_deltas`에 `licensed=false`가 있거나 의미·계약 항목이 하나라도 빠지면 `hard_gate.passed=false`로 둔다. 더 자연스럽다는 이유로 의미 변화를 절제 점수에만 반영하지 않는다.
5. hard gate를 통과한 경우에만 아래 축을 각각 1–5점으로 평가한다. 실패한 경우 `scores`는 빈 객체로 두고, 의미 보존 실패를 입증하는 `semantic_deltas`, `required_meaning_coverage`, `contract_checks`, `findings`만 기록한다.
   - `naturalness`
   - `genre_register_fit`
   - `voice_specificity`
   - `discourse_rhythm`
   - `editing_restraint`
6. hard gate를 통과한 후보는 다섯 점수 축마다 후보의 실제 구간, 독자에게 미치는 영향, 수정 의도를 최소 하나씩 기록한다. 실패 후보는 `meaning_preservation` finding을 최소 하나 기록한다.

문장이 짧거나 유창하다는 이유만으로 높은 점수를 주지 않는다. 장황함, 권위적 어조, 화려한 수사, 상투어 제거 개수도 품질의 대리 지표가 아니다.
hard gate를 통과한 후보의 `findings`에는 다섯 점수 축마다 실제 후보에서 가져온 구간을 최소 하나 넣는다. 수정할 문제가 없는 축이라면 가장 중요한 유지 근거를 인용하고 `edit_intent`에 `유지`라고 쓴다. 실패 후보의 문체 점수는 의미 실패를 상쇄하거나 비교 승자의 근거로 사용할 수 없다.
의미 차이가 없으면 `semantic_deltas`를 빈 배열로 둔다. 각 excerpt는 원문과 후보에 실제로 존재하는 연속 문자열이어야 한다.
`semantic_deltas[].axis`는 변화의 의미 차원을 짧은 영문 `snake_case`로 적는다. `scope`, `modality`, `negation`, `actor`, `temporal_scene`, `interpretation`, `discourse_mode`, `register`, `fixed_element`를 우선하고, 사례에 더 정확한 차원이 필요하면 `promotional_urgency`, `relationship_register`처럼 구체화한다. `naturalness` 같은 아래 품질 점수 축을 의미 변화 축으로 재사용하지 않는다.
`required_meaning_coverage[].requirement`는 case의 문구와 글자 단위로 같아야 한다. 통과 항목의 `evidence`와 통과한 `contract_checks`의 `evidence`는 후보에 실제로 존재하는 연속 문자열이어야 한다.

## JSON 출력

```json
{
  "hard_gate": {
    "passed": true,
    "failures": []
  },
  "scores": {
    "naturalness": 4,
    "genre_register_fit": 4,
    "voice_specificity": 4,
    "discourse_rhythm": 4,
    "editing_restraint": 4
  },
  "required_meaning_coverage": [
    {
      "requirement": "case required_meaning의 실제 항목",
      "passed": true,
      "evidence": "후보의 실제 근거 구간"
    }
  ],
  "contract_checks": {
    "task": {"passed": true, "evidence": "후보의 실제 근거 구간"},
    "genre": {"passed": true, "evidence": "후보의 실제 근거 구간"},
    "register": {"passed": true, "evidence": "후보의 실제 근거 구간"}
  },
  "semantic_deltas": [
    {
      "source_excerpt": "원문의 실제 구간",
      "candidate_excerpt": "후보의 실제 구간",
      "axis": "scope",
      "licensed": true,
      "reason": "편집 계약이 이 변화를 허용한 이유"
    }
  ],
  "findings": [
    {
      "excerpt": "평가한 실제 구간",
      "axis": "naturalness",
      "impact": "독자가 겪는 구체적 문제",
      "edit_intent": "실행 가능한 편집 의도"
    }
  ],
  "verdict": "pass",
  "confidence": 0.8
}
```

`verdict`는 `pass`, `fail`, `needs_human_review` 중 하나다. 근거가 부족하거나 원어민 사이에서도 판단이 갈릴 만한 사용역이면 `needs_human_review`를 사용한다.
위 JSON은 hard gate 통과 예시다. 실패 출력은 `scores`를 `{}`로 두고 `findings[].axis`에 `meaning_preservation`을 사용한다.
