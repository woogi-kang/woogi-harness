---
name: export-pptx
description: "PPT PPTX 내보내기 — HTML 프레젠테이션을 PPTX 파일로 변환"
---

# PPT Export Skill

HTML 슬라이드를 전문적인 PPTX 파일로 변환하는 Skill입니다.
**HTML → PPTX 파이프라인**을 통해 정밀한 디자인 제어가 가능합니다.

## 핵심 워크플로우

```
┌─────────────────────────────────────────────────────────────┐
│                    HTML → PPTX Pipeline                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   1. HTML 슬라이드 생성                                       │
│        │                                                     │
│        ▼                                                     │
│   2. 브라우저 렌더링 (Playwright)                             │
│        │                                                     │
│        ▼                                                     │
│   3. DOM 분석 & 요소 추출                                     │
│        │                                                     │
│        ▼                                                     │
│   4. 검증 (크기, 오버플로우, 위치)                             │
│        │                                                     │
│        ├── 실패 → 오류 보고 & 수정                            │
│        │                                                     │
│        ▼                                                     │
│   5. PptxGenJS로 PPTX 생성                                   │
│        │                                                     │
│        ▼                                                     │
│   6. 썸네일 생성 & 최종 검증                                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 출력 포맷

| 포맷 | 용도 | 라이브러리 | 확장자 |
|------|------|-----------|--------|
| **PPTX** | 편집 가능 | PptxGenJS / python-pptx | .pptx |
| **PDF (발표용)** | 화면 공유 | LibreOffice | .pdf |
| **PDF (핸드아웃)** | 배포용 | LibreOffice + Pillow | .pdf |
| **PNG/JPG** | 썸네일/SNS | Sharp / Pillow | .png/.jpg |
| **HTML** | 웹 발표 | 원본 유지 | .html |

## 슬라이드 규격

### 표준 크기

```javascript
// 16:9 (권장)
const SLIDE_WIDTH = 720;   // pt
const SLIDE_HEIGHT = 405;  // pt

// 단위 변환 상수
const PT_PER_PX = 0.75;
const PX_PER_IN = 96;
const EMU_PER_IN = 914400;
const PT_PER_IN = 72;
```

### PptxGenJS 레이아웃 설정

```javascript
const pres = new PptxGenJS();
pres.defineLayout({
  name: 'CUSTOM_16_9',
  width: 10,      // inches (720pt / 72)
  height: 5.625   // inches (405pt / 72)
});
pres.layout = 'CUSTOM_16_9';
```

## HTML 슬라이드 구조

### 파일 명명 규칙

```
slides/
├── slide-01.html    # 표지
├── slide-02.html    # 목차
├── slide-03.html    # 섹션 구분
├── slide-04.html    # 콘텐츠
├── ...
└── slide-25.html    # 마무리
```

### HTML 템플릿 기본 구조

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=720, height=405">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css">
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    body {
      width: 720pt;
      height: 405pt;
      font-family: 'Pretendard', sans-serif;
      overflow: hidden;
    }
  </style>
</head>
<body>
  <!-- 슬라이드 콘텐츠 -->
</body>
</html>
```

## 핵심 스크립트

### 1. html2pptx (HTML → PPTX 변환)

