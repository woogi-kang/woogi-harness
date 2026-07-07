# Claude Craft

AI 에이전트와 스킬을 체계적으로 관리하는 멀티 도메인 워크스페이스.
Claude Code, Gemini CLI, Codex CLI, OpenCode에서 동일한 에이전트/스킬 자산을 공유합니다.

## 한눈에 보기

| 자산 | 수량 | 설명 |
|------|------|------|
| 도메인 에이전트 | 25+ | 8개 카테고리 전문 에이전트 |
| 스킬 | 340+ | 에이전트 전용 + 독립 스킬 |
| 슬래시 커맨드 | 25 | `/commit`, `/review`, `/team`, `/today`, `/brain-search` 등 |
| 팀 템플릿 | 5 | fullstack-dev, content-pipeline 등 |
| 규칙 | 8 | 코딩, Git, 오케스트레이션, memory engine 등 |
| 컨텍스트 모드 | 4 | dev, plan, research, review |

---

## 프로젝트 구조

```
.claude/
├── agents/           # 도메인 에이전트 (8개 카테고리, 25+ 에이전트)
│   ├── 💻 개발/      # FastAPI, Flutter, Next.js, Figma 변환, TDD 등
│   ├── 🎯 기획/      # 디스커버리, 전략, GTM, 데이터 분석
│   ├── 🎨 디자인/    # UI/UX 디자인 시스템
│   ├── 📝 콘텐츠/    # PPT, 소셜 미디어, 블로그, 이모티콘
│   ├── 📣 마케팅/    # SEO, 마케팅 전략, 광고
│   ├── ⚖️ 법무/      # 계약 검토, 법인 운영
│   ├── 💰 재무/      # 결제 자동화, 재무 보고
│   └── 🔍 리뷰/      # 멀티 리뷰 오케스트레이션
├── skills/           # 스킬 원본 (Single Source of Truth, 340+)
│   ├── _template/    # 새 스킬 템플릿
│   ├── 💻 개발/      # 카테고리별 에이전트 스킬
│   ├── 🎯 기획/
│   └── ...           # 독립 스킬 (design, brand, social-content 등 22개)
├── commands/         # 슬래시 커맨드 (25개)
├── templates/        # 팀 오케스트레이션 TOML 템플릿 (5개)
├── hooks/            # 라이프사이클 훅 (3개)
├── rules/            # 모듈형 규칙 (common, python, typescript)
└── statusline.py     # 상태줄

.agents/skills/       # → .claude/skills/ symlink (Gemini, Codex, OpenCode 공용)
contexts/             # 행동 모드 (dev, plan, research, review)
scripts/              # 유틸리티 스크립트
docs/                 # 프로젝트 문서 (YYMMDD- prefix)
```

---

## 도메인 에이전트

### 💻 개발

| 에이전트 | 역할 |
|----------|------|
| `fastapi-agent` | FastAPI 앱 설계/구현/테스트 |
| `flutter-agent` | Flutter 앱 설계/구현/테스트 |
| `nextjs-agent` | Next.js 웹 앱 설계/구현/테스트 |
| `figma-to-nextjs` | Figma → Next.js 코드 변환 |
| `figma-to-flutter` | Figma → Flutter 코드 변환 |
| `flutter-to-nextjs` | Flutter → Next.js 마이그레이션 |
| `tdd-loop-agent` | 테스트 100% 통과까지 자율 루프 |
| `build-resolver-agent` | 최소 diff로 빌드 에러 수정 |
| `deadcode-cleaner-agent` | 데드코드/미사용 의존성 제거 |
| `loop-monitor-agent` | 자율 루프 모니터링/안전 관리 |

### 🎯 기획

| 에이전트 | 역할 |
|----------|------|
| `planning-agent` | 아이디어 → 출시 8단계 기획 (75개 스킬) |

### 🎨 디자인

| 에이전트 | 역할 |
|----------|------|
| `ui-design-agent` | 독창적 웹/모바일 UI 디자인 생성 |
| `figma-flutter-agent` | Figma MCP 통합 디자인 추출 |

### 📝 콘텐츠

| 에이전트 | 역할 |
|----------|------|
| `presentation-agent` | PPT 리서치 → 제작 전 과정 |
| `social-media-agent` | 멀티 플랫폼 소셜 콘텐츠 제작 |
| `tech-blog-agent` | 기술 블로그 작성 → Hashnode 발행 |
| `emoticon-orchestrator` | AI 캐릭터 이모티콘 제작 |

### 📣 마케팅

| 에이전트 | 역할 |
|----------|------|
| `marketing-agent` | 마케팅 전략 → 실행 산출물 |
| `seo-orchestrator` | SEO + 콘텐츠 마케팅 통합 |

