---
name: brain-search
description: GBrain에서 프로젝트/결정/과거 맥락을 검색하고 context pack으로 요약
allowed-tools: ["Bash", "Read", "Grep"]
---

$ARGUMENTS

GBrain memory engine에서 관련 맥락을 검색합니다.

## 사용 시점

- "지난번", "이어", "전에 정한", "왜 이렇게 했지" 같은 과거 맥락 요청
- 프로젝트, PRD, GTM, 디자인 결정, 기술 결정, 실패한 접근 조회
- 작업 계획 전에 기존 결정과 제약을 확인해야 할 때

## 절차

1. 검색어를 `$ARGUMENTS`에서 추출합니다.
2. 검색 결과만 필요하면 아래 명령으로 검색합니다.
   ```bash
   scripts/brain-memory.sh search "$QUERY"
   ```
3. 작업에 바로 넣을 맥락이 필요하면 context pack을 생성합니다.
   ```bash
   scripts/brain-memory.sh context "$QUERY"
   ```
4. 상위 slug의 전문이 필요하면 page를 읽습니다.
   ```bash
   scripts/brain-memory.sh get "$SLUG"
   ```
5. context pack은 다음 형식을 유지합니다.

```markdown
## Retrieved Context

### Relevant Decisions

### Relevant Project Docs

### Known Constraints

### Failed Approaches

### Open Questions

### Citations
```

## 품질 기준

- 검색 결과를 그대로 길게 붙이지 않는다.
- 출처 slug를 반드시 남긴다.
- 모르는 내용은 gap으로 표시한다.
- embedding disabled 상태이므로 결과가 없으면 정확한 한국어 표현, 원문 제목 단어, slug 조각으로 2-3회 재검색한다.