```javascript
const { chromium } = require('playwright');
const PptxGenJS = require('pptxgenjs');
const path = require('path');

async function html2pptx(htmlFile, pres, options = {}) {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  // HTML 로드
  await page.goto(`file://${path.resolve(htmlFile)}`);

  // 슬라이드 데이터 추출
  const slideData = await extractSlideData(page);

  // 검증
  const validation = validateSlide(slideData);
  if (!validation.valid) {
    throw new Error(validation.errors.join('\n'));
  }

  // PPTX 슬라이드 생성
  const slide = pres.addSlide();
  await addElements(slideData, slide, pres);

  await browser.close();
  return { slide, slideData };
}
```

### 2. extractSlideData (DOM 분석)

```javascript
async function extractSlideData(page) {
  return await page.evaluate(() => {
    const body = document.body;
    const elements = [];

    // 배경 추출
    const bgColor = getComputedStyle(body).backgroundColor;
    const bgImage = getComputedStyle(body).backgroundImage;

    // 요소 순회
    function traverse(node, parent = null) {
      if (node.nodeType !== Node.ELEMENT_NODE) return;

      const rect = node.getBoundingClientRect();
      const style = getComputedStyle(node);

      const element = {
        type: detectElementType(node),
        tag: node.tagName.toLowerCase(),
        text: node.innerText,
        position: {
          x: rect.left * 0.75,  // px to pt
          y: rect.top * 0.75,
          width: rect.width * 0.75,
          height: rect.height * 0.75
        },
        style: {
          fontSize: parseFloat(style.fontSize) * 0.75,
          fontWeight: style.fontWeight,
          color: style.color,
          textAlign: style.textAlign,
          backgroundColor: style.backgroundColor
        }
      };

      elements.push(element);

      for (const child of node.children) {
        traverse(child, element);
      }
    }

    traverse(body);

    return {
      background: { color: bgColor, image: bgImage },
      elements,
      dimensions: {
        width: body.offsetWidth * 0.75,
        height: body.offsetHeight * 0.75
      }
    };
  });
}
```

### 3. validateSlide (검증)

```javascript
function validateSlide(slideData) {
  const errors = [];

  // 1. 크기 검증
  const tolerance = 0.1;  // inches
  if (Math.abs(slideData.dimensions.width - 720) > tolerance * 72) {
    errors.push(`Width mismatch: ${slideData.dimensions.width}pt (expected 720pt)`);
  }
  if (Math.abs(slideData.dimensions.height - 405) > tolerance * 72) {
    errors.push(`Height mismatch: ${slideData.dimensions.height}pt (expected 405pt)`);
  }

  // 2. 오버플로우 검증
  for (const el of slideData.elements) {
    const right = el.position.x + el.position.width;
    const bottom = el.position.y + el.position.height;

    if (right > 720) {
      errors.push(`Element overflow (right): ${el.tag} exceeds by ${right - 720}pt`);
    }
    if (bottom > 405) {
      errors.push(`Element overflow (bottom): ${el.tag} exceeds by ${bottom - 405}pt`);
    }
  }

  // 3. 텍스트 위치 검증 (하단 여백 0.5inch)
  const minBottomMargin = 36;  // 0.5 * 72pt
  for (const el of slideData.elements) {
    if (el.type === 'text' && el.position.height > 100) {
      const bottom = el.position.y + el.position.height;
      if (bottom > 405 - minBottomMargin) {
        errors.push(`Text too close to bottom: ${el.tag}`);
      }
    }
  }

  // 4. CSS 그라데이션 금지
  for (const el of slideData.elements) {
    if (el.style.backgroundColor?.includes('gradient')) {
      errors.push(`CSS gradient not supported: ${el.tag} - convert to image`);
    }
  }

  return {
    valid: errors.length === 0,
    errors
  };
}
```

## 최종 레이아웃 QA 체크리스트

PPTX/PDF를 사용자에게 전달하기 전에 아래 항목을 모두 확인합니다.

- `slide/page`별 PNG를 모두 렌더링한다.
- contact sheet는 문제 후보를 찾는 보조 자료로만 사용한다.
- 각 PNG를 읽을 수 있는 크기로 개별 확대 확인하고, contact sheet만으로 통과 처리하지 않는다.
- 제목, 부제, 본문, 카드 제목, 캡션, 하단 핵심 문장의 위계가 서로 구분되는지 확인한다.
- 제목-부제, 부제-본문, 카드 간격, 표 row/column padding, 이미지-텍스트 간격, 하단 safe area를 확인한다.
- 한국어 제목과 본문에 negative letter spacing이나 과한 압축 자간을 적용하지 않는다.
- 조사, 어미, 단위가 줄 첫머리에 홀로 남으면 문장을 줄이거나 명시적 줄바꿈으로 조정한다.
- 실패한 슬라이드는 수정 후 다시 렌더링하고 마지막 렌더 결과 기준으로만 PASS를 기록한다.

사용자가 레이아웃 문제를 지적한 뒤에는 더 엄격하게 재검수합니다.

- 기존 QA 결과는 폐기하고 새 PPTX/PDF 렌더를 만든다.
- 문제 슬라이드와 같은 layout family를 쓰는 슬라이드를 함께 확인한다.
- overflow 없음만으로 PASS 처리하지 않고, 읽히는 순서와 시각 비중을 확인한다.
- 큰 한글 제목이 답답하면 negative tracking을 쓰지 말고 제목 길이, 줄바꿈, font size, box width를 조정한다.
- QA report에 슬라이드별로 `간격`, `텍스트 위계`, `자간`, `word breaking`, `이미지-텍스트 충돌` 확인 결과를 남긴다.

### 4. addElements (PPTX 요소 추가)

```javascript
function addElements(slideData, slide, pres) {
  // 배경 추가
  if (slideData.background.image && slideData.background.image !== 'none') {
    slide.addImage({
      path: extractImagePath(slideData.background.image),
      x: 0, y: 0, w: '100%', h: '100%'
    });
  } else if (slideData.background.color) {
    slide.background = { color: rgbToHex(slideData.background.color) };
  }

  // 요소 추가
  for (const el of slideData.elements) {
    const x = el.position.x / 72;  // pt to inches
    const y = el.position.y / 72;
    const w = el.position.width / 72;
    const h = el.position.height / 72;

    switch (el.type) {
      case 'text':
        slide.addText(el.text, {
          x, y, w, h,
          fontSize: el.style.fontSize,
          fontFace: 'Pretendard',
          color: rgbToHex(el.style.color),
          bold: el.style.fontWeight >= 600,
          align: mapTextAlign(el.style.textAlign)
        });
        break;

      case 'image':
        slide.addImage({
          path: el.src,
          x, y, w, h
        });
        break;

      case 'shape':
        slide.addShape(pres.ShapeType.rect, {
          x, y, w, h,
          fill: { color: rgbToHex(el.style.backgroundColor) }
        });
        break;
    }
  }
}
```

## Python 대안 (python-pptx)

### 기본 설정

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

# 16:9 슬라이드 생성
prs = Presentation()
prs.slide_width = Inches(10)
prs.slide_height = Inches(5.625)
```

