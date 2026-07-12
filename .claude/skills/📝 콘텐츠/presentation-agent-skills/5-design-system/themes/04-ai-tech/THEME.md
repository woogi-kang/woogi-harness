---
name: theme-ai-tech
description: |
  AI Futuristic 테마. AI/ML 데모, 테크 세미나, 개발자 컨퍼런스, 클라우드/인프라 발표에 최적화.
  "AI", "ML", "머신러닝", "딥러닝", "클라우드", "개발자", "테크" 키워드로 활성화.
tags: [ai, ml, machine-learning, deep-learning, tech, developer, cloud, infrastructure]
---

# AI Futuristic Theme

첨단 기술의 미래지향적 느낌을 주는 AI/테크 전문 디자인 테마입니다.

## Design Philosophy

- **첨단 기술의 미래지향적** 느낌
- **다크 테마**로 집중도 향상
- **뉴럴 네트워크/데이터 플로우** 시각적 모티프
- **코드/터미널 친화적** 디자인

## Color Palette

### CSS Variables

```css
:root {
  /* Primary - Terminal Dark */
  --bg-primary: #0a0a0f;        /* Terminal Black */
  --bg-secondary: #12121a;
  --bg-card: #1a1a25;
  --bg-code: #0d0d12;

  /* Text */
  --text-primary: #e8e8ec;
  --text-secondary: #888898;
  --text-muted: #585868;
  --text-code: #e8e8ec;

  /* AI Accent Colors */
  --accent-primary: #667eea;    /* Neural Blue */
  --accent-secondary: #00d9ff;  /* AI Cyan */
  --accent-tertiary: #a855f7;   /* ML Purple */
  --accent-success: #4ade80;    /* Matrix Green */
  --accent-node: #f472b6;       /* Node Pink */

  /* Gradients */
  --gradient-ai: linear-gradient(135deg, #667eea 0%, #a855f7 50%, #00d9ff 100%);
  --gradient-subtle: linear-gradient(180deg, rgba(102,126,234,0.1) 0%, rgba(0,0,0,0) 100%);
}
```

### Color Reference Table

| Role | HEX | PptxGenJS | Usage |
|------|-----|-----------|-------|
| Terminal Black | #0a0a0f | `0a0a0f` | 메인 배경 |
| Dark Secondary | #12121a | `12121a` | 보조 배경 |
| Card | #1a1a25 | `1a1a25` | 코드 블록, 카드 |
| Code BG | #0d0d12 | `0d0d12` | 코드 영역 |
| Light Text | #e8e8ec | `e8e8ec` | 주요 텍스트 |
| Gray Text | #888898 | `888898` | 보조 텍스트 |
| Neural Blue | #667eea | `667eea` | 주요 강조 |
| AI Cyan | #00d9ff | `00d9ff` | 하이라이트, 링크 |
| ML Purple | #a855f7 | `a855f7` | 보조 강조 |
| Matrix Green | #4ade80 | `4ade80` | 성공, 출력, 결과 |
| Node Pink | #f472b6 | `f472b6` | 노드, 데이터 포인트 |

## Typography

### Font Stack

```css
--font-family: 'Pretendard', 'Inter', sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
```

### Size Hierarchy (Points)

| Level | Size | Weight | Letter Spacing | Usage |
|-------|------|--------|----------------|-------|
| Hero | 80pt | 600 | -0.02em | 타이틀 슬라이드 |
| Title | 40pt | 600 | -0.01em | 슬라이드 제목 |
| Subtitle | 24pt | 500 | 0 | 부제목 |
| Body | 18pt | 400 | 0 | 본문 |
| Code | 16pt | 400 | 0 | 코드 블록 |
| Caption | 13pt | 400 | 0.02em | 캡션 |
| Label | 11pt | 500 | 0.05em | 라벨 |

### Code Typography

```css
.code-block {
  font-family: var(--font-mono);
  font-size: 16pt;
  line-height: 1.7;
  color: #e8e8ec;
  background: #0d0d12;
}
```

## Design Elements

### Code Blocks

```css
.code-container {
  background: #0d0d12;
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 8px;
  padding: 20pt;
  font-family: 'JetBrains Mono', monospace;
}

/* Syntax Highlighting */
.code-keyword { color: #a855f7; }   /* Purple */
.code-string { color: #4ade80; }    /* Green */
.code-function { color: #667eea; }  /* Blue */
.code-comment { color: #585868; }   /* Gray */
.code-number { color: #f472b6; }    /* Pink */
```

### Neural Network Nodes

```css
.node {
  width: 12pt;
  height: 12pt;
  border-radius: 50%;
  background: #f472b6;
  box-shadow: 0 0 20px rgba(244, 114, 182, 0.5);
}

.connection {
  stroke: #00d9ff;
  stroke-width: 2px;
  opacity: 0.6;
}
```

