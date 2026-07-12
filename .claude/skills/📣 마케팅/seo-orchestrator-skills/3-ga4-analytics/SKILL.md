---
name: ga4-analytics
description: Google Analytics 4 분석 및 리포팅 스킬
model: inherit
quality_tier: implementation
triggers:
  - "GA4"
  - "analytics"
  - "트래픽"
  - "분석"
  - "전환"
  - "구글 애널리틱스"
---

# GA4 Analytics Skill

Google Analytics 4 데이터 분석 및 마케팅 인사이트 추출 스킬입니다.

## 핵심 원칙

| 원칙 | 설명 |
|------|------|
| **데이터 기반** | 추측이 아닌 데이터 기반 의사결정 |
| **액션 지향** | 분석 → 인사이트 → 실행 가능한 액션 |
| **자동화** | 반복 리포트 자동 생성 |

## GA4 핵심 개념

### 이벤트 기반 모델

```yaml
ga4_event_model:
  description: "GA4는 모든 것이 이벤트"

  auto_events:
    - page_view        # 페이지 조회
    - session_start    # 세션 시작
    - first_visit      # 첫 방문
    - user_engagement  # 사용자 참여

  recommended_events:
    - sign_up          # 가입
    - login            # 로그인
    - purchase         # 구매
    - add_to_cart      # 장바구니
    - begin_checkout   # 결제 시작

  custom_events:
    - click_cta        # CTA 클릭
    - scroll_depth     # 스크롤 깊이
    - video_watch      # 비디오 시청
    - file_download    # 파일 다운로드
```

### 핵심 지표

```yaml
key_metrics:
  acquisition:
    users: "총 사용자 수"
    new_users: "신규 사용자"
    sessions: "세션 수"

  engagement:
    engagement_rate: "참여 세션 비율"
    engaged_sessions: "10초+ 또는 2페이지+ 세션"
    avg_engagement_time: "평균 참여 시간"
    events_per_session: "세션당 이벤트"

  retention:
    returning_users: "재방문 사용자"
    user_retention: "사용자 유지율"

  monetization:
    total_revenue: "총 수익"
    purchase_revenue: "구매 수익"
    average_purchase_revenue: "평균 구매 금액"
```

## 어트리뷰션 모델

### GA4 기본 설정

```yaml
attribution_models:
  data_driven:
    description: "GA4 기본 권장"
    how_it_works: "머신러닝 기반 기여도 분배"
    best_for: "충분한 데이터 (1000+ 전환/월)"

  last_click:
    description: "마지막 클릭에 100% 기여"
    best_for: "즉시 구매 패턴"

  first_click:
    description: "첫 클릭에 100% 기여"
    best_for: "인지도 캠페인 평가"

  linear:
    description: "모든 터치포인트 균등 배분"
    best_for: "고객 여정 전체 이해"

  position_based:
    description: "첫/마지막 40%, 중간 20%"
    best_for: "균형잡힌 분석"

  time_decay:
    description: "전환에 가까울수록 높은 기여"
    best_for: "짧은 구매 사이클"
```

### Lookback Window

```yaml
lookback_window:
  acquisition:
    default: "30일"
    options: ["7일", "30일", "90일"]

  other_conversions:
    default: "90일"
    options: ["30일", "60일", "90일"]
```

## 트래픽 분석

### 채널 그룹

```yaml
channel_groups:
  organic_search:
    description: "검색엔진 자연 유입"
    key_metrics:
      - landing_pages
      - keywords (Search Console 연동)
      - bounce_rate
    optimization: "SEO 콘텐츠 강화"

  paid_search:
    description: "검색 광고"
    key_metrics:
      - cost
      - cpc
      - roas
    optimization: "키워드 최적화, 랜딩 페이지"

  organic_social:
    description: "SNS 자연 유입"
    key_metrics:
      - referral_source
      - engagement_rate
    optimization: "콘텐츠 전략"

  paid_social:
    description: "SNS 광고"
    key_metrics:
      - campaign_performance
      - audience_segments
    optimization: "타겟팅 정교화"

  direct:
    description: "직접 방문"
    key_metrics:
      - returning_users
      - brand_awareness_proxy
    optimization: "브랜드 인지도"

  referral:
    description: "타 사이트 링크"
    key_metrics:
      - referring_sites
      - quality_score
    optimization: "파트너십, 백링크"

  email:
    description: "이메일 마케팅"
    key_metrics:
      - campaign_id
      - conversion_rate
    optimization: "세그먼트, 개인화"
```

### UTM 파라미터