### ⚖️ 법무

| 에이전트 | 역할 |
|----------|------|
| `legal-contract-agent` | 계약 검토/초안/위험 분석 |
| `corporate-legal-agent` | 법인 설립/등기/주총/정관 |

### 💰 재무

| 에이전트 | 역할 |
|----------|------|
| `payment-orchestrator` | 결제 시스템 (Lemon Squeezy, 포트원) |
| `finance-orchestrator` | 재무 보고/영수증/세금계산서 |

### 🔍 리뷰

| 에이전트 | 역할 |
|----------|------|
| `review-orchestrator` | 멀티 관점 리뷰 분배 |
| `review-code` | 코드 품질 리뷰 |
| `review-architecture` | 시스템 설계/ERD/API 리뷰 |
| `review-security` | 보안 취약점/컴플라이언스 리뷰 |
| `review-design` | UI/UX/접근성 리뷰 |
| `review-content` | 기획서/마케팅 카피/문서 리뷰 |

---

## 슬래시 커맨드

### 개발

| 커맨드 | 설명 |
|--------|------|
| `/commit` | 변경 분석 → 논리적 그루핑 → 스마트 커밋 |
| `/verify` | 6단계 검증 (빌드→타입→린트→테스트→보안→리뷰) |
| `/tdd` | TDD RED-GREEN-REFACTOR 사이클 |
| `/test-coverage` | 커버리지 분석 + 부족한 테스트 자동 생성 |

### 팀 오케스트레이션

| 커맨드 | 설명 |
|--------|------|
| `/team` | 자연어 → DAG 자동 구성 + 병렬 실행 |
| `/team-launch` | TOML 템플릿 기반 원커맨드 팀 실행 |
| `/orchestrate` | 수동 plan.json 기반 병렬 워크트리 실행 |

### 협업

| 커맨드 | 설명 |
|--------|------|
| `/review` | 멀티-LLM 리뷰 (Claude + Gemini + Codex 합의) |
| `/multi-plan` | 멀티-LLM 협업 기획 |
| `/multi-execute` | 멀티-LLM 구현 (프로토타입 정제) |

### 세션 관리

| 커맨드 | 설명 |
|--------|------|
| `/save-session` | 작업 세션 구조화 저장 |
| `/resume-session` | 이전 세션 복원 |
| `/checkpoint` | 이름 있는 체크포인트 생성/비교 |

### 기억 엔진

| 커맨드 | 설명 |
|--------|------|
| `/brain-search` | GBrain에서 프로젝트/결정/과거 맥락 검색 |
| `/brain-context` | 검색 결과를 cited context pack으로 압축 |
| `/brain-capture` | 결정, 가정, 실패 접근, 반복 패턴을 brain-craft에 저장 |
| `/brain-sync` | brain-craft repo를 GBrain index와 동기화 |
| `/brain-status` | GBrain 설치, MCP, source, 검색 모드 상태 확인 |
| `/brain-quality` | 월간 memory quality review 체크리스트 생성 |
| `/brain-pilot` | Phase 3 30일 파일럿 이벤트 기록과 Go/No-Go 리포트 |

로컬 wrapper:

```bash
scripts/brain-memory.sh status
scripts/brain-memory.sh search "검색어"
scripts/brain-memory.sh context "검색어"
scripts/brain-memory.sh sync
scripts/brain-memory.sh quality-report
scripts/brain-memory-qa.sh
scripts/brain-pilot.sh tasks
scripts/brain-pilot.sh report
```

### 유틸리티

| 커맨드 | 설명 |
|--------|------|
| `/today` | 데일리 컨텍스트 기반 작업 실행 |
| `/audit` | AI 하니스 설정 종합 감사 (0-100) |
| `/skill-audit` | 스킬 품질 감사 (Keep/Improve/Retire/Merge) |
| `/learn` | 세션 패턴 추출 → 스킬로 저장 |
| `/financial-report` | 월간 재무 보고서 생성 |

---

## 오케스트레이션

에이전트/스킬/커맨드의 자동 라우팅은 `.claude/rules/common/agent-orchestration.md`에 정의됩니다:

- **의사결정 트리**: 커맨드 → 멀티에이전트(/team) → 단일에이전트 → 스킬 → 직접 처리
- **키워드 기반 라우팅**: 사용자 요청의 키워드로 적절한 에이전트 자동 선택
- **워크플로우 체인**: 기획→디자인→구현→검증→리뷰 등 연계 패턴
- **모델 라우팅**: Opus(설계/추론), Sonnet(구현), Haiku(탐색)

