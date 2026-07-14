# 기여 가이드

Woogi Harness 프로젝트에 스킬, 에이전트, 커맨드를 추가하는 방법을 안내합니다.

---

## 1. 프로젝트 구조 개요

```
.claude/
├── agents/           # 전문 에이전트 정의 (9개 최상위 그룹, 25+)
│   ├── figma-to-nextjs/ # Figma 변환 공유 자산
│   ├── 💻 개발/      # FastAPI, Flutter, Next.js, Figma 변환, TDD 등
│   ├── 🎯 기획/      # 디스커버리, 전략, GTM, 데이터 분석
│   ├── 🎨 디자인/    # UI/UX 디자인 시스템
│   ├── 📝 콘텐츠/    # PPT, 소셜 미디어, 블로그, 이모티콘
│   ├── 📣 마케팅/    # SEO, 마케팅 전략, 광고
│   ├── ⚖️ 법무/      # 계약, 법인 운영
│   ├── 💰 재무/      # 결제, 재무 보고
│   └── 🔍 리뷰/      # 멀티 리뷰 오케스트레이션
├── skills/           # 스킬 원본 (9개 도메인, Single Source of Truth, 385개)
│   ├── _template/    # 새 스킬 템플릿
│   ├── 💻 개발/      # 카테고리별 스킬 디렉토리
│   ├── 🎯 기획/
│   ├── 🇰🇷 k-skill/  # 한국생활 스킬 31개
│   └── ...           # standalone 스킬 (brand, design, social-content 등)
├── commands/         # 슬래시 커맨드 (25개)
├── templates/        # 팀 오케스트레이션 TOML 템플릿 (5개)
├── hooks/            # 라이프사이클 훅 (4개)
├── rules/            # 모듈형 규칙 (13개)
├── registry/         # capability/provider/project/tech/design 계약
├── project-packs/    # sync v2 default pack + overlay
└── evals/            # 실행 가능한 평가 케이스/채점기

.agents/skills/       # → .claude/skills/ symlink (Gemini, Codex, OpenCode 공용)
contexts/             # 행동 모드 (dev, plan, research, review)
scripts/              # 유틸리티 (validate, catalog, sync, orchestrate)
third_party/          # SHA 고정 upstream runtime (로컬 patch 금지)
```

---

## 2. 새 스킬 추가하기

### 2.1 템플릿 복사

```bash
# 카테고리 하위에 생성하는 경우
cp -r .claude/skills/_template .claude/skills/💻\ 개발/agent-skills/my-new-skill

# standalone 스킬로 생성하는 경우
cp -r .claude/skills/_template .claude/skills/my-new-skill
```

### 2.2 필수 프론트매터 필드

```yaml
---
name: my-new-skill              # kebab-case, 디렉토리명과 일치
description: |                  # 한 줄 설명 + 트리거 조건
  REST API 테스트 자동화 스킬.
  When to use: API 테스트, 엔드포인트 검증이 필요할 때.
argument-hint: "[endpoint]"     # 선택 인자 힌트
metadata:
  category: "💻 개발"           # 9개 도메인 중 택 1 또는 "standalone"
  version: "1.0.0"              # SemVer
  tags: "api, test, rest"       # 검색용 태그
  author: "woogi"               # 작성자
---
```

### 2.3 배치 규칙

| 유형 | 경로 | 예시 |
|------|------|------|
| 에이전트 전용 스킬 | `.claude/skills/{카테고리}/{agent}-skills/{skill}/` | `💻 개발/fastapi-agent-skills/1-project-setup/` |
| 독립 스킬 | `.claude/skills/{skill-name}/` | `design/`, `social-content/` |
| 참조 파일 | 스킬 디렉토리 내 `references/` | `design/references/logo-design.md` |

### 2.4 네이밍 컨벤션

- **디렉토리명**: kebab-case (`my-new-skill`)
- **메인 파일**: `SKILL.md` (대문자, 고정)
- **번호 접두사**: 순서가 있는 스킬은 `1-`, `2-` 등 사용 (`1-project-setup`)
- **참조 파일**: 디렉토리 내 `references/` 하위에 배치

### 2.5 SKILL.md 작성 패턴

```markdown
# Skill Name

## Overview
스킬의 목적과 핵심 기능을 간결하게 설명합니다.

## When to Use  (또는 When to Apply)
- 이 스킬을 사용해야 하는 상황
- 이 스킬이 불필요한 상황

## Workflow
1. 단계별 실행 흐름

## Output Format
출력 형식 또는 예시
```

---

## 3. 새 에이전트 추가하기

### 3.1 에이전트 파일 구조

에이전트는 두 가지 형태로 정의할 수 있습니다:

**단일 파일 에이전트:**
```
.claude/agents/💻 개발/my-agent.md
```