### 슬라이드 생성 함수

```python
def create_slide(prs, layout_type='blank'):
    """슬라이드 생성"""
    layout = prs.slide_layouts[6]  # blank layout
    return prs.slides.add_slide(layout)

def add_text_box(slide, text, left, top, width, height, font_size=18,
                 bold=False, color='000000', align='left'):
    """텍스트 박스 추가"""
    from pptx.util import Inches, Pt

    txBox = slide.shapes.add_textbox(
        Inches(left), Inches(top),
        Inches(width), Inches(height)
    )
    tf = txBox.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = RGBColor.from_string(color)

    if align == 'center':
        p.alignment = PP_ALIGN.CENTER
    elif align == 'right':
        p.alignment = PP_ALIGN.RIGHT

    return txBox

def add_shape(slide, shape_type, left, top, width, height, fill_color=None):
    """도형 추가"""
    from pptx.enum.shapes import MSO_SHAPE

    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(left), Inches(top),
        Inches(width), Inches(height)
    )

    if fill_color:
        shape.fill.solid()
        shape.fill.fore_color.rgb = RGBColor.from_string(fill_color)

    shape.line.fill.background()  # 테두리 제거
    return shape
```

## 디자인 시스템 통합

### 팔레트 적용

```python
# Modern Dark 팔레트
PALETTE = {
    'bg_primary': '0f0f0f',
    'bg_secondary': '1a1a1a',
    'bg_card': '252525',
    'text_primary': 'ffffff',
    'text_secondary': 'a0a0a0',
    'accent': '667eea',
    'accent_secondary': '764ba2',
}

def apply_background(slide, color_key='bg_primary'):
    """배경색 적용"""
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor.from_string(PALETTE[color_key])
```

### 타이포그래피 적용

```python
TYPOGRAPHY = {
    'hero': {'size': 84, 'weight': 'bold', 'spacing': 0},
    'section': {'size': 54, 'weight': 'bold', 'spacing': 0},
    'title': {'size': 36, 'weight': 'semibold', 'spacing': 0},
    'subtitle': {'size': 22, 'weight': 'medium', 'spacing': 0},
    'body': {'size': 18, 'weight': 'regular', 'spacing': 0},
    'caption': {'size': 13, 'weight': 'regular', 'spacing': 0.02},
}

def apply_typography(paragraph, style='body'):
    """타이포그래피 스타일 적용"""
    settings = TYPOGRAPHY[style]
    paragraph.font.size = Pt(settings['size'])
    paragraph.font.bold = settings['weight'] in ['bold', 'semibold']
```

