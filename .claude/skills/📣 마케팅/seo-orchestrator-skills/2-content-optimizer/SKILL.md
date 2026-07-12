---
name: content-optimizer
description: SEO 콘텐츠 최적화 및 메타 태그 관리 스킬
model: inherit
quality_tier: fast_scan
triggers:
  - "최적화"
  - "메타태그"
  - "SEO"
  - "스키마"
  - "구조화데이터"
---

# Content Optimizer Skill

SEO를 위한 콘텐츠 최적화, 메타 태그, 구조화 데이터 관리 스킬입니다.

## 핵심 원칙

| 원칙 | 설명 |
|------|------|
| **검색 친화적** | 검색엔진이 이해하기 쉬운 구조 |
| **사용자 중심** | 클릭률과 체류시간 최적화 |
| **기술적 정확성** | 구조화 데이터 유효성 |

## On-Page SEO 체크리스트

### 타이틀 태그

```yaml
title_tag:
  best_practices:
    - length: "50-60자 (픽셀 기준 580px 이내)"
    - keyword_position: "가능한 앞에"
    - brand: "끝에 | 브랜드명 형식"
    - unique: "페이지마다 고유"

  formula: |
    [주요 키워드] - [부가 설명] | [브랜드]

  examples:
    good:
      - "SaaS 결제 연동 가이드 (2026) - 포트원 vs Stripe 비교 | MyApp"
      - "구독 결제 자동화 방법 - 실전 튜토리얼 | MyApp"
    bad:
      - "MyApp - 홈페이지"  # 키워드 없음
      - "SaaS 결제 연동 방법 완벽 가이드 2026년 최신판 포트원 Stripe 비교 분석"  # 너무 김

  length_check: |
    # 타이틀 길이 체크 (JavaScript)
    const title = document.title;
    console.log(`Length: ${title.length}자`);
    // 구글은 픽셀 기준이므로 Preview 도구 사용 권장
```

### 메타 설명

```yaml
meta_description:
  best_practices:
    - length: "120-155자"
    - keyword: "자연스럽게 포함"
    - cta: "행동 유도 문구 포함"
    - unique: "페이지마다 고유"
    - no_quotes: "큰따옴표 피하기 (잘림)"

  formula: |
    [문제/니즈 언급] + [해결책 제시] + [CTA/차별점]

  examples:
    good:
      - "SaaS 결제 연동이 어려우신가요? 포트원과 Stripe를 단계별로 비교하고 최적의 선택을 도와드립니다. 지금 무료 가이드를 확인하세요."
    bad:
      - "결제 연동 방법"  # 너무 짧음
      - "저희 서비스는 최고의..."  # 판매 문구만

  html: |
    <meta name="description" content="SaaS 결제 연동이 어려우신가요? 포트원과 Stripe를 단계별로 비교하고 최적의 선택을 도와드립니다.">
```

### 헤딩 구조

```yaml
heading_structure:
  rules:
    - h1: "페이지당 1개"
    - hierarchy: "H1 → H2 → H3 순서 준수"
    - keyword: "H1, H2에 키워드 포함"
    - descriptive: "내용 요약하는 헤딩"

  example_structure:
    h1: "SaaS 결제 연동 완벽 가이드 (2026)"
    sections:
      - h2: "1. 결제 연동이란?"
        - h3: "1.1 결제 게이트웨이 이해하기"
        - h3: "1.2 PG사 vs PSP 차이점"
      - h2: "2. 포트원 연동 방법"
        - h3: "2.1 계정 설정"
        - h3: "2.2 API 연동"
        - h3: "2.3 테스트 결제"
      - h2: "3. Stripe 연동 방법"
      - h2: "4. 포트원 vs Stripe 비교"
      - h2: "5. FAQ"
      - h2: "6. 결론"

  common_mistakes:
    - "H1 여러 개 사용"
    - "H2 없이 H3 사용"
    - "스타일링 목적으로 헤딩 사용"
```

### URL 구조

