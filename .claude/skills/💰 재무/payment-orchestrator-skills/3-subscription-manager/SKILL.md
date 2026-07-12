---
name: subscription-manager
description: 구독 라이프사이클 관리 및 플랜 변경 스킬
model: inherit
quality_tier: fast_scan
triggers:
  - "구독"
  - "플랜"
  - "업그레이드"
  - "다운그레이드"
  - "subscription"
---

# Subscription Manager Skill

구독 라이프사이클을 통합 관리하는 스킬입니다.

## 핵심 원칙

- **통합 관리**: Lemon Squeezy + 포트원 구독 통합
- **자동화**: 플랜 변경, 갱신, 취소 자동 처리
- **분석**: 이탈 예측, 확장 기회 식별

## 구독 상태 머신

```
┌─────────────────────────────────────────────────────────────────┐
│                   Subscription State Machine                     │
└─────────────────────────────────────────────────────────────────┘

          ┌──────────┐
          │  Trial   │ ← 시작
          └────┬─────┘
               │ 결제 성공
               ▼
          ┌──────────┐
     ┌───▶│  Active  │◀───┐
     │    └────┬─────┘    │
     │         │          │
     │    결제 실패    갱신 성공
     │         │          │
     │         ▼          │
     │    ┌──────────┐    │
     │    │ Past Due │────┘
     │    └────┬─────┘
     │         │ 복구 실패
     │         ▼
     │    ┌──────────┐
     │    │ Cancelled│
     │    └────┬─────┘
     │         │ 재구독
     └─────────┘

  ┌──────────┐
  │  Paused  │ ← 일시정지 (Active에서)
  └──────────┘
```

## 데이터 구조

### 구독 레코드

```json
{
  "subscription_id": "sub_xxx",
  "provider": "lemon_squeezy",  // or "portone"
  "external_id": "ls_sub_123",  // 외부 시스템 ID

  "customer": {
    "id": "cust_xxx",
    "email": "user@example.com",
    "name": "홍길동"
  },

  "plan": {
    "id": "plan_pro",
    "name": "Pro",
    "price": 29000,
    "currency": "KRW",
    "interval": "month",
    "features": ["unlimited_projects", "priority_support"]
  },

  "status": "active",
  "trial_ends_at": null,
  "current_period_start": "2026-01-01T00:00:00Z",
  "current_period_end": "2026-02-01T00:00:00Z",
  "cancel_at_period_end": false,

  "billing": {
    "method": "card",
    "card_last_four": "1234",
    "card_brand": "visa",
    "billing_key": "bk_xxx"  // 포트원 빌링키
  },

  "metadata": {
    "source": "website",
    "campaign": "launch_promo",
    "referrer": "ref_abc"
  },

  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-27T00:00:00Z"
}
```

### 플랜 정의

```yaml
plans:
  free:
    id: "plan_free"
    name: "Free"
    price: 0
    interval: null
    features:
      - 기본 기능
      - 1 프로젝트
      - 커뮤니티 지원
    limits:
      projects: 1
      storage_mb: 100
      api_calls_day: 100

  pro:
    id: "plan_pro"
    name: "Pro"
    price:
      krw: 29000
      usd: 19
    interval: "month"
    annual_discount: 0.17  # 2개월 무료
    features:
      - 모든 기능
      - 무제한 프로젝트
      - 우선 지원
      - API 액세스
    limits:
      projects: unlimited
      storage_mb: 10000
      api_calls_day: 10000

  enterprise:
    id: "plan_enterprise"
    name: "Enterprise"
    price: custom
    interval: "year"
    features:
      - Pro +
      - 전담 지원
      - SLA 보장
      - 온프레미스 옵션
      - 커스텀 연동
    limits:
      projects: unlimited
      storage_mb: unlimited
      api_calls_day: unlimited
```

## 워크플로우

### 1. 신규 구독

```yaml
new_subscription:
  trigger: "webhook.subscription_created"

  steps:
    - name: "구독 레코드 생성"
      action: |
        INSERT INTO subscriptions (...)
        VALUES (webhook_data)

    - name: "사용자 플랜 업데이트"
      action: |
        UPDATE users
        SET plan = 'pro', plan_updated_at = NOW()
        WHERE id = customer_id

    - name: "기능 활성화"
      action: |
        CALL activate_plan_features(user_id, 'pro')

    - name: "환영 이메일"
      action: |
        SEND email_template('subscription_welcome', {
          user: customer,
          plan: plan_details
        })

    - name: "Slack 알림"
      action: |
        NOTIFY slack_channel('#revenue', {
          message: "🎉 새 Pro 구독: {customer.email}"
        })

    - name: "MRR 업데이트"
      action: |
        UPDATE mrr_history
        SET new_mrr = new_mrr + plan.price
        WHERE month = CURRENT_MONTH
```

### 2. 플랜 업그레이드

