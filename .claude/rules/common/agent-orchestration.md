# Agent Orchestration — Lean Default

기본 경로는 orchestration이 아니라 직접 실행이다.

```text
사용자 요청
→ 현재 프로젝트와 기존 패턴 확인
→ 네이티브 모델이 직접 작업
→ 실제 테스트·화면·런타임 검증
→ 근거와 남은 위험 보고
```

## Default

- registry resolve와 context compile을 선행하지 않는다.
- agent, skill, command를 키워드로 자동 선택하지 않는다.
- memory를 프로젝트 이름만으로 자동 조회하지 않는다.
- routine 작업에 execution state를 만들지 않는다.
- multi-agent, DAG, external critic을 자동 실행하지 않는다.
- UI 작업에 Design Runtime, Design Read, dials, register, anti-slop prompt를 적용하지 않는다.

현재 소스, 프로젝트 문서, 설치된 dependency, 테스트를 모델이 직접 읽고 필요한 작업을 수행한다. 관련된 로컬 조회·편집·검증은 별도 승인 없이 진행하고 외부 전송, 배포, 파괴적 변경, 결제·게시·메시지 전에 승인받는다.

## Explicit opt-in

사용자가 특정 skill, command, agent, team/DAG, memory search, execution contract 또는 `$design-harness`를 명시한 경우에만 해당 자산을 연다. opt-in 범위가 끝나면 다시 direct mode로 돌아간다.

글자·줄·byte 제한이 있는 작업은 사용자가 요청한 경우 `korean-character-count`로 deterministic하게 확인한다.

서로 독립적인 조회가 많더라도 provider의 native parallel tool calling으로 충분하면 별도 worker를 만들지 않는다. multi-agent는 사용자가 요청했거나 단일 agent 평가에서 실제 병목이 확인된 경우에만 사용한다.

## Hard routes that remain

- 최신 SDK/API/library 주장은 로컬 버전과 공식 문서로 확인한다.
- repo context를 외부 서비스나 모델로 전송할 때는 범위와 secret을 확인하고 승인 경계를 지킨다.
- 생성형 raster image는 exact-vendored `image-prompt`를 거쳐 Codex `$imagegen`/required `gpt-image-2`만 사용한다.
- 이미지 provider/model fallback은 허용하지 않는다.

## UI verification

디자인 방향을 prompt checklist로 통제하지 않는다. 구현 후 실제 route/screen에서 다음을 검증한다.

- 요청 범위의 mobile/desktop viewport
- loading, empty, error, focus 등 관련 상태
- 접근성, overflow, contrast, touch target
- framework build/test/golden
- 필요 시 deterministic detector

정적 검사 통과를 시각적 품질 통과로 표현하지 않는다.

## Completion

최종 응답에는 바뀐 내용, 실제 실행한 검증, 실패·누락·남은 위험만 간결하게 남긴다. 구조 검사나 command exit 0을 결과물 품질의 증거로 확대하지 않는다.
