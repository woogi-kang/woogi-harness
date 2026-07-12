---
name: export-pdf
description: "PPT PDF 내보내기 — HTML 프레젠테이션을 PDF 파일로 변환"
---

# PPT PDF Export Skill

HTML 슬라이드를 고품질 PDF로 변환하는 Skill입니다.
**Playwright 렌더링 + pdf-lib 병합** 파이프라인을 사용합니다.

## 핵심 워크플로우

```
┌─────────────────────────────────────────────────────────────┐
│                    HTML → PDF Pipeline                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   1. HTML 슬라이드 로드                                       │
│        │                                                     │
│        ▼                                                     │
│   2. Playwright 브라우저 렌더링                               │
│        │                                                     │
│        ▼                                                     │
│   3. 개별 슬라이드 PDF 생성                                   │
│        │                                                     │
│        ▼                                                     │
│   4. pdf-lib으로 병합                                         │
│        │                                                     │
│        ▼                                                     │
│   5. 최종 PDF 출력                                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 출력 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| **width** | 슬라이드 너비 | 960px |
| **height** | 슬라이드 높이 | 540px |
| **printBackground** | 배경 포함 | true |
| **waitForFonts** | 폰트 로딩 대기 | 500ms |

## 빌드 스크립트

### build-pdf.js

```javascript
import { chromium } from 'playwright';
import { readdir } from 'fs/promises';
import path from 'path';
import { PDFDocument } from 'pdf-lib';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

async function buildPdf(options = {}) {
  const {
    slidesDir = path.join(__dirname, 'slides'),
    outputFile = 'presentation.pdf',
    width = 960,
    height = 540,
    waitForFonts = 500
  } = options;

  console.log('Building PDF...');

  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width, height }
  });

  // Get all slide files
  const files = await readdir(slidesDir);
  const slideFiles = files
    .filter(f => f.startsWith('slide-') && f.endsWith('.html'))
    .sort((a, b) => {
      const numA = parseInt(a.match(/slide-(\d+)/)[1]);
      const numB = parseInt(b.match(/slide-(\d+)/)[1]);
      return numA - numB;
    });

  console.log(`Found ${slideFiles.length} slides`);

  // Create merged PDF
  const mergedPdf = await PDFDocument.create();

  for (const file of slideFiles) {
    const filePath = path.join(slidesDir, file);
    const fileUrl = `file://${filePath}`;

    console.log(`Processing: ${file}`);

    const page = await context.newPage();
    await page.goto(fileUrl, { waitUntil: 'networkidle' });

    // Wait for fonts to load
    await page.waitForTimeout(waitForFonts);

    // Generate PDF for this slide
    const pdfBuffer = await page.pdf({
      width: `${width}px`,
      height: `${height}px`,
      printBackground: true,
      margin: { top: 0, right: 0, bottom: 0, left: 0 }
    });

    // Add to merged PDF
    const slidePdf = await PDFDocument.load(pdfBuffer);
    const [copiedPage] = await mergedPdf.copyPages(slidePdf, [0]);
    mergedPdf.addPage(copiedPage);

    await page.close();
  }

  // Save merged PDF
  const pdfBytes = await mergedPdf.save();

  const fs = await import('fs/promises');
  await fs.writeFile(outputFile, pdfBytes);

  await browser.close();

  console.log(`\nCreated: ${outputFile}`);
  return outputFile;
}

export default buildPdf;

// CLI execution
if (import.meta.url === `file://${process.argv[1]}`) {
  buildPdf().catch(err => {
    console.error('Build failed:', err);
    process.exit(1);
  });
}
```

## package.json 설정

```json
{
  "name": "ppt-project",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "build": "node build-pptx.js",
    "build:pdf": "node build-pdf.js",
    "build:all": "npm run build && npm run build:pdf"
  },
  "dependencies": {
    "pptxgenjs": "^4.0.1",
    "playwright": "^1.61.1",
    "pdf-lib": "^1.17.1",
    "sharp": "^0.35.3"
  }
}
```

## 통합 빌드 스크립트

### build-all.js

PPTX와 PDF를 동시에 생성하는 통합 스크립트:

```javascript
import PptxGenJS from 'pptxgenjs';
import { chromium } from 'playwright';
import { readdir } from 'fs/promises';
import path from 'path';
import { PDFDocument } from 'pdf-lib';
import { fileURLToPath } from 'url';
import html2pptx from './html2pptx.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