### Glow Effects

```css
.glow-blue {
  box-shadow: 0 0 30px rgba(102, 126, 234, 0.3),
              0 0 60px rgba(102, 126, 234, 0.15);
}

.glow-text {
  text-shadow: 0 0 20px currentColor;
}
```

## ⚠️ PDF 호환성 주의사항

### 사용 금지 CSS (PDF 렌더링 깨짐)

다음 CSS 기법은 Playwright PDF 출력 시 텍스트가 보이지 않거나 깨지는 문제가 발생합니다:

```css
/* ❌ 사용 금지 - PDF에서 텍스트 투명하게 렌더링됨 */
.gradient-text {
  background: linear-gradient(135deg, #e8e8ec 0%, #667eea 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

### PDF 호환 대안

```css
/* ✅ 권장 - 단색 사용 */
.title {
  color: #e8e8ec;
}

/* ✅ 권장 - 강조 텍스트는 accent 색상 */
.highlight-text {
  color: #00d9ff;  /* AI Cyan */
}

/* ✅ 허용 - text-shadow는 PDF에서 정상 작동 */
.glow-text {
  color: #667eea;
  text-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
}
```

### PDF 비호환 CSS 목록

| CSS 속성 | 문제 | 대안 |
|---------|------|------|
| `-webkit-background-clip: text` | 텍스트 투명화 | 단색 `color` 사용 |
| `-webkit-text-fill-color: transparent` | 텍스트 투명화 | 제거 |
| `background-clip: text` | 텍스트 투명화 | 제거 |
| `filter: blur()` on text | 텍스트 흐림 | `text-shadow` 사용 |
| `mix-blend-mode` on text | 예측 불가 | 제거 |

### Dot Grid Background

```css
.dot-grid {
  background-image: radial-gradient(
    rgba(255, 255, 255, 0.03) 1px,
    transparent 1px
  );
  background-size: 20px 20px;
}
```

### Terminal Style

```css
.terminal {
  background: #0a0a0f;
  border: 1px solid #1a1a25;
  border-radius: 8px;
  padding: 16pt;
  font-family: var(--font-mono);
}

.terminal-prompt {
  color: #4ade80;
}

.terminal-prompt::before {
  content: '$ ';
  color: #667eea;
}

.cursor {
  display: inline-block;
  width: 8pt;
  height: 16pt;
  background: #e8e8ec;
  animation: blink 1s step-end infinite;
}
```

## Slide Layouts

### Cover Slide

```
┌──────────────────────────────────────────────────┐
│░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░│
│░                                              ░░░│
│░  [Logo]                                      ░░░│
│░                                              ░░░│
│░           CLAUDE CODE 2.0                    ░░░│
│░           ──────────────────                 ░░░│
│░           Building the Future of Development ░░░│
│░                                              ░░░│
│░  [Speaker]                      [Event/Date] ░░░│
│░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░│
└──────────────────────────────────────────────────┘

