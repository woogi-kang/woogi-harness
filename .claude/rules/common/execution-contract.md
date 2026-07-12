# Execution Contract — Runtime v1

반복·장기·병렬·자율 작업과 배포/외부 전송/비용/파괴 위험이 있는 작업은 실행 전에 성공과 중단 조건을 typed record로 고정한다.

## Required fields

- `objective`: 구체적 최종 결과.
- `success_criteria`: 관찰 가능하고 검증 가능한 기준.
- `verification`: 각 기준을 증명할 명령/파일/flow.
- `approval_boundary`: 사용자 승인 없이 넘지 않을 경계.
- `stop_condition`: 반복 실패, 외부 blocker, 안전 경계.
- `state_record`: 실행 outcome JSON 경로.

```bash
python3 scripts/harness-execution.py init \
  --file <outcome.json> --id <execution-id> --objective "<objective>" \
  --success-criterion "<criterion>"

python3 scripts/harness-execution.py transition --file <outcome.json> --to running
```

## States

```text
pending → running → succeeded | failed | blocked | needs_approval
blocked/needs_approval → running only after the condition changes
```

- `succeeded`: 모든 criterion에 passed check와 evidence가 있다.
- `failed`: 구현 또는 검증 hard gate가 실패했다.
- `blocked`: 필요한 tool/input/external state가 없어 안전하게 진행할 수 없다.
- `needs_approval`: 배포, destructive change, 외부 전송, 비용, 개인정보 같은 승인 경계에 도달했다.

Process exit 0은 transport 신호일 뿐 성공 상태가 아니다.

```bash
python3 scripts/harness-execution.py from-exit \
  --exit-code 0 --outcome-file <outcome.json>
```

Outcome file이 없거나 evidence/check가 빠졌으면 `succeeded`로 변환하지 않는다.

## Evidence

Evidence는 실제로 확인한 것만 기록한다.

- test/build/analyze command와 결과.
- source diff 또는 schema validation.
- browser/device/API flow.
- screenshot/golden/accessibility artifact.
- 배포/운영 state의 live query.

“완료함”, 계획, prompt, 자체 평가, 실행하지 않은 명령은 evidence가 아니다. 개인정보·시크릿 원문은 record에 복사하지 않는다.
`succeeded` evidence에는 실제 실행의 `producer`, argv 배열 `command`, `exit_code`, `status`와 regular file의 `path`, `sha256`, `bytes`를 함께 기록한다. `artifact_root`는 고정값 `artifacts`이고, `path`는 outcome 옆 `artifacts/` 기준의 non-symlink 상대 경로만 사용한다. final validation이 artifact를 다시 hash한다. `TYPE:DESCRIPTION` 축약형은 diagnostic-only라 성공 증거가 아니다.

```bash
python3 scripts/harness-execution.py transition \
  --file <outcome.json> --to succeeded \
  --evidence '{"type":"test-log","description":"pytest passed","producer":"pytest","command":["python3","-m","pytest"],"exit_code":0,"status":"passed","path":"pytest.log","sha256":"<actual-lowercase-sha256>","bytes":<actual-bytes>}' \
  --check "<criterion>=passed"

python3 scripts/harness-execution.py validate --file <outcome.json> --final
```

## Retry and stop

- 같은 원인·같은 방식의 실패를 세 번 반복하지 않는다.
- 첫 실패는 원인을 분류하고, 두 번째는 접근 또는 조건을 바꾼다.
- 세 번째 동일 실패는 `blocked` 또는 `failed`로 기록하고 stop reason을 남긴다.
- UI/design repair는 Design Runtime 정책상 최대 2회다.
- test/eval 기준을 구현에 맞게 약화해 성공시키지 않는다.

## Approval boundary

다음은 명시 승인 없이 실행하지 않는다.

- production deploy/rollback/data mutation.
- destructive git 또는 target-only 파일 삭제.
- hosted/third-party service로 repo context 전송.
- 유료 API/대량 생성.
- 사용자 계정으로 외부 메시지/게시/구매.

승인을 기다리는 동안 read-only 진단, local test, dry-run, manifest 생성은 계속할 수 있다.

## Orchestration

Worker는 `success_criteria`, `stop_condition`, `approval_boundary`, `state_record`, 필요 시 `context_pack`을 받는다. Orchestrator는 worker process exit가 아니라 typed outcome을 검증해 DAG 상태를 갱신한다.

장기 목표의 recovery/progress 문서가 필요하면 `goal-prep-pack`; 반복 loop 설계가 필요하면 `autonomous-loops`; repo context 전달은 `context-pack-gate`를 함께 사용한다.
