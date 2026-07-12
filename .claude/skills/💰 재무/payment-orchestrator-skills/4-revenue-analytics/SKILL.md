---
name: revenue-analytics
description: SaaS 수익 지표 분석 및 대시보드 스킬
model: inherit
quality_tier: implementation
triggers:
  - "MRR"
  - "ARR"
  - "매출"
  - "수익"
  - "revenue"
  - "분석"
  - "LTV"
  - "CAC"
---

# Revenue Analytics Skill

SaaS 핵심 수익 지표를 분석하고 대시보드를 제공하는 스킬입니다.

## 핵심 지표

### 1. MRR (Monthly Recurring Revenue)

```yaml
mrr_components:
  new_mrr:
    description: "신규 구독에서 발생한 MRR"
    formula: "SUM(new_subscriptions.price)"

  expansion_mrr:
    description: "업그레이드로 증가한 MRR"
    formula: "SUM(upgrades.price_diff)"

  contraction_mrr:
    description: "다운그레이드로 감소한 MRR"
    formula: "SUM(downgrades.price_diff)"

  churned_mrr:
    description: "이탈로 손실된 MRR"
    formula: "SUM(cancelled.price)"

  reactivation_mrr:
    description: "재활성화로 복구된 MRR"
    formula: "SUM(reactivated.price)"

net_mrr_formula: |
  Net MRR Change = New MRR + Expansion MRR + Reactivation MRR
                   - Contraction MRR - Churned MRR
```

### 2. ARR (Annual Recurring Revenue)

```yaml
arr_calculation:
  simple: "MRR × 12"

  # 연간 구독 포함 시
  accurate: |
    monthly_arr = monthly_subscriptions.sum(price) × 12
    annual_arr = annual_subscriptions.sum(price)
    total_arr = monthly_arr + annual_arr
```

### 3. Churn Rate

```yaml
churn_rates:
  # 고객 이탈률
  customer_churn:
    formula: "Churned Customers / Starting Customers × 100"
    target: "< 5% monthly"

  # MRR 이탈률 (Gross)
  gross_revenue_churn:
    formula: "Churned MRR / Starting MRR × 100"
    target: "< 5% monthly"

  # MRR 순이탈률 (Net)
  net_revenue_churn:
    formula: "(Churned MRR - Expansion MRR) / Starting MRR × 100"
    target: "< 0% (음수 이탈 = 성장)"

  # 연간 환산
  annual_churn:
    formula: "1 - (1 - monthly_churn)^12"
```

### 4. LTV (Lifetime Value)

```yaml
ltv_calculations:
  # 간단한 계산
  simple:
    formula: "ARPU / Monthly Churn Rate"
    example: "$50 / 5% = $1,000"

  # 마진 반영
  with_margin:
    formula: "(ARPU × Gross Margin) / Monthly Churn Rate"
    example: "($50 × 80%) / 5% = $800"

  # 코호트 기반 (정확)
  cohort_based:
    formula: "SUM(Revenue from Cohort) / Cohort Size"
    note: "12개월+ 데이터 필요"
```

### 5. CAC (Customer Acquisition Cost)

```yaml
cac_calculation:
  formula: "Total Sales & Marketing Cost / New Customers"

  components:
    - paid_advertising
    - content_marketing
    - sales_salaries
    - sales_tools
    - events_sponsorships

  # 채널별 CAC
  by_channel:
    organic: "$50"
    paid_search: "$150"
    social_ads: "$200"
    referral: "$30"
```

### 6. LTV:CAC Ratio

```yaml
ltv_cac_ratio:
  formula: "LTV / CAC"

  benchmarks:
    poor: "< 1:1 (돈을 잃고 있음)"
    acceptable: "1-3:1 (수익성 낮음)"
    good: "3-5:1 (건강함)"
    excellent: "> 5:1 (더 투자 가능)"

  target: "> 3:1"
```

### 7. Payback Period

```yaml
payback_period:
  formula: "CAC / (ARPU × Gross Margin)"

  benchmarks:
    excellent: "< 6 months"
    good: "6-12 months"
    acceptable: "12-18 months"
    concerning: "> 18 months"
```

