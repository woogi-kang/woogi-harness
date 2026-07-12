---
name: tax-calendar
description: 한국 법인 세무 일정 관리 및 알림 스킬
model: inherit
quality_tier: fast_scan
triggers:
  - "세금 일정"
  - "신고"
  - "납부"
  - "tax calendar"
---

# Tax Calendar Skill

한국 법인의 세무 일정을 관리하고 리마인더를 제공하는 스킬입니다.

## 핵심 원칙

- **기한 준수**: 신고/납부 기한 사전 알림
- **자동화 연동**: 팝빌, CODEF 등 자동 신고 연동
- **벌금 방지**: 기한 도과 시 가산세 경고

## 연간 세무 캘린더 (2026년)

```
┌─────────────────────────────────────────────────────────────────┐
│                    2026년 세무 캘린더                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   📅 1월                                                        │
│   ├── 10일: 원천세 신고/납부 (12월분)                            │
│   ├── 25일: 부가세 확정신고 (2기)                                │
│   └── 31일: 면세사업자 사업장현황신고                             │
│                                                                 │
│   📅 2월                                                        │
│   ├── 10일: 원천세 신고/납부 (1월분)                             │
│   └── 28일: 연말정산 (지급명세서 제출)                            │
│                                                                 │
│   📅 3월                                                        │
│   ├── 10일: 원천세 신고/납부 (2월분)                             │
│   ├── 31일: 12월 결산법인 법인세 신고 ⭐                          │
│   └── 31일: 법인지방소득세 신고                                   │
│                                                                 │
│   📅 4월                                                        │
│   ├── 10일: 원천세 신고/납부 (3월분)                             │
│   └── 25일: 부가세 예정신고 (1기)                                │
│                                                                 │
│   📅 5월                                                        │
│   ├── 10일: 원천세 신고/납부 (4월분)                             │
│   └── 31일: 종합소득세 신고 (대표자 개인)                         │
│                                                                 │
│   📅 6월                                                        │
│   └── 10일: 원천세 신고/납부 (5월분)                             │
│                                                                 │
│   📅 7월                                                        │
│   ├── 10일: 원천세 신고/납부 (6월분)                             │
│   └── 25일: 부가세 확정신고 (1기) ⭐                              │
│                                                                 │
│   📅 8월                                                        │
│   ├── 10일: 원천세 신고/납부 (7월분)                             │
│   └── 31일: 법인세 중간예납 (12월 결산법인)                       │
│                                                                 │
│   📅 9월                                                        │
│   └── 10일: 원천세 신고/납부 (8월분)                             │
│                                                                 │
│   📅 10월                                                       │
│   ├── 10일: 원천세 신고/납부 (9월분)                             │
│   └── 25일: 부가세 예정신고 (2기)                                │
│                                                                 │
│   📅 11월                                                       │
│   └── 10일: 원천세 신고/납부 (10월분)                            │
│                                                                 │
│   📅 12월                                                       │
│   └── 10일: 원천세 신고/납부 (11월분)                            │
│                                                                 │
│   ⭐ = 주요 신고 (세무사 검토 권장)                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 세무 일정 데이터

```yaml
tax_events:
  # 원천세 (매월)
  - name: "원천세 신고/납부"
    frequency: "monthly"
    due_day: 10
    auto_capable: true
    service: "국세청 홈택스"
    penalty: "미납세액 × 3%/월"

  # 부가세 (분기)
  - name: "부가세 예정신고"
    frequency: "quarterly"
    due_months: [4, 10]
    due_day: 25
    auto_capable: true
    service: "팝빌 API"
    penalty: "미납세액 × 무신고가산세 20%"

  - name: "부가세 확정신고"
    frequency: "semi-annual"
    due_months: [1, 7]
    due_day: 25
    auto_capable: true
    service: "팝빌 API"
    penalty: "미납세액 × 무신고가산세 20%"

  # 법인세 (연간)
  - name: "법인세 신고"
    frequency: "annual"
    due_month: 3
    due_day: 31
    auto_capable: false
    requires: "세무사 검토"
    penalty: "미납세액 × 무신고가산세 20% + 납부불성실가산세"

  # 연말정산 (연간)
  - name: "연말정산"
    frequency: "annual"
    due_month: 2
    due_day: 28
    auto_capable: "partial"
    service: "MetaPay, flex"
    penalty: "지급명세서 미제출 가산세 2%"
