# Execution Contract

모든 구현, 루프, 오케스트레이션, 리뷰, 검증 작업은 시작 전에 짧은 실행 계약을 세운다. 이 규칙은 직접 작업, 스킬 실행, 에이전트 위임, `/team`, `/team-launch`, `/orchestrate`, `/verify`에 공통 적용된다.

## 기본 계약

작업 전 아래 항목을 명시하거나 내부적으로 확정한다.

| 항목 | 의미 |
|------|------|
| Outcome | 이번 작업이 끝났다고 말할 수 있는 구체적 결과 |
| Scope | 수정/조회 가능한 파일, 시스템, 환경 |
| Success criteria | PASS로 인정할 관찰 가능한 기준 |
| Verification | 기준을 증명할 명령, 테스트, 브라우저 플로우, 리뷰 방법 |
| Stop condition | success, clean no-op, blocked, approval-required, exhausted, stagnated 중 어느 상태로 멈출지 |
| Approval boundary | 승인 전까지 하지 않을 production, destructive, privacy/finance, external-send 작업 |
| State record | 다음 반복이나 인계가 읽을 기록 위치 |

작업이 작으면 사용자에게 길게 말하지 않는다. 그래도 구현 전에는 성공 기준과 검증 방법을 짧게 잡고, 완료 후 그 기준으로 확인한다.

## Goal Prep Pack 전환 기준

아래 중 하나라도 참이면 단순 계약 대신 `goal-prep-pack`을 사용해 `.claude/goals/{yyMMdd}-{goal-slug}/` 아래에 `VALIDATION.md`, `RECOVERY.md`, `PLAN.md`, `PROGRESS.md`, `goal-command.md`를 만든다.

- PRD, 로드맵, 출시 계획, 장기 목표를 실제 구현으로 전환한다.
- 작업이 여러 세션, 여러 에이전트, 여러 워크트리를 넘나든다.
- rollback, production, privacy, finance, external-send, deploy 승인이 필요할 수 있다.
- 실패 후 재시도/복구 경로를 다음 실행자가 읽어야 한다.

작업 중에는 `PROGRESS.md`를 최신 항목이 위로 오도록 갱신한다. 같은 blocker가 세 번 반복되면 진행을 멈추고 blocked 상태를 명시한다.

## 루프 판정

아래가 모두 참이면 루프로 설계한다.

- fresh observation이 다음 행동을 바꿀 수 있다.
- 각 반복에서 한 가지 bounded action을 할 수 있다.
- 같은 acceptance check를 반복 실행할 수 있다.
- 결과를 다음 반복이 읽을 곳에 기록할 수 있다.
- 명확한 stop condition과 approval boundary가 있다.

하나라도 빠지면 one-shot 작업으로 축소하거나 `.claude/rules/common/clarification-protocol.md`에 따라 선택지 기반 질문을 먼저 한다.

## 오케스트레이션 필드

`plan.json` worker에는 가능한 경우 아래 필드를 넣는다.

```json
{
  "name": "Worker",
  "task": "bounded task",
  "depends_on": ["OtherWorker"],
  "success_criteria": ["observable pass condition"],
  "eval_type": "unit|integration|ui|docs|security|review|manual",
  "stop_condition": "when this worker must stop",
  "approval_boundary": ["what requires explicit user approval"],
  "state_record": "handoff.md or another repo-local state file"
}
```

`success_criteria`는 task prose 안에 묻지 말고 가능하면 별도 필드로 둔다. 반복 작업은 `stop_condition`, `approval_boundary`, `state_record`까지 포함한다.
넓은 repo context를 worker에게 제공할 때는 `context-pack-gate` 산출물 경로를 `context_pack` 필드로 별도 기록한다.

## 완료 보고

완료 보고는 아래를 포함한다.

- 변경 요약
- 실행한 검증과 결과
- 충족한 success criteria
- 남은 blocked/approval-required/stagnated 항목
- 사용자가 바로 이어서 할 수 있는 다음 액션
