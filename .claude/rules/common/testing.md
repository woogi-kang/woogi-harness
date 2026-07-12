---
paths:
  - "**/test/**"
  - "**/tests/**"
  - "**/__tests__/**"
  - "**/*_test.py"
  - "**/*_test.dart"
  - "**/*.test.*"
  - "**/*.spec.*"
---

# Testing

## 원칙
- 코드 변경 후 관련 테스트 실행
- 새 기능에는 테스트 포함
- 테스트 실패 시 즉시 수정

## 구조
- pytest (Python), vitest/jest (TypeScript)
- 단위 테스트 우선, 통합 테스트 보완
- 모킹은 외부 의존성에만 사용
