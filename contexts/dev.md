# Context Mode: Dev

코드 작성 우선, 설명은 나중.

## 행동 규칙
- 동작하는 코드를 먼저 작성하고, 질문은 최소화
- 단, 결과가 달라지는 불확실성은 `.claude/rules/common/clarification-protocol.md`에 따라 native 선택 UI로 먼저 확인
- 기존 코드 패턴을 따라 일관성 유지
- project profile과 canonical capability를 resolve하고 필요한 context만 로드
- 테스트 작성 포함
- 긴 설명 대신 코드 주석으로 대체
- 에러 발생 시 즉시 수정 시도, 3회 실패 시 사용자에게 보고
- shell exit 0이 아니라 success criteria별 check/evidence로 완료 판단
- UI 변경이면 Design Runtime v3의 상태별 실제 화면과 독립 critic까지 검증
