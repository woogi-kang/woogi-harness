---
name: future-slide-qa
description: "Future Slide/Tightened Slide HTML 덱의 validator, screenshot, overflow, padding, Korean word breaking, image slot QA를 실행합니다."
argument-hint: "[path/to/index.html]"
metadata:
  category: "📝 콘텐츠"
  version: "0.1.0"
  tags: "presentation, qa, playwright, screenshot, future-slide"
  author: "woogi"
---

# Future Slide QA

Future Slide HTML 덱을 납품하기 전에 실행하는 자동 QA입니다.

## Workflow

1. 원본 validator 실행

```bash
node ".claude/skills/📝 콘텐츠/future-slide-skills/_vendor/future-slide-skill/skills/tightened-slide/scripts/validate-deck.mjs" path/to/index.html
```

2. 시각 QA 실행

```bash
node ".claude/skills/📝 콘텐츠/future-slide-skills/future-slide-qa/scripts/check-tightened-deck.cjs" path/to/index.html --out path/to/qa
```

모바일 반응형까지 검토해야 하면:

```bash
node ".claude/skills/📝 콘텐츠/future-slide-skills/future-slide-qa/scripts/check-tightened-deck.cjs" path/to/index.html --out path/to/qa --mobile
```

## 검사 항목

- slide offscreen
- text overflow
- safe padding
- bottom navigation collision
- Korean heading auto-wrap risk
- Korean orphan particles or sentence endings rendered alone, such as `다.`
- `word-break: break-all` / `overflow-wrap:anywhere`
- `%` 라벨 letter spacing
- local image existence
- `data-image-slot`
- image alt text
- S15/S16/S22 slot class consistency
- 인포그래픽/이미지 slot의 목적이 장식이 아니라 메시지 이해에 필요한지
- PDF 동시 생성 여부와 PDF 페이지 수 일치 여부

자동 검사 후 수동 확대 검수:

- contact sheet는 문제 후보를 찾는 용도이며 PASS 근거가 아닙니다.
- 각 slide/page PNG를 읽을 수 있는 크기로 열어 제목-부제-본문-카드-캡션-하단 문장 위계를 확인합니다.
- 카드 간 gap, 표 row/column padding, 이미지-텍스트 간격, 하단 safe area를 확인합니다.
- 한글 제목/본문에 negative letter spacing이나 과한 압축 자간이 들어가지 않았는지 확인합니다.
- 사용자가 레이아웃 깨짐을 지적한 경우 기존 QA report를 폐기하고 새 렌더 기준으로 다시 작성합니다.
- 문제 슬라이드와 같은 layout family를 쓰는 슬라이드도 함께 재검수합니다.

## 산출물

```text
qa/
├── qa-report.md
├── desktop-slide-01.png
├── desktop-slide-02.png
├── contact-sheet.png
└── pdf-contact-sheet.png
```

최종 납품 전에는 `.claude/rules/common/presentation-quality-gate.md`도 함께 적용합니다. 이 QA 스킬이 HTML 렌더 문제를 잡고, 공통 게이트가 PDF 생성과 인포그래픽 적합성까지 닫습니다.

## 교체 판단

기존 PPT agent를 대체할지 평가할 때는 `references/replacement-rubric.md`를 사용합니다.
Retire/Merge는 `/skill-audit` 절차와 사용자 확인 후에만 실행합니다.