## 10가지 슬라이드 템플릿 구현

### 1. Cover Slide (표지)

```python
def create_cover_slide(prs, title, subtitle, presenter='', date=''):
    slide = create_slide(prs)
    apply_background(slide, 'bg_primary')

    # Hero Title
    add_text_box(slide, title,
        left=0.67, top=2.0, width=8.66, height=1.0,
        font_size=84, bold=True, color=PALETTE['text_primary'],
        align='center')

    # Subtitle
    add_text_box(slide, subtitle,
        left=0.67, top=3.2, width=8.66, height=0.5,
        font_size=22, color=PALETTE['text_secondary'],
        align='center')

    # Footer
    if presenter:
        add_text_box(slide, presenter,
            left=0.67, top=5.0, width=4, height=0.3,
            font_size=14, color=PALETTE['text_secondary'])

    return slide
```

### 2. Content Slide (콘텐츠)

```python
def create_content_slide(prs, headline, bullets, section='', page_num=''):
    slide = create_slide(prs)
    apply_background(slide, 'bg_primary')

    # Section Badge
    if section:
        badge = add_shape(slide, 'rect', 0.67, 0.4, 1.5, 0.35,
                         PALETTE['accent'])
        add_text_box(slide, section, 0.67, 0.4, 1.5, 0.35,
                    font_size=11, color='ffffff', align='center')

    # Page Number
    if page_num:
        add_text_box(slide, page_num, 9.0, 0.4, 0.5, 0.35,
                    font_size=14, color=PALETTE['text_secondary'])

    # Headline
    add_text_box(slide, headline,
        left=0.67, top=1.0, width=8.66, height=0.6,
        font_size=36, bold=True, color=PALETTE['text_primary'])

    # Bullet Points
    bullet_text = '\n'.join([f'• {b}' for b in bullets])
    add_text_box(slide, bullet_text,
        left=0.67, top=1.8, width=4.0, height=3.0,
        font_size=18, color=PALETTE['text_secondary'])

    return slide
```

### 3. Statistics Slide (통계)

```python
def create_statistics_slide(prs, title, metrics):
    """
    metrics: [{'value': '85%', 'label': 'Accuracy'}, ...]
    """
    slide = create_slide(prs)
    apply_background(slide, 'bg_primary')

    # Title
    add_text_box(slide, title,
        left=0.67, top=0.67, width=8.66, height=0.6,
        font_size=36, bold=True, color=PALETTE['text_primary'])

    # Metric Cards
    card_width = 2.5
    gap = 0.5
    start_x = (10 - (len(metrics) * card_width + (len(metrics)-1) * gap)) / 2

    for i, metric in enumerate(metrics):
        x = start_x + i * (card_width + gap)

        # Card Background
        add_shape(slide, 'rect', x, 1.8, card_width, 2.5,
                 PALETTE['bg_card'])

        # Metric Value
        add_text_box(slide, metric['value'],
            left=x, top=2.2, width=card_width, height=1.0,
            font_size=60, bold=True, color=PALETTE['accent'],
            align='center')

        # Metric Label
        add_text_box(slide, metric['label'],
            left=x, top=3.4, width=card_width, height=0.5,
            font_size=16, color=PALETTE['text_secondary'],
            align='center')

    return slide
```

## 검증 체크리스트