### 팀 오케스트레이션 (Craft Orchestra)

DAG 기반 병렬 실행으로 여러 에이전트가 의존성 순서에 따라 자율 협업합니다.

| 커맨드 | 용도 | 예시 |
|--------|------|------|
| `/team` | 자연어 → 자동 DAG 구성 | `/team "백엔드 API + 프론트 UI + 테스트"` |
| `/team-launch` | 템플릿 기반 원커맨드 | `/team-launch fullstack-dev --goal "JWT 인증"` |
| `/orchestrate` | 수동 plan.json | `/orchestrate` |

```bash
# 실행 후 모니터링
python3 scripts/orchestrate-worktrees.py plan.json --watch    # DAG 자동 스폰
python3 scripts/orchestrate-dashboard.py --open                # 웹 대시보드
```

**TOML 팀 템플릿** (`.claude/templates/`):

| 템플릿 | 구성 |
|--------|------|
| `fullstack-dev` | Backend → Frontend → Tester |
| `content-pipeline` | Strategist → Writer → SEO → Reviewer |
| `multi-reviewer` | Code + Arch + Security → Consolidator |
| `figma-to-prod` | Design-Extractor → Implementer → Visual-Tester |
| `planning` | Researcher + Analyst → Strategist |

---

## 설치

```bash
git clone https://github.com/woogi-kang/claude-craft.git
cd claude-craft
./scripts/install.sh
```

설치 스크립트는 `~/.claude` 아래에 agents, skills, hooks, commands, statusline.py를 설치합니다.

---

## 다른 프로젝트에 동기화

claude-craft의 루트 엔트리포인트와 공유 하네스 자산을 다른 프로젝트에 복사합니다:

```bash
# 등록된 모든 프로젝트에 동기화
bash scripts/sync-to-projects.sh

# 특정 프로젝트에만 동기화
bash scripts/sync-to-projects.sh /path/to/my-project
```

기본 등록 프로젝트: `memoriz`, `memoriz-invite`, `Documents/Playground`

동기화 대상: `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `.agents/skills`, `contexts`, `.claude/{agents,commands,hooks,rules,skills,templates,evals}`, `.claude/statusline.py`
제외: 프로젝트별 권한/MCP 설정(`.claude/settings*.json`, `.mcp.json`), `logs/`

새 프로젝트를 등록하려면 `scripts/sync-to-projects.sh`의 `DEFAULT_PROJECTS` 배열에 추가합니다.

---

## 멀티 환경 지원

이 저장소 내에서 여러 AI 도구가 동일한 지시를 공유합니다:

```
CLAUDE.md              ← Claude Code (원본)
GEMINI.md → CLAUDE.md  ← Gemini CLI
AGENTS.md → CLAUDE.md  ← Codex CLI, OpenCode
.agents/skills/ → .claude/skills/  ← Gemini/Codex 스킬 공유
```

수정은 항상 원본(`.claude/`, `CLAUDE.md`)에서 합니다.

---

## 규칙

`.claude/rules/`에 모듈형으로 관리됩니다:

```
.claude/rules/
├── common/
│   ├── agent-orchestration.md   # 라우팅 매트릭스 + 워크플로우 체인
│   ├── coding-style.md          # 코딩 스타일 + 보안
│   ├── git-workflow.md          # 커밋/브랜치/PR 규칙
│   ├── testing.md               # 테스트 원칙
│   └── file-naming.md           # 파일명 컨벤션
├── python/
│   └── coding-style.md          # ruff, type hints, pathlib
└── typescript/
    └── coding-style.md          # Biome, Next.js App Router, shadcn/ui
```

---

## 스크립트

| 스크립트 | 설명 |
|----------|------|
| `install.sh` | ~/.claude에 자산 설치 |
| `sync-to-projects.sh` | 다른 프로젝트에 CLAUDE/AGENTS/GEMINI 엔트리포인트와 .claude/ 동기화 |
| `validate-skills.sh` | SKILL.md 프론트매터 검증 |
| `skill-catalog.py` | 스킬 카탈로그 자동 생성 |
| `integrity-check.py` | 참조 무결성 검증 |
| `orchestrate-worktrees.py` | 병렬 워크트리 오케스트레이션 (DAG 지원) |
| `orchestrate-dashboard.py` | 웹 대시보드 (실시간 세션 모니터링) |
| `usage-report.py` | 사용량 리포트 |
| `fix-frontmatter.py` | 프론트매터 일괄 수정 |

---

## 기여

새 스킬/에이전트/커맨드 추가 방법은 [CONTRIBUTING.md](docs/CONTRIBUTING.md)를 참고하세요.