## 대시보드

```
┌─────────────────────────────────────────────────────────────────┐
│                    Revenue Dashboard                             │
│                    2026년 1월 현재                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   💰 핵심 지표                                                   │
│   ┌─────────────┬─────────────┬─────────────┬─────────────┐     │
│   │    MRR      │    ARR      │  Customers  │   ARPU      │     │
│   │  ₩4.9M     │  ₩58.8M    │    150      │  ₩32,700   │     │
│   │  +17.3%    │  +17.3%    │   +20%     │   -2.3%    │     │
│   └─────────────┴─────────────┴─────────────┴─────────────┘     │
│                                                                 │
│   📈 MRR 변화 (이번 달)                                          │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  Starting MRR    ₩4,200,000                             │   │
│   │  ────────────────────────────────────────────────────   │   │
│   │  + New           ₩725,000    ████████████  (+17.3%)    │   │
│   │  + Expansion     ₩200,000    ████          (+4.8%)     │   │
│   │  - Contraction   -₩50,000    ██            (-1.2%)     │   │
│   │  - Churn         -₩150,000   ████          (-3.6%)     │   │
│   │  ────────────────────────────────────────────────────   │   │
│   │  = Ending MRR    ₩4,925,000  (+₩725,000, +17.3%)       │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   🎯 효율성 지표                                                 │
│   ┌────────────┬────────────┬────────────┬────────────┐        │
│   │   LTV      │    CAC     │  LTV:CAC   │  Payback   │        │
│   │  ₩654K    │  ₩150K    │   4.4:1    │  4.6 mo   │        │
│   │   Good    │   Good    │  Healthy  │  Healthy  │        │
│   └────────────┴────────────┴────────────┴────────────┘        │
│                                                                 │
│   📉 Churn 분석                                                  │
│   ┌────────────┬────────────┬────────────┐                     │
│   │ Customer   │ Gross Rev  │  Net Rev   │                     │
│   │   5.0%    │    3.6%   │   -0.5%   │                     │
│   │ (target<5)│ (target<5) │ (negative!)│                     │
│   └────────────┴────────────┴────────────┘                     │
│                                                                 │
│   📊 MRR 트렌드 (6개월)                                          │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  5M │                                            ●      │   │
│   │     │                                    ●              │   │
│   │  4M │                            ●                      │   │
│   │     │                    ●                              │   │
│   │  3M │            ●                                      │   │
│   │     │    ●                                              │   │
│   │  2M │────┼────┼────┼────┼────┼────┼                     │   │
│   │     │ Aug  Sep  Oct  Nov  Dec  Jan                      │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 코호트 분석

```yaml
cohort_analysis:
  # 월별 가입 코호트
  retention_matrix:
    headers: ["코호트", "M0", "M1", "M2", "M3", "M6", "M12"]
    data:
      - ["2025-07", "100%", "90%", "85%", "82%", "75%", "70%"]
      - ["2025-08", "100%", "92%", "88%", "84%", "78%", "-"]
      - ["2025-09", "100%", "91%", "86%", "83%", "-", "-"]
      - ["2025-10", "100%", "93%", "89%", "-", "-", "-"]
      - ["2025-11", "100%", "94%", "-", "-", "-", "-"]
      - ["2025-12", "100%", "-", "-", "-", "-", "-"]

  # 수익 코호트
  revenue_retention:
    headers: ["코호트", "M0", "M1", "M2", "M3", "M6", "M12"]
    data:
      - ["2025-07", "100%", "95%", "98%", "102%", "110%", "115%"]
      # >100% = 확장 수익 (업그레이드)
```

## 예측 모델

```yaml
forecasting:
  # 단순 성장률 기반
  linear:
    formula: "MRR × (1 + avg_growth_rate)^months"
    confidence: "low"

  # 시나리오 기반
  scenarios:
    optimistic:
      assumptions:
        - growth_rate: 20%
        - churn_rate: 3%
        - expansion_rate: 8%
      forecast_6m: "₩10.2M MRR"

    base:
      assumptions:
        - growth_rate: 15%
        - churn_rate: 5%
        - expansion_rate: 5%
      forecast_6m: "₩8.5M MRR"

    conservative:
      assumptions:
        - growth_rate: 10%
        - churn_rate: 7%
        - expansion_rate: 3%
      forecast_6m: "₩6.8M MRR"