async function buildAll(projectName = 'Presentation') {
  const slidesDir = path.join(__dirname, 'slides');
  const files = await readdir(slidesDir);
  const slideFiles = files
    .filter(f => f.startsWith('slide-') && f.endsWith('.html'))
    .sort((a, b) => {
      const numA = parseInt(a.match(/slide-(\d+)/)[1]);
      const numB = parseInt(b.match(/slide-(\d+)/)[1]);
      return numA - numB;
    });

  console.log(`Found ${slideFiles.length} slides\n`);

  // ═══════════════════════════════════════════════════════════
  // PPTX 생성
  // ═══════════════════════════════════════════════════════════
  console.log('═'.repeat(50));
  console.log('Building PPTX...');
  console.log('═'.repeat(50));

  const pres = new PptxGenJS();
  pres.layout = 'LAYOUT_16x9';
  pres.title = projectName;

  for (const file of slideFiles) {
    const filePath = path.join(slidesDir, file);
    console.log(`[PPTX] Processing: ${file}`);
    await html2pptx(filePath, pres);
  }

  const pptxFile = `${projectName.replace(/\s+/g, '_')}.pptx`;
  await pres.writeFile({ fileName: pptxFile });
  console.log(`Created: ${pptxFile}\n`);

  // ═══════════════════════════════════════════════════════════
  // PDF 생성
  // ═══════════════════════════════════════════════════════════
  console.log('═'.repeat(50));
  console.log('Building PDF...');
  console.log('═'.repeat(50));

  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 960, height: 540 }
  });

  const mergedPdf = await PDFDocument.create();

  for (const file of slideFiles) {
    const filePath = path.join(slidesDir, file);
    const fileUrl = `file://${filePath}`;

    console.log(`[PDF] Processing: ${file}`);

    const page = await context.newPage();
    await page.goto(fileUrl, { waitUntil: 'networkidle' });
    await page.waitForTimeout(500);

    const pdfBuffer = await page.pdf({
      width: '960px',
      height: '540px',
      printBackground: true,
      margin: { top: 0, right: 0, bottom: 0, left: 0 }
    });

    const slidePdf = await PDFDocument.load(pdfBuffer);
    const [copiedPage] = await mergedPdf.copyPages(slidePdf, [0]);
    mergedPdf.addPage(copiedPage);

    await page.close();
  }

  const pdfFile = `${projectName.replace(/\s+/g, '_')}.pdf`;
  const pdfBytes = await mergedPdf.save();

  const fs = await import('fs/promises');
  await fs.writeFile(pdfFile, pdfBytes);

  await browser.close();
  console.log(`Created: ${pdfFile}\n`);

  // ═══════════════════════════════════════════════════════════
  // 완료 리포트
  // ═══════════════════════════════════════════════════════════
  console.log('═'.repeat(50));
  console.log('BUILD COMPLETE');
  console.log('═'.repeat(50));
  console.log(`
  Project: ${projectName}
  Slides:  ${slideFiles.length}

  Output Files:
  ├── ${pptxFile}
  └── ${pdfFile}
  `);

  return { pptxFile, pdfFile };
}

export default buildAll;

// CLI execution
if (import.meta.url === `file://${process.argv[1]}`) {
  const projectName = process.argv[2] || 'Presentation';
  buildAll(projectName).catch(err => {
    console.error('Build failed:', err);
    process.exit(1);
  });
}
```

## 사용 방법

### 1. 의존성 설치

```bash
npm install pptxgenjs playwright pdf-lib sharp
npx playwright install chromium
```

### 2. 개별 빌드

```bash
# PPTX만 생성
npm run build

# PDF만 생성
npm run build:pdf
```

### 3. 통합 빌드

```bash
# PPTX + PDF 동시 생성
npm run build:all

