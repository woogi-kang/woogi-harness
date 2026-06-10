---
name: brain-pilot
description: GBrain Phase 3 30일 파일럿 이벤트를 기록하고 Go/No-Go 리포트를 생성
allowed-tools: ["Bash"]
---

GBrain memory engine의 Phase 3 파일럿 지표를 기록하고 리뷰합니다.

## 명령

```bash
scripts/brain-pilot.sh init
scripts/brain-pilot.sh log lookup useful 10 decisions/260610-gbrain-phase1-harness-wiring "Recovered Phase 1 decision"
scripts/brain-pilot.sh tasks
scripts/brain-pilot.sh report
```

## 이벤트 타입

- `lookup`: 작업 전 memory 조회
- `context`: context pack 사용
- `capture`: 작업 후 memory 저장
- `resume`: 프로젝트 재개에 memory 사용
- `quality`: 품질 리뷰 실행
- `miss`: 검색 실패 또는 유용하지 않은 결과

## 판정 기준

- 10개 이상 이벤트가 쌓이기 전에는 `collecting data`로 본다.
- useful rate와 citation rate가 50% 이상이면 확장 검토 가능하다.
- miss가 useful보다 많으면 trigger/search/capture 품질을 먼저 고친다.