**디렉토리 에이전트 (복잡한 경우):**
```
.claude/agents/💻 개발/my-agent/
├── my-agent-unified.md    # 메인 에이전트 정의
├── references/            # 참조 자료
└── USAGE-GUIDE.md         # 사용 가이드 (선택)
```

### 3.2 필수 프론트매터 필드

```yaml
---
name: my-agent
description: |
  에이전트의 역할과 전문 분야를 설명합니다.
  어떤 요청에 반응하는지 명시합니다.
model: inherit                 # provider/project profile이 실제 모델을 선택
quality_tier: reasoning_high   # reasoning_high, implementation, fast_scan, independent_critic
triggers:                       # 이 에이전트를 호출하는 키워드
  - "my domain 개발"
  - "my domain 설계"
---
```

### 3.3 스킬 참조 방법

에이전트 내에서 스킬을 참조할 때는 **점진적 공개(Progressive Disclosure)** 패턴을 따릅니다:

```markdown
## 스킬 세트

| 단계 | 스킬 | 설명 |
|------|------|------|
| 1 | project-setup | 프로젝트 초기 설정 |
| 2 | architecture | 아키텍처 설계 |

### 스킬 로딩 규칙
1. 사용자 요청을 분석하여 필요한 스킬만 로드
2. 전체 스킬을 한번에 로드하지 않음
3. 스킬 경로: `.claude/skills/{카테고리}/{agent}-skills/{skill}/SKILL.md`
```

---

## 4. 새 커맨드 추가하기

### 4.1 커맨드 파일 구조

`.claude/commands/` 디렉토리에 `command-name.md` 형식으로 생성합니다.

```yaml
---
description: "커맨드 설명 (영어, 한 줄)"
argument-hint: "[args]"
type: utility
allowed-tools: AskUserQuestion, Bash, Read, Write, Glob, Grep
model: inherit
quality_tier: implementation
---
```

### 4.2 커맨드 본문 구조

```markdown
## Pre-execution Context
!command-to-run-before      # 실행 전 자동 수집할 컨텍스트

---

# /command-name - Command Title

## Core Principle
핵심 동작 원칙

## Command Flow
실행 흐름 다이어그램

## Steps
단계별 상세 설명

## Output Format
출력 형식

## Error Handling
에러 처리

---
Version: 1.0.0
```

### 4.3 기존 커맨드 참고

| 커맨드 | 설명 | 파일 |
|--------|------|------|
| `/commit` | 스마트 커밋 (논리적 그루핑) | `commit.md` |
| `/review` | 멀티-LLM 리뷰 | `review.md` |
| `/team` | 자연어 → DAG 팀 오케스트레이션 | `team.md` |
| `/team-launch` | TOML 템플릿 기반 팀 실행 | `team-launch.md` |
| `/orchestrate` | 수동 plan.json 병렬 워크트리 | `orchestrate.md` |
| `/today` | 데일리 브리핑 | `today.md` |
| `/financial-report` | 월간 재무 보고 | `financial-report.md` |

---

## 5. 새 팀 템플릿 추가하기

### 5.1 템플릿 위치

`.claude/templates/` 디렉토리에 `template-name.toml` 형식으로 생성합니다.

### 5.2 TOML 구조

```toml
[team]
name = "my-template"
description = "템플릿 설명"

[[agents]]
name = "Worker-A"
role = "역할 설명"
task_template = """
{goal}에 대한 작업을 수행하세요.

## 기술 스택
- 사용할 기술

## 산출물
- handoff.md에 작업 결과 요약 기록

## 범위
- 프로젝트의 기존 디렉토리 구조를 따르세요
"""

[[agents]]
name = "Worker-B"
role = "역할 설명"
blocked_by = ["Worker-A"]
task_template = """
{goal}에 대한 후속 작업을 수행하세요.

## 지침
- Worker-A의 handoff.md에서 선행 작업 결과를 확인하세요
"""
```

### 5.3 템플릿 작성 규칙

| 규칙 | 설명 |
|------|------|
| `{goal}` 플레이스홀더 | 모든 task_template에 포함 (`/team-launch --goal` 값으로 치환) |
| `blocked_by` | 선행 에이전트 이름 배열 (plan.json의 `depends_on`으로 자동 변환) |
| handoff 패턴 | 루트 에이전트는 handoff.md **작성** 지침, 후속 에이전트는 **읽기** 지침 |
| 산출물 경로 | `docs/`에 저장 시 `YYMMDD-` prefix 규칙 안내 |
| 에이전트 이름 | 영어, 고유값 (브랜치/slug 생성에 사용) |

### 5.4 기존 템플릿 참고

