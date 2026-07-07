---
name: ppt-design-system
description: |
  전문 프레젠테이션 디자인 시스템. 정밀한 타이포그래피, 10가지 토픽별 테마, 10가지 슬라이드 템플릿 제공.
  "디자인 적용", "템플릿", "스타일 시스템" 요청 시 활성화.
---

# PPT Design System Skill

Extends: `../../../design-system/SKILL.md` (공통 디자인 시스템 토큰 아키텍처 참조)

전문적인 프레젠테이션 디자인을 위한 정밀 시스템입니다.
**"Less is More"** 철학을 기반으로 불필요한 요소를 제거하고 콘텐츠에 집중합니다.

## Topic-Based Themes (10가지)

각 주제에 맞는 전문 테마가 별도 파일로 분리되어 있습니다:

| Theme | File | Use Case |
|-------|------|----------|
| Healthcare Clean | [themes/01-healthcare/](./themes/01-healthcare/THEME.md) | 의료, 바이오, 헬스케어 |
| Education Bright | [themes/02-education/](./themes/02-education/THEME.md) | 교육, 트레이닝, 워크샵 |
| Fintech Bold | [themes/03-fintech/](./themes/03-fintech/THEME.md) | 핀테크, 금융, 크립토 |
| AI Futuristic | [themes/04-ai-tech/](./themes/04-ai-tech/THEME.md) | AI/ML, 테크, 개발자 |
| Sustainability Earth | [themes/05-sustainability/](./themes/05-sustainability/THEME.md) | ESG, 환경, 지속가능성 |
| Startup Gradient | [themes/06-startup/](./themes/06-startup/THEME.md) | 피치덱, 스타트업, VC |
| Luxury Noir | [themes/07-luxury/](./themes/07-luxury/THEME.md) | 럭셔리, 프리미엄, VIP |
| Creative Neon | [themes/08-creative/](./themes/08-creative/THEME.md) | 에이전시, 디자인, 포트폴리오 |
| Real Estate Trust | [themes/09-real-estate/](./themes/09-real-estate/THEME.md) | 부동산, 투자, 자산 |
| F&B Appetite | [themes/10-fnb/](./themes/10-fnb/THEME.md) | 식음료, 레스토랑, 호텔 |

> **Theme Selection:** [themes/INDEX.md](./themes/INDEX.md) - 테마 선택 가이드 및 키워드 매핑

## 슬라이드 규격

### 표준 크기 (포인트 단위)

| 비율 | 너비 | 높이 | 용도 |
|------|------|------|------|
| **16:9** | 720pt | 405pt | 표준 (권장) |
| 16:10 | 720pt | 450pt | 맥북/태블릿 |
| 4:3 | 720pt | 540pt | 레거시 프로젝터 |

### 단위 변환

```
1 inch = 72pt = 96px = 914400 EMU
PT_PER_PX = 0.75
PX_PER_IN = 96
```

---

## 상세 문서

디자인 시스템의 상세 내용은 아래 파일들로 분리되어 있습니다:

| 문서 | 설명 | 내용 |
|------|------|------|
| [typography.md](./typography.md) | 타이포그래피 시스템 | 폰트, 크기 계층, CSS 정의 |
| [palettes.md](./palettes.md) | 컬러 팔레트 | 5가지 팔레트 상세 및 선택 가이드 |
| [layout.md](./layout.md) | 레이아웃 & 템플릿 | 그리드 시스템 + 10가지 슬라이드 템플릿 |
| [components.md](./components.md) | 컴포넌트 라이브러리 | HTML 컴포넌트, 데이터 시각화, CTA |
| [THEMES.md](./THEMES.md) | 테마 선택 가이드 | 발표 유형별 테마 추천 |

---

## 디자인 적용 워크플로우

```
1. 발표 유형 분석
        │
        ▼
2. 팔레트 선택
   ├── Executive Minimal (임원/투자)
   ├── Sage Professional (컨설팅/ESG)
   ├── Modern Dark (테크/스타트업)
   ├── Corporate Blue (기업/금융)
   └── Warm Neutral (마케팅/브랜드)
        │
        ▼
3. 템플릿 매핑
   ├── 표지 → Cover Slide
   ├── 목차 → Contents
   ├── 섹션 시작 → Section Divider
   ├── 일반 내용 → Content Slide
   ├── 핵심 수치 → Statistics
   ├── 비교/사례 → Split Layout
   ├── 팀 소개 → Team Slide
   ├── 인용/강조 → Quote Slide
   ├── 로드맵 → Timeline
   └── 마무리 → Closing Slide
        │
        ▼
4. 타이포그래피 적용
        │
        ▼
5. 접근성 검증
   ├── 대비율 체크 (4.5:1 이상)
   ├── 최소 폰트 크기 (12pt)
   └── 색맹 친화적 팔레트
        │
        ▼
6. Export Skill로 전달
```

## 한국어 정보형 덱 재발 방지 게이트

TeamSparta AX 강의 덱 수정 이력에서 확인된 문제를 기본 설계 게이트로 적용합니다.
PPTX, HTML 덱, PDF 납품 모두에 적용합니다.

