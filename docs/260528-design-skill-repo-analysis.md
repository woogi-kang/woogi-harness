# 디자인 스킬 리서치 분석

분석 기준일: 2026-05-28 KST  
상태: 2026-05-29에 `design-harness`로 superseded. 이 문서는 `design-craft` 1차 초안의 배경 분석으로 보존한다. 최신 마이그레이션 기준은 `docs/260529-design-harness-migration.md`를 따른다.

분석 대상:

- https://github.com/emilkowalski/skill
- https://github.com/pbakaus/impeccable
- https://github.com/Leonxlnx/taste-skill

## 최신 HEAD

| Repo | Latest commit inspected | Commit date | Note |
|---|---|---:|---|
| `emilkowalski/skill` | `ecf66bbd1fb33c25332b6b0e454d08049978284c` | 2026-03-25 15:59:35 +0100 | `format` |
| `pbakaus/impeccable` | `84135db0e6bdd58d22828f7bc8331cae7bde3e7f` | 2026-05-22 09:28:36 -0700 | `Add DeepSeek live E2E adapter (#163)` |
| `Leonxlnx/taste-skill` | `3c7017d636c3a4aad378433ea6d0cfa6c921da4a` | 2026-05-26 21:31:36 +0200 | `feat(skill): round-5 hardening...` |

## 1. `emilkowalski/skill`

### 구조

- 매우 작은 레포.
- 실질 콘텐츠는 `skills/emil-design-eng/SKILL.md` 하나가 핵심이다.
- README는 배포 링크만 제공한다.

### 핵심 방향

이 스킬의 강점은 "디자인 엔지니어링 감각"을 미세 상호작용까지 끌고 내려오는 데 있다.

- Taste는 선천적 취향이 아니라 훈련된 판단이라고 본다.
- 사용자가 의식하지 않는 디테일이 누적되어 품질을 만든다는 관점을 반복한다.
- 애니메이션은 먼저 빈도와 목적을 따진다.
- 키보드/고빈도 액션은 애니메이션을 줄이거나 없앤다.
- UI 애니메이션의 easing, duration, transform-origin, active feedback 같은 세부 규칙이 구체적이다.
- 리뷰 출력은 `Before / After / Why` 테이블을 요구해 피드백을 실행 가능한 형태로 만든다.

### 가져올 만한 점

- 미세 상호작용을 취향 문제가 아니라 사용 빈도, 목적, 지각 성능으로 판단하는 프레임.
- 버튼 active state, popover origin, tooltip delay 같은 "작지만 누적되는" 품질 기준.
- 리뷰 결과를 Before/After/Why로 구조화하는 형식.

### 그대로 가져오면 안 되는 점

- 범위가 motion/detail에 집중되어 있어 랜딩/대시보드/리디자인 전체를 라우팅하기에는 좁다.
- 초기 응답을 고정하는 방식은 우리 harness의 협업 흐름과 맞지 않는다.

## 2. `pbakaus/impeccable`

### 구조

- 단순 스킬이 아니라 CLI, 웹사이트, 라이브 브라우저 모드, detector, 테스트 fixture를 포함한 큰 시스템이다.
- 핵심 스킬은 `plugin/skills/impeccable/SKILL.md`.
- `reference/brand.md`, `reference/product.md`가 brand/product register를 분리한다.
- `reference/*.md`에 craft, shape, audit, polish, bolder, quieter, harden 등 하위 명령별 워크플로우가 있다.
- `scripts/load-context.mjs`, detector, live iteration 관련 스크립트가 있다.

### 핵심 방향

Impeccable의 핵심은 "디자인 register와 프로젝트 컨텍스트를 먼저 로드한 뒤 작업하라"는 운영 체계다.

