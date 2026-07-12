---
name: regulatory-calendar
description: 등기/세무/규정 기한 관리 및 알림
model: inherit
quality_tier: fast_scan
triggers:
  - "기한"
  - "등기기한"
  - "신고기한"
  - "과태료"
  - "법인캘린더"
  - "컴플라이언스"
---

# Regulatory Calendar Skill

법인 운영에 필요한 등기, 세무, 규정 준수 기한을 관리하고 알림을 제공합니다.

## 핵심 원칙

| 원칙 | 설명 |
|------|------|
| **기한 엄수** | 지연 시 과태료 또는 가산세 |
| **선제적 알림** | 기한 7일, 3일 전 알림 |
| **통합 관리** | 등기 + 세무 + 노무 일원화 |

---

## 등기 기한

### 법정 기한

```yaml
registration_deadlines:
  general_rule:
    deadline: "변경일로부터 14일 이내"
    basis: "상업등기법 제15조"
    where: "본점 소재지 관할 등기소"

  branch_office:
    deadline: "본점 등기 후 14일 이내"

  applicable_changes:
    - "대표이사 변경"
    - "이사/감사 변경"
    - "본점 이전"
    - "자본금 변경"
    - "상호 변경"
    - "목적 변경"
    - "정관 변경 (등기사항)"
    - "지점 설치/이전/폐지"
```

### 과태료

```yaml
registration_penalties:
  대표이사_책임:
    note: "등기 해태는 대표이사 개인에게 과태료"

  금액:
    - period: "14일 이내"
      fine: "0원"
    - period: "14일 ~ 1개월"
      fine: "~30만원"
    - period: "1개월 ~ 3개월"
      fine: "~50만원"
    - period: "3개월 초과"
      fine: "~100만원"

  practical_tip: |
    등기소에서 과태료 통지서가 올 때까지
    과태료가 확정되지 않으며,
    사유서 제출로 감면 가능한 경우도 있음.
```

---

## 세무 기한

### 월별 정기 신고

```yaml
monthly_tax_calendar:
  매월_10일:
    - name: "원천세 신고/납부"
      who: "직원 급여 지급 법인"
      period: "전월분"
      method: "홈택스 전자신고"

    - name: "4대보험료 납부"
      who: "사업장"
      note: "고지서 기준"

  매월_25일:
    - name: "부가세 예정고지 납부"
      who: "예정고지 대상 (직전 납부세액 기준)"
      note: "1/4, 2/4분기"
```

### 분기별 신고

```yaml
quarterly_tax_calendar:
  1월_25일:
    - name: "부가세 확정신고"
      period: "직전년도 2기 (7-12월)"
      who: "일반과세자"

  3월_31일:
    - name: "법인세 신고"
      period: "직전 사업연도"
      who: "12월 결산 법인"
      note: "성실신고확인서 대상은 4월 30일"

  4월_25일:
    - name: "부가세 예정신고"
      period: "1기 예정 (1-3월)"
      who: "일반과세자"
      note: "예정고지 갈음 가능"

  5월_31일:
    - name: "종합소득세 신고"
      who: "개인사업자, 대표이사 (근로외소득)"

  7월_25일:
    - name: "부가세 확정신고"
      period: "1기 (1-6월)"

  10월_25일:
    - name: "부가세 예정신고"
      period: "2기 예정 (7-9월)"
```

### 연간 주요 기한

```yaml
annual_tax_calendar:
  1월:
    - date: "10일"
      name: "지급명세서 제출 (일용직)"
      period: "전년도"

    - date: "말일"
      name: "면세사업자 사업장현황신고"

  2월:
    - date: "말일"
      name: "지급명세서 제출 (근로/사업/기타)"
      period: "전년도"

  3월:
    - date: "10일"
      name: "법인지방소득세 특별징수명세서"

    - date: "31일"
      name: "법인세 신고"
      note: "12월 결산 법인"

  4월:
    - date: "30일"
      name: "법인지방소득세 신고"
      note: "법인세 신고 후 1개월"

  7월:
    - date: "31일"
      name: "재산세 납부 (1기)"
      note: "건물, 토지"

  8월:
    - date: "31일"
      name: "법인세 중간예납"
      note: "직전년도 법인세 50%"

  9월:
    - date: "30일"
      name: "재산세 납부 (2기)"

  12월:
    - date: "31일"
      name: "근로소득 연말정산 준비"
```

