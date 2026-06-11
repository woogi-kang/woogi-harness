# AI Marketing OS Redesign QA Audit

검토 대상: `docs/260611-ai-marketing-os-redesign/index.html`

## High-Impact Fixes Applied

| Before | After | Why |
|---|---|---|
| `#view` 해시 직접 진입 시 모바일에서 숨겨진 섹션 위치로 스크롤됨 | `?view=` 진입 지원과 manual scroll restoration 적용 | 화면별 QA 링크와 실제 공유 링크가 항상 상단에서 시작해야 함 |
| 모바일 버튼/탭 높이가 44px보다 작아질 수 있음 | 모바일에서 `.btn`, `.tab`, `select` 최소 높이 44px 적용 | 터치 타깃 접근성 기준 충족 |
| Hook table의 긴 risk tag가 데스크톱에서 오른쪽으로 잘림 | 데스크톱 표 `min-width: 100%`, 마지막 컬럼 최소 폭 보강 | 상태/리스크 정보는 잘리면 안 되는 핵심 정보 |
| 모바일 표가 가로 스크롤 표로 보여 핵심 컬럼이 잘림 | 모바일 표를 카드형 행으로 전환 | 좁은 화면에서 source, score, status를 모두 읽을 수 있어야 함 |
| Performance chart 막대가 보이지 않거나 모바일에서 우측으로 밀림 | 차트 막대 렌더링 수정, 모바일 4열 고정 chart 적용 | 성과 화면의 주 시각 요소가 즉시 보여야 함 |
| 모바일 editor 본문이 부모 폭을 밀어 제목/문단이 잘림 | 모바일 draft 텍스트 폭과 줄바꿈 규칙 보강 | 긴 한국어 제목과 본문이 viewport 밖으로 나가지 않아야 함 |
| 모바일 nav active item이 오른쪽에서 일부만 보임 | 모바일 nav를 300px 2열 grid로 고정 | 모든 화면 진입점과 현재 화면 상태가 항상 보여야 함 |

## Screen Audit

| Screen | Desktop | Mobile | Notes |
|---|---|---|---|
| Dashboard | Pass | Pass | 운영 신호, 결재선, 큐 보드의 밀도와 우선순위가 명확함 |
| Knowledge Base / Content Import / DNA | Pass | Pass | 모바일에서 테이블 카드형으로 전환되어 공개 등급과 출처가 읽힘 |
| Hook Library / Research Run | Pass | Pass | risk tag 잘림 해결, 원문/변형/위험 구조가 유지됨 |
| Content Calendar | Pass | Pass | 모바일에서 일자 column이 세로 리스트로 자연스럽게 접힘 |
| Content Editor | Pass | Pass | 모바일 긴 제목/본문 잘림 해결, evidence rail은 아래로 접힘 |
| Review Queue / Manual Publish | Pass | Pass | blocker/action/status가 모바일 카드형으로 읽힘 |
| Performance Log | Pass | Pass | 차트 막대 렌더링 복구, 모바일은 2줄 chart로 안전하게 표시 |

## Component Audit

| Component | Status | Notes |
|---|---|---|
| Sidebar nav | Pass | 데스크톱 상태/카운트/그룹 구조 명확함 |
| Mobile nav | Pass | 2열 grid로 overflow 제거, active state 유지 |
| Topbar actions | Pass | 모바일 44px touch target 보강 |
| Section headers | Pass | CTA와 상태 badge가 명확하게 분리됨 |
| Signal cards | Pass | 숫자, 설명, 상태 bar hierarchy 유지 |
| Queue cards | Pass | repeated item card로만 사용되어 nested-card 문제 없음 |
| Tables | Pass | 데스크톱은 표, 모바일은 카드형 row로 전환 |
| Tags/status chips | Pass | approved/review/danger/research color semantics 일관 |
| Editor split pane | Pass | 데스크톱은 split, 모바일은 stacked flow |
| Review rail/checklist | Pass | evidence/safety/next action 구조 유지 |
| Chart | Pass | desktop 7-day bar, mobile 4-column wrapped chart |

## Verification

- `node .claude/skills/design-harness/scripts/detect-design-slop.mjs docs/260611-ai-marketing-os-redesign`
- `git diff --check -- docs/260611-ai-marketing-os-redesign/index.html docs/260611-ai-marketing-os-redesign/review.md`
- Chrome headless screenshots generated for all 7 screens at `1440x1000` and `390x844`.