```

## CLI 사용법

```bash
# MRR 리포트
/revenue mrr [--month 2026-01]

# MRR 변화 breakdown
/revenue mrr-breakdown --month 2026-01

# ARR 계산
/revenue arr

# Churn 분석
/revenue churn [--period monthly|quarterly]

# LTV/CAC 분석
/revenue unit-economics

# 코호트 분석
/revenue cohort --start 2025-07 --end 2026-01

# 예측
/revenue forecast --months 6 --scenario base

# 전체 대시보드
/revenue dashboard
```

## 외부 연동

### ChartMogul (권장)

```yaml
chartmogul:
  description: "SaaS 수익 분석 전문 도구"
  pricing: "$120K ARR까지 무료"

  setup:
    - name: "API 연결"
      action: |
        chartmogul.configure({
          api_key: CHARTMOGUL_API_KEY
        })

    - name: "데이터 소스 연결"
      sources:
        - Lemon Squeezy (직접 연동)
        - PortOne (커스텀 연동)

    - name: "자동 동기화"
      frequency: "실시간"

  features:
    - MRR/ARR 자동 계산
    - 코호트 분석
    - LTV 계산
    - Churn 분석
    - 예측
```

## 출력 포맷

```json
{
  "report_type": "monthly_revenue",
  "period": "2026-01",
  "generated_at": "2026-01-27T10:00:00Z",

  "summary": {
    "mrr": {
      "amount": 4925000,
      "currency": "KRW",
      "change": 725000,
      "change_percent": 17.3
    },
    "arr": {
      "amount": 59100000,
      "currency": "KRW"
    },
    "customers": {
      "total": 150,
      "new": 25,
      "churned": 5,
      "net_change": 20
    },
    "arpu": {
      "amount": 32833,
      "currency": "KRW"
    }
  },

  "mrr_movement": {
    "starting": 4200000,
    "new": 725000,
    "expansion": 200000,
    "contraction": -50000,
    "churned": -150000,
    "reactivation": 0,
    "ending": 4925000
  },

  "churn": {
    "customer_churn_rate": 5.0,
    "gross_revenue_churn_rate": 3.6,
    "net_revenue_churn_rate": -0.5
  },

  "unit_economics": {
    "ltv": 654000,
    "cac": 150000,
    "ltv_cac_ratio": 4.4,
    "payback_months": 4.6
  },

  "insights": [
    {
      "type": "positive",
      "message": "음수 순이탈률 달성! 확장 MRR이 이탈을 상쇄하고 있습니다."
    },
    {
      "type": "positive",
      "message": "LTV:CAC 4.4:1로 건강한 수준입니다."
    },
    {
      "type": "info",
      "message": "이번 달 신규 고객의 50%가 Referral 채널에서 유입되었습니다."
    }
  ]
}
```

## 알림 설정

```yaml
alerts:
  # MRR 마일스톤
  mrr_milestone:
    thresholds: [1000000, 5000000, 10000000, 50000000]
    message: "🎉 MRR {amount} 달성!"

  # Churn 경고
  churn_alert:
    threshold: 8  # 8% 초과 시
    message: "⚠️ 이번 달 이탈률이 {rate}%로 높습니다."

  # LTV:CAC 경고
  unit_economics_alert:
    threshold: 2  # 2:1 미만 시
    message: "⚠️ LTV:CAC가 {ratio}:1로 낮습니다. CAC 최적화 검토 필요."

  # 대형 이탈
  large_churn:
    threshold: 500000  # ₩500K 이상 MRR 고객 이탈
    message: "🔴 대형 고객 이탈: {customer.name} (MRR: {mrr})"
```

---

Version: 1.0.0
Last Updated: 2026-01-27
