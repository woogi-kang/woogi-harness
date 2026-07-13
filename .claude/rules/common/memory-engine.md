# Memory Engine

GBrain은 Woogi Harness의 하부 장기 기억 엔진이다. Woogi Harness의 에이전트, 스킬, 커맨드, DAG 오케스트레이션을 대체하지 않는다.

## 원칙

1. 운영 repo와 지식 repo를 분리한다.
   - Woogi Harness 운영 자산: `/Users/woogi/Development/claude-craft` (레거시 로컬 source root)
   - 장기 지식 repo: `/Users/woogi/brain-craft`
2. `.claude/skills/`, `.claude/agents/`, secrets, env, logs, generated files는 bulk import하지 않는다.
3. 작업 전에는 필요한 경우만 memory를 조회한다.
4. 작업 후에는 장기적으로 재사용할 결정, 가정, 실패 접근, 패턴만 명시적으로 캡처한다.
5. 사용자 응답 스타일 같은 운영 선호는 GBrain이 아니라 agent memory 또는 규칙에 둔다.

## 조회해야 하는 경우

다음 의도가 있으면 답변 또는 작업 계획 전에 GBrain을 먼저 조회한다.

- "지난번", "전에", "이어", "다시", "왜 이렇게 했지", "왜 하기로 했지", "왜 정했지"
- 프로젝트, 제품, 고객, 회사, 사람, 계약, 전략, GTM, PRD에 관한 과거 맥락
- 이전에 결정한 방향, 실패한 접근, open question, 다음 액션
- "이 프로젝트", "그때 정한 것", "관련 문서", "기존 전략"

권장 명령:

```bash
scripts/brain-memory.sh search "<query>"
scripts/brain-memory.sh get "<slug>"
```

## 조회하지 않아도 되는 경우

- 단순 코드 포맷팅, 오타 수정, 작은 파일 편집
- 현재 대화 안에 필요한 맥락이 모두 있는 경우
- 외부 최신 정보가 필요한 경우. 이때는 web/search가 우선이며, GBrain은 보조 맥락이다.

## 캡처해야 하는 경우

작업 후 아래 항목은 `/Users/woogi/brain-craft`에 저장하고 `scripts/brain-memory.sh sync`로 반영한다.

- 제품/기술/운영 결정
- 중요한 가정과 근거
- 거절한 대안과 이유
- 실패한 접근과 재시도 금지 사항
- 반복 가능한 업무 패턴
- 프로젝트 재개에 필요한 다음 액션
- 구조화 선택 질문에서 드러난 반복 가능한 사용자 선호 또는 하네스 라우팅 기본값

캡처 후 응답 또는 작업 로그에는 capture receipt를 남긴다.

```text
Capture receipt:
- slug: sessions/260610-example
- file: /Users/woogi/brain-craft/sessions/260610-example.md
- commit: abc1234
- source: brain-craft
- synced: yes
```

## 캡처하지 않는 항목

- API key, token, credential, password, private env
- 사용자의 말투 선호 같은 agent 운영 선호
- 일회성 임시 로그
- 이번 한 번만 적용되는 선택지 응답
- 원본 소스 코드 전체
- 검증되지 않은 추측

## Import Policy

MVP와 Phase 1에서는 curated copy만 허용한다.

Include:

- PRD, GTM, 전략 문서, 통합 계획, 마이그레이션 기록
- 명시적 의사결정, open question, next action
- 반복 가능한 작업 패턴과 검증된 실패 접근
- 세션 전체가 아니라 재개에 필요한 요약

Exclude:

- `.claude/skills/`, `.claude/agents/`, `.claude/sessions/` 전체 bulk import
- `.env`, API key, token, credential, password, private config
- raw source tree, generated binaries, screenshots/media dump
- 일회성 로그, command output 전체, 검증되지 않은 추측

Import 전에는 `scripts/brain-memory.sh secret-scan`을 통과해야 한다.

## 출처 표기

GBrain에서 가져온 내용을 답변에 사용할 때는 page slug를 함께 남긴다.

예:

```text
기존 결정은 decisions/260610-gbrain-memory-engine-integration 기준입니다.
```

## 현재 파일럿 상태

- GBrain binary: `/Users/woogi/.bun/bin/gbrain`
- Harness wrapper: `scripts/brain-memory.sh`
- Engine: PGLite
- Brain repo: `/Users/woogi/brain-craft`
- Source id: `brain-craft`
- Search mode: `conservative`
- Embedding: disabled for Phase 0. Keyword search only.

## 운영 명령

```bash
scripts/brain-memory.sh status
scripts/brain-memory.sh search "<query>"
scripts/brain-memory.sh context "<query>"
scripts/brain-memory.sh get "<slug>"
scripts/brain-memory.sh capture decision "YYMMDD-kebab-title" "Title" < body.md
scripts/brain-memory.sh sync
scripts/brain-memory.sh secret-scan
scripts/brain-memory.sh quality-report
scripts/brain-memory-qa.sh
scripts/brain-pilot.sh report
```

`sync`와 `capture`는 `/Users/woogi/brain-craft`에 커밋되지 않은 변경이 있으면 중단한다.