### 1. 타이틀-핵심문장-본문 위계

- 제목과 핵심문장 사이 간격은 덱 전체에서 같은 기준선을 사용합니다. 슬라이드별 임의 y값을 두지 않습니다.
- `핵심 · ...` 문장은 제목 바로 아래의 보조 헤드라인입니다. 본문 카드나 플로우 영역처럼 보일 정도로 떨어뜨리지 않습니다.
- 같은 유형의 슬라이드에서는 제목, 핵심문장, 첫 콘텐츠 블록의 top y 기준을 토큰화합니다.
- 본문이 많아져도 핵심문장을 아래로 밀지 말고, 본문 카드 수/문장 길이를 줄입니다.

### 2. 텍스트 크기와 줄바꿈

- 주요 본문은 발표용 화면에서 읽히는 크기를 우선합니다. 작은 설명을 8-9pt대로 밀어 넣지 않습니다.
- 한국어 설명은 의미 단위로 2-4줄에 나눕니다. 한 줄이 너무 길면 문장을 줄이지 말고 정보 구조를 나눕니다.
- 라벨은 짧게, 설명은 왼쪽 정렬을 기본으로 합니다. 문장형 설명을 중앙 정렬하지 않습니다.
- 긴 영문/코드/JSON은 보조 예시로만 쓰고, 한국어 설명보다 시각적으로 강해지지 않게 합니다.

### 3. 디자인 처리와 정렬

- 좌우 비교 박스, 상하 보조 박스, 플로우 바는 같은 좌우 기준선과 같은 높이 규칙을 사용합니다.
- 동일 위계 카드의 크기, fill, border, title/body spacing은 같아야 합니다.
- 제목 옆 장식 라인, 번호 밑줄, shadow 라인은 의미를 설명하지 않으면 제거합니다.
- 연결선은 단계 흐름을 보여줄 때만 사용합니다. 섹션 제목을 꾸미기 위한 라인은 쓰지 않습니다.

### 4. 강조 포인트

- accent color는 의미가 있는 한 가지 상태에만 씁니다. 임의로 한 단계만 초록/강조색 처리하지 않습니다.
- 프로세스 카드에서 한 단계가 강조색이면 `현재 단계`, `핵심 단계`, `위험 단계` 등 명시적 이유가 있어야 합니다.
- 강조 이유가 없으면 같은 프로세스의 모든 카드는 같은 위계로 맞춥니다.
- `예:`, `핵심 지표`, `판단 기준` 같은 보조 바는 중간 플로우/카드 영역과 좌우 폭을 맞춥니다.

### 5. 예시와 설명 밀도

- 추상 문구만으로 끝내지 않습니다. `질문/입력 → AI 답변 → 왜 문제인가 → 구조화/검증 결과` 흐름을 보여줍니다.
- "방지 방향", "서비스 데이터", "앱과 서버가 읽는다"처럼 모호한 표현은 실제 동작으로 바꿉니다.
  예: `출처 확인`, `최신 문서 검색(RAG)`, `편향·형식 오류 평가`, `summary/use_cases/risk 필드 저장`.
- 위험/편향 사례는 가능하면 실제 사례와 출처를 사용합니다. 실제 사례가 없으면 "가상의 예"라고 명시합니다.
- AI식 일반론보다 수업 맥락의 질문, 답변, 실패 조건, 재요청/폴백 같은 운영 흐름을 우선합니다.

## PptxGenJS 변환 규칙

### 색상 코드

```javascript
// HEX에서 '#' 제거 필수
const color = "667eea";  // ✅ 올바름
const color = "#667eea"; // ❌ 오류 발생
```

### 폰트 매핑

```javascript
const FONT_MAP = {
  'Pretendard': 'Pretendard',  // 로컬 설치 필요
  'Inter': 'Arial',            // 폴백
  'Poppins': 'Arial',          // 폴백
};
```

### 그라데이션 처리

```javascript
// CSS 그라데이션은 이미지로 변환 필요
// PptxGenJS는 CSS gradient 미지원

// 방법 1: 단일 색상으로 대체
// 방법 2: 배경 이미지로 렌더링
```

## 주의사항

1. **폰트 임베딩**: Pretendard는 로컬 설치 또는 이미지 변환 필요
2. **그라데이션**: CSS gradient는 이미지로 사전 렌더링
3. **색상 코드**: HEX에서 '#' 제거
4. **단위 변환**: pt ↔ px ↔ inch 정확히 계산
5. **텍스트 태그**: 시맨틱 HTML 사용 (p, h1-h6, ul, li)
6. **이미지 경로**: 절대 경로 사용

## 팔레트 선택 가이드

| 발표 상황 | 추천 팔레트 | 이유 |
|----------|------------|------|
| 투자자 피치 | Executive Minimal | 신뢰감, 집중도 |
| 기술 세미나 | Modern Dark | 몰입감, 트렌디 |
| 기업 보고서 | Corporate Blue | 전문성, 안정감 |
| ESG/지속가능성 | Sage Professional | 자연, 신뢰 |
| 마케팅 제안 | Warm Neutral | 친근함, 감성 |
