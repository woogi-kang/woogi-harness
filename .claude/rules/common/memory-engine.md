# Memory Engine — Explicit Opt-in

GBrain은 기본 작업 경로에 포함하지 않는다. 프로젝트나 회사 이름이 등장했다는 이유만으로 조회하지 않는다.

## 조회 조건

다음 중 하나가 분명할 때만 조회한다.

- 사용자가 `지난번`, `전에 정한`, `이어 진행`, `왜 이렇게 결정했지`처럼 과거 맥락을 요구한다.
- 현재 저장소에서 확인할 수 없는 이전 결정이 작업 결과를 실질적으로 바꾼다.
- 사용자가 GBrain 또는 memory 조회를 명시한다.

```bash
scripts/brain-memory.sh search "<query>"
scripts/brain-memory.sh get "<slug>"
```

조회 실패는 routine 작업을 막지 않는다. 현재 소스와 사용자 입력만으로 안전하게 진행할 수 있으면 memory 없이 계속한다. memory-derived 사실을 사용했다면 출처와 stale 가능성을 표시한다.

## 캡처

자동 캡처하지 않는다. 사용자가 명시적으로 요청했을 때만 결정, 가정, 실패 접근, 반복 가능한 패턴을 저장한다. 시크릿, 개인정보, raw source, 임시 로그는 저장하지 않는다.

운영 repo는 `/Users/woogi/Development/claude-craft`, 장기 지식 repo는 `/Users/woogi/brain-craft`로 분리한다.
