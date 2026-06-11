# CraftOps AI Work OS PRD

## 1. Summary

CraftOps AI Work OS는 사용자의 반복 업무를 자연어 입력에서 실행 가능한 작업 그래프까지 자동 변환하는 개인 AI 운영 시스템이다. Claude Craft의 25+ 에이전트, 340+ 스킬, 슬래시 커맨드, DAG 오케스트레이션을 하나의 업무 실행 계층으로 묶어, 기획, 리서치, 개발, 검증, 콘텐츠, 마케팅 업무 시간을 50% 이상 줄이는 것을 목표로 한다.

핵심 제품은 "작업을 부탁하면 끝까지 굴러가는 AI PM + 오케스트레이터"다. 사용자는 목표만 말하고, 시스템은 컨텍스트 수집, 스킬 선택, 계획 생성, 병렬 실행, 검증, 결과 정리, 학습 반영을 자동으로 처리한다.

## 2. Contacts

| Name | Role | Comment |
| --- | --- | --- |
| Woogi | Owner / Primary User | 첫 고객이자 제품 설계자. 실제 반복 업무 시간을 기준으로 효과를 검증한다. |
| Codex / Claude / Gemini | Execution Runtimes | 각 모델의 강점에 맞게 계획, 구현, 리뷰, 검증을 분배한다. |
| Claude Craft | Core Asset Layer | 에이전트, 스킬, 커맨드, 템플릿, 규칙의 단일 원천이다. |

## 3. Background

현재 Claude Craft에는 이미 강한 자산이 있다.

- 멀티 도메인 에이전트와 340개 이상의 스킬
- `/team`, `/team-launch`, `/orchestrate` 기반 병렬 실행
- 기획, 개발, 디자인, 콘텐츠, 마케팅, 법무, 재무, 한국생활 자동화 범위
- 여러 프로젝트로 스킬을 동기화하는 스크립트
- 내부 감사, 하니스 개선, Multica 연동 계획 등 운영 고도화 문서

문제는 자산의 양이 아니라 실행 전후의 사람 손작업이다. 매번 사용자가 해야 하는 일이 많다.

- 어떤 에이전트와 스킬을 쓸지 판단한다.
- 관련 문서와 저장소 맥락을 직접 모은다.
- 작업을 작은 단위로 나누고 의존성을 정한다.
- 여러 도구와 런타임을 직접 실행한다.
- 결과를 검토하고 부족한 부분을 다시 지시한다.
- 반복되는 성공 패턴을 스킬이나 템플릿으로 저장한다.

따라서 가장 가치 있는 제품은 새 에이전트 하나가 아니다. 이미 있는 에이전트와 스킬을 "자동으로 선택하고 실행하며, 결과를 검증하고, 다음에는 더 잘하게 만드는 운영 계층"이다.

## 4. Objective

### Objective

Woogi의 고빈도 지식 업무에서 사람의 직접 조작 시간을 50% 이상 줄인다.

### Why It Matters

Claude Craft는 이미 자동화 가능한 자산을 많이 갖고 있다. 병목은 실행 자산의 부재가 아니라, 사용자가 매번 해야 하는 조립, 라우팅, 감시, 검증, 재사용화 작업이다. 이 병목을 제거하면 생산성 증가는 선형이 아니라 복리로 쌓인다.

### Key Results

- KR1: 상위 10개 반복 업무의 평균 사람 개입 시간을 50% 이상 감소
- KR2: 자연어 요청에서 실행 가능한 DAG 생성까지 걸리는 시간을 5분 이하로 단축
- KR3: 완료된 작업의 70% 이상이 자동 검증 리포트를 포함
- KR4: 반복 업무 30개 이상을 재사용 가능한 playbook으로 저장
- KR5: 한 달 내 사용자가 직접 수정한 프롬프트, 계획, 체크리스트 수를 50% 이상 감소

## 5. Market Segments

### Primary Segment

AI를 업무 운영 체계로 쓰는 1인 창업가, PM, 개발자, 콘텐츠/마케팅 운영자.

이들은 한 사람이 여러 역할을 동시에 맡는다. 기획, 리서치, 개발, 디자인, 콘텐츠, 세일즈, 운영이 모두 한 사람에게 몰린다. 도구는 많지만, 도구 사이의 연결과 검증은 여전히 사람이 한다.

### Beachhead

Claude Craft의 현재 사용자 자신이다. 이유는 명확하다.

