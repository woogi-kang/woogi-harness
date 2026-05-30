# Claude Craft 내실 점검 감사 리포트

> 상태: 2026-05-29 디자인 스킬 정리로 ISS-005의 `ui-ux-pro-max`/`design-craft`/`ui-design-agent-skills` 문제는 `design-harness` 중심 구조로 superseded. 최신 디자인 라우팅 기준은 `docs/260529-design-harness-migration.md`를 따른다.

**일자:** 2026-03-24
**범위:** 전체 프로젝트 (342 스킬, 30+ 에이전트, 18 커맨드, 3 훅, 11 스크립트)
**종합 점수:** 8.2 / 10

---

## 요약

에이전트 아키텍처(unified orchestrator, progressive disclosure, multi-LLM consensus)는 우수.
문제는 **스킬 레이어**에 집중 — 메타데이터 부재, 중복 구현, 경계 불명확.

---

## 🔴 심각 (P0)

### ISS-001: 스킬 70% 설명 없음 (240/342개)

대부분의 에이전트 하위 스킬 YAML description이 비어있거나 `|`만 존재.
에이전트가 스킬을 참조할 때 무슨 스킬인지 판단 불가.

**영향받는 에이전트:**
- planning-agent-skills: 82개
- fastapi-agent-skills: 37개
- flutter-agent-skills: 31개
- nextjs-agent-skills: 31개
- 기타 에이전트 스킬셋 다수

**해결:** Phase 2 — 전체 스킬 description 보강

---

### ISS-002: 동일 기능 중복 구현 (9개 함수 × 3~4 복사본)

| 기능 | 중복 위치 | 복사본 수 |
|------|-----------|-----------|
| project-setup | fastapi / flutter / nextjs | 3 |
| architecture | fastapi / flutter / nextjs | 3 |
| unit-test | fastapi / flutter / nextjs | 3 |
| e2e-test | fastapi / flutter / nextjs | 3 |
| cicd | fastapi / flutter / nextjs | 3 |
| performance | fastapi / flutter / nextjs / ui-design | 4 |
| design-system | flutter / nextjs / presentation / standalone | 4 |
| research | presentation / social-media / tech-blog | 3 |
| validation | fastapi / presentation / social-media | 3 |

**해결:** Phase 1 — 공통 스킬 추출 및 공유 참조

---

### ISS-003: 스킬 이름 충돌 (7건)

| 충돌 이름 | 위치 |
|-----------|------|
| `1-project-setup` | fastapi / flutter / nextjs |
| `2-architecture` | fastapi / flutter / nextjs |
| `1-research` | presentation / social-media / tech-blog |
| `2-validation` | presentation / social-media |
| `3-design-system` | flutter / nextjs |
| `18-performance` | ui-design / flutter |
| `8-review` | flutter-to-nextjs / presentation |

**해결:** Phase 1과 함께 네이밍 정리

---

## 🟡 중요 (P1)

### ISS-004: 고아 스킬 7개 (어떤 에이전트도 미참조)

| 스킬 | 적합한 에이전트 |
|------|----------------|
| `eval-harness` | tdd-loop-agent, build-resolver |
| `search-first` | 모든 개발 에이전트 |
| `autonomous-loops` | loop-monitor-agent |
| `notion-tech-writer` | 콘텐츠 에이전트들 |
| `obsidian-vault-architect` | planning-agent |
| `notebooklm` | presentation-agent, tech-blog |
| `learn` | 독립형 (OK) |

**해결:** 에이전트 정의에 참조 추가 또는 독립형으로 명시

---

### ISS-005: 디자인 스킬 경계 불명확 (6개 겹침)