```yaml
upgrade_subscription:
  trigger: "user.request_upgrade"

  proration:
    # 비례 계산 (일할 계산)
    formula: |
      remaining_days = period_end - today
      daily_rate_old = old_plan.price / days_in_period
      daily_rate_new = new_plan.price / days_in_period

      credit = remaining_days * daily_rate_old
      charge = remaining_days * daily_rate_new
      proration_amount = charge - credit

  steps:
    - name: "비례 금액 계산"
      action: calculate_proration()

    - name: "즉시 결제"
      action: |
        IF proration_amount > 0:
          charge_customer(proration_amount)

    - name: "플랜 변경"
      action: |
        UPDATE subscriptions
        SET plan_id = new_plan.id,
            price = new_plan.price

    - name: "기능 업그레이드"
      action: activate_plan_features(user_id, new_plan)

    - name: "확인 이메일"
      action: send_upgrade_confirmation()
```

### 3. 구독 취소

```yaml
cancel_subscription:
  trigger: "user.request_cancel"

  retention_flow:
    step_1_reason:
      prompt: "취소 사유를 알려주세요"
      options:
        - "가격이 비싸요"
        - "필요한 기능이 없어요"
        - "다른 서비스로 이동해요"
        - "일시적으로 사용 안 해요"
        - "기타"

    step_2_offer:
      conditions:
        - reason: "가격이 비싸요"
          offer: "3개월 50% 할인"
        - reason: "일시적으로 사용 안 해요"
          offer: "3개월 무료 일시정지"
        - default:
          offer: null

    step_3_confirm:
      if_accepted_offer:
        action: apply_offer()
      if_declined:
        action: proceed_with_cancellation()

  cancellation_steps:
    - name: "취소 예약"
      action: |
        UPDATE subscriptions
        SET cancel_at_period_end = true,
            cancellation_reason = reason

    - name: "확인 이메일"
      action: send_cancellation_confirmation()

    - name: "피드백 수집"
      action: create_feedback_survey()

    - name: "Churn 기록"
      action: |
        INSERT INTO churn_events (...)
```

### 4. 갱신 처리

```yaml
renewal_process:
  schedule: "0 0 * * *"  # 매일 자정

  steps:
    - name: "만료 예정 구독 조회"
      query: |
        SELECT * FROM subscriptions
        WHERE current_period_end <= NOW() + INTERVAL '1 day'
          AND status = 'active'
          AND cancel_at_period_end = false

    - name: "결제 실행"
      for_each: subscription
      action: |
        IF provider == 'lemon_squeezy':
          # Lemon Squeezy가 자동 처리
          pass
        ELIF provider == 'portone':
          # 빌링키로 결제
          charge_billing_key(subscription.billing.billing_key)

    - name: "성공 처리"
      on_success:
        - extend_period()
        - send_receipt()
        - update_mrr()

    - name: "실패 처리"
      on_failure:
        - mark_as_past_due()
        - start_dunning_sequence()
```

## CLI 사용법

```bash
# 구독 목록
/subscription list [--status active|cancelled|past_due]

# 구독 상세
/subscription get {subscription_id}

# 플랜 변경
/subscription upgrade {subscription_id} --plan pro
/subscription downgrade {subscription_id} --plan free

# 구독 취소
/subscription cancel {subscription_id} [--immediately]

# 구독 일시정지
/subscription pause {subscription_id} --until 2026-03-01

# 구독 재개
/subscription resume {subscription_id}

# 통계
/subscription stats --month 2026-01
```

## 알림 설정

```yaml
notifications:
  # 갱신 리마인더
  renewal_reminder:
    - days_before: 7
      template: "renewal_reminder_7d"
    - days_before: 3
      template: "renewal_reminder_3d"
    - days_before: 1
      template: "renewal_reminder_1d"

  # 시험 종료 알림
  trial_ending:
    - days_before: 3
      template: "trial_ending_soon"
    - days_before: 1
      template: "trial_ends_tomorrow"

  # 결제 수단 만료
  card_expiring:
    - days_before: 30
      template: "card_expiring_soon"
    - days_before: 7
      template: "card_expires_soon"
```

## 출력 포맷

```json
{
  "command": "subscription_stats",
  "period": "2026-01",
  "summary": {
    "total_subscriptions": 150,
    "active": 120,
    "trial": 15,
    "past_due": 10,
    "cancelled": 5
  },
  "changes": {
    "new_subscriptions": 25,
    "upgrades": 8,
    "downgrades": 2,
    "cancellations": 5,
    "reactivations": 3
  },
  "mrr_impact": {
    "starting_mrr": 4200000,
    "new_mrr": 725000,
    "expansion_mrr": 200000,
    "contraction_mrr": -50000,
    "churned_mrr": -150000,
    "ending_mrr": 4925000,
    "net_mrr_change": 725000,
    "growth_rate": "17.3%"
  }
}
```

---

Version: 1.0.0
Last Updated: 2026-01-27
