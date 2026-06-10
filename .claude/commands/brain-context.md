---
name: brain-context
description: GBrain 검색 결과를 cited context pack으로 압축
allowed-tools: ["Bash", "Read", "Grep"]
---

$ARGUMENTS

GBrain memory engine에서 관련 맥락을 검색하고 Claude Craft 작업에 넣을 context pack을 생성합니다.

## 절차

1. 쿼리를 `$ARGUMENTS`에서 추출합니다.
2. 아래 명령을 실행합니다.
   ```bash
   scripts/brain-memory.sh context "$QUERY"
   ```
3. 결과의 `Citations`, `Stale And Gap Notes`, `Gap:` 항목을 확인합니다.
4. 실행 결과에 사용할 때는 citation slug를 유지합니다.

## 품질 기준

- context pack은 1,500 단어 이하로 유지한다.
- top result를 그대로 길게 붙이지 않는다.
- 누락된 결정, 실패 접근, open question은 `Gap:`으로 남긴다.
- 오래된 전략, 가격, 법무, 시장 정보는 stale 가능성을 명시한다.
- 정확도가 부족하면 `scripts/brain-memory.sh get "$SLUG"`로 cited page를 직접 읽는다.
