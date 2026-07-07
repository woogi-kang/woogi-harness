---
name: future-slide-design
description: "Future Slide HTML 덱의 폰트, 컬러, 레이아웃 밀도, 한국어 줄바꿈, 이미지 사용 원칙을 정하는 디자인 가드레일."
argument-hint: "[deck-context]"
metadata:
  category: "📝 콘텐츠"
  version: "0.1.0"
  tags: "presentation, typography, korean, future-slide, design-system"
  author: "woogi"
---

# Future Slide Design

Future Slide 덱을 만들기 전에 적용하는 디자인 가드레일입니다.

## 기본 원칙

- Future Slide template의 locked layout을 유지합니다.
- 하나의 덱에는 하나의 accent color만 사용합니다.
- 장식용 gradient, shadow, glass, rounded-card 남발은 피합니다.
- 정보형 덱은 차분하고 밀도 있게, 브랜드/제품 덱은 이미지 slot을 더 적극적으로 사용합니다.

## 한국어 타이포그래피

기본 선택:
- 제목/본문: `SUIT`, `Pretendard`, `Noto Sans KR`
- 영문 보조: `Inter`
- 코드/숫자 보조: `JetBrains Mono`, 단 표/라벨에만 제한적으로 사용

규칙:
- 한국어 display heading은 의미 단위로 `<br>`을 명시합니다.
- `word-break: break-all`, `overflow-wrap:anywhere`로 한국어 제목을 억지로 맞추지 않습니다.
- 본문은 2-4줄 단위로 짧게 나누고, 한 줄에 너무 긴 복합명사를 넣지 않습니다.
- 숫자와 `%` 표기는 letter spacing을 넓히지 않습니다.
- 작은 라벨은 mono를 써도 되지만, 긴 한국어 문장에는 mono를 쓰지 않습니다.

## Layout 밀도

- 7-8장 덱은 최소 6개 이상의 Sxx layout을 사용합니다.
- S03/S09/S10 같은 statement layout은 핵심 전환점에만 사용합니다.
- 표/카드/매트릭스는 S04/S15/S16/S19/S20 안에서 처리합니다.
- 긴 본문을 한 슬라이드에 밀어 넣지 말고 S16 brief, S19 cards, S20 ledger로 분산합니다.

## 정보형 덱 레이아웃 게이트

한국어 강의/교육/기술 설명 덱은 아래 기준을 기본값으로 둡니다.

- **타이틀-핵심문장 간격**: 핵심문장/lede는 제목 바로 아래 공통 기준선에 둡니다. 슬라이드마다 y값을 다르게 두지 않습니다.
- **첫 콘텐츠 기준선**: 카드, 플로우, 표의 시작 y는 핵심문장과 충분히 분리하되 덱 전체에서 비슷하게 맞춥니다.
- **동일 위계 대칭**: 좌우 박스, 비교 카드, 프로세스 단계, 상단 예시 바와 하단 지표 바는 같은 left/right 기준을 공유합니다.
- **장식 제거**: 제목 옆 긴 라인, 번호 밑줄, 의미 없는 shadow는 기본적으로 금지합니다. 연결선은 실제 단계 흐름에만 씁니다.
- **강조색 제한**: 같은 프로세스 안에서 한 카드만 accent fill을 쓰려면 `현재 단계`, `핵심 위험`, `선택 상태` 같은 의미가 있어야 합니다. 의미가 없으면 같은 위계로 통일합니다.
- **문장 정렬**: 한국어 문장형 설명은 left align을 기본으로 합니다. 라벨은 짧게 분리하고, 라벨-본문 사이 spacing을 명시합니다.
- **최소 본문 크기**: 발표용 주요 본문은 축소하지 말고 문장과 구조를 줄입니다. 작은 meta label을 제외하고 읽기 어려운 8-9pt대 본문을 만들지 않습니다.

## 예시 설계 원칙

- 추상 개념은 `입력/질문 → 자연어 답변 → 문제점 → 구조화/검증 결과` 흐름으로 보여줍니다.
- `AI 답변을 서비스 데이터로 바꾼다`처럼 추상적인 말은 실제 필드와 동작으로 풉니다.
  예: `summary`는 화면 표시, `use_cases`는 저장/분류, `risk`는 검증/재요청 기준.
- 위험/편향/운영 실패는 가능하면 실제 사례를 사용하고, 실제 사례가 아니면 가상 예시임을 표시합니다.
- `방지 방향`처럼 모호한 제목은 피하고 `대응 설계`, `검증 흐름`, `운영 기준`처럼 행동이 드러나는 제목을 사용합니다.

## 이미지 사용

- 전체 슬라이드를 이미지로 만들지 않습니다. 텍스트는 HTML 레이어에 둡니다.
- 생성 이미지는 텍스트 없는 hero visual, diagram base, icon, texture, object illustration로 제한합니다.
- S22는 21:9 hero, S15/S16은 21:9 또는 16:10 slot을 우선 사용합니다.
- 이미지 prompt에는 "no text, no letters, no numbers, no UI labels"를 기본으로 넣습니다.
- 이미지 파일마다 alt text와 `data-image-slot`을 기록합니다.

## 기존 디자인 시스템과의 관계

필요하면 기존 PPT 디자인 시스템을 먼저 참고합니다.

```text
.claude/skills/📝 콘텐츠/presentation-agent-skills/5-design-system/
.claude/skills/design-system/data/slide-typography.csv
.claude/skills/design-system/data/slide-layouts.csv
```

Future Slide는 HTML locked layout을 우선하되, 브랜드 색상/폰트/톤은 기존 디자인 시스템의 결정을 재사용합니다.
