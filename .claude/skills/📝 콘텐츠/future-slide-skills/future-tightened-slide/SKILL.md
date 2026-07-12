---
name: future-tightened-slide
description: "Future Slide/Tightened Slide 기반 HTML 프레젠테이션 생성. locked layout, 한국어 타이포그래피, 이미지 slot, 자동 QA가 필요한 HTML 덱에 사용합니다."
argument-hint: "[topic-or-brief]"
metadata:
  category: "📝 콘텐츠"
  version: "0.1.0"
  tags: "presentation, html-deck, future-slide, tightened-slide, qa"
  author: "woogi"
---

# Future Tightened Slide

Future Slide의 `tightened-slide`를 우리 환경에 맞게 감싼 HTML 덱 생성 스킬입니다.

## 사용 기준

사용:
- "Future Slide로 만들어줘", "tightened slide", "HTML 덱", "web presentation", "키노트형 비주얼 덱"
- locked layout 기반의 시각 완성도가 중요한 분석/전략/브랜드 덱
- 최종 산출물이 `index.html`이고 screenshot/PDF 검증이 가능한 경우

사용하지 않음:
- 편집 가능한 `.pptx`가 1차 산출물인 경우. 이때는 `presentation-agent`와 `export-pptx`를 우선 사용합니다.
- 리서치/검증/스토리라인이 아직 필요한 경우. 기존 `ppt-research`, `ppt-validation`, `ppt-structure`를 먼저 사용합니다.
- 데이터 밀도가 높고 Chart.js 중심인 경우. 기존 `slides` 스킬을 우선 검토합니다.

## Vendor 위치

Future Slide에서 가져온 deterministic `tightened-slide` layout/validator 부분만 아래 경로에 보존합니다. 원본의 GPT image slide/prompt 서브스킬은 단일 이미지 경로와 충돌하므로 배포 표면에서 제거되었습니다.

```text
.claude/skills/📝 콘텐츠/future-slide-skills/_vendor/future-slide-skill/
```

충돌 방지를 위해 vendor 내부의 원본 `SKILL.md`는 `VENDOR_SKILL.md`로 이름을 바꿔 보존합니다. 실제 생성 시 먼저 원본 지침을 확인합니다.

```bash
sed -n '1,220p' ".claude/skills/📝 콘텐츠/future-slide-skills/_vendor/future-slide-skill/skills/tightened-slide/VENDOR_SKILL.md"
```

## Workflow

1. 입력 정리
   - 청중, 목적, 슬라이드 수, 언어, 최종 산출물 형식을 확인합니다.
   - 언어가 한국어이면 `<html lang="ko" data-language="ko">`를 사용합니다.

2. 디자인 방향 고정
   - `future-slide-design`을 적용해 폰트, accent, display heading 줄바꿈, 숫자 표기 규칙을 먼저 정합니다.
   - 한 덱에는 하나의 accent만 사용합니다.

3. Layout plan 작성
   - 슬라이드별 `data-layout`을 S01-S22 안에서만 고릅니다.
   - 7-8장 덱은 최소 6개 이상의 서로 다른 layout을 사용합니다.
   - 이미지가 있으면 layout slot을 먼저 고르고 그 다음 이미지를 생성합니다.

4. HTML 생성
   - vendor template을 복사해 `index.html`을 만듭니다.
   - global class를 새로 만들지 않고 template class와 inline tuning 중심으로 작성합니다.
   - 한국어 제목은 무작위 자동 줄바꿈에 맡기지 말고 필요한 위치에 `<br>`을 명시합니다.

5. 이미지 asset 적용
   - 새 이미지가 필요하면 `future-slide-asset-gen`을 사용합니다.
   - 생성형 raster는 `image-prompt` → upstream validator → Codex `$imagegen` → `gpt-image-2`로만 만듭니다.
   - 생성 이미지는 전체 슬라이드가 아니라 `S22`, `S15`, `S16` 등의 slot에 들어갈 보조 asset이어야 합니다.
   - 모든 로컬 이미지는 `images/` 아래에 저장하고 `data-image-slot`과 `alt`를 넣습니다.

6. 검증
   - vendor validator를 먼저 실행합니다.
   - 이어서 `future-slide-qa`를 실행해 screenshot/contact sheet 기반 QA를 남깁니다.
   - 최종 납품 전 `.claude/rules/common/presentation-quality-gate.md`를 적용해 인포그래픽 적합성, 전수 렌더, Korean word breaking, PDF 생성을 확인합니다.

## 필수 검증 명령

```bash
node ".claude/skills/📝 콘텐츠/future-slide-skills/_vendor/future-slide-skill/skills/tightened-slide/scripts/validate-deck.mjs" path/to/index.html
node ".claude/skills/📝 콘텐츠/future-slide-skills/future-slide-qa/scripts/check-tightened-deck.cjs" path/to/index.html --out path/to/qa
```

## Output

```text
target/
├── index.html
├── images/
├── asset_manifest.json        # 이미지 생성/slot 사용 시
├── pdf/
│   └── presentation.pdf
└── qa/
    ├── qa-report.md
    ├── desktop-slide-01.png
    ├── contact-sheet.png
    └── pdf-contact-sheet.png
```

## 합격 기준

- vendor validator error 0건
- QA report의 FAIL 0건
- layout overflow, offscreen, bottom nav collision, padding violation 0건
- 한국어 display heading의 부자연스러운 자동 줄바꿈 없음
- 생성 이미지 안에 읽어야 하는 텍스트 없음
- PDF 페이지 수가 슬라이드 수와 일치하고, PDF 렌더 contact sheet에서 잘림/overflow가 없음