| 스킬 | 현재 범위 | 겹치는 부분 |
|------|-----------|-------------|
| `design` | 종합 래퍼 (브랜드, 토큰, UI, 로고, CIP, 배너, 아이콘) | 모든 하위 스킬과 겹침 |
| `ui-ux-pro-max` | 50+ 스타일, 161 컬러, 99 UX 가이드 | design, ui-styling |
| `ui-styling` | shadcn/ui + Tailwind 구현 | ui-ux-pro-max |
| `design-system` | 3-레이어 토큰 아키텍처 | design |
| `logo-creator` | AI 로고 생성 파이프라인 | design |
| `banner-design` | 22 스타일 배너 | design |

**해결:** Phase 3 — 스킬별 책임 범위 정의 + 라우팅 매트릭스

---

### ISS-006: figma-to-nextjs ↔ figma-to-flutter ~90% 코드 중복

두 에이전트가 거의 동일한 구조 (Pro/Hybrid/Pure 전략, 8단계 파이프라인).
프레임워크 셀렉터를 가진 단일 에이전트로 통합 가능.

**해결:** 별도 이슈로 추적 (구조 변경 큼)

---

## 🟢 경미 (P2)

### ISS-007: 훅 문서 없음

3개 훅 shell script에 설명/사용법 문서 없음:
- `git-push-guard.sh`
- `quality-gate.sh`
- `usage-tracker.sh`

### ISS-008: agent-orchestration.md 커맨드 누락

`/learn`, `/financial-report`가 라우팅 매트릭스에서 빠져있음.

### ISS-009: 데드 스크립트

`scripts/generate_diagrams.py` — 아무 곳에서도 참조되지 않음.

### ISS-010: 커맨드 frontmatter 불일치

일부 커맨드는 `type`, `model` 필드가 있고 일부는 없음.

### ISS-011: .orchestration/ gitignore 미정의

런타임 상태 파일이 실수로 커밋될 수 있음.

### ISS-012: sync-to-projects.sh 에러 핸들링 부족

대상 디렉토리 존재 여부 검증 없이 rsync 실행.

### ISS-013: orchestrate-worktrees.py 상태 파일 스키마 미문서화

`.orchestration/{session}/` 내부 파일 형식 설명 없음.

---

## 액션 플랜 — 실행 결과

### Phase 1: 중복 정리 ✅ 완료

**생성된 공유 스킬:**
- `💻 개발/_shared/`: project-setup, architecture, unit-test, e2e-test, cicd, performance (6개)
- `📝 콘텐츠/_shared/`: research, validation (2개)

**업데이트된 원본 스킬:** 23개 파일에 `Extends:` 참조 추가 (원본 콘텐츠 보존)
**design-system 통합:** flutter/nextjs/presentation 스킬이 canonical `design-system/SKILL.md` 참조

### Phase 2: 스킬 메타데이터 보강 ✅ 완료

- 121개 스킬 description 한국어화
- 전체 350/350 스킬 Korean description 보유 (100% 커버리지)

### Phase 3: 디자인 스킬 정리 ✅ 완료

- 6개 디자인 스킬에 범위/위임/제외 섹션 추가
- `design/ROUTING.md` 생성 (22개 사용자 의도 라우팅 + 7개 경계 규칙)
- `agent-orchestration.md` Section 3 업데이트 (비중복 트리거 키워드)

### 리뷰 결과 (8개 서브에이전트)

| # | 리뷰 대상 | 결과 | 수정 |
|---|-----------|------|------|
| 1 | 공유 개발 스킬 품질 | ⚠️ | E2E FastAPI 범위 명확화, 세션 TTL 수정 |
| 2 | 공유 콘텐츠 + design-system | ❌→✅ | Extends 경로 오류 2건 수정 |
| 3 | Extends 참조 무결성 | ✅ | 23/23 통과 |
| 4 | 기획 스킬 description | ✅ | - |
| 5 | 마케팅/기타 description | ✅ | - |
| 6 | 라우팅 매트릭스 | ⚠️→✅ | slides 라우팅 통일 |
| 7 | 디자인 스킬 경계 | ✅ | - |
| 8 | 크로스커팅 일관성 | ⚠️→✅ | CLAUDE.md _shared 구조 추가 |
