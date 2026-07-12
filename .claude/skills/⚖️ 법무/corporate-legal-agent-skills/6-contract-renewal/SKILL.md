---
name: contract-renewal
description: 계약 갱신 기한 관리 및 알림
model: inherit
quality_tier: fast_scan
triggers:
  - "계약갱신"
  - "계약만료"
  - "갱신알림"
  - "임대차"
  - "라이선스"
  - "구독"
---

# Contract Renewal Skill

법인의 주요 계약 갱신 기한을 추적하고 적시에 알림을 제공합니다.

## 핵심 원칙

| 원칙 | 설명 |
|------|------|
| **선제적 관리** | 만료 90일 전부터 검토 |
| **자동 갱신 주의** | 해지 통보 기한 놓치지 않기 |
| **비용 최적화** | 갱신 전 조건 재협상 기회 |

---

## 계약 유형별 관리

### 임대차 계약

```yaml
lease_contract:
  typical_term: "2년"

  key_dates:
    renewal_notice:
      timing: "만료 6개월 ~ 1개월 전"
      action: "갱신 또는 해지 통보"
      note: "묵시적 갱신 주의"

    rent_increase:
      limit: "5% 이내 (상가)"
      commercial_note: "상가건물임대차보호법 적용 여부 확인"

  checklist:
    - "[ ] 임대료 시세 조사"
    - "[ ] 갱신 조건 검토 (임대료, 기간)"
    - "[ ] 필요 시 이전 검토"
    - "[ ] 갱신 또는 해지 서면 통보"

  auto_renewal:
    condition: "당사자 중 어느 일방이 기간 만료 전 통지 없을 시"
    effect: "동일 조건으로 묵시적 갱신"
    term: "묵시적 갱신 후 2년"

  template: |
    # 임대차계약 갱신 요청서

    임대인 OOO 귀하

    당사와 귀하 간 체결된 아래 임대차계약에 대하여
    동일 조건으로 갱신을 요청합니다.

    ## 계약 정보
    - 대상: 서울시 강남구 OO로 OO, OO층 OO호
    - 현 계약기간: 2024.03.01 ~ 2026.02.28
    - 월 임대료: 5,000,000원
    - 보증금: 50,000,000원

    ## 갱신 요청 조건
    - 기간: 2026.03.01 ~ 2028.02.28 (2년)
    - 임대료: 현행 유지 또는 협의

    2026년 1월 27일
    임차인: 주식회사 OOO
    대표이사: 홍길동 (인)
```

### 소프트웨어/SaaS 라이선스

```yaml
software_license:
  common_types:
    연간_구독:
      example: ["Microsoft 365", "Google Workspace", "Slack", "Notion"]
      renewal: "자동 갱신 (카드 결제)"
      cancel_notice: "보통 30일 전"

    볼륨_라이선스:
      example: ["Adobe Enterprise", "MS EA"]
      renewal: "계약 갱신 협상"
      timing: "만료 90일 전 협상 시작"

    영구_라이선스:
      example: ["On-premise 소프트웨어"]
      renewal: "유지보수 계약 갱신"

  checklist:
    - "[ ] 현재 사용량 대비 라이선스 수 적정성"
    - "[ ] 미사용 라이선스 정리"
    - "[ ] 대안 솔루션 비용 비교"
    - "[ ] 장기 계약 할인 확인"
    - "[ ] 결제 수단 유효성 확인"

  cost_optimization:
    - "연간 선결제 시 할인 확인"
    - "스타트업 프로그램 자격 확인"
    - "비영리/교육 할인 해당 여부"
    - "장기 계약 (2-3년) 할인"
```

### 서비스 계약

```yaml
service_contract:
  types:
    용역_계약:
      example: ["회계법인", "법무법인", "컨설팅"]
      typical_term: "1년"
      renewal: "자동 갱신 또는 재계약"

    유지보수_계약:
      example: ["IT 시스템", "장비", "시설"]
      typical_term: "1년"
      renewal: "갱신 협상"

    보험_계약:
      example: ["배상책임보험", "화재보험", "임원배상"]
      typical_term: "1년"
      renewal: "자동 갱신 (보통)"
      review: "담보/보상한도 적정성"

  checklist:
    - "[ ] 서비스 품질 만족도 평가"
    - "[ ] 비용 대비 효과 분석"
    - "[ ] 대안 제공업체 검토"
    - "[ ] 계약 조건 개선 협상"
```

### 인적 계약

