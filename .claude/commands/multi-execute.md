---
name: multi-execute
description: 멀티 LLM 협업 실행 — 계획 기반 구현 with 프로토타입 정제
allowed-tools: ["Bash", "Read", "Write", "Edit", "Glob", "Grep", "AskUserQuestion", "Agent"]
model: inherit
quality_tier: implementation
---

$ARGUMENTS

`/multi-plan`으로 생성된 계획을 기반으로 멀티 LLM 협업 구현을 수행합니다.

## 원칙
- **계획 우선** — `.claude/plans/` 에서 관련 계획 로드
- **프로토타입 → 정제** — 외부 LLM의 초안을 Claude가 프로덕션 품질로 정제
- **단계별 검증** — 각 작업 완료 후 테스트/린트 실행

## 절차

### Phase 1: 계획 로드
- `$ARGUMENTS`에서 계획 파일 경로 또는 키워드로 `.claude/plans/` 검색
- 계획이 없으면 `/multi-plan` 먼저 실행하도록 안내

### Phase 2: 컨텍스트 준비
계획의 작업 분해를 순서대로 처리. 각 작업마다:
1. 관련 파일 읽기
2. 기존 패턴 확인

### Phase 3: 프로토타입 획득 (선택적)
복잡한 작업은 project profile에 등록된 provider의 `implementation` quality
binding과 새 context를 사용합니다. repo context를 넘기기 전에는
`context-pack-gate`를 통과해야 합니다.

```bash
# profile에 선언된 provider binding 확인
python3 scripts/harness-provider.py --provider "${HARNESS_PROVIDER}" --quality-tier implementation
```

binding을 실행할 host-native substrate가 없으면 model/provider를 임의로 고르지
않고 typed `blocked`로 반환합니다. 외부 worker 출력은 항상 "dirty prototype"으로
취급합니다.

### Phase 4: 구현 및 정제
Claude가 직접 구현하거나 프로토타입을 정제:
- 프로젝트 컨벤션에 맞게 수정
- 타입 안전성 확보
- 에러 핸들링 추가
- 테스트 작성

### Phase 5: 검증 및 전달
각 작업 완료 후:
1. 린트 실행 (`ruff check` / `npx biome check`)
2. 테스트 실행
3. 작업 체크리스트 업데이트

## 진행 상황 추적
계획 파일의 체크리스트를 업데이트:
```
1. [x] 작업 1 — 완료 (2026-03-16)
2. [ ] 작업 2 — 진행중
3. [ ] 작업 3 — 대기
```

## 사용 예시
```
/multi-execute 260316-jwt-migration    # 계획 파일명으로
/multi-execute oauth                    # 키워드로 검색
```