---

## 노무 기한

```yaml
labor_calendar:
  매월:
    - date: "10일"
      name: "4대보험료 납부"
      note: "고지서 기준"

    - date: "말일"
      name: "급여 지급"
      note: "취업규칙/근로계약 기준"

  연간:
    - date: "1월 10일"
      name: "연차휴가 사용 촉진 (1차 통보)"
      who: "10일 이상 미사용 근로자"

    - date: "3월 15일"
      name: "전년도 퇴직연금 운용현황 통지"

    - date: "7월 10일"
      name: "근로자 건강검진 실시 (상반기)"

  입사_시:
    - date: "+14일"
      name: "4대보험 취득 신고"

    - date: "+30일"
      name: "근로계약서 교부"
      note: "즉시 교부 권장"

  퇴사_시:
    - date: "+14일"
      name: "4대보험 상실 신고"

    - date: "+14일"
      name: "퇴직금 지급"
      note: "1년 이상 근무자"

    - date: "+10일"
      name: "이직확인서 제출 (퇴사자 요청 시)"
```

---

## 법인 정기 일정

```yaml
corporate_annual_schedule:
  정기주주총회:
    timing: "사업연도 종료 후 3개월 내"
    typical: "3월 중"
    agenda:
      - "재무제표 승인"
      - "이익배당 결정"
      - "임원 선임 (필요 시)"

  결산_관련:
    - date: "1월 중"
      action: "장부 마감, 재무제표 작성"

    - date: "2월 중"
      action: "감사 (감사보고서 작성)"

    - date: "3월"
      action: "이사회 → 주주총회"

    - date: "3월 31일"
      action: "법인세 신고/납부"

  등기_갱신:
    이사_임기:
      typical: "3년"
      action: "임기 만료 전 재선임 또는 퇴임 등기"

    감사_임기:
      typical: "3년"
      action: "임기 만료 전 재선임 또는 퇴임 등기"
```

---

## 알림 설정

### 알림 규칙

```yaml
notification_rules:
  registration:
    - days_before: 7
      message: "등기 기한 7일 전입니다. 준비 상황을 확인하세요."
      priority: "medium"

    - days_before: 3
      message: "등기 기한 3일 전입니다. 신청을 완료하세요."
      priority: "high"

    - days_before: 1
      message: "내일이 등기 기한입니다!"
      priority: "urgent"

  tax:
    - days_before: 14
      message: "세무 신고 2주 전입니다. 자료를 준비하세요."
      priority: "low"

    - days_before: 7
      message: "세무 신고 1주 전입니다."
      priority: "medium"

    - days_before: 3
      message: "세무 신고 3일 전입니다. 신고를 완료하세요."
      priority: "high"

  corporate:
    - days_before: 30
      message: "주주총회 1개월 전입니다. 준비를 시작하세요."
      priority: "medium"

    - days_before: 14
      message: "주주총회 2주 전입니다. 소집통지를 발송하세요."
      priority: "high"
```

### 캘린더 연동

```yaml
calendar_integration:
  supported:
    - "Google Calendar"
    - "Apple Calendar (iCal)"
    - "Notion Calendar"
    - "Outlook"

  sync_options:
    - ".ics 파일 내보내기"
    - "Google Calendar 직접 연동"
    - "Zapier/Make 자동화"

  recommended_setup: |
    1. 법인 전용 캘린더 생성
    2. 세무/등기/노무 색상 구분
    3. 팀 공유 설정
    4. 모바일 알림 활성화
```

---

## CLI 사용법

```bash
# 이번 달 기한 조회
/regulatory-calendar this-month

# 특정 기간 기한 조회
/regulatory-calendar --from 2026-01-01 --to 2026-03-31

# 등기 기한만 조회
/regulatory-calendar --type registration

# 세무 기한만 조회
/regulatory-calendar --type tax

# 알림 설정
/regulatory-calendar alert --event "법인세신고" --days-before 7,3,1

# 캘린더 내보내기
/regulatory-calendar export --format ics --period 2026

# 과태료 계산
/regulatory-calendar penalty --type registration --days-overdue 45
```