```
출력 전 최종 확인:

□ 슬라이드 크기 (720pt × 405pt)
□ 콘텐츠 오버플로우 없음
□ 텍스트 하단 여백 (0.5인치 이상)
□ contact sheet만이 아니라 각 slide/page PNG를 확대 검수
□ 제목-부제-본문-카드-캡션-하단 문장의 텍스트 위계 확인
□ 카드/표/이미지 간격과 하단 safe area 확인
□ 한글 제목/본문 negative letter spacing 미사용
□ CSS 그라데이션 → 이미지 변환 완료
□ 폰트 임베딩 또는 시스템 폰트 사용
□ 각 슬라이드의 slide_intent와 layout_family가 manifest에 기록됐는지 확인
□ 10장 이상 덱에서 최소 5개 layout family를 사용했는지 확인
□ 같은 layout family가 연속 반복되면 pattern_repeat_reason이 있는지 확인
□ 챕터별 실제 예시, 전후 비교, 진단표, 실습 중 하나 이상이 포함됐는지 확인
□ 인포그래픽은 imagegen 생성 asset인지 확인
□ 인포그래픽/이미지 사용 목적과 asset manifest 확인
□ imagegen asset prompt에 텍스트 금지와 한국어 텍스트용 여백 조건이 포함됐는지 확인
□ 정확한 표, 수치, 단계명, 한국어 라벨은 이미지가 아니라 편집 가능한 PPTX 요소인지 확인
□ 한국어 word breaking 확인 (`break-all`, 조사/어미 고립, 어색한 직역투 없음)
□ 색상 코드 '#' 제거
□ 이미지 절대 경로 확인
□ 하이퍼링크 작동 확인
□ PPTX 전체 슬라이드 렌더/contact sheet 확인
□ PDF 생성 및 PDF 전체 페이지 렌더/contact sheet 확인
□ PDF 페이지 수와 PPTX 슬라이드 수 일치
□ 파일명 규칙 준수
```

## 파일 명명 규칙

```
[프로젝트]_[유형]_v[버전]_[날짜].[확장자]

예시:
├── ClaudeCode_deck_v1.0_20250104.pptx
├── ClaudeCode_presentation_v1.0_20250104.pdf
├── ClaudeCode_handout_v1.0_20250104.pdf
└── ClaudeCode_thumb_slide01.png

유형:
├── deck      : 편집용 PPTX
├── presentation : 발표용 PDF
├── handout   : 핸드아웃 PDF
├── thumb     : 썸네일 이미지
└── html      : HTML 원본
```

## 의존성

### Node.js

```json
{
  "dependencies": {
    "pptxgenjs": "^3.12.0",
    "playwright": "^1.40.0",
    "sharp": "^0.33.0"
  }
}
```

### Python

```txt
python-pptx>=0.6.21
Pillow>=10.0.0
playwright>=1.40.0
defusedxml>=0.7.1
```

### 시스템 도구

```bash
# PDF 변환용
apt-get install libreoffice

# 이미지 처리용
apt-get install poppler-utils
```

## 출력 완료 리포트

```markdown
# 출력 완료 리포트

## 프로젝트 정보
- **제목:** Claude Code 2.0 세미나
- **버전:** v1.0
- **출력일:** 2025-01-04

## 생성 파일

| 파일명 | 포맷 | 크기 | 상태 |
|--------|------|------|------|
| ClaudeCode_deck_v1.0.pptx | PPTX | 2.1 MB | ✅ |
| ClaudeCode_presentation.pdf | PDF | 1.8 MB | ✅ |
| ClaudeCode_handout.pdf | PDF | 1.2 MB | ✅ |

## 검증 결과

- [x] 슬라이드 크기 검증 통과
- [x] 오버플로우 검증 통과
- [x] 인포그래픽 imagegen asset 검토 완료
- [x] 인포그래픽/이미지 적합성 검토 완료
- [x] 한국어 word breaking 검증 통과
- [x] PPTX/PDF slide/page PNG 확대 검수 완료
- [x] PDF 페이지 수 일치
- [x] 폰트 임베딩 완료
- [x] 색상 코드 검증 통과

## 슬라이드 구성

| # | 유형 | 제목 |
|---|------|------|
| 1 | Cover | Claude Code 2.0 완벽 활용 가이드 |
| 2 | Contents | 오늘 다룰 7가지 핵심 주제 |
| ... | ... | ... |
| 25 | Closing | 감사합니다 |
```

## 주의사항

1. **색상 코드**: HEX에서 '#' 제거 필수 (`667eea` O, `#667eea` X)
2. **CSS 그라데이션**: 이미지로 사전 렌더링 필요
3. **폰트**: 시스템 미설치 시 Arial로 폴백
4. **이미지**: 절대 경로 사용, 상대 경로 금지
5. **텍스트 태그**: 시맨틱 HTML만 사용 (p, h1-h6, ul, li)
6. **인라인 스타일**: margin 미지원, padding으로 대체
7. **검증 필수**: 출력 전 반드시 validateSlide 실행
8. **최종 게이트**: 납품 전 `.claude/rules/common/presentation-quality-gate.md` 적용
