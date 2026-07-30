# 한국어 AI 흔적 보조 카탈로그

이 카탈로그는 AI 작성 여부를 판정하는 목록이 아니다. 반복되는 번역투·상투어·서식 공식을 찾아 사람이 문맥을 다시 보게 하는 보조 기준이다. 한 표현이 나왔다는 이유만으로 고치거나, 플래그 수를 자연스러움 점수로 환산하지 않는다.

## 사용 원칙

1. `source_span`, 반복 횟수, 장르 적합성, 독자 훼손을 함께 기록한다.
2. 한 번의 저확신 신호보다 같은 구간에 겹친 신호를 먼저 본다.
3. 고유명사, 수치, 인용, 코드 식별자와 작성자의 구체적인 곁말은 보존한다.
4. 서식만 문제면 산문을 다시 쓰지 않는다.
5. 탐지 결과로 AI 작성 여부를 단정하지 않는다.

## 선별 신호

| ID | 신호 | 기본 강도 | 검토 기준 |
|---|---|---|---|
| `have_calque` | 의미·중요성·영향력을 `가지다`로 표현 | high | 더 정확한 형용사나 동사가 있는지 본다. |
| `plural_suffix_pileup` | 문맥상 분명한 복수에 `-들` 반복 | medium | 수량어와 복수 표지가 겹치는지 본다. |
| `stacked_particle` | `에서의`, `으로의`, `에의`, `로부터의` | high | 절이나 동사로 풀면 역할이 선명해지는지 본다. |
| `connective_comma` | `-고,`, `-며,`, `-지만,` 반복 | medium | 쉼표가 실제 의미 단위를 나누는지 본다. |
| `chatbot_residue` | `좋은 질문이에요`, `도움이 되었으면` | high | 대화 응대가 독립 원고에 섞였는지 본다. |
| `formulaic_closing` | `행보가 기대된다`, `귀추가 주목된다` | high | 앞선 근거 없이 전망이나 교훈이 붙었는지 본다. |
| `hype_lexicon_cluster` | `다채로운`, `자리매김`, `방증` 등 반복 | high | 평가어를 지웠을 때 남는 사실이 있는지 본다. |
| `vague_authority` | `전문가들은`, `많은 사람이`, `알려져 있다` | medium | 구체 출처나 판단 주체가 있는지 본다. |
| `hedging_stack` | 추정·미래·안전 표현 누적 | medium | 가능성, 의무, 확신의 강도가 구분되는지 본다. |
| `english_parenthetical_pileup` | 한글 뒤 영어 괄호 병기 반복 | medium | 첫 등장 이후에도 병기가 필요한지 본다. |
| `decorative_dash_cluster` | em/en dash 반복 | low | 장르상 정상 편집 부호인지 먼저 확인한다. |
| `emoji_decoration_cluster` | 제목·항목 앞 이모지 반복 | low | 장식이 정보 위계를 대신하는지 본다. |
| `bold_label_list` | `- **머리말:**` 구조 반복 | low | 보고서·매뉴얼의 정상 형식인지 먼저 확인한다. |
| `colon_heading_repetition` | `제목: 부제` 헤딩 반복 | low | 모든 헤딩이 같은 공식으로 평평해졌는지 본다. |

`low` 신호는 단독으로 수정 근거가 되지 않는다. 기술 문서, 법률 문서, 매뉴얼, 소셜 게시물처럼 서식 관습이 강한 장르에서는 같은 표지가 정상일 수 있다.

## 출처와 흡수 경계

카탈로그는 다음 공개 자산에서 한국어 특화 관찰을 선별해 재구성했다.

- [NomaDamas/k-skill `korean-humanizer`](https://github.com/NomaDamas/k-skill/tree/42473dad91ca919fd21d6d8b7fc6dbae3fa48b2c/korean-humanizer), MIT
- [epoko77-ai/im-not-ai](https://github.com/epoko77-ai/im-not-ai), MIT
- [blader/humanizer](https://github.com/blader/humanizer), MIT

원본의 `S1 한 번이면 AI 확신`, 보편적인 줄표 금지, 자기평가 등급, 정의되지 않은 변경률 기준은 가져오지 않는다. Woogi Harness에서는 모든 신호를 advisory로 유지하고, 장르 계약·의미 보존 hard gate·독립 비평보다 앞세우지 않는다.
