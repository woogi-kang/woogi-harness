---
name: social-scheduler
description: 소셜 미디어 스케줄링 및 자동화 스킬
model: inherit
quality_tier: fast_scan
triggers:
  - "소셜"
  - "스케줄"
  - "SNS"
  - "트위터"
  - "링크드인"
  - "인스타그램"
---

# Social Scheduler Skill

멀티 플랫폼 소셜 미디어 스케줄링 및 자동화 스킬입니다.

## 핵심 원칙

| 원칙 | 설명 |
|------|------|
| **플랫폼 최적화** | 각 플랫폼 특성에 맞는 콘텐츠 |
| **일관성** | 규칙적인 발행으로 알고리즘 우대 |
| **데이터 기반** | 최적 시간, 해시태그, 포맷 분석 |

## 플랫폼별 전략

### Twitter/X

```yaml
twitter_strategy:
  content_types:
    thread:
      description: "연결된 트윗 시리즈"
      best_for: "가이드, 리스트, 스토리"
      optimal_length: "5-12 트윗"
      tip: "첫 트윗에서 가치 약속"

    single_tweet:
      description: "단일 트윗"
      best_for: "인사이트, 질문, 공지"
      optimal_length: "100-200자"

    quote_tweet:
      description: "인용 + 의견"
      best_for: "업계 뉴스, 토론"

  posting_frequency:
    recommended: "3-5회/일"
    max_safe: "10회/일"
    warning: "10회 초과 시 알고리즘 페널티 가능"

  optimal_times:
    korea:
      weekday: ["08:00", "12:00", "18:00", "21:00"]
      weekend: ["10:00", "14:00", "20:00"]
    us_focused:
      weekday: ["09:00 EST", "12:00 EST", "17:00 EST"]

  hashtags:
    max_count: 2
    placement: "끝에 자연스럽게"
    research: "트렌딩 + 니치 조합"

  dont_do:
    - "자동 답글"
    - "대량 팔로우/언팔"
    - "동일 콘텐츠 반복"
    - "링크만 있는 트윗"
```

### LinkedIn

```yaml
linkedin_strategy:
  content_types:
    text_post:
      description: "텍스트 중심 포스트"
      best_for: "인사이트, 경험 공유"
      optimal_length: "1,200-1,500자"
      format: |
        {훅 - 첫 줄로 주의 끌기}

        {스토리 또는 문제}

        {해결책 또는 배움}

        💡 Key takeaway:
        → {핵심 메시지}

        {질문으로 참여 유도}

        #해시태그1 #해시태그2

    carousel:
      description: "슬라이드 문서 (PDF)"
      best_for: "가이드, 리스트, 데이터"
      optimal_slides: "8-12장"

    article:
      description: "LinkedIn 내 블로그"
      best_for: "긴 형식 thought leadership"
      note: "포스트 대비 도달 낮음"

    poll:
      description: "투표"
      best_for: "참여 유도, 리서치"
      duration: "1주일 권장"

  posting_frequency:
    recommended: "1-2회/일"
    max_safe: "3회/일"

  optimal_times:
    korea:
      best: ["08:00", "12:00"]
      good: ["17:00", "19:00"]
    global:
      best: ["07:00-08:00", "12:00"]

  hashtags:
    max_count: "3-5"
    placement: "포스트 끝"
    research: "팔로워 많은 해시태그 + 니치"

  algorithm_tips:
    - "첫 1시간 참여가 중요 → 직접 답글"
    - "외부 링크는 첫 댓글에"
    - "태깅으로 도달 확장"
    - "질문으로 댓글 유도"
```

### Instagram

```yaml
instagram_strategy:
  content_types:
    carousel:
      description: "슬라이드 이미지"
      best_for: "가이드, 리스트, 비포/애프터"
      optimal_slides: "7-10장"
      first_slide: "스크롤 멈추게 하는 훅"

    reels:
      description: "짧은 영상"
      best_for: "도달 확장, 새 팔로워"
      optimal_length: "15-30초"

    stories:
      description: "24시간 콘텐츠"
      best_for: "일상, BTS, 참여"
      frequency: "3-7회/일"

    single_image:
      description: "단일 이미지"
      best_for: "브랜드, 명언"
      note: "도달 낮음"

  posting_frequency:
    feed: "1회/일"
    reels: "3-5회/주"
    stories: "3-7회/일"

  optimal_times:
    best: ["11:00", "14:00", "19:00"]
    weekend: "조금 늦은 시간 (10-14시)"

  hashtags:
    max_count: "10-15 (최대 30)"
    strategy: |
      - 대형 (1M+): 2-3개
      - 중형 (100K-1M): 5-7개
      - 니치 (10K-100K): 5-7개

  captions:
    length: "첫 125자가 중요 (더보기 전)"
    cta: "저장, 공유, 댓글 유도"
```

