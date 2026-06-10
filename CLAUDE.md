# Claude Craft

AI 에이전트(25+)와 스킬(340+)을 체계적으로 관리하는 멀티 도메인 워크스페이스.
Claude Code, Gemini CLI, Codex CLI, OpenCode에서 동일한 에이전트/스킬 자산을 공유합니다.

## 프로젝트 구조

```
.claude/
├── agents/      # 도메인 에이전트 (8개 카테고리)
├── skills/      # 스킬 원본 (Single Source of Truth)
│   ├── {카테고리}/_shared/  # 공유 스킬 (에이전트 간 중복 제거)
│   │                        # 💻 개발: project-setup, architecture, unit-test, e2e-test, cicd, performance
│   │                        # 📝 콘텐츠: research, validation
├── commands/    # 슬래시 커맨드 (24개)
├── hooks/       # 라이프사이클 훅 (3개)
├── rules/       # 모듈형 규칙 (common, python, typescript)
├── templates/   # 팀 오케스트레이션 TOML 템플릿 (5개)
└── statusline.py

.agents/skills/  # → .claude/skills/ symlink (Gemini, Codex, OpenCode 공용)
contexts/        # 행동 모드 (dev, plan, research, review)
scripts/         # 유틸리티 스크립트
docs/            # 프로젝트 문서 (YYMMDD- prefix)
```

## 도메인 에이전트 (9개 카테고리)

| 카테고리 | 영역 |
|----------|------|
| 💻 개발 | FastAPI, Flutter, Next.js, Figma 변환, TDD, 빌드 수정, 데드코드 정리 |
| 🎯 기획 | 디스커버리, 전략, 실행, GTM, 데이터 분석 (75개 스킬) |
| 🎨 디자인 | 프론트엔드 UI/UX 디자인 시스템 |
| 📝 콘텐츠 | 프레젠테이션, 소셜 미디어, 기술 블로그, 이모티콘 |
| 📣 마케팅 | SEO, 마케팅 전략, 광고 카피 |
| ⚖️ 법무 | 계약 검토, 법인 운영 |
| 💰 재무 | 결제 자동화, 재무 보고 |
| 🔍 리뷰 | 코드/아키텍처/보안/콘텐츠/디자인 멀티 리뷰 |
| 🇰🇷 한국생활 | SRT/KTX, 날씨, 지하철, 법률, 주식, 배송추적, 쿠팡, 맞춤법 등 31개 (k-skill) |

## 오케스트레이션

에이전트/스킬/커맨드의 자동 라우팅은 `.claude/rules/common/agent-orchestration.md`에 정의됩니다.
사용자 요청을 분석하여 적절한 에이전트, 스킬, 커맨드로 자동 분배합니다.

### 팀 오케스트레이션 (DAG 기반 병렬 실행)

| 커맨드 | 용도 | 예시 |
|--------|------|------|
| `/team` | 자연어 → 자동 DAG 구성 + 실행 | `/team "백엔드 API + 프론트 UI + 테스트"` |
| `/team-launch` | TOML 템플릿 기반 원커맨드 실행 | `/team-launch fullstack-dev --goal "JWT 인증"` |
| `/orchestrate` | 수동 plan.json 기반 병렬 실행 | `/orchestrate` |

템플릿: `.claude/templates/` (fullstack-dev, content-pipeline, multi-reviewer, figma-to-prod, planning)

## 멀티 환경 지원

```
CLAUDE.md              ← Claude Code (원본)
GEMINI.md → CLAUDE.md  ← Gemini CLI
AGENTS.md → CLAUDE.md  ← Codex CLI, OpenCode
.agents/skills/ → .claude/skills/
```

수정은 항상 원본(`.claude/`, `CLAUDE.md`)에서 하고, 다른 환경은 자동 반영됩니다.

## 다른 프로젝트 동기화

```bash
bash scripts/sync-to-projects.sh              # 등록된 전체 프로젝트
bash scripts/sync-to-projects.sh ../memoriz   # 특정 프로젝트
```

## 작업 원칙

- 사용자 응답은 현재 대화 언어를 따릅니다.
- 서로 독립적인 조회 작업은 병렬 실행을 우선합니다.
- 사람, 회사, 프로젝트, 과거 결정, 이전 작업 맥락을 묻는 요청은 답하기 전에 GBrain memory engine을 먼저 조회합니다. 세부 규칙은 `.claude/rules/common/memory-engine.md`를 따릅니다.
- 도메인 에이전트와 스킬을 적극 활용합니다.
- 코드 변경 시 기존 패턴과 컨벤션을 따릅니다.
- 결과가 달라지는 불확실성은 먼저 질문하고, 사소한 가정은 명시한 뒤 진행합니다.
- 요청 범위를 벗어난 기능, 추상화, 리팩토링을 추가하지 않습니다.
- 변경한 모든 라인은 사용자 요청과 직접 연결되어야 합니다.
- 구현 전 성공 기준과 검증 방법을 짧게 정하고, 변경 후 확인합니다.
- 보안 민감 정보(API 키, 시크릿)는 절대 커밋하지 않습니다.

## Rules

프로젝트 규칙은 `.claude/rules/`에 모듈형으로 관리됩니다:

```
.claude/rules/
├── common/
│   ├── agent-orchestration.md   # 라우팅 매트릭스 + 워크플로우 체인
│   ├── memory-engine.md         # GBrain 기반 장기 기억 조회/캡처
│   ├── coding-style.md
│   ├── git-workflow.md
│   ├── testing.md
│   └── file-naming.md
├── python/
│   └── coding-style.md
└── typescript/
    └── coding-style.md
```

상세 규칙은 각 파일을 참조하세요.
