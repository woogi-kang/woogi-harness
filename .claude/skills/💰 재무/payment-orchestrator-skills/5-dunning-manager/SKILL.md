---
name: dunning-manager
description: 결제 실패 복구 및 이탈 방지 스킬
model: inherit
quality_tier: fast_scan
triggers:
  - "결제 실패"
  - "dunning"
  - "재시도"
  - "복구"
  - "카드 만료"
---

# Dunning Manager Skill

결제 실패를 복구하고 비자발적 이탈(Involuntary Churn)을 방지하는 스킬입니다.

## 핵심 원칙

| 원칙 | 설명 |
|------|------|
| **적시 개입** | 실패 즉시 복구 프로세스 시작 |
| **다단계 접근** | 자동 재시도 → 이메일 → SMS → 수동 |
| **고객 친화적** | 압박 없이 도움 제안 |

## 결제 실패 원인

```yaml
failure_reasons:
  card_issues:
    - insufficient_funds     # 잔액 부족 (가장 흔함)
    - card_declined         # 카드 승인 거절
    - card_expired          # 유효기간 만료
    - invalid_card          # 카드 정보 오류

  bank_issues:
    - bank_declined         # 은행 거절
    - do_not_honor         # 승인 거부
    - fraud_suspected      # 사기 의심

  technical:
    - network_error        # 네트워크 오류
    - gateway_error        # PG사 오류
    - timeout              # 타임아웃
```

## Dunning 시퀀스

```
┌─────────────────────────────────────────────────────────────────┐
│                    Dunning Sequence Timeline                     │
└─────────────────────────────────────────────────────────────────┘

Day 0: 결제 실패
├── [자동] Smart Retry #1 (4시간 후)
├── [이메일] "결제가 실패했습니다" + 업데이트 링크
└── [CRM] 고객 상태: Past Due

Day 1: 재시도 #2
├── [자동] Smart Retry #2 (24시간 후)
└── [인앱] 결제 실패 배너 표시

Day 3: 재시도 #3
├── [자동] Smart Retry #3
├── [이메일] "결제 수단을 확인해주세요"
└── [SMS] 선택적 (고가 플랜)

Day 5: 긴급 알림
├── [이메일] "서비스가 곧 중단됩니다"
├── [인앱] 긴급 모달
└── [고가 고객] 수동 연락 플래그

Day 7: 최종 경고
├── [이메일] "마지막 기회" + 할인 제안 (선택적)
└── [전화] 엔터프라이즈 고객

Day 10: 유예 기간 종료
├── [서비스] 기능 제한 (읽기 전용)
├── [이메일] "서비스가 제한되었습니다"
└── [데이터] 백업 안내

Day 14: 계정 비활성화
├── [구독] 취소 처리
├── [이메일] "계정이 비활성화되었습니다"
├── [데이터] 30일 보관 후 삭제 예정 안내
└── [Churn] 기록

복구 가능 기간: Day 0 ~ Day 30
평균 복구율: 35-50%
```

## Smart Retry 전략

```yaml
smart_retry:
  description: "최적의 시간에 재시도하여 성공률 향상"

  strategies:
    # 잔액 부족 - 월급일 맞춤
    insufficient_funds:
      retry_times:
        - next_business_day_morning  # 다음 영업일 오전
        - first_of_month             # 월초
        - fifteenth_of_month         # 15일
      max_retries: 4

    # 카드 만료 - 갱신 대기
    card_expired:
      action: "request_update"  # 재시도 의미 없음
      retry_after_update: true

    # 일시적 오류
    gateway_error:
      retry_times:
        - 4_hours
        - 12_hours
        - 24_hours
      max_retries: 3

  # 재시도 최적 시간대
  optimal_times:
    weekday:
      - "09:00"  # 출근 후
      - "12:00"  # 점심
      - "18:00"  # 퇴근 후
    weekend:
      - "10:00"
      - "14:00"

  # 지역별 월급일
  payday_by_region:
    korea:
      - 10   # 10일
      - 15   # 15일
      - 25   # 25일
    us:
      - 1
      - 15
```

## 이메일 템플릿

### Day 0: 첫 번째 알림

```yaml
email_day_0:
  subject: "[{app_name}] 결제가 처리되지 않았습니다"

  body: |
    안녕하세요 {customer.name}님,

    {app_name} 구독 결제가 처리되지 않았습니다.

    **결제 정보**
    - 플랜: {plan.name}
    - 금액: {amount}
    - 결제 수단: {card.brand} ****{card.last_four}

    결제 수단을 확인하고 업데이트해주세요:
    [결제 수단 업데이트하기]({update_payment_url})

    문제가 지속되면 언제든 연락주세요.

    감사합니다,
    {app_name} 팀

  cta_button: "결제 수단 업데이트"
  cta_url: "{update_payment_url}"
```

### Day 5: 긴급 알림

```yaml
email_day_5:
  subject: "[긴급] {app_name} 서비스가 곧 중단됩니다"

  body: |
    안녕하세요 {customer.name}님,

    결제가 계속 실패하고 있어 서비스가 {grace_period_end}에
    중단될 예정입니다.

    **조치가 필요합니다**

    지금 결제 수단을 업데이트하시면 중단 없이
    서비스를 계속 이용하실 수 있습니다.

    [지금 업데이트하기]({update_payment_url})

    데이터는 안전하게 보관되어 있으며, 결제가 완료되면
    즉시 모든 기능이 복구됩니다.

    도움이 필요하시면 reply로 답장해주세요.

    {app_name} 팀
```