# 프로젝트 이름 지정
node build-all.js "My Project Name"
```

## PDF 품질 옵션

### 고화질 설정

```javascript
const pdfBuffer = await page.pdf({
  width: '1920px',    // 2x 해상도
  height: '1080px',
  printBackground: true,
  scale: 2,           // 스케일 업
  margin: { top: 0, right: 0, bottom: 0, left: 0 }
});
```

### 압축 설정

```javascript
// pdf-lib 저장 옵션
const pdfBytes = await mergedPdf.save({
  useObjectStreams: true,  // 압축 활성화
});
```

## 트러블슈팅

### 1. 텍스트 안보임 / 깨짐 (Gradient Text 문제)

**원인:** CSS gradient text 효과 (`-webkit-background-clip: text`)가 PDF 렌더링에서 지원되지 않음

```css
/* ❌ PDF에서 텍스트가 투명하게 렌더링됨 */
.gradient-text {
  background: linear-gradient(135deg, #e8e8ec 0%, #667eea 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

**해결 방법:**
```css
/* ✅ 단색으로 변경 */
.title {
  color: #e8e8ec;
}

/* ✅ 강조가 필요하면 accent 색상 사용 */
.highlight {
  color: #00d9ff;
}
```

**PDF 비호환 CSS 목록:**
| CSS 속성 | 대안 |
|---------|------|
| `-webkit-background-clip: text` | 단색 `color` |
| `-webkit-text-fill-color: transparent` | 제거 |
| `background-clip: text` | 제거 |
| `filter: blur()` on text | `text-shadow` |

### 2. 폰트 깨짐

```javascript
// 폰트 로딩 시간 증가
await page.waitForTimeout(1000);

// 또는 폰트 로딩 완료 대기
await page.waitForFunction(() => {
  return document.fonts.ready;
});
```

### 3. 배경 이미지 누락

```javascript
// networkidle 대기
await page.goto(fileUrl, { waitUntil: 'networkidle' });

// 또는 특정 이미지 로딩 대기
await page.waitForSelector('img');
```

### 4. 브라우저 미설치

```bash
# Playwright 브라우저 설치
npx playwright install chromium
```

### 5. 메모리 부족 (대용량 PDF)

```javascript
// 배치 처리로 메모리 관리
const BATCH_SIZE = 20;
for (let i = 0; i < slideFiles.length; i += BATCH_SIZE) {
  const batch = slideFiles.slice(i, i + BATCH_SIZE);
  // 배치별 처리...
}
```

## 파일 명명 규칙

```
[프로젝트명]_[버전]_[날짜].[확장자]

예시:
├── Claude_Code_Team_Guide.pptx
├── Claude_Code_Team_Guide.pdf
├── Claude_Code_Team_Guide_v1.1.pptx
└── Claude_Code_Team_Guide_handout.pdf
```

## 체크리스트

```
PDF 출력 전 확인:

□ Playwright 브라우저 설치됨
□ pdf-lib 의존성 설치됨
□ 슬라이드 HTML 파일 존재
□ 배경 이미지 경로 유효
□ 폰트 CDN 접근 가능
□ 출력 디렉토리 쓰기 권한
□ PDF 페이지 수와 원본 슬라이드 수 일치
□ PDF 전체 페이지 PNG 렌더 완료
□ PDF contact sheet 전수 확인 완료
□ 텍스트/이미지 잘림, overflow, 겹침 없음
□ 한국어 word breaking 문제 없음
□ `.claude/rules/common/presentation-quality-gate.md` 적용
```

## 출력 완료 예시

```
═══════════════════════════════════════════════════
BUILD COMPLETE
═══════════════════════════════════════════════════

  Project: Claude Code Team Guide
  Slides:  71

  Output Files:
  ├── Claude_Code_Team_Guide.pptx (1.97 MB)
  ├── Claude_Code_Team_Guide.pdf (2.96 MB)
  └── qa_pdf_render/contact-sheet.png

  QA:
  ├── PDF pages match slide count
  ├── PDF page render complete
  └── No visible overflow/clipping in contact sheet
```
