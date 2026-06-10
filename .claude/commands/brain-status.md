---
name: brain-status
description: GBrain 설치, MCP, source, 검색 모드, stats 상태 확인
allowed-tools: ["Bash"]
---

GBrain memory engine 상태를 점검합니다.

## 명령

```bash
scripts/brain-memory.sh status
scripts/brain-memory-qa.sh
scripts/brain-memory.sh quality-report
codex mcp list
claude mcp get gbrain
```

## 판정 기준

- `get_brain_identity`가 `engine: pglite`와 page count를 반환한다.
- `stats`에서 pages/chunks가 0보다 크다.
- `search modes`는 conservative가 active다.
- Codex MCP list에 `gbrain`이 있다.
- Claude MCP get gbrain이 `Connected`다.
- Phase 1 routing QA가 0 failure로 끝난다.

## 알려진 Phase 0 경고

- embedding provider 없음: 의도된 상태다.
- `doctor`의 cycle freshness 경고: dream/autopilot은 Phase 1 이후 검토한다.
- links/timeline 0: seed 문서에 wikilink/timeline 구조가 없어서 정상이다.
