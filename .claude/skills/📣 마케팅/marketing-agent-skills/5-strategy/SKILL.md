---
name: mkt-strategy
description: |
  마케팅 전략 수립 (PESO 미디어 믹스, North Star Metric).
  전체 마케팅 방향과 로드맵을 정의합니다.
triggers:
  - "마케팅 전략"
  - "전략 수립"
  - "PESO"
  - "마케팅 로드맵"
input:
  - context/{project}-context.md
  - strategy/positioning.md
  - personas/*.md
output:
  - strategy/marketing-strategy.md
---

# Strategy Skill

PESO 미디어 믹스와 North Star Metric 기반의 마케팅 전략을 수립합니다.

## PESO 프레임워크

```
┌─────────────────────────────────────────────────────────────┐
│                      PESO Model                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐│
│   │  Paid    │   │  Earned  │   │  Shared  │   │  Owned   ││
│   │  Media   │   │  Media   │   │  Media   │   │  Media   ││
│   └──────────┘   └──────────┘   └──────────┘   └──────────┘│
│                                                              │
│   광고, 스폰서     PR, 언론       소셜, 바이럴    웹사이트,    │
│                                                 블로그,      │
│                                                 뉴스레터     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### PESO 상세

```yaml
paid:                         # 유료 미디어
  channels:
    - search_ads              # 검색 광고
    - display_ads             # 디스플레이
    - social_ads              # 소셜 광고
    - sponsored_content       # 스폰서 콘텐츠
    - influencer_paid         # 인플루언서 (유료)
  characteristics:
    - immediate_results
    - scalable
    - measurable
    - requires_budget

earned:                       # 획득 미디어
  channels:
    - press_coverage          # 언론 보도
    - reviews                 # 리뷰
    - word_of_mouth          # 입소문
    - organic_mentions        # 자연 언급
  characteristics:
    - high_credibility
    - free
    - unpredictable
    - hard_to_scale

shared:                       # 공유 미디어
  channels:
    - social_media            # 소셜 미디어
    - user_generated_content  # UGC
    - community               # 커뮤니티
    - viral_content           # 바이럴
  characteristics:
    - engagement_focused
    - community_building
    - amplification

owned:                        # 소유 미디어
  channels:
    - website                 # 웹사이트
    - blog                    # 블로그
    - email_list              # 이메일
    - app                     # 앱
  characteristics:
    - full_control
    - long_term_asset
    - requires_content
```

## North Star Metric (NSM)

```
┌─────────────────────────────────────────────────────────────┐
│                    North Star Metric                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   "고객에게 전달하는 핵심 가치를 반영하는 단 하나의 지표"       │
│                                                              │
│   예시:                                                      │
│   • Airbnb: "예약된 숙박 일수"                               │
│   • Spotify: "청취 시간"                                     │
│   • Slack: "일일 활성 사용자의 메시지 수"                     │
│   • Facebook: "일일 활성 사용자"                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### NSM 선정 기준

```yaml
criteria:
  - reflects_value: true      # 고객 가치 반영
  - measurable: true          # 측정 가능
  - actionable: true          # 행동 유도
  - leading_indicator: true   # 선행 지표
  - team_aligned: true        # 팀 정렬 가능
```

## 워크플로우

```
1. 기존 문서 확인
   ├─ 컨텍스트
   ├─ 포지셔닝
   └─ 페르소나
      │
      ▼
2. 목표 설정
   ├─ North Star Metric 정의
   └─ SMART Goals 수립
      │
      ▼
3. PESO 믹스 설계
   ├─ 채널별 역할 정의
   └─ 예산 배분
      │
      ▼
4. 전략 프레임워크
   ├─ 핵심 전략 3가지
   └─ 실행 로드맵
      │
      ▼
5. 문서 저장
   → workspace/work-marketing/strategy/marketing-strategy.md
```

## 출력 템플릿

```markdown
# {Project Name} Marketing Strategy

## Executive Summary

{전략 한 문단 요약}

---

## 1. Strategic Foundation

### Vision
{마케팅 비전}

### Mission
{마케팅 미션}

### North Star Metric

| 항목 | 내용 |
|------|------|
| NSM | {north_star_metric} |
| 현재 | {current_value} |
| 목표 | {target_value} |
| 기간 | {timeline} |

**선정 이유**: {rationale}

---

## 2. Goals & Objectives

### Primary Goal
{primary_goal}

### SMART Objectives

| 목표 | Specific | Measurable | Achievable | Relevant | Time-bound |
|------|----------|------------|------------|----------|------------|
| {obj_1} | {s} | {m} | {a} | {r} | {t} |
| {obj_2} | {s} | {m} | {a} | {r} | {t} |
| {obj_3} | {s} | {m} | {a} | {r} | {t} |

### KPI Dashboard

| KPI | 현재 | 목표 | 측정 방법 |
|-----|------|------|----------|
| {kpi_1} | {current} | {target} | {method} |
| {kpi_2} | {current} | {target} | {method} |
| {kpi_3} | {current} | {target} | {method} |

---

## 3. Target Audience

### Primary Target
{primary_target_summary}
→ 상세: [Persona 1 링크]

### Secondary Target
{secondary_target_summary}
→ 상세: [Persona 2 링크]

---

## 4. Positioning Recap

> "{positioning_statement}"

### Key Messages

1. **Primary**: {primary_message}
2. **Supporting**: {supporting_message_1}
3. **Supporting**: {supporting_message_2}

---

## 5. PESO Media Mix

### 채널 전략

```
┌──────────────────────────────────────────────────────────┐
│                    PESO Allocation                        │
├──────────────────────────────────────────────────────────┤
│                                                           │
│   Paid (40%)        Earned (10%)                         │
│   ████████          ██                                   │
│                                                           │
│   Shared (20%)      Owned (30%)                          │
│   ████              ██████                               │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

### Paid Media

| 채널 | 목적 | 예산 비중 | 예상 결과 |
|------|------|----------|----------|
| {channel_1} | {purpose} | {%} | {result} |
| {channel_2} | {purpose} | {%} | {result} |

**핵심 전략**: {paid_strategy}

### Earned Media

| 채널 | 목적 | 활동 | 예상 결과 |
|------|------|------|----------|
| {channel_1} | {purpose} | {activity} | {result} |

**핵심 전략**: {earned_strategy}

### Shared Media

| 채널 | 목적 | 콘텐츠 유형 | 빈도 |
|------|------|------------|------|
| {channel_1} | {purpose} | {content} | {frequency} |
| {channel_2} | {purpose} | {content} | {frequency} |

**핵심 전략**: {shared_strategy}

### Owned Media

| 채널 | 목적 | 콘텐츠 유형 | 빈도 |
|------|------|------------|------|
| {channel_1} | {purpose} | {content} | {frequency} |
| {channel_2} | {purpose} | {content} | {frequency} |

**핵심 전략**: {owned_strategy}

---

## 6. Core Strategies (핵심 전략 3가지)

### Strategy 1: {name}

**목표**: {goal}

**접근법**: {approach}

**핵심 활동**:
1. {activity_1}
2. {activity_2}
3. {activity_3}

**성공 지표**: {metrics}

### Strategy 2: {name}

**목표**: {goal}

**접근법**: {approach}

**핵심 활동**:
1. {activity_1}
2. {activity_2}
3. {activity_3}

**성공 지표**: {metrics}

### Strategy 3: {name}

**목표**: {goal}

**접근법**: {approach}

**핵심 활동**:
1. {activity_1}
2. {activity_2}
3. {activity_3}

**성공 지표**: {metrics}

---

## 7. Budget Allocation

### 전체 예산

| 항목 | 금액 | 비중 |
|------|------|------|
| 총 예산 | {total} | 100% |
| Paid | {paid} | {%} |
| Content | {content} | {%} |
| Tools | {tools} | {%} |
| Other | {other} | {%} |

### 채널별 예산

| 채널 | 월 예산 | 분기 예산 | 예상 ROI |
|------|--------|----------|---------|
| {channel_1} | {monthly} | {quarterly} | {roi} |
| {channel_2} | {monthly} | {quarterly} | {roi} |

---

## 8. Roadmap

### Phase 1: Foundation ({month_1}-{month_2})

**목표**: {phase_1_goal}

| 주차 | 활동 | 담당 | 산출물 |
|------|------|------|--------|
| W1-2 | {activity} | {owner} | {deliverable} |
| W3-4 | {activity} | {owner} | {deliverable} |

### Phase 2: Growth ({month_3}-{month_4})

**목표**: {phase_2_goal}

| 주차 | 활동 | 담당 | 산출물 |
|------|------|------|--------|
| W1-2 | {activity} | {owner} | {deliverable} |
| W3-4 | {activity} | {owner} | {deliverable} |

### Phase 3: Optimization ({month_5}-{month_6})

**목표**: {phase_3_goal}

| 주차 | 활동 | 담당 | 산출물 |
|------|------|------|--------|
| W1-2 | {activity} | {owner} | {deliverable} |
| W3-4 | {activity} | {owner} | {deliverable} |

---

## 9. Risk & Mitigation

| 리스크 | 영향도 | 발생 확률 | 대응 방안 |
|--------|--------|----------|----------|
| {risk_1} | High | Medium | {mitigation} |
| {risk_2} | Medium | High | {mitigation} |
| {risk_3} | Low | High | {mitigation} |

---

## 10. Success Criteria

### 단기 (1-3개월)
- [ ] {criteria_1}
- [ ] {criteria_2}
- [ ] {criteria_3}

### 중기 (3-6개월)
- [ ] {criteria_1}
- [ ] {criteria_2}

### 장기 (6-12개월)
- [ ] {criteria_1}
- [ ] {criteria_2}

---

## 11. 다음 단계

1. [ ] Campaign Skill로 캠페인 상세 기획
2. [ ] Funnel Skill로 퍼널 설계
3. [ ] Content 스킬들로 실행물 제작

---

*Strategy Version: 1.0*
*Created: {date}*
*Review Date: {review_date}*
```

## 전략 예시

### B2B SaaS 예시

```markdown
## North Star Metric
"주간 활성 API 호출 수"
→ 고객이 우리 제품에서 가치를 얻고 있다는 직접적 증거

## PESO Mix
- Paid (30%): Google Ads (개발자 키워드), LinkedIn
- Earned (10%): Product Hunt, 개발자 미디어
- Shared (30%): Twitter, GitHub, 개발자 커뮤니티
- Owned (30%): 블로그 (기술 콘텐츠), 뉴스레터

## Core Strategies
1. Developer Evangelism - 개발자 커뮤니티 신뢰 구축
2. Content-Led Growth - 기술 블로그로 SEO 확보
3. Product-Led Growth - 무료 티어로 바이럴
```

## AI 시대 전략 강화 (2025)

### 2025 핵심 트렌드

```yaml
key_insights:
  숏폼이_왕이다:
    stat: "78%의 사람들이 숏폼 비디오로 새 제품을 알게 됨"
    implication: "숏폼 80% + 이미지/텍스트 20%"

  바이럴_equals_참여:
    principle: "팔리는 콘텐츠 ❌ → 공감이 전염되는 콘텐츠 ✅"
    implication: "소비자가 공동 창작자가 되어야 확산"

  커뮤니티가_핵:
    principle: "신뢰 + 공감 + 커뮤니티 = 2025 확산의 3축"
    implication: "초기 100명의 열성 팬이 1만 명보다 가치있음"

  AI_도구가_게임_체인저:
    stat: "79% 크리에이터가 AI로 더 많은 콘텐츠 생산"
    implication: "예산 0원도 AI 도구로 프로급 콘텐츠 가능"
```

### 숏폼 우선 전략 (PESO 재정의)

```yaml
peso_2025:
  Paid:
    전통: "검색광고, 디스플레이"
    AI강화: "틱톡/릴스 프로모션, 마이크로 인플루언서"

  Earned:
    전통: "PR, 언론"
    AI강화: "바이럴 챌린지 참여, UGC 확산"

  Shared:
    전통: "소셜 미디어"
    AI강화:
      - "숏폼 비디오 80%"
      - "참여형 챌린지"
      - "밈화 유도"
      - "커뮤니티 팬덤"

  Owned:
    전통: "웹사이트, 블로그"
    AI강화:
      - "Discord/카톡 커뮤니티"
      - "Building in Public"
      - "앰배서더 프로그램"
```

### 콘텐츠 비중 가이드

```
2025 콘텐츠 믹스
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
숏폼 비디오    ████████████████████████  80%
(TikTok, Reels, Shorts)

이미지/텍스트  █████                      20%
(피드, 카드뉴스, 블로그)
```

### 플랫폼 우선순위

```yaml
platform_priority:
  바이럴_잠재력:
    1: "TikTok (알고리즘 노출 기회 최고)"
    2: "Instagram Reels"
    3: "YouTube Shorts"

  타겟별_선택:
    2030_국내: [TikTok, Instagram]
    B2B: [LinkedIn, Twitter]
    개발자: [Twitter, GitHub, Discord]
    10대: [TikTok]
```

### AI 도구 추천

```yaml
ai_tools:
  무료_필수:
    영상_편집: "CapCut"
    그래픽: "image-prompt → Codex gpt-image-2"
    스크립트: "ChatGPT"
    랜딩페이지: "Carrd, Tally"
    이메일: "Mailchimp (무료 티어)"
    분석: "Google Analytics 4"

  유료_추천:
    영상: "Descript, Runway"
    그래픽: "image-prompt → Codex gpt-image-2"
    아바타: "HeyGen, Synthesia"
    카피: "Jasper, Copy.ai"
    자동화: "Zapier, Make"
```

### 전략 체크리스트 (AI 시대)

```markdown
□ 숏폼 비디오가 콘텐츠 믹스의 80%인가?
□ 참여형 챌린지/밈 요소가 있는가?
□ 커뮤니티 빌딩 계획이 있는가?
□ AI 도구 활용 계획이 구체적인가?
□ Building in Public 전략이 있는가?
□ 마이크로 인플루언서 활용 계획이 있는가?
□ 무예산으로도 실행 가능한 전략이 있는가?
```

---

<!-- Merged from coreyhaines31/marketingskills -->

## Searchable vs Shareable 콘텐츠 프레임워크

모든 콘텐츠는 **Searchable**, **Shareable**, 또는 **둘 다**여야 합니다. 검색 트래픽이 기반이므로 Searchable을 우선합니다.

```
┌─────────────────────────────────────────────────────────────┐
│              Searchable vs Shareable                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Searchable (기존 수요 포착)                                 │
│   ─────────────────────────────                              │
│   • 특정 키워드/질문 타겟                                     │
│   • 검색 의도 정확히 매칭                                     │
│   • 검색 쿼리와 일치하는 명확한 제목                           │
│   • 데이터, 예시, 권위 있는 소스 포함                          │
│   • AI/LLM 검색 최적화도 고려                                │
│                                                              │
│   Shareable (수요 창출)                                      │
│   ─────────────────────────────                              │
│   • 새로운 인사이트, 원본 데이터, 반직관적 관점                │
│   • 통념에 도전하는 논리적 주장                               │
│   • 감정을 불러일으키는 스토리텔링                             │
│   • 공유하면 "나 똑똑해 보이는" 콘텐츠                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Hub and Spoke / Topic Cluster 아키텍처

콘텐츠를 3-5개의 핵심 필러(Pillar) 토픽으로 구조화합니다.

### Hub and Spoke 구조

```
Hub = 포괄적 개요 페이지
Spoke = 관련 세부 토픽

/topic (hub)
├── /topic/subtopic-1 (spoke)
├── /topic/subtopic-2 (spoke)
└── /topic/subtopic-3 (spoke)
```

### 필러 선정 기준

```yaml
pillar_criteria:
  product_led: "우리 제품이 해결하는 문제와 연결"
  audience_led: "ICP가 배워야 할 것"
  search_led: "검색 볼륨이 있는 토픽"
  competitor_led: "경쟁사가 랭킹하는 토픽"
```

### 필러 구조 예시

```
Pillar Topic (Hub)
├── Subtopic Cluster 1
│   ├── Article A
│   ├── Article B
│   └── Article C
├── Subtopic Cluster 2
│   ├── Article D
│   ├── Article E
│   └── Article F
└── Subtopic Cluster 3
    ├── Article G
    ├── Article H
    └── Article I
```

> **참고**: 대부분의 콘텐츠는 `/blog`에서 충분합니다. 전용 Hub/Spoke URL 구조는 깊이 있는 가이드 콘텐츠(예: Atlassian의 `/agile`)에만 사용하세요.

---

## Content Prioritization Scoring Model

콘텐츠 아이디어를 4가지 요소로 점수화하여 우선순위를 결정합니다.

### 점수 기준

```yaml
scoring_weights:
  customer_impact: 40%           # 고객 임팩트
  content_market_fit: 30%        # 콘텐츠-마켓 핏
  search_potential: 20%          # 검색 잠재력
  resource_requirements: 10%     # 리소스 요구사항
```

### 상세 기준

| 요소 | 비중 | 평가 질문 |
|------|------|----------|
| **Customer Impact** | 40% | 이 주제가 리서치에서 얼마나 자주 언급됐나? 고객의 몇 %가 이 문제를 겪나? 감정적 강도는? |
| **Content-Market Fit** | 30% | 우리 제품이 해결하는 문제와 연결되나? 고유한 인사이트를 제공할 수 있나? 자연스럽게 제품에 관심을 유도하나? |
| **Search Potential** | 20% | 월간 검색 볼륨은? 경쟁 강도는? 롱테일 기회가 있나? 검색 관심도가 증가 추세인가? |
| **Resources** | 10% | 권위 있는 콘텐츠를 만들 전문성이 있나? 추가 리서치가 필요한가? 그래픽/데이터 에셋이 필요한가? |

### 스코어링 템플릿

| 아이디어 | Customer Impact (40%) | Content-Market Fit (30%) | Search Potential (20%) | Resources (10%) | Total |
|---------|----------------------|-------------------------|----------------------|-----------------|-------|
| Topic A | 8 | 9 | 7 | 6 | **8.0** |
| Topic B | 6 | 7 | 9 | 8 | **7.1** |
| Topic C | 9 | 6 | 5 | 9 | **7.2** |

---

## Content Ideation 소스

다양한 소스에서 콘텐츠 아이디어를 발굴합니다.

### 1. 콜 트랜스크립트 (세일즈/CS 통화 녹취)

```yaml
call_transcript_mining:
  extract:
    - questions_asked: "→ FAQ 콘텐츠 또는 블로그 포스트"
    - pain_points: "→ 고객 언어 그대로의 문제 설명"
    - objections: "→ 선제적 반론 처리 콘텐츠"
    - language_patterns: "→ Voice of Customer 정확한 표현"
    - competitor_mentions: "→ 비교 콘텐츠"
```

### 2. 서베이 응답

```yaml
survey_data_mining:
  focus:
    - open_ended_responses: "토픽과 언어 추출"
    - common_themes: "30%+ 언급 = 높은 우선순위"
    - resource_requests: "고객이 원하는 자료"
    - content_preferences: "선호하는 콘텐츠 형식"
```

### 3. 포럼/커뮤니티 리서치

```yaml
forum_research:
  reddit: "site:reddit.com [topic] — 인기 포스트, 질문, 공감 댓글"
  quora: "site:quora.com [topic] — 팔로워 많은 질문, 인기 답변"
  others:
    - "Indie Hackers"
    - "Hacker News"
    - "Product Hunt 댓글"
    - "업계 Slack/Discord"
  extract: "FAQ, 오해, 논쟁, 해결 중인 문제, 사용 용어"
```

### 4. 경쟁사 콘텐츠 분석

```yaml
competitor_analysis:
  method: "site:competitor.com/blog"
  analyze:
    - top_performing_posts: "댓글, 공유 수"
    - repeated_topics: "자주 다루는 주제"
    - content_gaps: "다루지 않는 주제"
    - case_studies: "고객 문제, 사용 사례, 결과"
    - content_structure: "필러, 카테고리, 형식"
  opportunities:
    - "더 잘 다룰 수 있는 토픽"
    - "경쟁사가 놓친 앵글"
    - "오래되어 업데이트가 필요한 콘텐츠"
```

<!-- End of merged content from coreyhaines31/marketingskills -->

---

## 🌏 글로벌 시장 확장 전략 (Global Market Expansion)

### 영어권 SaaS Go-to-Market 채널

```yaml
global_gtm_channels:
  launch_platforms:
    product_hunt:
      description: "신제품 런칭 최고 채널"
      strategy: |
        - 런칭 당일 아침 (PST 00:01)에 게시
        - Hunter를 통해 런칭 (팔로워 많은 사람)
        - 첫 4시간 초기 업보트가 핵심
        - 런칭 전 2주간 커뮤니티 빌딩
      expected: "Top 5 = 수천 명 방문, 수백 가입"
      tip: "한국 제품도 영어 LP로 Product Hunt 런칭 가능"

    hacker_news:
      description: "테크 커뮤니티 신뢰 구축"
      strategy: |
        - "Show HN: [제품명] – [한 줄 설명]" 포맷
        - 기술적 깊이 있는 설명 필요
        - 댓글에 적극 응답 (창업자 직접)
        - 자기 홍보 과도하면 역효과
      expected: "프론트페이지 = 수만 방문"

    reddit:
      description: "닛치 커뮤니티 타겟팅"
      subreddits:
        saas: [r/SaaS, r/microsaas, r/startups]
        dev: [r/webdev, r/programming, r/reactjs]
        marketing: [r/marketing, r/entrepreneur, r/smallbusiness]
      strategy: |
        - 가치 제공 먼저 (90% 기여, 10% 프로모션)
        - AMA (Ask Me Anything) 진행
        - 문제 해결 포스트에서 자연스럽게 제품 언급

    indie_hackers:
      description: "인디 메이커/부트스트래퍼 커뮤니티"
      strategy: |
        - 수익/성장 과정 공유 (Building in Public)
        - 마일스톤 포스트 (첫 $1K MRR, 첫 100유저 등)
        - 실패/학습 경험 공유가 더 인기

  content_marketing_channels:
    dev_to:
      description: "개발자 타겟 기술 블로그"
      format: "기술 튜토리얼, How-to, 비교 리뷰"
      benefit: "SEO + 커뮤니티 노출"

    medium:
      description: "비즈니스/기술 롱폼 콘텐츠"
      strategy: |
        - 자체 퍼블리케이션 운영 또는 유명 퍼블리케이션에 기고
        - Towards Data Science, Better Programming 등
      benefit: "도메인 권위 + 기존 독자층"

    hashnode:
      description: "개발자 블로그 플랫폼"
      benefit: "커스텀 도메인 + 커뮤니티 노출"

    substack:
      description: "뉴스레터 기반 콘텐츠"
      strategy: "주 1회 업계 인사이트 뉴스레터"
      benefit: "이메일 리스트 직접 소유"

  social_channels_global:
    x_twitter:
      strategy: "Building in Public, 업계 대화 참여"
      posting: "일 2-5회"
    linkedin:
      strategy: "B2B 전문성 확보, 의사결정자 타겟"
      posting: "주 3-5회"
    tiktok:
      strategy: "비하인드 씬, 제품 데모, 창업 스토리"
      posting: "일 1-2회"
    youtube:
      strategy: "튜토리얼, 제품 비교, 웨비나"
      posting: "주 1-2회"
```

### 크로스보더 마케팅 고려사항

```yaml
cross_border_considerations:
  localization:
    website: |
      - 영어 LP 필수 (글로벌 타겟 시)
      - 한국어/영어 별도 도메인 또는 서브디렉토리 (/ko, /en)
      - 결제 통화 다중 지원 (USD, KRW, EUR)
    content: |
      - 문화적 맥락에 맞는 카피라이팅
      - 한국 사례 → 글로벌에서 이해 가능한 사례로 보충
      - 시간대/공휴일 고려한 캠페인 일정

  legal_compliance:
    gdpr: "유럽 타겟 시 GDPR 준수 필수"
    ccpa: "캘리포니아 타겟 시 CCPA 준수"
    privacy_policy: "다국어 개인정보처리방침"

  payment:
    global: "Stripe (가장 광범위한 글로벌 지원)"
    korea: "토스페이먼츠, 아임포트"
    strategy: "글로벌 + 한국 결제 동시 지원"

  support:
    timezone: "비동기 지원 체계 구축 (이메일, 도움말 센터)"
    language: "영어 지원 필수, 한국어는 보너스"
    tools: "Intercom, Crisp, 또는 이메일 기반"

  market_entry_priority:
    tier_1: "US, UK (영어권, 가장 큰 SaaS 시장)"
    tier_2: "EU (독일, 프랑스, 네덜란드)"
    tier_3: "JP, SEA (아시아 확장)"
    strategy: |
      - 한국에서 PMF 검증 후 영어권 확장
      - 또는 처음부터 영어로 글로벌 론칭
      - 한국 시장 특수성 (네이버, 카카오) vs 글로벌 표준 (Google, Stripe)
```

## 다음 스킬 연결

- **Campaign Skill**: 전략을 구체적 캠페인으로 (챌린지 포함)
- **Funnel Skill**: AARRR 퍼널 상세 설계
- **Copywriting Skill**: 숏폼 스크립트 제작
- **Analytics KPI Skill**: KPI 측정 체계 구축

---

*좋은 전략은 "무엇을 하지 않을 것인가"를 명확히 합니다.*
*모든 것을 다 할 수는 없습니다. 선택과 집중이 핵심입니다.*
*2025년엔 "어떻게 참여하게 만들 것인가?"가 선택의 기준입니다.*