- `PRODUCT.md`와 `DESIGN.md`를 컨텍스트로 로드한다.
- 작업이 brand surface인지 product surface인지 먼저 결정한다.
- product UI는 익숙함, 상태 완성도, 일관성을 우선한다.
- brand surface는 distinctiveness, imagery, 색/타입의 명확한 POV를 요구한다.
- shared design laws는 OKLCH, theme scene sentence, card 절제, absolute bans, AI slop test로 구성된다.
- 명령형 서브커맨드가 세분화되어 있어 `audit`, `polish`, `typeset`, `colorize`, `harden` 등이 각각 다른 레퍼런스를 로드한다.
- detector와 live mode가 있는 점이 일반 SKILL.md보다 훨씬 실행 중심이다.

### 가져올 만한 점

- Brand/Product register 분리. 우리 기존 스킬은 웹/모바일/대시보드 규칙은 많지만 "디자인이 상품인가, 업무를 돕는가"의 기준이 상대적으로 약하다.
- `PRODUCT.md`/`DESIGN.md` 같은 프로젝트 컨텍스트를 먼저 읽는 흐름.
- "카테고리에서 바로 예측되는 디자인이면 실패"라는 anti-slop 판단.
- 절대 금지 패턴을 mechanical preflight로 확인하는 방식.
- 리디자인/폴리시/감사/하드닝을 구분하는 명령형 사고.

### 그대로 가져오면 안 되는 점

- Impeccable은 자체 CLI와 스크립트를 전제로 한다. 우리 repo에 그대로 들이면 유지 비용이 크다.
- 세부 reference tree 전체를 복제하면 기존 `ui-ux-pro-max`, `ui-styling`, `design-system`과 중복된다.
- "absolute ban"이 너무 많아지면 작업자의 판단 폭을 과하게 줄일 수 있다. 핵심 tell만 우선해야 한다.

## 3. `Leonxlnx/taste-skill`

### 구조

- 여러 개의 agent skill 묶음이다.
- 기본 스킬은 `skills/taste-skill/SKILL.md`의 `design-taste-frontend` v2.
- `gpt-tasteskill`, `redesign-skill`, `minimalist-skill`, `brutalist-skill`, `soft-skill`, `image-to-code-skill`, image generation skills가 함께 있다.
- `research/laziness` 폴더에 LLM lazy output의 원인과 remediation 문서가 있다.

### 핵심 방향

Taste Skill의 강점은 AI가 자주 내는 구체적 실패를 매우 세밀하게 막는 데 있다.

- 작업 전 `Design Read`를 한 줄로 선언한다.
- `DESIGN_VARIANCE`, `MOTION_INTENSITY`, `VISUAL_DENSITY` 3개 dial로 출력 경향을 조절한다.
- 실제 design system을 써야 하는 경우와 aesthetic만 빌려야 하는 경우를 구분한다.
- dependency verification을 강제한다.
- Inter, purple glow, beige/brass premium palette, generic bento, repeated eyebrows, hero overflow, fake precise numbers, fake screenshots 등 구체적인 AI tell을 금지한다.
- pre-flight check가 길고 세밀하다.
- 리디자인 스킬은 기존 프로젝트를 스캔, 진단, 타깃 수정하는 흐름이 실전적이다.

### 가져올 만한 점

- `brief read -> dials -> implementation -> preflight` 흐름.
- "AI default"를 일반론이 아니라 실제 실패 패턴으로 적는 방식.
- Hero, nav, bento, CTA, copy, image strategy 같은 화면 수준 검증.
- dependency check와 package import 검증.
- 리디자인에서 큰 재작성 대신 기존 stack을 존중하는 접근.

### 그대로 가져오면 안 되는 점

- rule 양이 매우 많아 모든 작업에 로드하면 context cost가 크다.
- Awwwards/GSAP 중심 variant는 product UI나 업무형 SaaS에는 과하다.
- 일부 규칙은 특정 스타일 취향에 강하게 기울어 있어 우리 harness의 범용 디자인 스킬로는 더 중립적으로 다듬어야 한다.

## 4. 우리 harness의 현재 상태

현재 관련 스킬:

- `ui-ux-pro-max`: 설계 DB. 스타일, 팔레트, 폰트, UX 룰, 차트 추천이 강하다.
- `ui-styling`: shadcn/ui + Tailwind 구현. 컴포넌트 구현 지침과 reference가 강하다.
- `design-system`: 토큰, CSS 변수, 컴포넌트 스펙 관리.
- `design`: CIP, 슬라이드, 아이콘, 소셜 포토 중심 오케스트레이터.
- `🎨 디자인/ui-design-agent-skills/*`: 방향, 컬러, 타이포그래피, 랜딩, 접근성 등 세부 가이드.

빈틈:

- 설계 DB와 구현 스킬 사이에 "이 결과가 AI template처럼 보이는가"를 막는 실행 가드레일이 약하다.
- 기존 `landing`류 스킬에는 centered hero, badge, gradient, trusted-by, card section 같은 템플릿 패턴이 예시로 많이 들어 있어 출력이 안전하지만 흔해질 수 있다.
- product UI와 brand surface를 같은 디자인 기준으로 처리하는 경향이 있다.
- visual asset strategy, copy self-audit, repeated section layout, fake screenshot ban 같은 현대적 anti-slop 항목이 라우팅에 명시되어 있지 않다.
- 구현 후 screenshot/mobile QA는 개발 지침에는 있으나 디자인 스킬의 preflight로 명문화되어 있지 않다.

## 5. 새 스킬 설계

추가한 스킬:

- Path: `.claude/skills/design-craft/SKILL.md`
- Name: `design-craft`
- 역할: `ui-ux-pro-max`의 추천과 `ui-styling`의 구현 사이에서 anti-slop 판단, register 결정, visual QA, redesign polish를 담당한다.

핵심 구성:

1. Brief read
   - surface, audience, physical scene, register, visual stance, risk를 한 줄로 선언.
2. Dials
   - `DISTINCTION`, `MOTION`, `DENSITY`로 작업별 강도를 조절.
3. Register
   - product: 익숙함, 상태 완성도, restrained color, standard affordance.
   - brand: POV, imagery, committed color, layout variation.
4. Anti-slop rules
   - AI purple gradient, centered hero + three cards, gradient text, default glass, hero metric, fake screenshot, repeated cards, cliche copy 금지.
5. Craft rules
   - typography, color, layout, motion, assets, interaction states.
6. Redesign protocol
   - stack scan, current design inventory, top slop/trust issue, low-risk improvement order.
7. Review format
   - Before / After / Why table.
8. Mechanical preflight
   - `rg` 기반 텍스트/패턴 탐지와 수동 QA 체크리스트.

## 6. 라우팅 제안

디자인 요청이 아래 중 하나라면 `design-craft`를 함께 사용한다:

- "AI스럽다", "템플릿 같다", "더 고급스럽게", "덜 제네릭하게", "감각 있게"
- 랜딩/포트폴리오/브랜드 페이지의 실제 구현 또는 리디자인
- UI polish, visual QA, launch 전 최종 디자인 점검
- 기존 화면을 큰 구조 변경 없이 더 믿을 만하게 만드는 작업
- 디자인 리뷰에서 before/after 근거가 필요한 경우

사용하지 않을 경우:

- 순수 색상/폰트 추천만 필요하면 `ui-ux-pro-max`.
- 이미 구체 스펙이 있고 컴포넌트 구현만 하면 `ui-styling`.
- 토큰 체계만 만들면 `design-system`.
- 로고/배너/CIP 등 asset-only 작업이면 전문 asset 스킬.

## 7. 기대 효과

- 기존 스킬을 대체하지 않고 사이에 품질 게이트를 추가한다.
- 스킬이 너무 데이터베이스형으로 흘러 "추천은 많지만 결과가 흔한" 문제를 줄인다.
- product와 brand의 성공 기준을 분리해 대시보드에 과한 아트디렉션을 넣거나, 브랜드 페이지를 업무형 UI처럼 죽이는 실수를 줄인다.
- 구현 전과 후 모두 사용할 수 있어 리디자인, 리뷰, QA에 재사용 가능하다.