- 에이전트와 스킬 자산이 이미 존재한다.
- 실제 업무 로그와 문서가 저장소에 쌓여 있다.
- 자동화 효과를 시간 단위로 바로 측정할 수 있다.
- 성공하면 같은 구조를 다른 AI 파워 유저에게 판매할 수 있다.

## 6. Value Propositions

### Core Value

"목표만 말하면, AI 팀이 계획하고 실행하고 검증하고 다음에 재사용할 수 있게 만든다."

### Time Savings By Work Type

| Work Type | Current Manual Load | CraftOps Target |
| --- | --- | --- |
| 서비스 기획 | 리서치, PRD, 경쟁 분석, MVP, 로드맵을 직접 연결 | 목표 입력 후 8단계 기획 자동 실행 |
| 개발 | 구현 범위 분해, 에이전트 선택, 테스트 지시 | DAG 생성, 워크트리 실행, 검증 루프 자동화 |
| 콘텐츠/마케팅 | 아이디어, 초안, SEO, SNS 변환, 검토 반복 | 콘텐츠 파이프라인 playbook으로 일괄 생성 |
| 리뷰/감사 | 코드, 보안, 디자인, 콘텐츠 리뷰를 따로 요청 | 리뷰 오케스트레이터 자동 호출 및 통합 리포트 |
| 스킬 관리 | 성공 패턴을 사람이 문서화 | 완료 작업에서 스킬 후보 자동 추출 |

### Differentiation

- 일반 챗봇이 아니라, 로컬 저장소와 실제 워크플로우를 실행하는 시스템이다.
- 프롬프트 모음이 아니라, 에이전트, 스킬, 템플릿, 검증을 가진 운영 레이어다.
- 단일 모델 의존이 아니라 Claude, Codex, Gemini, Multica 같은 런타임을 역할별로 분배할 수 있다.
- 결과물을 만드는 데서 끝나지 않고, 성공 패턴을 다시 스킬과 playbook으로 흡수한다.

## 7. Solution

### Product Name

CraftOps AI Work OS

### Product Concept

로컬 우선 AI 업무 운영 시스템. 사용자는 하나의 인박스에 목표를 적는다. 시스템은 목표를 분류하고, 필요한 컨텍스트를 모으고, Claude Craft의 에이전트와 스킬을 선택하고, 실행 계획을 DAG로 만들고, 각 작업을 런타임에 할당하고, 검증 결과를 모아 최종 산출물을 만든다.

### Core Loop

1. Capture: 사용자가 목표, 자료, 제약을 입력한다.
2. Clarify: 결과가 달라질 핵심 불확실성만 질문한다.
3. Plan: 스킬과 에이전트를 선택하고 작업 그래프를 만든다.
4. Execute: 병렬 워커가 각 작업을 수행한다.
5. Verify: 독립 평가자가 테스트, 리뷰, 체크리스트로 검증한다.
6. Deliver: 산출물, 변경 파일, 의사결정, 다음 액션을 정리한다.
7. Learn: 반복 가능한 패턴을 playbook 또는 skill 후보로 저장한다.

### MVP Features

#### 1. Work Intake

자연어 요청을 받아 업무 유형, 목표, 산출물, 제약, 마감, 참조 문서를 추출한다.

필수 입력:
- 목표
- 기대 산출물
- 관련 프로젝트 또는 문서
- 허용 범위
- 검증 방식

#### 2. Context Pack Builder

작업에 필요한 파일, 문서, 규칙, 과거 산출물을 자동으로 묶는다.

예:
- 기획 업무: 기존 PRD, 시장조사, 경쟁분석, GTM 문서
- 개발 업무: README, CLAUDE.md, 관련 소스, 테스트, 규칙
- 콘텐츠 업무: 브랜드 보이스, SEO 문서, 기존 게시물

#### 3. Router

요청을 에이전트, 스킬, 커맨드로 매핑한다.

출력:
- 선택된 에이전트
- 선택된 스킬
- 필요한 슬래시 커맨드
- 병렬 가능 여부
- 검증 담당

#### 4. DAG Planner

작업을 의존성 그래프로 만든다. `/team`과 `/orchestrate`가 이해할 수 있는 plan.json 또는 TOML로 변환한다.

각 노드는 다음을 가져야 한다.
- task
- owner agent
- input context
- output artifact
- success criteria
- validation method

#### 5. Execution Console

