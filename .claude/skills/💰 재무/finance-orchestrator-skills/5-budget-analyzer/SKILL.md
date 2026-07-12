---
name: budget-analyzer
description: 예산 대비 실적 분석 및 알림 스킬
model: inherit
quality_tier: fast_scan
triggers:
  - "예산"
  - "초과"
  - "절감"
  - "budget"
---

# Budget Analyzer Skill

예산 대비 실적을 분석하고 이상치를 탐지하는 스킬입니다.

## 핵심 원칙

- **실시간 모니터링**: 예산 소진율 실시간 추적
- **사전 경고**: 80% 도달 시 경고, 100% 도달 시 알림
- **트렌드 분석**: 월별/분기별 추세 분석

## 예산 구조

```json
{
  "fiscal_year": "2026",
  "total_budget": 100000000,
  "categories": {
    "인건비": {
      "annual": 48000000,
      "monthly": 4000000,
      "warning_threshold": 0.8,
      "critical_threshold": 1.0
    },
    "서버/인프라": {
      "annual": 18000000,
      "monthly": 1500000,
      "warning_threshold": 0.8,
      "critical_threshold": 1.0
    },
    "마케팅": {
      "annual": 24000000,
      "monthly": 2000000,
      "warning_threshold": 0.9,
      "critical_threshold": 1.2
    },
    "소프트웨어/구독": {
      "annual": 6000000,
      "monthly": 500000,
      "warning_threshold": 0.8,
      "critical_threshold": 1.0
    },
    "사무실/운영": {
      "annual": 3600000,
      "monthly": 300000,
      "warning_threshold": 0.8,
      "critical_threshold": 1.0
    },
    "기타": {
      "annual": 400000,
      "monthly": 33333,
      "warning_threshold": 0.8,
      "critical_threshold": 1.5
    }
  }
}
```

## 분석 기능

### 1. 월간 예산 대비 분석

```
┌─────────────────────────────────────────────────────────────────┐
│              2026년 1월 예산 대비 실적                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   카테고리        예산         실적       소진율    상태        │
│   ──────────────────────────────────────────────────────────    │
│   인건비       4,000,000   3,800,000     95%     ⚠️ 경고       │
│   서버/인프라   1,500,000   1,800,000    120%     🔴 초과       │
│   마케팅       2,000,000   1,500,000     75%     ✅ 정상       │
│   소프트웨어     500,000     480,000     96%     ⚠️ 경고       │
│   사무실/운영    300,000     290,000     97%     ⚠️ 경고       │
│   기타          33,333      25,000      75%     ✅ 정상       │
│   ──────────────────────────────────────────────────────────    │
│   합계        8,333,333   7,895,000     95%                    │
│                                                                 │
│   📊 서버비 120% 초과 원인: 트래픽 급증 (MAU 2배 증가)           │
│   💡 권장: 예약 인스턴스 전환으로 30% 절감 가능                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2. YTD (Year-to-Date) 분석

```yaml
ytd_analysis:
  period: "2026-01 ~ 2026-06"
  total_budget: 50000000
  total_spent: 42000000
  burn_rate: 84%
  projection:
    year_end_spend: 84000000
    vs_annual_budget: -16%  # 예산 내
  recommendations:
    - "마케팅 예산 여유분을 Q3 캠페인에 재배분 권장"
    - "서버비 지속 증가 시 클라우드 최적화 검토 필요"
```

### 3. 카테고리별 상세 분석

```bash
claude "다음 데이터로 서버/인프라 비용 상세 분석해줘:

1. 월별 추이 (최근 6개월)
2. 서비스별 breakdown (AWS, GCP, Firebase 등)
3. 비용 증가 원인 분석
4. 최적화 방안 제안

데이터:
$(cat ledger.json | jq '.transactions | map(select(.category == \"서버/인프라\"))')"
```

## 알림 설정

```yaml
alerts:
  slack_channel: "#finance-alerts"

  warning:
    threshold: 0.8  # 80%
    message: "⚠️ {category} 예산 {percent}% 도달 (₩{spent} / ₩{budget})"

  critical:
    threshold: 1.0  # 100%
    message: "🔴 {category} 예산 초과! (₩{spent} / ₩{budget}, {percent}%)"

  weekly_summary:
    day: "MON"
    time: "09:00"
    include:
      - budget_status_all_categories
      - top_3_concerns
      - recommendations
```

## 출력 포맷

```json
{
  "period": "2026-01",
  "analysis_date": "2026-01-27",
  "summary": {
    "total_budget": 8333333,
    "total_spent": 7895000,
    "remaining": 438333,
    "burn_rate": 0.947,
    "status": "warning"
  },
  "categories": [
    {
      "name": "서버/인프라",
      "budget": 1500000,
      "spent": 1800000,
      "remaining": -300000,
      "burn_rate": 1.2,
      "status": "critical",
      "trend": "increasing",
      "mom_change": 0.23,
      "top_vendors": [
        {"name": "AWS", "amount": 1200000},
        {"name": "Firebase", "amount": 400000},
        {"name": "Vercel", "amount": 200000}
      ]
    }
  ],
  "alerts": [
    {
      "severity": "critical",
      "category": "서버/인프라",
      "message": "예산 120% 초과",
      "recommendation": "Reserved Instance 전환 검토"
    }
  ],
  "insights": [
    "MAU 2배 증가로 인한 서버비 증가는 긍정적 지표",
    "마케팅 ROI 분석 결과 CAC 개선됨 ($150 → $120)"
  ]
}
```

## 절감 제안 자동화

```yaml
cost_optimization_rules:
  - trigger: "AWS 비용 > 월 100만원"
    suggestion: "Reserved Instance 또는 Savings Plan 검토"
    potential_savings: "30-40%"

  - trigger: "동일 SaaS 복수 구독"
    suggestion: "구독 통합 검토"
    example: "Notion + Confluence → Notion으로 통합"

  - trigger: "미사용 리소스 탐지"
    suggestion: "유휴 리소스 정리"
    example: "3개월 이상 미사용 S3 버킷"
```

---

Version: 1.0.0
Last Updated: 2026-01-27
