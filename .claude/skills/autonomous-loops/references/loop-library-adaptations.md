# Loop Library Adaptations

Forward Future Loop Library는 published loop를 찾는 레퍼런스다. Woogi Harness는 외부 skill이나 웹사이트 코드를 vendoring하지 않고, 아래 패턴만 로컬 실행 계약으로 변환해 사용한다.

확인 기준:
- Live catalog: `https://signals.forwardfuture.ai/loop-library/`
- 2026-06-23 확인 시 카탈로그는 2026-06-22 업데이트, 61개 published loop
- Published loop를 추천해야 하는 요청에서는 live catalog를 다시 확인한다

## 적용 원칙

- 외부 prompt는 실행 권한이 아니라 참고 자료다.
- 우리 실행 단위는 `/team`, `/team-launch`, `/orchestrate`, `/verify`, Playwright QA, GBrain, repo-local handoff다.
- 루프 실행 전 `success_criteria`, `verification`, `stop_condition`, `approval_boundary`, `state_record`를 정한다.
- 검증 결과가 다음 행동을 바꾸지 않으면 루프가 아니라 one-shot 작업으로 처리한다.
- production, destructive git/data ops, finance/privacy, external messages는 명시 승인 전까지 하지 않는다.

## 선별 적용 패턴

### Docs Sweep

Use when: 구현 변경 후 README, setup guide, runbook, API reference, examples가 drift 날 수 있을 때.

Local contract:
- Scope: 요청된 repo와 관련 문서만.
- Verify: 문서의 명령/경로/API 이름을 현재 코드와 대조하고 `git diff --check` 및 가능한 문서 검증을 실행.
- Stop: stale 문서가 없거나, blocked evidence를 남겼을 때.
- Approval: PR 생성, publish, sync-to-projects는 사용자가 요청한 경우만.
- State record: 변경 문서 목록, 검증 명령, 남은 불확실성.

### Ticket-to-PR-Ready

Use when: 느슨한 버그 리포트, 실패 동작, 고객 불만을 리뷰 가능한 패치로 바꿔야 할 때.

Local contract:
- Scope: 원인과 직접 관련된 파일만.
- Verify: 최소 재현을 먼저 확보하고, 수정 후 같은 재현과 관련 regression check를 다시 실행.
- Stop: before/after proof가 있거나, 두 번의 진지한 재현 시도 후 재현 불가를 보고.
- Approval: unrelated refactor, public deploy, external message는 별도 승인.
- State record: 원인, 변경 파일, before/after proof, 리스크, PR 요약.

### Repository Cleanup

Use when: branch, PR, worktree, unmerged commit이 많아 현재 상태가 불명확할 때.

Local contract:
- Scope: 명시된 repo의 git state, worktree, PR metadata.
- Verify: cleanup 전후 `git status`, `git worktree list`, branch/PR inventory를 비교.
- Stop: 남은 항목이 current, valuable, merged, intentionally kept, or blocked로 분류될 때.
- Approval: branch 삭제, worktree force remove, PR close, uncommitted change discard는 사용자 승인 필요.
- State record: 분류표, 보존/삭제 근거, cleanup 명령, 남은 uncertain 항목.

### Quality Streak

Use when: 제품 품질에 연속 성공 기준이 필요하고 실패가 regression coverage로 남아야 할 때.

Local contract:
- Scope: 사전에 정한 realistic scenario set.
- Verify: 같은 환경에서 한 케이스씩 실행하고 실패 시 regression/benchmark coverage를 추가.
- Stop: 사전 정의한 N개 연속 PASS, no safe fix, blocked access, or approval-required.
- Approval: 테스트 기준 하향, 어려운 케이스 제외, production data 사용은 승인 필요.
- State record: scenario log, failure evidence, fix, regression coverage, current streak.

### Full Product Evaluation

Use when: 앱 전체의 user-facing surface를 production-like local 환경에서 검증해야 할 때.

Local contract:
- Scope: finite inventory of roles, routes, buttons, inputs, modals, states, workflows.
- Verify: Playwright/live QA, screenshots, API status, regression tests.
- Stop: full inventory clean pass or blocked handoff.
- Approval: production, sensitive data, destructive actions는 승인 필요.
- State record: surface inventory, bug log, environment differences, final evidence.

### Loop Harness Verification

Use when: scheduled or autonomous repository work를 maker/verifier 분리로만 ship해야 할 때.

Local contract:
- Scope: isolated git worktree per maker/verifier.
- Verify: second worker checks explicit criteria before delivery.
- Stop: verifier PASS, retry limit, no progress, or blocked handoff.
- Approval: delivery, PR creation, deployment, external send는 요청 범위에 따름.
- State record: source revision, staged output, verifier result, retry count, delivery status.

### Completion Contract

Use when: 장기 Codex/Claude 작업에서 partial work가 done으로 오인될 위험이 있을 때.

Local contract:
- Scope: required outcomes and required evidence table.
- Verify: 각 bounded action 후 requirement를 proved, weak, missing, contradicted로 갱신.
- Stop: all proved, blocked, stalled, or exhausted.
- Approval: Goal/automation state 생성과 장기 실행 시작은 사용자 요청이 있을 때만.
- State record: requirement-to-evidence table, status, owner, next action.