```yaml
personnel_contracts:
  근로계약:
    types:
      정규직: "무기한 (수습 포함 시 3개월)"
      계약직: "1년 또는 특정 기간"
      파견직: "파견계약 기간"

    renewal_consideration:
      계약직_전환: "2년 초과 시 무기계약 전환 여부"
      급여_조정: "연봉 협상"

  프리랜서_계약:
    typical_term: "프로젝트 단위 또는 1년"
    renewal: "재계약 협상"
    checklist:
      - "[ ] 성과 평가"
      - "[ ] 단가 조정"
      - "[ ] 계약 형태 유지 또는 변경"

  이사_감사_임기:
    이사: "3년 (정관 규정)"
    감사: "3년 (정관 규정)"
    renewal: "주주총회 선임"
    registration: "14일 내 등기"
```

---

## 알림 설정

### 표준 알림 일정

```yaml
notification_schedule:
  high_value_contracts:  # 고가 계약 (임대차, 대형 라이선스)
    - days_before: 90
      action: "갱신 검토 시작, 시장 조사"
    - days_before: 60
      action: "협상 시작, 대안 검토"
    - days_before: 30
      action: "최종 결정, 통보 발송"
    - days_before: 7
      action: "서류 확정, 서명"

  standard_contracts:  # 일반 계약
    - days_before: 60
      action: "갱신 여부 검토"
    - days_before: 30
      action: "갱신 또는 해지 결정"
    - days_before: 7
      action: "서류 처리"

  subscription_services:  # 자동갱신 구독
    - days_before: 30
      action: "사용량 검토, 필요성 재평가"
    - days_before: 14
      action: "해지 필요 시 통보 (해지 기한 확인)"
```

### 알림 우선순위

```yaml
priority_levels:
  critical:
    criteria:
      - "월 1,000만원 이상 비용"
      - "핵심 업무 영향 (사무실, ERP 등)"
      - "해지 시 위약금 발생"
    notification: "90, 60, 30, 14, 7, 3, 1일 전"

  high:
    criteria:
      - "월 100만원 ~ 1,000만원"
      - "대체 어려운 서비스"
    notification: "60, 30, 14, 7일 전"

  medium:
    criteria:
      - "월 100만원 미만"
      - "대체 가능한 서비스"
    notification: "30, 14, 7일 전"

  low:
    criteria:
      - "소액 구독"
      - "쉽게 해지/재가입 가능"
    notification: "14, 7일 전"
```

---

## 계약 데이터베이스

### 필수 기록 항목

```yaml
contract_record:
  identification:
    - "계약 ID (내부 관리용)"
    - "계약명"
    - "상대방 (법인명/담당자)"
    - "계약 유형"

  terms:
    - "계약 시작일"
    - "계약 종료일"
    - "갱신 조건 (자동/수동)"
    - "해지 통보 기한"

  financial:
    - "계약 금액"
    - "결제 주기 (월/분기/연)"
    - "결제 방법"
    - "다음 결제일"

  management:
    - "담당 부서/담당자"
    - "알림 설정"
    - "관련 문서 링크"
    - "메모/히스토리"
```

### 계약 목록 템플릿

```markdown
# 계약 관리 대장

## 임대차

| 계약명 | 상대방 | 시작일 | 종료일 | 월 비용 | 해지통보 | 담당자 |
|--------|--------|--------|--------|---------|----------|--------|
| 본사 사무실 | OO부동산 | 2024-03-01 | 2026-02-28 | 500만원 | 만료 1월 전 | 총무팀 |
| 창고 | XX물류 | 2025-01-01 | 2025-12-31 | 100만원 | 만료 1월 전 | 총무팀 |

## 소프트웨어/SaaS

| 서비스 | 제공사 | 갱신일 | 연 비용 | 자동갱신 | 해지기한 | 담당자 |
|--------|--------|--------|---------|----------|----------|--------|
| Google Workspace | Google | 2026-04-01 | 1,200만원 | Y | 30일 전 | IT팀 |
| Slack | Salesforce | 2026-06-15 | 600만원 | Y | 30일 전 | IT팀 |
| 회계 ERP | 더존 | 2026-01-31 | 480만원 | N | 60일 전 | 재무팀 |

## 서비스 계약

| 계약명 | 상대방 | 종료일 | 연 비용 | 담당자 |
|--------|--------|--------|---------|--------|
| 세무 기장 | OO회계법인 | 2026-12-31 | 600만원 | 재무팀 |
| 법률 자문 | XX법률사무소 | 2026-06-30 | 1,200만원 | 경영지원 |
| 배상책임보험 | OO화재 | 2026-03-01 | 150만원 | 총무팀 |
```