```yaml
utm_parameters:
  structure:
    utm_source: "트래픽 출처 (google, facebook, newsletter)"
    utm_medium: "매체 유형 (cpc, email, social)"
    utm_campaign: "캠페인명 (spring_sale, launch_2026)"
    utm_term: "유료 검색 키워드 (선택)"
    utm_content: "광고 변형 구분 (선택)"

  naming_convention:
    rules:
      - lowercase_only: true
      - use_underscores: true  # 공백 대신
      - consistent_format: "YYYY_MM_campaigntype_name"

    examples:
      good:
        - "?utm_source=twitter&utm_medium=social&utm_campaign=2026_01_product_launch"
      bad:
        - "?utm_source=Twitter&utm_medium=Social Media&utm_campaign=Launch!"

  url_builder: |
    # UTM URL 생성 예시
    base_url = "https://example.com/pricing"
    utm = {
      source: "linkedin",
      medium: "social",
      campaign: "2026_01_saas_guide"
    }
    # → https://example.com/pricing?utm_source=linkedin&utm_medium=social&utm_campaign=2026_01_saas_guide
```

## 전환 추적

### 전환 이벤트 설정

```yaml
conversion_events:
  saas_funnel:
    stage_1_visit:
      event: "page_view"
      page: "/pricing"

    stage_2_signup:
      event: "sign_up"
      parameters:
        method: "email|google|github"

    stage_3_trial_start:
      event: "begin_trial"
      parameters:
        plan: "pro|enterprise"

    stage_4_purchase:
      event: "purchase"
      parameters:
        value: "금액"
        currency: "KRW|USD"
        items: "구매 항목"

  tracking_code: |
    // 가입 이벤트
    gtag('event', 'sign_up', {
      method: 'email'
    });

    // 구매 이벤트
    gtag('event', 'purchase', {
      transaction_id: 'T_12345',
      value: 29000,
      currency: 'KRW',
      items: [{
        item_id: 'pro_monthly',
        item_name: 'Pro Plan',
        price: 29000
      }]
    });
```

### 전환 퍼널 분석

```yaml
funnel_analysis:
  closed_funnel:
    description: "순서대로 진행해야 하는 퍼널"
    example:
      - step_1: "랜딩페이지 조회"
      - step_2: "가격 페이지 조회"
      - step_3: "가입 시작"
      - step_4: "가입 완료"
      - step_5: "첫 결제"

  open_funnel:
    description: "순서 상관없이 분석"
    use_case: "사용자 행동 패턴 발견"

  metrics:
    - completion_rate: "퍼널 완료율"
    - drop_off_rate: "단계별 이탈률"
    - avg_time_to_convert: "전환까지 평균 시간"
```

## 리포트 템플릿

### 주간 트래픽 리포트

```yaml
weekly_traffic_report:
  period: "월~일"

  sections:
    overview:
      metrics:
        - total_users
        - new_users
        - sessions
        - engagement_rate
      comparison: "전주 대비"

    channel_breakdown:
      dimensions: ["channel_group"]
      metrics: ["users", "sessions", "conversions"]

    top_pages:
      dimensions: ["page_path"]
      metrics: ["pageviews", "avg_time", "bounce_rate"]
      limit: 10

    conversions:
      events: ["sign_up", "purchase"]
      metrics: ["count", "conversion_rate", "value"]

    insights:
      - "트래픽 변화 원인 분석"
      - "개선 기회 식별"
      - "다음 주 액션 아이템"
```

### 월간 마케팅 리포트

```yaml
monthly_marketing_report:
  sections:
    executive_summary:
      - "핵심 지표 요약"
      - "목표 대비 달성률"
      - "주요 성과/이슈"

    acquisition:
      - channel_performance
      - campaign_roi
      - cac_by_channel

    engagement:
      - content_performance
      - user_behavior_flow
      - retention_cohort

    conversion:
      - funnel_analysis
      - conversion_rate_trend
      - revenue_attribution

    recommendations:
      - "다음 달 액션 아이템"
      - "예산 재배분 제안"
      - "테스트 아이디어"
```

## CLI 사용법

```bash
# 트래픽 요약
/ga4 summary --period 7d

# 채널별 성과
/ga4 channels --period 30d

# 전환 분석
/ga4 conversions --event purchase --period 30d

# 페이지 성과
/ga4 pages --metric pageviews --limit 20

# 커스텀 리포트
/ga4 report --template weekly_traffic

# 실시간 현황
/ga4 realtime

# 목표 대비 현황
/ga4 goals --period mtd
```

## API 연동 (선택)

### GA4 Data API