```yaml
url_structure:
  best_practices:
    - short: "3-5 단어"
    - keyword: "주요 키워드 포함"
    - lowercase: "소문자만 사용"
    - hyphens: "단어 구분 하이픈"
    - no_params: "불필요한 파라미터 제거"

  examples:
    good:
      - "/blog/saas-payment-integration-guide"
      - "/pricing"
      - "/features/subscription-management"
    bad:
      - "/blog/post?id=12345"
      - "/Blog/SaaS_Payment_Integration_Complete_Guide_2026"
      - "/page/a/b/c/d/e/article"
```

### 이미지 최적화

```yaml
image_optimization:
  alt_text:
    purpose: "스크린리더 + 이미지 검색"
    rules:
      - descriptive: "이미지 내용 설명"
      - keyword: "자연스러우면 키워드 포함"
      - length: "125자 이내"
    examples:
      good: "포트원 결제 연동 대시보드 스크린샷"
      bad: "image1.png" or "결제 결제 결제"

  file_naming:
    good: "portone-dashboard-screenshot.png"
    bad: "IMG_20260127.png"

  format_choice:
    - webp: "사진 (최적 압축)"
    - svg: "로고, 아이콘"
    - png: "투명 배경 필요 시"

  lazy_loading: |
    <img src="image.webp" alt="설명" loading="lazy">
```

## 구조화 데이터 (Schema.org)

### Article 스키마

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "SaaS 결제 연동 완벽 가이드",
  "description": "포트원과 Stripe를 단계별로 비교하고 최적의 결제 연동 방법을 알아봅니다.",
  "image": "https://example.com/images/payment-guide.webp",
  "author": {
    "@type": "Person",
    "name": "홍길동",
    "url": "https://example.com/author/hong"
  },
  "publisher": {
    "@type": "Organization",
    "name": "MyApp",
    "logo": {
      "@type": "ImageObject",
      "url": "https://example.com/logo.png"
    }
  },
  "datePublished": "2026-01-27",
  "dateModified": "2026-01-27"
}
```

### FAQ 스키마

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "SaaS 결제 연동에 얼마나 걸리나요?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "포트원의 경우 기본 연동은 1-2일, 고급 기능은 1주일 정도 소요됩니다."
      }
    },
    {
      "@type": "Question",
      "name": "포트원과 Stripe 중 어떤 것이 좋나요?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "국내 결제 중심이면 포트원, 글로벌 진출이면 Stripe를 권장합니다."
      }
    }
  ]
}
```

### HowTo 스키마

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "포트원 결제 연동 방법",
  "description": "포트원을 사용하여 SaaS 결제를 연동하는 단계별 가이드",
  "totalTime": "PT2H",
  "step": [
    {
      "@type": "HowToStep",
      "name": "포트원 계정 생성",
      "text": "포트원 대시보드에서 계정을 생성합니다.",
      "url": "https://example.com/guide#step1"
    },
    {
      "@type": "HowToStep",
      "name": "API 키 발급",
      "text": "설정 > API에서 키를 발급받습니다."
    },
    {
      "@type": "HowToStep",
      "name": "SDK 설치",
      "text": "npm install @portone/browser-sdk"
    }
  ]
}
```

### Product 스키마 (SaaS)

```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "MyApp",
  "applicationCategory": "BusinessApplication",
  "operatingSystem": "Web",
  "offers": {
    "@type": "Offer",
    "price": "29000",
    "priceCurrency": "KRW",
    "priceValidUntil": "2026-12-31"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "ratingCount": "150"
  }
}
```

## OG 태그 (소셜 공유)

```yaml
og_tags:
  basic:
    - og:title: "페이지 제목"
    - og:description: "페이지 설명"
    - og:image: "공유 이미지 URL"
    - og:url: "페이지 URL"
    - og:type: "article/website"

  image_specs:
    recommended: "1200x630px"
    minimum: "600x315px"
    format: "PNG, JPG"
    file_size: "< 8MB"

  twitter_cards:
    - twitter:card: "summary_large_image"
    - twitter:site: "@YourHandle"
    - twitter:creator: "@AuthorHandle"

  html_example: |
    <!-- Open Graph -->
    <meta property="og:title" content="SaaS 결제 연동 가이드">
    <meta property="og:description" content="포트원과 Stripe 비교 분석">
    <meta property="og:image" content="https://example.com/og-image.png">
    <meta property="og:url" content="https://example.com/blog/payment-guide">
    <meta property="og:type" content="article">

    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:site" content="@MyApp">
