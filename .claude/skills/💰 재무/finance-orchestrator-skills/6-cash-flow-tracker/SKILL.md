---
name: cash-flow-tracker
description: 현금흐름 추적 및 런웨이 분석 스킬
model: inherit
quality_tier: fast_scan
triggers:
  - "현금흐름"
  - "런웨이"
  - "캐시플로우"
  - "cash flow"
---

# Cash Flow Tracker Skill

현금흐름을 추적하고 런웨이를 분석하는 스킬입니다.

## 핵심 원칙

- **런웨이 모니터링**: 현재 자금으로 운영 가능한 기간
- **예측**: 3-6개월 현금흐름 예측
- **사전 경고**: 자금 부족 사전 알림

## 핵심 지표

### 1. 런웨이 (Runway)

```
런웨이 = 현금 잔액 / 월평균 순 소진율 (Net Burn Rate)

예시:
- 현금 잔액: ₩150,000,000
- 월 수입: ₩50,000,000
- 월 지출: ₩40,000,000
- Net Burn: -₩10,000,000 (흑자)
- 런웨이: ∞ (수익성 달성)

또는:
- 현금 잔액: ₩150,000,000
- 월 수입: ₩30,000,000
- 월 지출: ₩40,000,000
- Net Burn: ₩10,000,000 (적자)
- 런웨이: 15개월
```

### 2. Burn Multiple

```
Burn Multiple = 순 소진액 / 순 신규 ARR

<1.0x = 매우 효율적 (유니콘 수준)
1.0-2.0x = 효율적
2.0-3.0x = 보통
>3.0x = 비효율적 (개선 필요)
```

## 대시보드

```
┌─────────────────────────────────────────────────────────────────┐
│                    Cash Flow Dashboard                           │
│                    2026년 1월 27일 현재                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   💰 현금 잔액                                                   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │              ₩ 150,000,000                              │   │
│   │              전월 대비 +₩10,000,000 (+7.1%)             │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   📊 월간 현금 흐름                                              │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │   수입        ₩ 50,000,000   ████████████████  100%    │   │
│   │   지출        ₩ 40,000,000   ████████████      80%     │   │
│   │   ─────────────────────────────────────────────────     │   │
│   │   순 흐름    +₩ 10,000,000   (흑자!)                    │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   🎯 핵심 지표                                                   │
│   ┌────────────┬────────────┬────────────┬────────────┐        │
│   │  런웨이    │ Burn Mult. │ 현금 회전  │ AR Days   │        │
│   │    ∞      │   -0.3x   │    45일    │   32일    │        │
│   │  (흑자)   │  (수익성)  │           │           │        │
│   └────────────┴────────────┴────────────┴────────────┘        │
│                                                                 │
│   📈 6개월 예측                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  Feb   Mar   Apr   May   Jun   Jul                      │   │
│   │  160M  170M  180M  190M  200M  210M  (낙관적 시나리오)  │   │
│   │  155M  160M  165M  170M  175M  180M  (기본 시나리오)    │   │
│   │  150M  145M  140M  135M  130M  125M  (보수적 시나리오)  │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   ⚠️ 알림: 없음 (재정 건전)                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 예측 모델

### 시나리오 분석

```yaml
scenarios:
  optimistic:
    revenue_growth: 0.15  # 월 15% 성장
    expense_growth: 0.05  # 월 5% 증가
    probability: 0.25

  base:
    revenue_growth: 0.08  # 월 8% 성장
    expense_growth: 0.05  # 월 5% 증가
    probability: 0.50

  conservative:
    revenue_growth: 0.00  # 성장 없음
    expense_growth: 0.05  # 월 5% 증가
    probability: 0.25
```

### 예측 수식

```python
def forecast_cash(months: int, scenario: str) -> List[float]:
    """
    현금 잔액 예측

    Args:
        months: 예측 기간
        scenario: optimistic/base/conservative

    Returns:
        월별 예상 현금 잔액
    """
    params = SCENARIOS[scenario]
    cash = current_cash
    forecasts = []

    for m in range(months):
        revenue = current_revenue * (1 + params['revenue_growth']) ** m
        expense = current_expense * (1 + params['expense_growth']) ** m
        net_flow = revenue - expense
        cash += net_flow
        forecasts.append(cash)

    return forecasts
```

## 알림 설정

```yaml
alerts:
  runway_warning:
    threshold: 6  # 6개월 이하
    severity: "warning"
    message: "⚠️ 런웨이 {months}개월 - 자금 확보 계획 검토 필요"

  runway_critical:
    threshold: 3  # 3개월 이하
    severity: "critical"
    message: "🔴 런웨이 {months}개월 - 즉시 자금 확보 필요!"

  negative_cash_flow:
    threshold: 3  # 3개월 연속
    severity: "warning"
    message: "⚠️ 3개월 연속 현금 순유출 - 비용 구조 검토 필요"

  large_outflow:
    threshold: 0.2  # 현금의 20% 이상 단일 지출
    severity: "info"
    message: "ℹ️ 대규모 지출 감지: {description} (₩{amount})"
```

## 출력 포맷

```json
{
  "snapshot_date": "2026-01-27",
  "cash_position": {
    "current": 150000000,
    "previous_month": 140000000,
    "change": 10000000,
    "change_percent": 7.14
  },
  "monthly_flow": {
    "inflow": 50000000,
    "outflow": 40000000,
    "net_flow": 10000000,
    "is_positive": true
  },
  "metrics": {
    "runway_months": null,
    "runway_status": "profitable",
    "burn_multiple": -0.3,
    "cash_conversion_days": 45,
    "ar_days": 32,
    "ap_days": 28
  },
  "forecast": {
    "base_case": [155000000, 160000000, 165000000, 170000000, 175000000, 180000000],
    "optimistic": [160000000, 170000000, 180000000, 190000000, 200000000, 210000000],
    "conservative": [150000000, 145000000, 140000000, 135000000, 130000000, 125000000]
  },
  "alerts": [],
  "recommendations": [
    "현재 수익성 달성 상태 유지",
    "여유 자금 일부 예치 검토 (MMF, 정기예금)"
  ]
}
```

## CLI 사용법

```bash
# 현재 현금 상태
/cash-flow status

# 런웨이 계산
/cash-flow runway

# 6개월 예측
/cash-flow forecast --months 6

# 시나리오 분석
/cash-flow scenario --type all
```

---

Version: 1.0.0
Last Updated: 2026-01-27
