---
name: brain-quality
description: brain-craft 월간 메모리 품질 리뷰 체크리스트 생성
allowed-tools: ["Bash"]
---

`/Users/woogi/brain-craft`의 월간 memory quality review를 실행합니다.

## 명령

```bash
scripts/brain-memory.sh quality-report
scripts/brain-memory-qa.sh
scripts/brain-memory.sh secret-scan
```

## 판정 기준

- repo가 dirty 상태가 아니다.
- secret scan이 통과한다.
- routing/context QA가 통과한다.
- 최신 memory page에 유용한 `Summary`가 있다.
- raw logs, screenshots/media dump, source dump가 import되지 않았다.
- stale 전략, 가격, 법무, 시장 정보는 refresh 또는 stale 표시가 되어 있다.