```

## 알림 설정

```yaml
reminders:
  # 사전 알림
  - days_before: 14
    severity: "info"
    message: "📅 {event_name} D-14"

  - days_before: 7
    severity: "warning"
    message: "⚠️ {event_name} D-7 - 준비 상태 확인 필요"

  - days_before: 3
    severity: "critical"
    message: "🔴 {event_name} D-3 - 최종 확인!"

  - days_before: 1
    severity: "urgent"
    message: "🚨 {event_name} 내일 마감!"

  # 자동 처리 상태
  auto_status:
    - on_complete: "✅ {event_name} 자동 처리 완료"
    - on_fail: "❌ {event_name} 자동 처리 실패 - 수동 확인 필요"
```

## 자동화 연동

### 원천세 자동 신고

```yaml
automation:
  withholding_tax:
    service: "홈택스"
    method: "Playwright 자동화"
    data_source: "급여 시스템 (flex/시프티)"
    steps:
      1: "급여 데이터 집계"
      2: "원천징수이행상황신고서 작성"
      3: "홈택스 제출"
      4: "납부서 생성"
      5: "결과 알림"
```

### 부가세 자동 신고

```yaml
automation:
  vat:
    service: "팝빌 API"
    method: "API 호출"
    data_source: "세금계산서 (매출/매입)"
    steps:
      1: "매출 세금계산서 집계"
      2: "매입 세금계산서 집계"
      3: "부가세 신고서 생성"
      4: "팝빌 API로 제출"
      5: "결과 알림"
```

## CLI 사용법

```bash
# 이번 달 세무 일정
/tax-calendar month

# 다음 7일 일정
/tax-calendar upcoming --days 7

# 연간 캘린더
/tax-calendar year 2026

# 특정 세금 상세
/tax-calendar detail --type 부가세

# 리마인더 설정
/tax-calendar reminder --event "법인세" --days 14,7,3,1
```

## 출력 포맷

```json
{
  "today": "2026-01-27",
  "upcoming_events": [
    {
      "name": "부가세 확정신고 (2기)",
      "due_date": "2026-01-25",
      "status": "completed",
      "auto_processed": true,
      "result": "success"
    },
    {
      "name": "면세사업자 사업장현황신고",
      "due_date": "2026-01-31",
      "days_remaining": 4,
      "status": "pending",
      "auto_capable": false,
      "action_required": "세무사 확인 필요"
    },
    {
      "name": "원천세 신고/납부",
      "due_date": "2026-02-10",
      "days_remaining": 14,
      "status": "scheduled",
      "auto_capable": true,
      "data_ready": true
    }
  ],
  "alerts": [
    {
      "severity": "warning",
      "message": "면세사업자 신고 D-4 - 세무사 제출 서류 확인"
    }
  ]
}
```

## 가산세 계산

```yaml
penalty_calculator:
  무신고가산세:
    rate: 0.20  # 20%
    base: "납부세액"

  과소신고가산세:
    rate: 0.10  # 10%
    base: "과소신고세액"

  납부불성실가산세:
    rate: 0.00025  # 일 0.025%
    base: "미납세액"
    max_days: 365

  example:
    미납세액: 1000000
    지연일수: 30
    무신고가산세: 200000
    납부불성실가산세: 7500
    총_가산세: 207500
```

---

Version: 1.0.0
Last Updated: 2026-01-27
