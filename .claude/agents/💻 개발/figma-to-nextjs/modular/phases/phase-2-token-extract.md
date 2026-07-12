---
name: "Phase 2: Token Extract"
phase_id: 2
phase_name: "Token Extract"
description: "Extract Figma design tokens and generate Tailwind/CSS configuration"

dependencies:
  - phase_id: 1
    artifacts: [design_scan.json]
    validation: design_scan_exists

inputs:
  required: [figma_file_key, node_ids]
  optional: [existing_tailwind_config, existing_css_variables]

outputs:
  artifacts: [tokens.json, tailwind.config.patch.ts, css_variables.css]
  state_updates: [artifacts.phase_2.tokens, artifacts.phase_2.tailwind_config]

validation:
  success_criteria:
    - Colors extracted
    - Spacing values mapped
    - Typography defined
  quality_gates:
    - Token naming follows convention
    - CSS variables use RGB format for opacity support

rollback:
  on_failure: use_default_tokens
  cleanup: [tokens.json]
  can_resume: true

mcp_calls:
  estimated: 1
  tools: [get_variable_defs]
---

# Phase 2: Token Extract

> Figma 디자인 토큰 → Tailwind/CSS 변수 변환

---

## 실행 조건

- Phase 1 완료 후
- 디자인 시스템 정의된 Figma 파일

---

## Step 2-1: 토큰 추출

```typescript
// MCP 호출
get_variable_defs({
  fileKey: "ABC123",
  nodeId: "123:456"
})
```

### 반환 예시

```json
{
  "colors": {
    "primary": "#3B82F6",
    "primary-hover": "#2563EB",
    "secondary": "#10B981",
    "background": "#FFFFFF",
    "foreground": "#1F2937",
    "muted": "#9CA3AF",
    "border": "#E5E7EB"
  },
  "spacing": {
    "xs": "4px",
    "sm": "8px",
    "md": "16px",
    "lg": "24px",
    "xl": "32px",
    "2xl": "48px"
  },
  "typography": {
    "heading-1": { "fontSize": "48px", "lineHeight": "56px", "fontWeight": "700" },
    "heading-2": { "fontSize": "36px", "lineHeight": "44px", "fontWeight": "700" },
    "heading-3": { "fontSize": "24px", "lineHeight": "32px", "fontWeight": "600" },
    "body": { "fontSize": "16px", "lineHeight": "24px", "fontWeight": "400" },
    "caption": { "fontSize": "14px", "lineHeight": "20px", "fontWeight": "400" }
  },
  "radius": {
    "sm": "4px",
    "md": "8px",
    "lg": "12px",
    "xl": "16px",
    "full": "9999px"
  },
  "shadow": {
    "sm": "0 1px 2px rgba(0,0,0,0.05)",
    "md": "0 4px 6px rgba(0,0,0,0.1)",
    "lg": "0 10px 15px rgba(0,0,0,0.1)"
  }
}
```

---

## Step 2-2: CSS 변수 생성

```css
/* globals.css */
@layer base {
  :root {
    /* Colors */
    --figma-color-primary: 59 130 246;        /* #3B82F6 */
    --figma-color-primary-hover: 37 99 235;   /* #2563EB */
    --figma-color-secondary: 16 185 129;      /* #10B981 */
    --figma-color-background: 255 255 255;    /* #FFFFFF */
    --figma-color-foreground: 31 41 55;       /* #1F2937 */
    --figma-color-muted: 156 163 175;         /* #9CA3AF */
    --figma-color-border: 229 231 235;        /* #E5E7EB */

    /* Spacing */
    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 16px;
    --spacing-lg: 24px;
    --spacing-xl: 32px;
    --spacing-2xl: 48px;

    /* Border Radius */
    --radius-sm: 4px;
    --radius-md: 8px;
    --radius-lg: 12px;
    --radius-xl: 16px;

    /* Shadows */
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
    --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
    --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
  }

  .dark {
    --figma-color-background: 17 24 39;       /* #111827 */
    --figma-color-foreground: 249 250 251;    /* #F9FAFB */
  }
}
```

---

## Step 2-3: Tailwind CSS 4 theme 확장