| 템플릿 | 패턴 | 에이전트 수 |
|--------|------|------------|
| `fullstack-dev` | 선형 DAG (A → B → C) | 3 |
| `content-pipeline` | 선형 체인 (A → B → C → D) | 4 |
| `multi-reviewer` | 팬인 (A + B + C → D) | 4 |
| `figma-to-prod` | 선형 DAG | 3 |
| `planning` | 팬인 (A + B → C) | 3 |

---

## 6. 동기화

### 6.1 저장소 내 멀티 환경 (symlink)

```
GEMINI.md  → CLAUDE.md           # Gemini CLI용
AGENTS.md  → CLAUDE.md           # Codex CLI, OpenCode용
.agents/skills/ → .claude/skills/  # 스킬 공유
```

### 6.2 다른 프로젝트에 동기화 (복사)

다른 프로젝트(예: memoriz)에 `CLAUDE.md`/`AGENTS.md`/`GEMINI.md` 엔트리포인트, `contexts`, `.agents/skills`, `.claude/` 공유 자산과 runtime closure를 동기화할 때는 `sync-to-projects.sh`를 사용합니다. 기본 동작은 읽기 전용 dry-run입니다:

```bash
# 등록된 모든 프로젝트의 변경 계획
bash scripts/sync-to-projects.sh

# 특정 프로젝트의 변경 계획
bash scripts/sync-to-projects.sh /path/to/project

# canary 1개에 명시 적용
bash scripts/sync-to-projects.sh --canary --apply
```

새 프로젝트는 `.claude/registry/projects/projects.json`에 등록합니다. 배포 closure는 `.claude/project-packs/default/pack.json`과 project profile overlay가 소유하며, registry/rules/evals/runtime scripts와 고정된 Gongnyang runtime도 여기서 선언합니다.
프로젝트별 권한/MCP 설정(`.claude/settings*.json`, `.mcp.json`)은 동기화하지 않습니다.

### 6.3 핵심 원칙

- **원본은 항상 `.claude/`에서 수정**
- 다른 프로젝트의 `.claude/`를 직접 수정하지 않음 (sync로 덮어씌워짐)
- 스킬/에이전트 변경 후 `sync-to-projects.sh` dry-run을 검토하고 승인된 경우에만 `--apply`

---

## 7. 검증

커밋 전에 다음 스크립트를 실행하여 무결성을 확인합니다.

### 7.1 Runtime closure 검증

```bash
bash -n scripts/install.sh docs/install.sh scripts/sync-to-projects.sh
python3 -m unittest discover -s tests/runtime -p 'test_install_script.py' -v
python3 scripts/harness-registry.py validate
python3 scripts/harness-context.py --output /tmp/harness-context.json
python3 scripts/harness-doctor.py
```

### 7.2 프론트매터 검증

모든 SKILL.md에 YAML 프론트매터가 있는지 확인:

```bash
bash scripts/validate-skills.sh
```

### 7.3 참조 무결성 검증

SKILL.md에서 참조하는 파일이 실제로 존재하는지 확인:

```bash
python scripts/integrity-check.py
```

### 7.4 카탈로그 재생성

스킬 추가/수정 후 카탈로그를 업데이트:

```bash
python scripts/skill-catalog.py
```

---

## 8. 네이밍 컨벤션 요약

| 대상 | 형식 | 예시 |
|------|------|------|
| 스킬 디렉토리 | kebab-case | `my-new-skill/` |
| 스킬 파일 | 고정 | `SKILL.md` |
| 에이전트 (단일) | `{domain}-agent.md` | `fastapi-agent.md` |
| 에이전트 (디렉토리) | `{domain}/{domain}-unified.md` | `figma-to-flutter/figma-to-flutter-unified.md` |
| 커맨드 | kebab-case | `financial-report.md` |
| 팀 템플릿 | kebab-case `.toml` | `fullstack-dev.toml` |
| 문서 (docs/) | `YYMMDD-description.md` | `260316-liff-integration-guide.md` |
| 메타 문서 | 날짜 없이 | `CONTRIBUTING.md`, `CHANGELOG.md` |

---

## 9. 체크리스트

새 스킬/에이전트 추가 시:

- [ ] `_template/SKILL.md` 기반으로 생성했는가
- [ ] 필수 프론트매터 필드가 모두 있는가 (`name`, `description`, `metadata`)
- [ ] 올바른 카테고리 디렉토리에 배치했는가
- [ ] kebab-case 네이밍을 따르는가
- [ ] `scripts/validate-skills.sh` 통과하는가
- [ ] `scripts/skill-catalog.py`로 카탈로그를 갱신했는가
- [ ] `.claude/` 원본을 수정했는가 (다른 프로젝트 직접 수정 금지)
- [ ] `bash scripts/sync-to-projects.sh`로 다른 프로젝트에 동기화했는가
