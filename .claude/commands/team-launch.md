---
description: "TOML 템플릿으로 사전 정의된 팀을 원커맨드 실행"
argument-hint: "<template-name> --goal '<목표 설명>'"
allowed-tools: Bash, Read, Write, Glob, Grep, AskUserQuestion
model: inherit
quality_tier: reasoning_high
---

## Pre-execution Context

!ls .claude/templates/*.toml 2>/dev/null || echo "No templates found"
!tmux ls 2>/dev/null || echo "No tmux sessions"

---

# /team-launch - One-Command Team Launch from Templates

## Core Principle

`.claude/templates/` 디렉토리의 TOML 템플릿을 사용하여
사전 정의된 팀 구성을 한 명령으로 실행합니다. 생성되는 plan에는 가능한 경우 실행 계약(`success_criteria`, `eval_type`, `stop_condition`, `approval_boundary`, `state_record`)을 포함합니다.

## Usage

```
/team-launch fullstack-dev --goal "JWT 인증 시스템 구현"
/team-launch content-pipeline --goal "신규 서비스 런칭 콘텐츠"
/team-launch multi-reviewer --goal "PR #42 리뷰"
/team-launch --list                                          → 사용 가능한 템플릿 목록
```

## Step 1: Parse Arguments

`$ARGUMENTS`에서 추출:
- `template-name`: TOML 파일명 (without .toml)
- `--goal`: 팀의 구체적 목표 (태스크에 주입)
- `--list`: 사용 가능한 템플릿 목록 표시

## Step 2: List Templates (--list)

If `--list`:
```bash
# Read all .toml files in .claude/templates/
# Show: name, description, agents, dependency structure
```
STOP after showing list.

## Step 3: Load Template

`.claude/templates/{template-name}.toml` 읽기.

TOML 구조:
```toml
[team]
name = "fullstack-dev"
description = "Full-stack: backend + frontend + tester"

[[agents]]
name = "Backend"
role = "API 엔드포인트 구현"
task_template = """
{goal}에 대한 백엔드 API를 구현하세요.
## 기술 스택
- FastAPI + SQLAlchemy + Clean Architecture
## 범위
- src/api/ 디렉토리
"""

[[agents]]
name = "Frontend"
role = "UI 컴포넌트 구현"
blocked_by = ["Backend"]
task_template = """
{goal}에 대한 프론트엔드 UI를 구현하세요.
## 기술 스택
- Next.js App Router + TanStack Query + shadcn/ui
## 범위
- src/app/ 디렉토리
"""

[[agents]]
name = "Tester"
role = "테스트 작성 및 실행"
blocked_by = ["Backend", "Frontend"]
task_template = """
{goal}에 대한 테스트를 작성하세요.
## 범위
- tests/ 디렉토리
"""

```

## Step 4: Generate Plan

TOML → plan.json 변환:
1. `--goal`이 없거나 비어 있으면 에러 → 사용 예시를 보여주고 STOP
2. `{goal}`을 사용자의 `--goal` 값으로 치환 (str.replace, format 아님)
3. `blocked_by` → `depends_on` 변환
4. 템플릿에 `success_criteria`, `eval_type`, `stop_condition`, `approval_boundary`, `state_record`, `context_pack`가 있으면 plan worker에 그대로 전달
5. 세션 이름 생성: `{template-name}-{goal-slug}`

```json
{
  "session": "fullstack-dev-jwt-auth",
  "workers": [
    { "name": "Backend", "task": "...(goal 주입됨)..." },
    { "name": "Frontend", "task": "...", "depends_on": ["Backend"] },
    {
      "name": "Tester",
      "task": "...",
      "depends_on": ["Backend", "Frontend"],
      "success_criteria": ["Relevant tests pass"],
      "eval_type": "integration",
      "stop_condition": "Stop when the relevant tests pass or a blocker is recorded.",
      "state_record": ".orchestration/{session}/tester/handoff.md",
      "context_pack": ".orchestration/context-packs/{session}-tester/report.md"
    }
  ]
}
```

## Step 5: Confirm & Execute

- Dry-run 실행하여 계획 표시
- AskUserQuestion으로 확인
- --execute 실행
- --watch 안내 (DAG인 경우)

---

## EXECUTION DIRECTIVE

1. Parse `$ARGUMENTS` for template name, --goal, or --list

2. IF --list:
   - Read all `.claude/templates/*.toml` files
   - Display formatted table: name | description | agents | deps
   - STOP

3. IF template launch:
   - Read `.claude/templates/{name}.toml`
   - If not found, show available templates and suggest closest match
   - Replace `{goal}` in all task_template fields with --goal value
   - Convert to plan.json format (blocked_by → depends_on, execution-contract fields and context_pack preserved)
   - Generate session name: `{name}-{slugified-goal}`
   - Save plan.json to `.orchestration/{session}/plan.json`
   - Run dry-run
   - Ask user to confirm
   - If confirmed, run --execute
   - Show post-execution guide with --watch instructions

4. Key principles:
   - Template TOML is the source of truth for team structure
   - --goal provides the variable context
   - Session names are auto-generated but predictable
   - All TOML fields except task_template are optional

---

Version: 1.0.0
Last Updated: 2026-03-19
Core: TOML template → plan.json → DAG execution