현재 실행 중인 작업, 막힌 작업, 검증 실패, 산출물을 한 화면에서 보여준다.

MVP에서는 웹 대시보드보다 CLI/TUI로 시작한다.

#### 6. Evaluator

완료된 작업을 독립적으로 검증한다.

검증 유형:
- 코드: 빌드, 타입, 린트, 테스트, 보안
- 웹 UI: Playwright 스크린샷, 사용자 플로우
- 기획: PRD 체크리스트, 가정/리스크, 누락 섹션
- 콘텐츠: 톤, SEO, 중복, CTA, 사실성
- 스킬: description, progressive disclosure, 중복, 라우팅 가능성

#### 7. Playbook Memory

완료된 작업에서 반복 가능한 절차를 추출한다.

저장 단위:
- task pattern
- required context
- agent/skill mapping
- default checklist
- known pitfalls
- example output

### Future Features

- 캘린더와 할 일 목록 기반 자동 일일 실행
- 이메일, Notion, GitHub Issues, Google Drive 연동
- 비용과 시간 절감 리포트
- 팀용 권한과 승인 플로우
- SaaS 버전의 playbook marketplace
- Multica 기반 원격 실행 및 이슈 자동 할당

### Non-Goals For MVP

- 모든 업무를 완전 자동화하지 않는다.
- 새 범용 챗 UI를 만들지 않는다.
- 복잡한 팀 권한 관리부터 만들지 않는다.
- 처음부터 SaaS로 만들지 않는다.
- 모든 스킬을 다시 설계하지 않는다.

## 8. Business Model Canvas

### Customer Segments

- AI 네이티브 1인 창업가
- 소규모 제품팀 리더
- 개발과 마케팅을 함께 하는 indie hacker
- 에이전트/스킬 자산을 직접 운영하는 AI 파워 유저

### Value Proposition

- 반복 업무 시간 50% 이상 절감
- AI 도구 전환 비용 감소
- 작업 품질 검증 자동화
- 성공 패턴을 개인 업무 자산으로 축적

### Channels

- Claude Craft 공개 저장소
- 실제 업무 사례 블로그
- X / LinkedIn 빌드 로그
- AI agent workflow 템플릿 배포
- Multica, GitHub, Codex, Claude Code 사용자 커뮤니티

### Customer Relationships

- Solo: 로컬 설치형 self-serve
- Pro: 템플릿과 playbook 구독
- Team: 온보딩, 워크플로우 커스터마이징

### Revenue Streams

- 개인용 Pro 구독: playbook, 대시보드, 자동 학습 기능
- 팀용 라이선스: 사용자 수 또는 워크플로우 수 기준
- 컨설팅: 기존 팀 업무를 CraftOps playbook으로 전환
- 템플릿 마켓: 검증된 업무 그래프 판매

### Key Activities

- 라우팅 정확도 개선
- 실행 그래프 생성
- 검증 루브릭 관리
- playbook 추출
- 런타임 연동 유지

### Key Resources

- Claude Craft 스킬/에이전트 저장소
- 과거 업무 문서와 산출물
- 오케스트레이션 스크립트
- 평가 루브릭
- 런타임 연동 코드

### Key Partners

- Claude Code, Codex, Gemini CLI, OpenCode 생태계
- Multica
- GitHub
- Notion / Google Drive / Gmail 등 업무 컨텍스트 제공자

### Cost Structure

- 모델 사용 비용
- 로컬/클라우드 실행 인프라
- 템플릿과 스킬 유지보수
- 검증 자동화 개발 비용
- 고객 온보딩 비용

## 9. North Star Metric

### Business Game

Productivity Game.

### North Star Metric

주당 자동 절감된 집중 업무 시간.

정의: 사용자가 원래 직접 수행해야 했지만 CraftOps가 자동 실행, 검증, 정리까지 처리한 업무 시간의 합계.

### Input Metrics

- 자동 생성된 실행 그래프 수
- 사람 개입 없이 완료된 작업 비율
- 검증 포함 완료율
- 저장된 playbook 수
- playbook 재사용률
- 작업당 평균 수동 프롬프트 수

## 10. MVP Scope

### Version 0.1: Local Operator

목표: 현재 Claude Craft 저장소 안에서 바로 쓸 수 있는 로컬 운영자.

포함:
- `work-intake` 명령
- context pack 생성
- agent/skill/router 결과 출력
- plan.json 생성
- success criteria 자동 생성
- 실행 후 리포트 템플릿