### Day 7: 최종 경고 + 할인 제안

```yaml
email_day_7:
  subject: "[마지막 기회] {discount}% 할인으로 계속 이용하세요"

  condition: "high_value_customer OR long_tenure"

  body: |
    안녕하세요 {customer.name}님,

    {tenure_months}개월간 함께해주셔서 감사합니다.

    결제 문제로 서비스가 중단되기 전에,
    특별히 **{discount}% 할인**을 제안드립니다.

    - 기존 금액: {original_price}
    - 할인 금액: {discounted_price}
    - 적용 기간: {discount_duration}

    [할인 적용하고 계속 이용하기]({discount_url})

    이 제안은 {offer_expires}까지 유효합니다.

    {app_name} 팀
```

## 인앱 알림

```yaml
in_app_notifications:
  # 상단 배너
  top_banner:
    type: "warning"
    message: "결제가 실패했습니다. 결제 수단을 확인해주세요."
    cta: "지금 확인"
    dismissible: false

  # 모달 (긴급)
  urgent_modal:
    trigger: "day >= 5"
    title: "결제 업데이트 필요"
    message: |
      서비스가 {days_until_suspension}일 후 중단됩니다.
      지금 결제 수단을 업데이트해주세요.
    primary_cta: "업데이트"
    secondary_cta: "나중에"
    show_once_per_session: true
```

## 복구 메트릭

```yaml
recovery_metrics:
  # 추적 지표
  tracked:
    - initial_failure_count    # 총 실패 건수
    - recovered_count          # 복구 건수
    - recovery_rate            # 복구율
    - avg_recovery_time        # 평균 복구 시간
    - recovery_by_method       # 방법별 복구

  # 벤치마크
  benchmarks:
    overall_recovery_rate: "35-50%"
    auto_retry_recovery: "20-30%"
    email_recovery: "10-15%"
    manual_outreach: "5-10%"

  # 목표
  targets:
    recovery_rate: "> 40%"
    avg_recovery_time: "< 5 days"
```

## CLI 사용법

```bash
# 실패 건 목록
/dunning list [--status pending|recovered|churned]

# 특정 고객 상태
/dunning status {customer_id}

# 수동 재시도
/dunning retry {payment_id}

# 유예 기간 연장
/dunning extend {subscription_id} --days 7

# 복구 리포트
/dunning report --month 2026-01

# 알림 수동 발송
/dunning notify {customer_id} --type email
```

## 설정

```yaml
config:
  grace_period_days: 14

  retry_schedule:
    - delay: "4h"
    - delay: "24h"
    - delay: "72h"
    - delay: "120h"

  email_schedule:
    - day: 0
      template: "payment_failed"
    - day: 3
      template: "payment_reminder"
    - day: 5
      template: "urgent_warning"
    - day: 7
      template: "final_notice"

  sms_enabled: true
  sms_threshold: 100000  # ₩100K 이상 고객

  discount_offer:
    enabled: true
    threshold_tenure_months: 6
    discount_percent: 20
    duration_months: 3
```

## 출력 포맷

```json
{
  "report_type": "dunning_summary",
  "period": "2026-01",

  "summary": {
    "total_failures": 50,
    "recovered": 22,
    "churned": 8,
    "in_progress": 20,
    "recovery_rate": 44.0
  },

  "recovery_by_method": {
    "auto_retry": 12,
    "email_cta": 6,
    "manual_update": 3,
    "phone_outreach": 1
  },

  "mrr_impact": {
    "at_risk_mrr": 1500000,
    "recovered_mrr": 660000,
    "churned_mrr": 240000,
    "pending_mrr": 600000
  },

  "avg_recovery_time_days": 3.2,

  "in_progress": [
    {
      "customer_id": "cust_xxx",
      "email": "user1@example.com",
      "mrr": 29000,
      "days_past_due": 5,
      "retries": 3,
      "last_email": "urgent_warning",
      "next_action": "final_notice (Day 7)"
    }
  ],

  "recommendations": [
    "카드 만료로 인한 실패가 30%입니다. 만료 사전 알림 강화 권장.",
    "금요일 재시도 성공률이 낮습니다. 월요일 재시도로 조정 검토."
  ]
}
```

## 자동화 연동

```yaml
automation:
  # 결제 실패 시 자동 시작
  webhook_trigger:
    event: "payment.failed"
    action: |
      1. dunning_record 생성
      2. smart_retry 스케줄
      3. email_day_0 발송
      4. slack 알림

  # 결제 성공 시 종료
  recovery_trigger:
    event: "payment.succeeded"
    condition: "dunning_record.exists"
    action: |
      1. dunning_record 종료
      2. 감사 이메일 발송
      3. 메트릭 업데이트

  # 일일 점검
  daily_job:
    schedule: "0 9 * * *"
    action: |
      1. 단계별 이메일 발송
      2. 유예 기간 종료 처리
      3. 일일 리포트 생성
```

---

Version: 1.0.0
Last Updated: 2026-01-27