---

## 체크리스트

### 월간 체크리스트

```yaml
monthly_checklist:
  매월_초:
    - "[ ] 전월 세금계산서 발행 내역 확인"
    - "[ ] 전월 카드/현금영수증 매입 정리"

  매월_10일_전:
    - "[ ] 원천세 신고/납부 준비"
    - "[ ] 4대보험료 확인"

  매월_25일_전:
    - "[ ] 부가세 관련 확인 (해당 월)"

  매월_말:
    - "[ ] 급여 지급 확인"
    - "[ ] 다음 달 일정 확인"
```

### 분기 체크리스트

```yaml
quarterly_checklist:
  분기_말:
    - "[ ] 부가세 신고 준비"
    - "[ ] 매출/매입 자료 정리"
    - "[ ] 임시 결산 검토"
```

### 연간 체크리스트

```yaml
annual_checklist:
  1월:
    - "[ ] 지급명세서 제출"
    - "[ ] 연간 세무 일정 확인"

  2월:
    - "[ ] 재무제표 확정"
    - "[ ] 감사 진행"

  3월:
    - "[ ] 정기주주총회 개최"
    - "[ ] 법인세 신고"
    - "[ ] 배당 결의 (필요 시)"

  12월:
    - "[ ] 연말정산 준비"
    - "[ ] 내년 일정 계획"
    - "[ ] 임원 임기 확인"
```

---

## 출력 포맷

### 기한 목록

```json
{
  "report_type": "regulatory_calendar",
  "period": "2026-01-01 ~ 2026-03-31",
  "generated_at": "2026-01-27T10:00:00+09:00",

  "upcoming": [
    {
      "date": "2026-01-31",
      "category": "tax",
      "name": "부가세 확정신고 (2기)",
      "days_remaining": 4,
      "priority": "high",
      "status": "pending"
    },
    {
      "date": "2026-02-10",
      "category": "tax",
      "name": "원천세 신고 (1월분)",
      "days_remaining": 14,
      "priority": "medium",
      "status": "pending"
    },
    {
      "date": "2026-02-15",
      "category": "registration",
      "name": "본점이전 등기",
      "days_remaining": 19,
      "priority": "high",
      "status": "pending",
      "note": "1/30 이전일 기준 14일"
    },
    {
      "date": "2026-03-25",
      "category": "corporate",
      "name": "정기주주총회",
      "days_remaining": 57,
      "priority": "medium",
      "status": "planning"
    },
    {
      "date": "2026-03-31",
      "category": "tax",
      "name": "법인세 신고",
      "days_remaining": 63,
      "priority": "medium",
      "status": "pending"
    }
  ],

  "overdue": [],

  "summary": {
    "total_items": 12,
    "high_priority": 3,
    "this_week": 1,
    "this_month": 4
  },

  "alerts": [
    {
      "type": "warning",
      "message": "부가세 확정신고 4일 남았습니다."
    }
  ]
}
```

### 과태료 계산

```json
{
  "calculation_type": "registration_penalty",
  "registration_type": "본점이전",
  "change_date": "2026-01-15",
  "deadline": "2026-01-29",
  "current_date": "2026-03-15",
  "days_overdue": 45,

  "estimated_penalty": {
    "range": "30만원 ~ 50만원",
    "basis": "1개월 ~ 3개월 초과",
    "note": "실제 금액은 등기소 결정"
  },

  "recommendation": "즉시 등기 신청 + 사유서 제출로 감면 시도"
}
```

---

## 유용한 서비스

| 서비스 | 용도 | URL |
|--------|------|-----|
| 홈택스 | 세금 신고/납부 | hometax.go.kr |
| 위택스 | 지방세 신고/납부 | wetax.go.kr |
| 인터넷등기소 | 등기 신청/열람 | iros.go.kr |
| 4대보험포털 | 취득/상실 신고 | 4insure.or.kr |
| 고용보험 | 고용/산재 | ei.go.kr |

---

⚠️ **면책 조항**
기한은 법령 개정, 공휴일 등에 따라 변경될 수 있습니다.
실제 신고 전 관할 기관에서 정확한 기한을 확인하세요.
