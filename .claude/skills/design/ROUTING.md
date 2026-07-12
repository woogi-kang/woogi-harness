# Design 스킬 라우팅 매트릭스

새 디자인 하네스를 중심으로 디자인 관련 스킬의 역할 분담과 라우팅 규칙을 정의한다.

## 스킬 역할 요약

| 스킬 | 역할 | 핵심 키워드 |
|------|------|-------------|
| `design` | **오케스트레이터** — 종합 디자인 요청을 적절한 스킬로 분배. 자체 구현은 CIP, 슬라이드, 아이콘, 소셜 포토만 담당 | CIP, 아이콘, 소셜 포토, 브랜드 패키지 |
| `design-harness` | **1차 디자인 하네스** — UI/UX 설계, 리디자인, audit/polish, brand/product register, anti-slop preflight, visual QA | UI/UX, 랜딩, 대시보드, 앱 UI, 스타일/컬러/폰트, 리디자인, AI스럽다, visual QA |
| `text-to-lottie` | **Lottie 제작 하네스** — Bodymovin JSON 생성/수정, Skottie 플레이어 검증, slots/controls 작성 | Lottie, 로티, Bodymovin, Skottie, lottie.json, animated JSON |
| `ui-styling` | **구현 단계** — shadcn/ui 컴포넌트 + Tailwind CSS로 실제 코드 작성 | shadcn, Tailwind, 컴포넌트 코드, 다크모드 구현 |
| `design-system` | **시스템 단계** — 3-레이어 토큰 아키텍처, CSS 변수, 컴포넌트 스펙 정의 | 토큰, CSS 변수, 컴포넌트 스펙, 토큰 검증 |
| `logo-creator` | **전문 특화** — `image-prompt` → validator → Codex `$imagegen`/`gpt-image-2` 로고 생성과 deterministic 파생 산출물 | 로고, brand mark, favicon, 앱 아이콘 |
| `banner-design` | **전문 특화** — 배너 디자인 (소셜/광고/웹/인쇄) | 배너, 커버, 헤더, 광고 배너 |

## 라우팅 매트릭스

| 사용자 의도 | 1차 스킬 | 2차 스킬 (위임) | 사용하지 않음 |
|-------------|----------|-----------------|---------------|
| "랜딩 페이지 디자인해줘" | `design-harness` | `ui-styling` (구현) | `design`, `design-system`, `logo-creator`, `banner-design` |
| "AI스럽지 않게/템플릿 같지 않게 개선해줘" | `design-harness` | `ui-styling` (구현) | `logo-creator`, `banner-design` |
| "이 페이지 UX 리뷰해줘" | `design-harness` | — | `ui-styling`, `design`, `design-system` |
| "리디자인/폴리시/고급스럽게 다듬어줘" | `design-harness` | `ui-styling` (구현) | `logo-creator`, `banner-design` |
| "Lottie/로티 애니메이션 만들어줘" | `text-to-lottie` | `design-harness` (모션 의도/타이밍 결정) | `ui-styling`, `banner-design` |
| "SVG path를 움직이는 Lottie로 변환해줘" | `text-to-lottie` | `design-harness` (브랜드/모션 방향 필요 시) | `logo-creator`, `slides` |
| "대시보드 컬러/폰트 추천해줘" | `design-harness` | `design-system` (토큰화 필요 시) | `ui-styling`, `design` |
| "버튼 컴포넌트 만들어줘" | `ui-styling` | `design-harness` (의사결정 필요 시) | `design` |
| "shadcn Dialog 추가해줘" | `ui-styling` | — | `design`, `design-system` |
| "다크모드 구현해줘" | `ui-styling` | `design-harness` (컬러/대비 검증) | `design`, `design-system` |
| "디자인 토큰 만들어줘" | `design-system` | `design-harness` (방향 결정 필요 시) | `ui-styling` |
| "CSS 변수 시스템 구축해줘" | `design-system` | `design-harness` (방향 결정 필요 시) | `ui-styling` |
| "컴포넌트 스펙 정의해줘" | `design-system` | `design-harness` (상태/UX 기준 필요 시) | `ui-styling` |
| "로고 만들어줘" | `logo-creator` | — | `design`, `design-harness`, `ui-styling` |
| "favicon 만들어줘" | `logo-creator` | — | `design`, `design-harness` |
| "배너 디자인해줘" | `banner-design` | `design-harness` (아트 디렉션/anti-slop) | `design`, `ui-styling` |
| "트위터 헤더 만들어줘" | `banner-design` | — | `design`, `design-harness` |
| "CIP 만들어줘" | `design` | `logo-creator` (로고 없으면) | `design-harness`, `ui-styling` |
| "명함/레터헤드 디자인" | `design` | — | `design-harness`, `ui-styling`, `banner-design` |
| "아이콘 생성해줘" | `design` | — | `ui-styling`, `banner-design` |
| "소셜 포토 만들어줘" | `design` | `design-harness` (아트 디렉션/anti-slop) | `ui-styling`, `banner-design` |
| "슬라이드/발표자료 만들어줘" | `slides` | `design-system` (토큰 적용) | `design-harness`, `ui-styling` |
| "브랜드 패키지 전체 만들어줘" | `design` (오케스트레이션) | `logo-creator` → `design` (CIP) → `banner-design` | `ui-styling` |
| "새 프로젝트 디자인 시스템 구축" | `design-harness` (방향) | `design-system` (토큰) → `ui-styling` (구현) | `design`, `logo-creator`, `banner-design` |
| "Tailwind 테마 설정해줘" | `ui-styling` | `design-system` (토큰 연동) | `design` |
| "프레젠테이션 만들어줘" | `slides` | `design-system` (토큰) | `ui-styling` |

