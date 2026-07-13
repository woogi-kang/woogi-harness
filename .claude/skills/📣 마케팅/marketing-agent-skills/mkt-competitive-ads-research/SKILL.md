---
name: mkt-competitive-ads-research
description: |
  공개 광고 라이브러리와 사용자가 제공한 광고 자료를 기반으로 경쟁사 광고 메시지, 크리에이티브 패턴, CTA, 오퍼, 랜딩 경로를 분석합니다. "경쟁사 광고 분석", "광고 라이브러리", "Meta Ad Library", "Facebook Ad Library", "LinkedIn Ads Library", "경쟁 광고 벤치마크", "경쟁사 카피 추출" 요청에 사용합니다.
triggers:
  - "경쟁사 광고 분석"
  - "광고 라이브러리"
  - "Meta Ad Library"
  - "Facebook Ad Library"
  - "LinkedIn Ads Library"
  - "경쟁 광고 벤치마크"
input:
  - context/{project}-context.md
  - .agents/product-marketing-context.md
  - competitor names, ad library URLs, screenshots, CSV exports, or public ad pages
output:
  - research/competitive-ads/ads.csv
  - research/competitive-ads/analysis.md
  - research/competitive-ads/pattern-library.md
  - research/competitive-ads/creative-brief.md
metadata:
  category: "📣 마케팅"
  version: "1.0.0"
  tags: "marketing, ads, competitor-research, creative-analysis"
  source: "https://github.com/ComposioHQ/awesome-claude-skills/tree/master/competitive-ads-extractor"
  license_note: "Inspired by an Apache-2.0 repository skill; rewritten for Woogi Harness conventions."
---

# Competitive Ads Research

공개적으로 접근 가능한 경쟁 광고 증거를 수집하고, 광고 제작에 바로 넘길 수 있는 리서치 브리프를 만든다.

## Guardrails

- 공개 광고 라이브러리, 공식 export/API, 사용자가 제공한 URL/스크린샷/CSV만 사용한다.
- 로그인 우회, 캡차 우회, 비공개 타겟팅 데이터 추정, 개인정보 수집을 하지 않는다.
- 성과 데이터가 없으면 "잘 먹힌다"라고 단정하지 않는다. 반복 빈도, 최근성, 변형 수는 방향성 신호로만 다룬다.
- 경쟁사 문구와 디자인은 참고만 한다. 그대로 복제하지 않고 원본성 있는 테스트 가설로 변환한다.
- 관찰값과 추론값을 분리한다. 추론에는 confidence를 붙인다.

## Context First

작업 시작 전 다음 순서로 제품/브랜드 컨텍스트를 확인한다.

1. `.agents/product-marketing-context.md`
2. `context/{project}-context.md`
3. 없으면 사용자에게 제품, 타겟, 경쟁사, 플랫폼, 기간을 최소 질문한다.

## Workflow

1. Scope
   - 분석 목적: 포지셔닝, 카피 개선, 캠페인 기획, 경쟁 모니터링 중 하나로 정한다.
   - 경쟁사: 직접 경쟁사 3-5개를 우선한다.
   - 플랫폼: Meta, LinkedIn, Google Ads Transparency, TikTok Creative Center 등 사용 가능한 공개 소스를 명시한다.
   - 기간과 지역: 최근 30-90일을 기본으로 하되 사용자가 지정하면 따른다.

2. Collect
   - 각 광고의 출처 URL, 관찰 날짜, 플랫폼, 광고주명, 활성 상태, 포맷, 카피, CTA, 오퍼, 랜딩 URL을 기록한다.
   - 이미지/영상은 가능한 경우 스크린샷 경로나 간단한 creative description으로 남긴다.
   - 접근 제한이 있으면 우회하지 말고 coverage gap으로 기록한다.

3. Normalize
   - 모든 광고를 같은 필드로 표준화한다.
   - 텍스트가 길면 핵심 메시지만 요약하고, 원문 인용은 짧게 제한한다.

4. Analyze
   - 문제 제기: 어떤 pain point를 반복하는가?
   - 가치 제안: 기능, 결과, 비용, 속도, 신뢰 중 무엇을 앞세우는가?
   - 오퍼: 무료 체험, 데모, 할인, 리드마그넷, 이벤트 등 어떤 제안을 쓰는가?
   - 크리에이티브: 제품 UI, 창업자/고객, before/after, 숫자 proof, 비교, 교육형 등 패턴을 분류한다.
   - 퍼널 단계: awareness, consideration, conversion, retention 중 어디에 가까운지 추론한다.
   - 플랫폼 차이: Meta와 LinkedIn 등 플랫폼별 톤/CTA/포맷 차이를 비교한다.

5. Synthesize
   - 반복 패턴과 빈틈을 분리한다.
   - 우리 제품에 적용 가능한 가설을 3-7개 만든다.
   - `mkt-ads-creative`가 바로 사용할 수 있도록 original creative brief로 변환한다.

## Evidence Schema

`ads.csv`에는 가능한 범위에서 아래 필드를 사용한다.

```csv
competitor,platform,source_url,observed_date,active_status,first_seen,last_seen,format,primary_text,headline,cta,offer,landing_url,creative_description,message_theme,funnel_stage,audience_inference,confidence,notes
```

Confidence 기준:

| Level | Meaning |
|-------|---------|
| observed | 광고 라이브러리나 제공 자료에서 직접 확인 |
| inferred-high | 여러 광고 변형에서 반복되어 강하게 추론 |
| inferred-low | 단일 단서 기반 가설 |
| unknown | 데이터 부족 |

## Output Format

### `analysis.md`

```markdown
# {Project} Competitive Ads Analysis

## Executive Summary
- Corpus: {n} ads from {competitors} across {platforms}
- Strongest observed themes: ...
- Main opportunity for us: ...

## Source Coverage
| Competitor | Platform | Ads Reviewed | Date Checked | Coverage Gaps |
|------------|----------|--------------|--------------|---------------|

## Messaging Themes
| Theme | Competitors | Evidence | Confidence | Implication |
|-------|-------------|----------|------------|-------------|

## Creative Patterns
| Pattern | Where Observed | Why It May Work | Original Adaptation |
|---------|----------------|-----------------|---------------------|

## Copy And CTA Patterns
| Pattern | Example Summary | Use Case | Risk |
|---------|-----------------|----------|------|

## Platform Differences
## Gaps And White Space
## Recommended Test Hypotheses
## Handoff To Ads Creative
```

### `pattern-library.md`

Group reusable patterns by message theme, creative format, CTA, offer, and funnel stage.

### `creative-brief.md`

Write original ad directions, not copied competitor ads.

```markdown
# {Project} Ads Creative Brief

## Target
## Campaign Goal
## Angles To Test
1. {angle}: source insight, original hook, proof needed, suggested platform

## Do Not Copy
- Competitor claims/designs that should only be used as reference

## Inputs For `mkt-ads-creative`
- Platforms:
- Required formats:
- Claims that need proof:
- Landing page:
```

## Failure Modes

- If public sources are unavailable, return a coverage report and ask for URLs, screenshots, exports, or approved browser access.
- If only one competitor has data, avoid market-wide conclusions.
- If performance metrics are unavailable, frame outputs as creative hypotheses, not winners.
- If legal/regulatory constraints exist, flag them before recommending ad angles.

## Handoff

Use this skill before `mkt-ads-creative` when the user asks for competitor-informed ads. Pass `creative-brief.md` into `mkt-ads-creative` and generate new ad variants that preserve strategic patterns without copying competitor assets.