```

## 콘텐츠 최적화 워크플로우

### 자동 최적화 체크

```yaml
auto_optimization:
  pre_publish_check:
    title:
      - [ ] 50-60자 이내
      - [ ] 주요 키워드 포함
      - [ ] 중복 없음

    meta_description:
      - [ ] 120-155자
      - [ ] 키워드 포함
      - [ ] CTA 포함

    headings:
      - [ ] H1 1개
      - [ ] H2 5개 이상
      - [ ] 계층 구조 올바름

    content:
      - [ ] 키워드 밀도 1-2%
      - [ ] 내부 링크 3개 이상
      - [ ] 외부 링크 2개 이상

    images:
      - [ ] alt 텍스트 모두 있음
      - [ ] WebP 포맷
      - [ ] lazy loading

    technical:
      - [ ] URL 최적화
      - [ ] 구조화 데이터 유효
      - [ ] OG 태그 설정

  score_calculation:
    perfect: 100
    good: 80-99
    needs_work: 60-79
    poor: < 60
```

## CLI 사용법

```bash
# 페이지 SEO 분석
/seo analyze {url}

# 메타 태그 생성
/seo meta --title "제목" --keyword "키워드"

# 구조화 데이터 생성
/seo schema --type article --title "제목"

# OG 이미지 생성
# 텍스트/카드는 Next.js ImageResponse로 deterministic하게 만듭니다.
# 생성형 raster가 필요하면 image-prompt → validator → Codex $imagegen → gpt-image-2를 사용합니다.
/seo og-image --title "제목" --subtitle "부제"

# 콘텐츠 최적화 제안
/seo optimize {content_file}

# SEO 점수 체크
/seo score {url}
```

## 출력 포맷

### SEO 분석 결과

```json
{
  "url": "https://example.com/blog/payment-guide",
  "seo_score": 85,
  "analysis": {
    "title": {
      "value": "SaaS 결제 연동 가이드",
      "length": 15,
      "score": 90,
      "suggestion": "키워드를 앞에 배치하면 좋습니다"
    },
    "meta_description": {
      "value": "포트원과 Stripe 비교 분석",
      "length": 17,
      "score": 60,
      "suggestion": "120자 이상으로 확장 권장"
    },
    "headings": {
      "h1_count": 1,
      "h2_count": 6,
      "score": 100,
      "structure": "optimal"
    },
    "content": {
      "word_count": 2500,
      "keyword_density": 1.5,
      "internal_links": 4,
      "external_links": 2,
      "score": 95
    },
    "images": {
      "total": 5,
      "with_alt": 5,
      "score": 100
    },
    "schema": {
      "present": true,
      "types": ["Article", "FAQPage"],
      "valid": true,
      "score": 100
    }
  },
  "recommendations": [
    {
      "priority": "high",
      "issue": "메타 설명이 너무 짧습니다",
      "action": "120-155자로 확장"
    },
    {
      "priority": "medium",
      "issue": "타이틀에 연도 추가 권장",
      "action": "'2026' 추가"
    }
  ]
}
```

### 메타 태그 생성 결과

```json
{
  "generated_meta": {
    "title": "SaaS 결제 연동 완벽 가이드 (2026) | MyApp",
    "description": "SaaS 결제 연동이 어려우신가요? 포트원과 Stripe를 단계별로 비교하고 최적의 선택을 도와드립니다. 실전 코드 예제 포함.",
    "og_tags": {
      "og:title": "SaaS 결제 연동 완벽 가이드 (2026)",
      "og:description": "포트원과 Stripe를 단계별로 비교하고 최적의 결제 연동 방법을 알아봅니다.",
      "og:image": "https://example.com/og/payment-guide.png",
      "og:type": "article"
    },
    "twitter_tags": {
      "twitter:card": "summary_large_image",
      "twitter:title": "SaaS 결제 연동 완벽 가이드 (2026)",
      "twitter:description": "포트원 vs Stripe 비교 분석"
    }
  },
  "html_snippet": "<!-- 복사해서 사용 -->\n<title>SaaS 결제 연동 완벽 가이드 (2026) | MyApp</title>\n..."
}
```

---

Version: 1.0.0
Last Updated: 2026-01-27