## 의사결정 플로우차트

```
사용자 요청 분석
      │
      ├─ 로고/favicon/앱 아이콘? ──────────→ logo-creator
      │
      ├─ 배너/커버/헤더/광고 배너? ────────→ banner-design
      │
      ├─ Lottie/Bodymovin/로티/Skottie?
      │  lottie.json/animated JSON? ───────→ text-to-lottie
      │
      ├─ CIP/명함/아이콘/소셜포토/슬라이드? → design (자체 처리)
      │
      ├─ 브랜드 패키지 전체? ──────────────→ design (오케스트레이션)
      │                                      ├→ logo-creator
      │                                      ├→ design (CIP)
      │                                      └→ banner-design
      │
      ├─ 토큰/CSS 변수/컴포넌트 스펙? ─────→ design-system
      │
      ├─ UI/UX/스타일/컬러/폰트/리디자인?
      │  UX 리뷰/anti-slop/visual QA? ─────→ design-harness
      │
      └─ 컴포넌트 코드 구현? ──────────────→ ui-styling
         shadcn/Tailwind 작업?
         다크모드/반응형 구현?
```

## 핵심 경계 규칙

1. **`design`은 구현하지 않는다** — CIP, 슬라이드, 아이콘, 소셜 포토만 자체 처리. 나머지는 위임.
2. **`design-harness`가 UI/UX 의사결정의 1차 진입점이다** — brief read, register, dials, anti-slop, audit/polish/redesign을 담당한다.
3. **`ui-styling`은 디자인 의사결정을 하지 않는다** — 주어진 스펙대로 구현. 스타일 선택은 `design-harness`에 위임.
4. **`design-system`은 UI 코드를 작성하지 않는다** — 토큰과 스펙만 정의. 실제 적용은 `ui-styling`이 담당.
5. **`logo-creator`와 `banner-design`은 독립적이다** — 다른 스킬의 영역을 침범하지 않는다.
6. **`logo-creator`는 로고만 만든다** — CIP, 배너, 아이콘은 절대 처리하지 않는다.
7. **`banner-design`은 배너만 만든다** — 로고, CIP, UI 컴포넌트는 절대 처리하지 않는다.
8. **`text-to-lottie`는 Lottie JSON 산출물에만 사용한다** — 모션 의도는 `design-harness`, 영상 타임라인은 Remotion 계열, 일반 UI 전환은 `ui-styling`/프레임워크 코드가 맡는다.
9. **생성형 raster는 단일 경로를 사용한다** — 자체 prompt를 만들지 않고 `image-prompt` → upstream validator → Codex `$imagegen` → `gpt-image-2`로만 생성한다.