---

## CLI 사용법

```bash
# 전체 계약 목록 조회
/contract-renewal list

# 30일 내 만료 계약
/contract-renewal expiring --days 30

# 특정 유형 조회
/contract-renewal list --type lease
/contract-renewal list --type software
/contract-renewal list --type service

# 계약 추가
/contract-renewal add --name "본사 임대차" --type lease --end-date 2026-02-28 --cost 5000000 --notice-days 30

# 갱신 알림 설정
/contract-renewal alert --contract-id C001 --days 90,60,30

# 갱신 체크리스트 생성
/contract-renewal checklist --contract-id C001

# 비용 분석
/contract-renewal cost-analysis --period annual
```

---

## 갱신 협상 팁

```yaml
negotiation_tips:
  준비:
    - "시장 가격 조사 (경쟁 견적)"
    - "현재 계약 조건 정리"
    - "협상 목표 설정 (가격, 조건)"
    - "BATNA (대안) 준비"

  타이밍:
    - "만료 60-90일 전 협상 시작"
    - "상대방 영업 사이클 고려"
    - "연말/분기말 실적 압박 활용"

  전략:
    다년_계약:
      approach: "2-3년 약정으로 단가 인하"
      discount: "10-20% 가능"

    선결제:
      approach: "연간 선결제로 할인"
      discount: "5-15% 가능"

    번들링:
      approach: "여러 서비스 통합 계약"
      discount: "10-25% 가능"

    경쟁_활용:
      approach: "대안 견적 제시"
      effect: "협상력 강화"

  주의사항:
    - "구두 합의는 서면으로 확인"
    - "자동갱신 조항 꼼꼼히 확인"
    - "해지 위약금 조항 확인"
    - "가격 인상 제한 조항 협상"
```

---

## 출력 포맷

### 계약 현황

```json
{
  "report_type": "contract_status",
  "generated_at": "2026-01-27T10:00:00+09:00",

  "summary": {
    "total_contracts": 15,
    "total_annual_cost": 48000000,
    "expiring_30_days": 2,
    "expiring_90_days": 5
  },

  "by_category": {
    "lease": {
      "count": 2,
      "annual_cost": 72000000
    },
    "software": {
      "count": 8,
      "annual_cost": 30000000
    },
    "service": {
      "count": 5,
      "annual_cost": 19500000
    }
  },

  "upcoming_renewals": [
    {
      "contract_id": "C001",
      "name": "회계 ERP (더존)",
      "type": "software",
      "end_date": "2026-01-31",
      "days_remaining": 4,
      "annual_cost": 4800000,
      "auto_renewal": false,
      "action_required": "갱신 계약 체결 필요",
      "priority": "critical"
    },
    {
      "contract_id": "C002",
      "name": "본사 사무실 임대차",
      "type": "lease",
      "end_date": "2026-02-28",
      "days_remaining": 32,
      "monthly_cost": 5000000,
      "notice_deadline": "2026-01-28",
      "action_required": "갱신 통보 또는 이전 결정",
      "priority": "critical"
    }
  ],

  "alerts": [
    {
      "type": "urgent",
      "contract": "회계 ERP",
      "message": "4일 후 만료. 즉시 조치 필요."
    },
    {
      "type": "warning",
      "contract": "본사 사무실",
      "message": "해지/갱신 통보 기한이 내일입니다."
    }
  ],

  "recommendations": [
    {
      "contract": "Google Workspace",
      "suggestion": "연간 선결제로 10% 할인 가능",
      "potential_saving": 120000
    }
  ]
}
```

---

## 통합 서비스 연동

```yaml
integrations:
  calendar:
    - "Google Calendar"
    - "Outlook"
    - "Notion Calendar"

  notification:
    - "Slack"
    - "Email"
    - "카카오톡 알림"

  document_storage:
    - "Google Drive"
    - "Dropbox"
    - "Notion"

  recommended_workflow: |
    1. 계약 체결 시 → 계약 DB 등록
    2. 자동 알림 → 캘린더 + Slack
    3. 원본 문서 → Drive 저장 (링크 연결)
    4. 갱신 시 → 히스토리 업데이트
```

---

⚠️ **면책 조항**
계약 갱신 조건은 개별 계약에 따라 다릅니다.
중요한 계약은 반드시 원본 계약서를 확인하고,
필요 시 법률 전문가와 상담하세요.
