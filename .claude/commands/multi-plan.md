---
name: multi-plan
description: 멀티 LLM 협업 기획 — Claude 오케스트레이션 + 전문가 LLM 분석
allowed-tools: ["Bash", "Read", "Write", "Glob", "Grep", "AskUserQuestion", "Agent"]
model: inherit
quality_tier: reasoning_high
---

$ARGUMENTS

여러 LLM을 활용한 협업 기획을 수행합니다. Claude가 오케스트레이터, 다른 LLM이 전문가 역할.

## 원칙
- **기획만, 구현 없음** — 코드 작성 금지
- **모든 결정에 근거 필요** — 트레이드오프 명시
- **사용자 승인 후 다음 단계** — 각 단계 끝에서 확인

## 절차

### Phase 1: 요구사항 정리
사용자의 요청(`$ARGUMENTS`)을 분석하여 명확한 목표와 범위 정의:
- 무엇을 만들/변경할 것인지
- 제약 조건 (기술 스택, 시간, 호환성)
- 성공 기준

### Phase 2: 컨텍스트 수집
관련 코드/문서를 읽어 현재 상태 파악:
- 프로젝트 구조 탐색
- 기존 패턴/컨벤션 확인
- 의존성 확인

### Phase 3: 전문가 분석 (병렬)
project profile에 등록된 provider와 quality class로 독립적 분석을 수행합니다.
외부 worker에 repo context를 전달하기 전에 `context-pack-gate`를 통과해야 합니다.

```bash
# profile에 선언된 provider의 reasoning_high binding 확인
python3 scripts/harness-provider.py --provider "${HARNESS_PROVIDER}" --quality-tier reasoning_high

# 전달할 파일/예산/secret을 먼저 검증
python3 scripts/context-pack-gate.py --mode worker --token-budget 12000 "$SCOPED_TARGET"
```

등록 provider가 required tools/capabilities를 충족하지 않거나 host-native 실행을
현재 환경에서 시작할 수 없으면 다른 model로 추측해 대체하지 않고 typed `blocked`로
반환합니다. 병렬 worker는 provider-native substrate에서 새 context로 시작합니다.

### Phase 4: 종합 및 계획 수립
전문가 분석 결과를 종합하여 구조화된 계획 작성:

```markdown
# Plan: {제목}

## 목표
{한 문장}

## 아키텍처 결정
| 결정 | 선택 | 근거 | 대안 |
|------|------|------|------|
| ... | ... | ... | ... |

## 작업 분해
1. [ ] {작업 1} — {예상 범위}
2. [ ] {작업 2} — {예상 범위}
...

## 리스크
- {리스크 1}: {완화 방안}

## 의존성
{작업간 의존성 그래프}

## 전문가 의견
- **Codex**: {요약}
- **Gemini**: {요약}
- **합의**: {공통점}
- **이견**: {차이점과 Claude의 판단}
```

### Phase 5: 저장
`.claude/plans/{YYMMDD}-{topic}.md` 에 저장.

## 사용 예시
```
/multi-plan JWT 인증 시스템을 OAuth2로 마이그레이션
/multi-plan 실시간 알림 시스템 설계
```