예상 기간: 1~2주.

### Version 0.2: Execution + Verify Loop

목표: 실제 실행과 검증을 자동 연결.

포함:
- `/team` 또는 `/orchestrate` 연동
- 작업 상태 추적
- 검증 실패 시 재작업 요청 생성
- 최종 리포트 자동 생성

예상 기간: 2~4주.

### Version 0.3: Playbook Memory

목표: 반복 업무를 자동으로 저장하고 재사용.

포함:
- 완료 작업 분석
- playbook 후보 생성
- skill 후보 생성
- 사용자 승인 후 저장
- 재사용 추천

예상 기간: 3~6주.

## 11. First 10 Workflows To Automate

1. 새 서비스 기획: 아이디어 → PRD → MVP → 로드맵
2. SEO/AEO 콘텐츠 파이프라인: 리서치 → 글 → SNS → 검토
3. Next.js 기능 구현: 스펙 → 구현 → 테스트 → 리뷰
4. FastAPI 기능 구현: API 설계 → 구현 → 테스트 → OpenAPI 확인
5. 디자인 하니스 QA: UI 생성 → 스크린샷 → 루브릭 평가
6. 스킬 감사: 중복, description, 라우팅, 참조 무결성 확인
7. GitHub 이슈 분해: 목표 → 이슈 묶음 → 우선순위
8. 판매 자료 생성: 제품 문서 → 랜딩 카피 → 콜드메일 → FAQ
9. 법무 문서 초안: 약관, 개인정보처리방침, 리스크 체크
10. 월간 운영 리포트: 완료 작업, 시간 절감, 비용, 다음 우선순위

## 12. Assumptions

- 사용자의 가장 큰 병목은 생성 자체가 아니라 작업 전후의 조립, 실행, 검증, 재사용화다.
- 현재 Claude Craft 자산만으로도 MVP를 만들 수 있다.
- 50% 절감은 모든 업무가 아니라 고빈도 반복 업무 상위 10개에서 먼저 달성한다.
- 사용자는 완전 자동화보다 "검증된 자동 실행 + 필요한 지점의 승인"을 더 신뢰한다.
- 첫 제품은 외부 SaaS보다 로컬 우선 시스템이 더 빠르게 검증된다.

## 13. Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| 라우팅 오류 | 잘못된 에이전트가 실행되어 시간 낭비 | 라우팅 결과를 먼저 보여주고 승인 옵션 제공 |
| 검증 부실 | 자동화 결과를 신뢰하기 어려움 | success criteria와 독립 Evaluator를 필수화 |
| 설정 복잡도 | 도입 장벽 상승 | 초기 MVP는 CLI 한 명령으로 시작 |
| playbook 품질 저하 | 재사용할수록 결과가 나빠짐 | playbook마다 성공률, 수정률, 최근성 기록 |
| 과도한 범위 | 제품이 너무 커짐 | 상위 10개 개인 워크플로우만 먼저 자동화 |

## 14. Success Criteria

MVP가 성공하려면 다음이 가능해야 한다.

- 사용자가 "웨딩 SaaS PRD 업데이트해줘"라고 입력하면 관련 문서 탐색, 기획 스킬 선택, 작업 계획, 검증 체크리스트가 자동 생성된다.
- 사용자가 "Next.js 대시보드 기능 만들어줘"라고 입력하면 구현, 테스트, 리뷰, 최종 리포트까지 연결된다.
- 완료된 작업에서 다음에 재사용할 playbook 후보가 자동 생성된다.
- 한 달 동안 실제 업무 로그 기준으로 상위 10개 반복 업무의 수동 시간이 50% 이상 줄어든다.

## 15. Recommended Next Step

첫 구현은 "완전한 앱"이 아니라 `scripts/craftops.py` 형태의 로컬 오퍼레이터로 시작한다.

최소 명령:

```bash
python3 scripts/craftops.py intake "의료관광 SEO 리포트 UX 개선 기획해줘"
python3 scripts/craftops.py plan .craftops/jobs/{job_id}/intake.json
python3 scripts/craftops.py run .craftops/jobs/{job_id}/plan.json
python3 scripts/craftops.py learn .craftops/jobs/{job_id}/report.md
```

이 방식은 현재 저장소 구조를 거의 바꾸지 않고도 핵심 가설을 검증할 수 있다. 성공하면 CLI를 대시보드와 SaaS로 확장한다.
