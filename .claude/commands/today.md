---
description: "Daily command - Context-aware task execution with auto skill routing"
argument-hint: "[instruction]"
type: utility
allowed-tools: AskUserQuestion, Bash, Read, Write, Edit, Glob, Grep, Task, Skill
model: inherit
quality_tier: reasoning_high
---

## Pre-execution Context

!date +%Y-%m-%d

---

# /today - Context-Aware Daily Command

## Core Principle

Thin router with category-based briefings.
When no arguments given, show categories. Each category runs ALL its skills as a combined briefing.
Keywords still work for individual skill access.

## Categories

| Category | Skills | Description |
|----------|--------|-------------|
| Dev | daily-hackernews, daily-producthunt | Developer news briefing (HN + Product Hunt) |
| Biz | daily-kstartup, daily-invest-news | Business briefing (K-Startup announcements + funding news) |
| Content | daily-blog-idea | Content creation (blog topic ideas from trending data) |

## Routing Rules

### Category Keywords (runs ALL skills in category)

| Keywords | Category |
|----------|----------|
| dev, developer, 개발 | Dev |
| biz, business, 비즈니스, 사업 | Biz |
| content, 콘텐츠, 글쓰기 | Content |
| all, 전체, 브리핑, briefing | ALL categories |

### Individual Skill Keywords (runs single skill)

| Keywords | Skill |
|----------|-------|
| k-startup, 사업공고, 창업지원, kstartup | daily-kstartup |
| hackernews, hn, tech news, 뉴스, 트렌드 | daily-hackernews |
| producthunt, product hunt, ph, 런칭, 신제품 | daily-producthunt |
| 투자, 펀딩, investment, funding, 스타트업투자 | daily-invest-news |
| blog idea, 블로그 주제, 글감, blog topic | daily-blog-idea |

If no match → treat as general instruction and route to appropriate agent.

## Command Flow

```
/today "$ARGUMENTS"
  |
  +-- No arguments? → AskUserQuestion with 3 categories
  |     - "Dev" → run hackernews + producthunt together
  |     - "Biz" → run kstartup + invest-news together
  |     - "Content" → run blog-idea
  |     - "Other" → free-form keyword input
  |
  +-- Has arguments?
        - Match category keyword? → run ALL skills in category
        - Match individual keyword? → run single skill
        - No match? → route to appropriate agent
```

## No Arguments Mode

When `/today` is called without arguments, use AskUserQuestion:

- Question: "What briefing do you want today?"
- Options:
  1. "Dev" - HN top stories + Product Hunt launches (developer news)
  2. "Biz" - K-Startup announcements + startup funding news
  3. "Content" - Blog post ideas from trending topics
- User can select "Other" to type specific keywords (e.g., "hn", "invest")

## Category Execution Pattern

When a category is selected, run ALL skills in that category:

1. Load each skill file in the category via Read tool
2. Execute each skill's data fetching steps (in parallel when possible)
3. Combine results into a unified briefing format

### Dev Briefing Output Format

```markdown
## Dev Briefing ({DATE})

### Hacker News - Top Stories
{hackernews results}

### Product Hunt - New Launches
{producthunt results}
```

### Biz Briefing Output Format

```markdown
## Biz Briefing ({DATE})

### K-Startup Announcements
{kstartup results}

### Investment News
{invest-news results}
```

### Content Briefing Output Format

```markdown
## Content Briefing ({DATE})

### Blog Post Ideas
{blog-idea results}
```

## Output Language

Always respond in user's conversation_language (detect from conversation context).

---

## EXECUTION DIRECTIVE

1. Read today's date from pre-execution context

2. Check $ARGUMENTS:
   - IF empty → AskUserQuestion with 3 category options
   - IF matches category keyword → run all skills in that category
   - IF matches individual skill keyword → run single skill
   - IF "all" / "전체" → run all categories sequentially

3. For category execution:
   - Read each skill SKILL.md in the category
   - Execute data fetching steps from each skill (parallel when independent)
   - Combine into unified briefing format

4. For individual skill execution:
   - Read the matching skill SKILL.md
   - Execute according to skill instructions

5. For unmatched instructions:
   - Analyze intent and route to appropriate agent

6. Present results in clean, organized format

---

Version: 2.0.0
Last Updated: 2026-02-13
Core: Category-based daily briefing with keyword fallback
