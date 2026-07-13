---
name: autonomous-loops
description: "자율 에이전트 루프 패턴 레퍼런스 — 8가지 루프 패턴, 실행 계약, Loop Doctor, 의사결정 매트릭스 제공"
metadata:
  category: "standalone"
  version: "1.1.0"
  tags: "loops, automation, orchestration, patterns, architecture, execution-contract"
  author: "woogi"
---

# Autonomous Loop Patterns

자율 에이전트 루프 설계를 위한 8가지 패턴, 실행 계약, Loop Doctor, 의사결정 가이드.

외부 Loop Library는 레퍼런스로만 사용한다. published loop를 찾거나 비교해야 하면 라이브 카탈로그를 확인하고, 실행은 Woogi Harness의 권한/검증/중단 규칙에 맞게 변환한다. 통째로 vendoring하지 않는다.

추가 레퍼런스:
- `references/loop-library-adaptations.md` — Loop Library에서 우리 하네스에 맞게 선별한 로컬 적용 패턴

## 패턴 개요

| # | 패턴 | 복잡도 | 병렬성 | 적합한 작업 |
|---|------|--------|--------|------------|
| 1 | Sequential Pipeline | 낮음 | 없음 | 단순 변환, 배치 처리 |
| 2 | Persistent REPL | 낮음 | 없음 | 탐색적 작업, 대화형 |
| 3 | Worktree Parallel | 중간 | 높음 | 독립적 하위 작업 분할 |
| 4 | Continuous PR Loop | 중간 | 없음 | CI 게이트 반복 개선 |
| 5 | De-Sloppify | 낮음 | 없음 | 구현 후 품질 정리 |
| 6 | RFC-DAG | 높음 | 높음 | 대규모 기능, 의존성 복잡 |
| 7 | Sprint-Reset Loop | 중간 | 없음 | 장기 순차 작업, 컨텍스트 초과 |
| 8 | GAN-Loop | 높음 | 중간 | UI/풀스택 품질 정제, 독립 검증 |

## 루프 실행 계약

루프는 "계속 해줘"가 아니라 반복 가능한 피드백 시스템이다. 루프를 만들거나 실행하기 전 아래 항목을 짧게 고정한다.

| 항목 | 질문 | 예시 |
|------|------|------|
| Outcome | 무엇이 끝나야 하는가? | PR-ready patch, docs drift zero, QA PASS |
| Scope | 무엇을 볼 수 있고 바꿀 수 있는가? | repo docs only, changed files only, local env only |
| Success criteria | 어떤 증거가 PASS인가? | 테스트명, benchmark, screenshot, reviewer verdict |
| Verification | 매 반복 후 같은 검증을 어떻게 재실행하는가? | `/verify`, Playwright flow, coverage report |
| Stop condition | 언제 성공/정체/차단/소진으로 멈추는가? | no remaining failures, 2 no-gain passes, blocked handoff |
| Approval boundary | 무엇은 사용자 승인 전까지 하지 않는가? | production, destructive git/data ops, external messages |
| State record | 다음 반복/인계가 무엇을 읽는가? | `handoff.md`, `.orchestration/...`, `LOOP-STATE.md` |

계약이 불명확하면 루프를 시작하지 말고 one-shot 작업으로 축소하거나 먼저 질문한다. 특히 검증 결과가 다음 행동을 바꾸지 않는 작업은 루프가 아니다.

## 패턴 상세

### 1. Sequential Pipeline
```bash
claude -p "작업 1 수행" --output-file result1.md
claude -p "result1.md 기반으로 작업 2 수행" --output-file result2.md
```
- 각 단계의 출력이 다음 단계의 입력
- 상태 없음, 단순함
- 실패 시 해당 단계부터 재시작

### 2. Persistent REPL
```bash
claude  # 세션 시작
# /save-session 으로 상태 저장
# /resume-session 으로 복원
```
- 컨텍스트가 세션 내 유지
- 탐색적 작업에 적합
- 컨텍스트 윈도우 한계 주의

### 3. Worktree Parallel (우리의 /orchestrate)
```bash
python scripts/orchestrate-worktrees.py plan.json --execute
```
- git worktree로 격리된 작업 디렉토리
- tmux로 병렬 Claude 인스턴스
- 파일 기반 조율 (task.md → handoff.md)
- **Woogi Harness의 기본 병렬 패턴**

### 4. Continuous PR Loop
```
while true:
  1. 코드 변경
  2. 커밋 + 푸시
  3. CI 결과 대기
  4. CI 실패 시 → 수정 후 1로
  5. CI 통과 시 → PR 생성 → 종료
```
- CI/CD가 품질 게이트 역할
- 자동 수렴 보장 (CI가 통과할 때까지)
- 네트워크/CI 지연 비용 고려