## 크로스 플랫폼 전략

### 콘텐츠 변환 매트릭스

```yaml
content_transformation:
  source: "블로그 포스트"

  transformations:
    twitter:
      format: "스레드 5-10개"
      adaptation:
        - "핵심 포인트만 추출"
        - "숫자/이모지로 스캔 가능하게"
        - "마지막에 원문 링크"

    linkedin:
      format: "텍스트 포스트"
      adaptation:
        - "스토리텔링 강조"
        - "개인 경험 추가"
        - "전문성 어필"

    instagram:
      format: "캐러셀"
      adaptation:
        - "시각적으로 변환"
        - "한 슬라이드 = 한 포인트"
        - "텍스트 최소화"

    youtube_shorts:
      format: "60초 영상"
      adaptation:
        - "핵심 1가지만"
        - "자막 필수"
        - "훅 3초 내"
```

### 발행 시간표

```yaml
publishing_schedule:
  content_piece: "블로그 발행 기준"

  day_0:  # 블로그 발행일
    - platform: "Blog"
      time: "09:00"
      action: "원문 발행"

    - platform: "Twitter"
      time: "10:00"
      action: "스레드 발행"

    - platform: "LinkedIn"
      time: "12:00"
      action: "포스트 발행"

  day_1:
    - platform: "Twitter"
      time: "09:00"
      action: "핵심 인사이트 단일 트윗"

    - platform: "Instagram"
      time: "19:00"
      action: "캐러셀 발행"

  day_3:
    - platform: "LinkedIn"
      time: "08:00"
      action: "다른 각도 포스트"

  day_7:
    - platform: "Twitter"
      time: "12:00"
      action: "스레드 재발행 (리마인더)"
```

## 자동화 도구 연동

### SocialBee

```yaml
socialbee:
  description: "에버그린 콘텐츠 재활용"
  pricing: "$29/월~"

  features:
    - 카테고리별 큐
    - 재발행 자동화
    - AI 캡션 생성
    - 최적 시간 자동

  integration:
    - RSS 피드 연결
    - Canva 연동
    - 분석 대시보드
```

### Buffer

```yaml
buffer:
  description: "심플한 스케줄링"
  pricing: "무료 (3채널) / $6/월"

  features:
    - 직관적 UI
    - 기본 분석
    - 팀 협업
```

### Typefully

```yaml
typefully:
  description: "Twitter/X 전문"
  pricing: "무료 / $15/월"

  features:
    - 스레드 작성 최적화
    - 성과 분석
    - 자동 리트윗
```

## CLI 사용법

```bash
# 포스트 스케줄
/social schedule --platform twitter --content "내용" --time "2026-01-28 09:00"

# 블로그를 소셜로 변환
/social transform --source blog.md --platforms twitter,linkedin

# 큐 확인
/social queue [--platform twitter]

# 최적 시간 조회
/social best-times --platform linkedin

# 성과 분석
/social analytics --period 7d

# 해시태그 추천
/social hashtags --topic "SaaS 결제" --platform instagram
```

## 콘텐츠 템플릿

### Twitter 스레드 템플릿

```yaml
twitter_thread_template:
  tweet_1: |
    🧵 {훅 - 문제/질문/통계}

    {해결책 약속}

    ↓ {무엇을 배울지}

  tweet_2_to_n: |
    {번호}/ {포인트 제목}

    {상세 설명}

    {예시 또는 팁}

  last_tweet: |
    {요약}

    💡 마무리 인사이트

    👉 더 자세한 내용: {링크}

    RT/북마크로 저장해두세요!
```

### LinkedIn 포스트 템플릿

```yaml
linkedin_post_template:
  standard: |
    {훅 - 첫 줄에서 멈추게}

    {빈 줄}

    {스토리 또는 문제 상황}

    {빈 줄}

    {배움 또는 해결책}

    {빈 줄}

    💡 핵심:
    → {테이크어웨이 1}
    → {테이크어웨이 2}

    {빈 줄}

    {질문으로 참여 유도}

    {빈 줄}

    #해시태그1 #해시태그2 #해시태그3
```

