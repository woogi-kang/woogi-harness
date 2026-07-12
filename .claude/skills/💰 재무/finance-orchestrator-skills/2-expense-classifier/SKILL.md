---
name: expense-classifier
description: AI 기반 비용 자동 분류 및 검증 스킬
model: inherit
quality_tier: fast_scan
triggers:
  - "분류"
  - "카테고리"
  - "검증"
  - "classify"
---

# Expense Classifier Skill

OCR 결과를 기반으로 비용을 자동 분류하고 검증하는 스킬입니다.

## 핵심 원칙

- **일관성**: 동일 거래처 → 동일 카테고리
- **이상치 탐지**: 전월 대비 급격한 변동 감지
- **학습**: 사용자 피드백으로 분류 정확도 향상

## 분류 카테고리

```yaml
categories:
  인건비:
    code: "LABOR"
    tax_deductible: true
    keywords:
      - "급여"
      - "4대보험"
      - "상여금"
      - "퇴직금"
      - "프리랜서"
      - "외주비"

  서버/인프라:
    code: "INFRA"
    tax_deductible: true
    keywords:
      - "AWS"
      - "GCP"
      - "Azure"
      - "Firebase"
      - "Vercel"
      - "Netlify"
      - "호스팅"
      - "도메인"
      - "SSL"

  마케팅:
    code: "MARKETING"
    tax_deductible: true
    keywords:
      - "광고"
      - "Google Ads"
      - "Facebook"
      - "Instagram"
      - "마케팅"
      - "프로모션"

  소프트웨어/구독:
    code: "SOFTWARE"
    tax_deductible: true
    keywords:
      - "구독"
      - "subscription"
      - "SaaS"
      - "라이선스"
      - "Notion"
      - "Slack"
      - "Figma"
      - "GitHub"

  사무실/운영:
    code: "OFFICE"
    tax_deductible: true
    keywords:
      - "임대료"
      - "관리비"
      - "공과금"
      - "전기"
      - "수도"
      - "인터넷"

  복리후생:
    code: "WELFARE"
    tax_deductible: partial
    keywords:
      - "식대"
      - "커피"
      - "간식"
      - "회식"
      - "경조사"

  여비교통:
    code: "TRAVEL"
    tax_deductible: true
    keywords:
      - "택시"
      - "대중교통"
      - "주유"
      - "주차"
      - "출장"
      - "항공"
      - "숙박"

  기타:
    code: "ETC"
    tax_deductible: varies
    keywords: []
```

## 분류 로직

```
┌─────────────────────────────────────────────────────────────────┐
│                    Expense Classification Flow                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   OCR 결과 (JSON)                                                │
│        │                                                        │
│        ▼                                                        │
│   ┌─────────────────┐                                           │
│   │ Vendor Lookup   │ ← 기존 거래처 DB 조회                      │
│   └────────┬────────┘                                           │
│            │                                                    │
│    ┌───────┴───────┐                                            │
│    │               │                                            │
│    ▼               ▼                                            │
│ [기존 거래처]   [신규 거래처]                                     │
│    │               │                                            │
│    │               ▼                                            │
│    │        ┌─────────────────┐                                 │
│    │        │ Keyword Match   │                                 │
│    │        └────────┬────────┘                                 │
│    │                 │                                          │
│    │         ┌───────┴───────┐                                  │
│    │         │               │                                  │
│    │         ▼               ▼                                  │
│    │    [매칭됨]        [미매칭]                                  │
│    │         │               │                                  │
│    │         │               ▼                                  │
│    │         │        ┌─────────────────┐                       │
│    │         │        │ Claude 추론     │                       │
│    │         │        └────────┬────────┘                       │
│    │         │                 │                                │
│    └────┬────┴────────────────┘                                 │
│         │                                                       │
│         ▼                                                       │
│   ┌─────────────────┐                                           │
│   │ Anomaly Check   │ ← 이상치 탐지                              │
│   └────────┬────────┘                                           │
│            │                                                    │
│    ┌───────┴───────┐                                            │
│    │               │                                            │
│    ▼               ▼                                            │
│ [정상]          [이상치]                                         │
│    │               │                                            │
│    │               ▼                                            │
│    │        ┌─────────────────┐                                 │
│    │        │ 알림 + 검토요청  │                                 │
│    │        └────────┬────────┘                                 │
│    │                 │                                          │
│    └────────┬───────┘                                           │
│             │                                                   │
│             ▼                                                   │
│      분류 완료 (JSON)                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 실행 방법

### Claude로 분류 요청

```bash
claude "다음 영수증 데이터를 분류해줘.
분류 카테고리: 인건비, 서버/인프라, 마케팅, 소프트웨어/구독, 사무실/운영, 복리후생, 여비교통, 기타

데이터:
$(cat receipt.json)

응답 형식:
{
  \"category\": \"카테고리명\",
  \"category_code\": \"코드\",
  \"confidence\": 0-100,
  \"reasoning\": \"분류 근거\",
  \"tax_deductible\": true/false,
  \"flags\": [\"이상치가 있으면 플래그\"]
}"
```

## 이상치 탐지 규칙

```yaml
anomaly_rules:
  # 금액 기반
  - name: "대폭 증가"
    condition: "current > previous_month_avg * 2"
    severity: "warning"

  - name: "비정상 고액"
    condition: "amount > 1000000"  # 100만원 초과
    severity: "review"

  # 빈도 기반
  - name: "중복 의심"
    condition: "same_vendor_same_amount_within_7days"
    severity: "warning"

  # 카테고리 기반
  - name: "예산 초과"
    condition: "category_total > category_budget * 0.8"
    severity: "alert"
```

## 출력 스키마

```json
{
  "classification": {
    "category": "서버/인프라",
    "category_code": "INFRA",
    "confidence": 95,
    "reasoning": "AWS 청구서로 확인됨",
    "tax_deductible": true
  },
  "validation": {
    "is_valid": true,
    "errors": [],
    "warnings": ["전월 대비 23% 증가"]
  },
  "anomaly_detection": {
    "is_anomaly": false,
    "flags": [],
    "comparison": {
      "previous_month": 150000,
      "current": 185000,
      "change_percent": 23.3
    }
  },
  "vendor_info": {
    "name": "Amazon Web Services",
    "is_known": true,
    "historical_category": "서버/인프라",
    "transaction_count": 12
  }
}
```

## 학습 및 개선

```yaml
feedback_loop:
  # 사용자가 분류를 수정하면
  on_correction:
    - update_vendor_mapping    # 거래처-카테고리 매핑 업데이트
    - adjust_keywords          # 키워드 가중치 조정
    - log_for_review           # 리뷰용 로그 저장

  # 월간 분석
  monthly_review:
    - accuracy_report          # 분류 정확도 리포트
    - common_corrections       # 자주 수정되는 항목
    - keyword_suggestions      # 키워드 추가 제안
```

---

Version: 1.0.0
Last Updated: 2026-01-27