```css
/* src/app/globals.css — CSS-first configuration */
@import "tailwindcss";

@theme inline {
  --color-primary: rgb(var(--figma-color-primary));
  --color-primary-hover: rgb(var(--figma-color-primary-hover));
  --color-secondary: rgb(var(--figma-color-secondary));
  --color-background: rgb(var(--figma-color-background));
  --color-foreground: rgb(var(--figma-color-foreground));
  --color-muted: rgb(var(--figma-color-muted));
  --color-border: rgb(var(--figma-color-border));
  --spacing-figma-xs: var(--spacing-xs);
  --spacing-figma-sm: var(--spacing-sm);
  --spacing-figma-md: var(--spacing-md);
  --spacing-figma-lg: var(--spacing-lg);
  --spacing-figma-xl: var(--spacing-xl);
  --radius-figma-sm: var(--radius-sm);
  --radius-figma-md: var(--radius-md);
  --radius-figma-lg: var(--radius-lg);
  --shadow-figma-sm: var(--shadow-sm);
  --shadow-figma-md: var(--shadow-md);
  --shadow-figma-lg: var(--shadow-lg);
}
```

---

## Step 2-4: 토큰 타입 정의

```typescript
// types/design-tokens.ts
export interface DesignTokens {
  colors: {
    primary: string;
    secondary: string;
    background: string;
    foreground: string;
    muted: string;
    border: string;
  };
  spacing: {
    xs: string;
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
  typography: {
    [key: string]: {
      fontSize: string;
      lineHeight: string;
      fontWeight: string;
    };
  };
  radius: {
    sm: string;
    md: string;
    lg: string;
    xl: string;
    full: string;
  };
}
```

---

## Step 2-5: Typography 유틸리티

```typescript
// lib/typography.ts
export const typography = {
  h1: 'text-5xl font-bold leading-tight',      // 48px/56px
  h2: 'text-4xl font-bold leading-tight',      // 36px/44px
  h3: 'text-2xl font-semibold leading-snug',   // 24px/32px
  body: 'text-base font-normal leading-relaxed', // 16px/24px
  caption: 'text-sm font-normal leading-normal', // 14px/20px
} as const;

// 사용 예시
// <h1 className={typography.h1}>Title</h1>
```

---

## Figma → Tailwind 매핑 테이블

### Colors

| Figma | Tailwind Class | CSS Variable |
|-------|---------------|--------------|
| `primary` | `bg-primary`, `text-primary` | `--figma-color-primary` → `--color-primary` |
| `secondary` | `bg-secondary` | `--figma-color-secondary` → `--color-secondary` |
| `#FFFFFF` | `bg-white` | - |
| `#000000` | `bg-black` | - |
| `#F3F4F6` | `bg-gray-100` | - |

### Spacing

| Figma | Tailwind Class | Value |
|-------|---------------|-------|
| 4px | `p-1`, `m-1`, `gap-1` | 0.25rem |
| 8px | `p-2`, `m-2`, `gap-2` | 0.5rem |
| 12px | `p-3`, `m-3`, `gap-3` | 0.75rem |
| 16px | `p-4`, `m-4`, `gap-4` | 1rem |
| 24px | `p-6`, `m-6`, `gap-6` | 1.5rem |
| 32px | `p-8`, `m-8`, `gap-8` | 2rem |
| 48px | `p-12`, `m-12`, `gap-12` | 3rem |
| 64px | `p-16`, `m-16`, `gap-16` | 4rem |

### Typography

| Figma | Tailwind Class |
|-------|---------------|
| 12px | `text-xs` |
| 14px | `text-sm` |
| 16px | `text-base` |
| 18px | `text-lg` |
| 20px | `text-xl` |
| 24px | `text-2xl` |
| 30px | `text-3xl` |
| 36px | `text-4xl` |
| 48px | `text-5xl` |

### Border Radius

| Figma | Tailwind Class |
|-------|---------------|
| 0px | `rounded-none` |
| 2px | `rounded-sm` |
| 4px | `rounded` |
| 6px | `rounded-md` |
| 8px | `rounded-lg` |
| 12px | `rounded-xl` |
| 16px | `rounded-2xl` |
| 24px | `rounded-3xl` |
| 9999px | `rounded-full` |

---

## 산출물

```markdown
# Token Extraction Report

## Extracted Tokens
- Colors: 7
- Spacing: 6
- Typography: 5
- Border Radius: 5
- Shadows: 3

## Files Created/Modified
- [x] `globals.css` - CSS 변수 추가
- [x] `globals.css` - Tailwind CSS 4 `@theme inline` 확장
- [x] `types/design-tokens.ts` - 타입 정의

## Token Mapping
[매핑 테이블]
```

---

## 다음 단계

Phase 2 완료 후 → **Phase 3: Component Mapping** 진행