```yaml
ga4_api:
  authentication:
    method: "Service Account"
    setup:
      - Google Cloud Console에서 프로젝트 생성
      - GA4 Data API 활성화
      - Service Account 생성
      - GA4 속성에 권한 부여

  python_example: |
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import RunReportRequest

    client = BetaAnalyticsDataClient()

    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[{"start_date": "7daysAgo", "end_date": "today"}],
        dimensions=[{"name": "sessionSource"}],
        metrics=[{"name": "sessions"}, {"name": "conversions"}]
    )

    response = client.run_report(request)
```

## 출력 포맷

### 주간 리포트

```json
{
  "report_type": "weekly_traffic",
  "period": "2026-01-20 ~ 2026-01-26",
  "generated_at": "2026-01-27T09:00:00Z",

  "summary": {
    "total_users": 12500,
    "change_vs_prev": "+15.2%",
    "new_users": 8200,
    "sessions": 18500,
    "engagement_rate": "62.3%",
    "avg_engagement_time": "2m 45s"
  },

  "channels": [
    {
      "channel": "Organic Search",
      "users": 5200,
      "share": "41.6%",
      "change": "+22.1%",
      "conversions": 156,
      "cvr": "3.0%"
    },
    {
      "channel": "Direct",
      "users": 3100,
      "share": "24.8%",
      "change": "+8.5%"
    },
    {
      "channel": "Social",
      "users": 2400,
      "share": "19.2%",
      "change": "+45.2%"
    }
  ],

  "top_pages": [
    {
      "page": "/blog/saas-payment-guide",
      "pageviews": 3200,
      "avg_time": "4m 12s",
      "bounce_rate": "35%"
    }
  ],

  "conversions": {
    "sign_up": {
      "count": 312,
      "change": "+18.5%",
      "rate": "2.5%"
    },
    "purchase": {
      "count": 45,
      "value": 1305000,
      "change": "+12.3%"
    }
  },

  "insights": [
    {
      "type": "positive",
      "message": "Organic Search 트래픽 22% 증가 - SEO 콘텐츠 전략 효과"
    },
    {
      "type": "positive",
      "message": "Social 트래픽 45% 급증 - 'SaaS 결제 가이드' 포스트 바이럴"
    },
    {
      "type": "action",
      "message": "Social 트래픽 전환율(1.2%)이 낮음 - 랜딩페이지 최적화 필요"
    }
  ],

  "recommendations": [
    "Social 트래픽용 전용 랜딩페이지 A/B 테스트",
    "인기 콘텐츠 '결제 가이드' 시리즈화",
    "Organic Search 성과 키워드 추가 콘텐츠 제작"
  ]
}
```

### 전환 퍼널 분석

```json
{
  "report_type": "conversion_funnel",
  "funnel_name": "Trial to Paid",
  "period": "2026-01",

  "stages": [
    {
      "step": 1,
      "name": "가격 페이지 조회",
      "users": 5000,
      "rate": "100%"
    },
    {
      "step": 2,
      "name": "트라이얼 시작",
      "users": 750,
      "rate": "15%",
      "drop_off": "85%"
    },
    {
      "step": 3,
      "name": "핵심 기능 사용",
      "users": 450,
      "rate": "60%",
      "drop_off": "40%"
    },
    {
      "step": 4,
      "name": "결제 완료",
      "users": 180,
      "rate": "40%",
      "drop_off": "60%"
    }
  ],

  "overall_conversion": "3.6%",
  "avg_time_to_convert": "5.2 days",

  "bottleneck_analysis": {
    "biggest_drop": "가격 페이지 → 트라이얼 (85% 이탈)",
    "hypothesis": [
      "가격이 명확하지 않음",
      "트라이얼 가입 장벽 높음",
      "가치 제안 부족"
    ],
    "recommended_tests": [
      "가격 페이지 레이아웃 A/B 테스트",
      "소셜 로그인 추가",
      "트라이얼 혜택 강조"
    ]
  }
}
```

## 자동화 설정

```yaml
automation:
  # 주간 리포트 자동 생성
  weekly_report:
    schedule: "0 9 * * 1"  # 매주 월요일 9시
    action:
      - generate_report: "weekly_traffic"
      - send_to: ["slack:#marketing", "email:team@"]

  # 이상 감지 알림
  anomaly_alerts:
    traffic_drop:
      threshold: "-20%"  # 전일 대비 20% 이상 하락
      action: "slack_alert"

    conversion_spike:
      threshold: "+50%"
      action: "celebrate_and_analyze"

  # 목표 추적
  goal_tracking:
    monthly_signup_target: 1000
    alert_at: ["50%", "75%", "90%", "100%"]
```

---

Version: 1.0.0
Last Updated: 2026-01-27