Background: Terminal Black (#0a0a0f) + dot grid
Title: Light Text (#e8e8ec), 80pt
Subtitle: AI Cyan (#00d9ff), 24pt
```

### Code Demo Slide

```
┌──────────────────────────────────────────────────┐
│  [DEMO]                                   [##]   │
├──────────────────────────────────────────────────┤
│                                                   │
│  Model Implementation                            │
│                                                   │
│  ┌────────────────────────────────────────────┐  │
│  │  import torch                              │  │
│  │  from transformers import AutoModel       │  │
│  │                                            │  │
│  │  model = AutoModel.from_pretrained(       │  │
│  │      "provider-native-reasoning-high",       │  │
│  │      device_map="auto"                    │  │
│  │  )                                        │  │
│  │                                            │  │
│  │  output = model.generate(prompt)          │  │
│  └────────────────────────────────────────────┘  │
│                                                   │
└──────────────────────────────────────────────────┘

Code Background: #0d0d12
Keywords: ML Purple (#a855f7)
Strings: Matrix Green (#4ade80)
Functions: Neural Blue (#667eea)
```

### Architecture Diagram

```
┌──────────────────────────────────────────────────┐
│  SYSTEM ARCHITECTURE                      [##]   │
├──────────────────────────────────────────────────┤
│                                                   │
│        ┌─────┐      ┌─────┐      ┌─────┐        │
│        │  ●  │──────│  ●  │──────│  ●  │        │
│        │Input│      │Model│      │Output│        │
│        └──┬──┘      └──┬──┘      └──┬──┘        │
│           │            │            │            │
│     ┌─────┴─────┐ ┌────┴────┐ ┌────┴────┐       │
│     │  ●     ●  │ │  ●   ●  │ │  ●   ●  │       │
│     │  Vector   │ │Attention│ │ Decode  │       │
│     └───────────┘ └─────────┘ └─────────┘       │
│                                                   │
└──────────────────────────────────────────────────┘

Nodes: Node Pink (#f472b6) with glow
Connections: AI Cyan (#00d9ff)
Labels: Light Text (#e8e8ec), 14pt
Boxes: Card background (#1a1a25)
```

### Section Divider

```
┌──────────────────────────────────────────────────┐
│░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░│
│░                                              ░░░│
│░  02                                          ░░░│
│░  ─────────────────────                       ░░░│
│░  EXTENDED THINKING                           ░░░│
│░  Deep reasoning capabilities                 ░░░│
│░                                              ░░░│
│░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░ ░│
└──────────────────────────────────────────────────┘

Background: Terminal Black + gradient overlay
Number: Neural Blue (#667eea), 96pt, glow
Title: Light Text (#e8e8ec), 54pt
Description: Gray Text (#888898), 18pt
```

### Metrics Dashboard

```
┌──────────────────────────────────────────────────┐
│  PERFORMANCE METRICS                      [##]   │
├──────────────────────────────────────────────────┤
│                                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │  Latency       Accuracy     Throughput      │ │
│  │                                             │ │
│  │   45ms          99.2%        1.2K/s        │ │
│  │   ▼ -12%        ▲ +3.5%      ▲ +28%        │ │
│  │                                             │ │
│  │  ████████░░   ██████████   ████████░░░     │ │
│  └─────────────────────────────────────────────┘ │
│                                                   │
└──────────────────────────────────────────────────┘

Values: Matrix Green (#4ade80), 48pt
Trends Up: Matrix Green
Trends Down: AI Cyan
Progress Bars: Neural Blue → ML Purple gradient
```

## Special Effects

### AI Gradient Overlay

```css
.ai-gradient {
  background: linear-gradient(
    135deg,
    rgba(102, 126, 234, 0.15) 0%,
    rgba(168, 85, 247, 0.1) 50%,
    rgba(0, 217, 255, 0.15) 100%
  );
}
```

### Animated Neural Connection (for web)

```css
.neural-line {
  stroke-dasharray: 5, 5;
  animation: dash 1s linear infinite;
}

@keyframes dash {
  to { stroke-dashoffset: -10; }
}
```

## Accessibility Guidelines

### Contrast Ratios (Dark Mode)

| Combination | Ratio | Status |
|-------------|-------|--------|
| Light Text on Black | 17.1:1 | ✅ AAA |
| Neural Blue on Black | 6.3:1 | ✅ AA |
| AI Cyan on Black | 11.8:1 | ✅ AAA |
| Matrix Green on Black | 9.5:1 | ✅ AAA |
| Gray Text on Black | 5.4:1 | ✅ AA |

### Code Readability

- Minimum code font: 14pt
- Line height: 1.7 for code
- Use syntax highlighting for accessibility

## Use Cases

| Scenario | Recommended Style |
|----------|-------------------|
| AI 제품 데모 | Code blocks, architecture diagrams |
| 테크 세미나 | Terminal style, dot grid bg |
| 개발자 컨퍼런스 | Code-heavy, neural networks |
| 클라우드 인프라 | Architecture diagrams |
| ML 연구 발표 | Metrics dashboard, data viz |

## PptxGenJS Implementation

```javascript
// AI Tech theme colors (no # prefix)
const AI_TECH_COLORS = {
  bgPrimary: '0a0a0f',
  bgSecondary: '12121a',
  bgCard: '1a1a25',
  bgCode: '0d0d12',
  textPrimary: 'e8e8ec',
  textSecondary: '888898',
  accentPrimary: '667eea',
  accentSecondary: '00d9ff',
  accentTertiary: 'a855f7',
  accentSuccess: '4ade80',
  accentNode: 'f472b6'
};

// Dark slide
slide.background = { color: AI_TECH_COLORS.bgPrimary };

// Code block
slide.addShape('rect', {
  x: 0.7, y: 2, w: 11.93, h: 3.5,
  fill: { color: AI_TECH_COLORS.bgCode },
  line: { color: AI_TECH_COLORS.accentPrimary, width: 1, transparency: 80 }
});

slide.addText('const model = new AI();', {
  x: 1, y: 2.3, w: 11.33, h: 0.5,
  fontSize: 16,
  fontFace: 'Consolas',
  color: AI_TECH_COLORS.textPrimary
});

// Neural node with glow
slide.addShape('ellipse', {
  x: 5, y: 3, w: 0.3, h: 0.3,
  fill: { color: AI_TECH_COLORS.accentNode },
  shadow: { type: 'outer', blur: 20, color: AI_TECH_COLORS.accentNode, offset: 0, opacity: 0.5 }
});
```

## Related Themes

- **Alternative:** Fintech Bold (금융 AI)
- **Lighter Version:** Education Bright (AI 교육)
- **Creative Version:** Creative Neon (AI 아트)