## 분석 지표

### 플랫폼별 KPI

```yaml
kpis:
  twitter:
    primary:
      - impressions: "노출 수"
      - engagement_rate: "참여율 (좋아요+RT+답글)/노출"
      - profile_visits: "프로필 방문"
      - followers_growth: "팔로워 증가"
    benchmark:
      engagement_rate: "> 2%"

  linkedin:
    primary:
      - impressions: "노출 수"
      - engagement_rate: "참여율"
      - click_through_rate: "링크 클릭률"
      - followers_growth: "팔로워 증가"
    benchmark:
      engagement_rate: "> 4%"

  instagram:
    primary:
      - reach: "도달"
      - engagement_rate: "참여율"
      - saves: "저장 수"
      - shares: "공유 수"
    benchmark:
      engagement_rate: "> 3%"
```

## 출력 포맷

### 스케줄 결과

```json
{
  "action": "schedule_posts",
  "source": "/blog/saas-payment-guide.md",
  "generated_at": "2026-01-27T10:00:00Z",

  "scheduled": {
    "twitter": {
      "thread": {
        "tweets": 7,
        "scheduled_at": "2026-01-28T09:00:00+09:00",
        "preview": "🧵 SaaS 결제 연동, 어디서부터..."
      }
    },
    "linkedin": {
      "post": {
        "scheduled_at": "2026-01-28T12:00:00+09:00",
        "preview": "3년간 100+ SaaS 결제 연동을 도우며..."
      }
    },
    "instagram": {
      "carousel": {
        "slides": 10,
        "scheduled_at": "2026-01-28T19:00:00+09:00"
      }
    }
  },

  "next_actions": [
    "Instagram 캐러셀 생성형 asset 필요: social-visual → image-prompt → Codex gpt-image-2",
    "LinkedIn 포스트 검토 대기"
  ]
}
```

### 성과 분석

```json
{
  "report_type": "social_analytics",
  "period": "2026-01-20 ~ 2026-01-26",

  "summary": {
    "total_posts": 35,
    "total_impressions": 125000,
    "total_engagements": 4200,
    "avg_engagement_rate": "3.4%",
    "follower_growth": "+250"
  },

  "by_platform": {
    "twitter": {
      "posts": 20,
      "impressions": 75000,
      "engagements": 2100,
      "engagement_rate": "2.8%",
      "best_post": {
        "content": "🧵 SaaS 결제 연동 스레드",
        "impressions": 15000,
        "engagement_rate": "5.2%"
      }
    },
    "linkedin": {
      "posts": 10,
      "impressions": 35000,
      "engagements": 1800,
      "engagement_rate": "5.1%"
    },
    "instagram": {
      "posts": 5,
      "reach": 15000,
      "engagements": 300,
      "engagement_rate": "2.0%"
    }
  },

  "top_performing": [
    {
      "platform": "twitter",
      "type": "thread",
      "topic": "SaaS 결제 연동",
      "engagement_rate": "5.2%"
    }
  ],

  "insights": [
    "스레드 형식이 단일 트윗 대비 2x 성과",
    "LinkedIn 오전 8시 발행이 12시 대비 30% 높은 도달",
    "Instagram 캐러셀이 단일 이미지 대비 3x 저장"
  ],

  "recommendations": [
    "Twitter: 스레드 비중 늘리기",
    "LinkedIn: 오전 발행 집중",
    "Instagram: 캐러셀 + Reels 병행"
  ]
}
```

## 금지 행위 (계정 안전)

```yaml
dont_do:
  twitter:
    - "자동 답글/멘션"
    - "대량 팔로우/언팔"
    - "동일 콘텐츠 반복 게시"
    - "10개/일 초과 발행"

  linkedin:
    - "자동 연결 요청"
    - "스팸성 DM"
    - "외부 링크만 있는 포스트"

  instagram:
    - "해시태그 30개 초과"
    - "자동 좋아요/팔로우"
    - "댓글 스팸"

  general:
    - "구매한 팔로워"
    - "가짜 참여"
    - "저작권 침해 콘텐츠"
```

---

Version: 1.0.0
Last Updated: 2026-01-27