### 5. De-Sloppify Pattern
```
Phase 1: 빠른 구현 (품질 무시)
Phase 2: 전용 정리 패스
  - 콘솔 로그 제거
  - 에러 핸들링 보강
  - 타입 정리
  - 네이밍 개선
```
- "부정 지시어 대신 별도 정리 패스"
- 구현 속도와 품질을 분리
- Phase 2에서 `/verify` 실행 권장

### 6. RFC-DAG (의존성 그래프 기반)
```
RFC 작성 → 작업 분해 → 의존성 DAG 생성
→ 독립 레이어 병렬 실행
→ 머지 큐 (충돌 시 eviction + 재실행)
→ 통합 테스트
```
- 가장 복잡하지만 대규모 작업에 최적
- 작업간 의존성을 명시적으로 관리
- 머지 충돌 자동 해결

## 의사결정 매트릭스

```
작업이 독립적으로 분할 가능한가?
├── Yes → 하위 작업이 3개 이상인가?
│   ├── Yes → 의존성이 복잡한가?
│   │   ├── Yes → RFC-DAG
│   │   └── No → Worktree Parallel (/orchestrate)
│   └── No → Sequential Pipeline
└── No → 반복 개선이 필요한가?
    ├── Yes → CI가 있는가?
    │   ├── Yes → Continuous PR Loop
    │   └── No → 컨텍스트 윈도우 초과 예상?
    │       ├── Yes → Sprint-Reset Loop
    │       └── No → Persistent REPL + /verify
    └── No → 단순 구현 후 De-Sloppify
```

### 7. Sprint-Reset Loop (컨텍스트 리셋)
```bash
bash scripts/sprint-reset-loop.sh --session {name} --input {initial_input}
bash scripts/sprint-reset-loop.sh --session {name} --status
bash scripts/sprint-reset-loop.sh --session {name} --resume
```
- 각 스프린트가 독립 Claude 인스턴스에서 실행 (컨텍스트 완전 리셋)
- 이전 결과를 구조화된 파일로 전달 (핸드오프)
- 컨텍스트 불안감 제거 — 항상 깨끗한 컨텍스트에서 시작
- 순차 의존성 작업에 적합 (기획, 마이그레이션, 긴 리팩토링)
- **주의**: 각 스프린트 시작에 토큰 오버헤드 발생
- 자동 조기 종료: "남은 작업 없음" 감지 시 루프 종료

### 8. GAN-Loop (Generator-Evaluator)
```
Generator 구현 → Evaluator 라이브 테스트 → 피드백 → 재구현 (반복)
```
- Anthropic 하네스 패턴에서 영감
- Generator와 Evaluator가 독립 에이전트 (자체 평가 편향 제거)
- Evaluator는 Playwright로 라이브 상호작용 + 스크린샷
- 도메인별 평가 루브릭 적용 (`.claude/evals/presets/`)
- fullstack-dev.toml, figma-to-prod.toml에 QA 워커로 통합

## Loop Doctor

기존 루프, 자동화, `/team` plan, 장기 작업 지시를 리뷰할 때는 아래 결함만 고친다. 의도나 범위를 임의로 넓히지 않는다.

| 결함 | 수리 기준 |
|------|----------|
| 약한 검증 | "확인한다", "좋게 만든다"를 재현 가능한 테스트/루브릭/리뷰 판정으로 바꾼다 |
| 무한 반복 | 성공, clean no-op, blocked, approval-required, exhausted, stagnated 상태를 명시한다 |
| 오래된 상태 | 각 반복 전 fresh state를 다시 읽고, 결과는 state record에 남긴다 |
| 자기 승인 | 고영향 산출물은 maker와 verifier를 분리한다 |
| 권한 과잉 | production, destructive, finance/privacy, external-send는 승인 경계로 분리한다 |
| 범위 누수 | unrelated refactor, broad cleanup, stale branches를 루프 안으로 끌어오지 않는다 |
| 증거 부재 | 완료 보고에는 변경, 검증, 남은 리스크, stop reason을 포함한다 |

Loop Doctor 결과는 가능하면 짧은 수리 프롬프트나 plan 필드 변경으로 끝낸다. 스타일만 바꾸는 rewrite는 하지 않는다.

## 안전 장치

모든 루프 패턴에 공통으로 적용:
- **최대 반복 횟수**: 무한 루프 방지 (기본 10회)
- **비용 한도**: 예상 비용 초과 시 중단
- **교착 감지**: 3회 연속 동일 에러 시 에스컬레이션
- **체크포인트**: `/checkpoint` 으로 중간 상태 저장
- **증거 테이블**: 성공 기준별 PASS/FAIL/blocked와 증거 경로 기록
- **승인 게이트**: production, 삭제, 외부 전송, 민감 데이터 작업 전 중단
