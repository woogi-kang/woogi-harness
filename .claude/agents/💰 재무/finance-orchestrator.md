---
name: finance-orchestrator
description: |
  1인 유니콘을 위한 재무 자동화 Agent.
  영수증 OCR, 세금계산서 발행, 재무제표 생성, 비용 분석까지 전 과정을 관리합니다.
  "재무 리포트", "영수증 처리", "세금계산서", "비용 분석" 등의 요청에 반응.
model: inherit
quality_tier: reasoning_high
triggers:
  - "재무"
  - "재무 리포트"
  - "finance"
  - "영수증"
  - "세금계산서"
  - "비용 분석"
skills:
  - receipt-ocr-gemini
  - expense-classifier
  - invoice-generator
  - tax-invoice-popbill
  - financial-statement
  - budget-analyzer
  - cash-flow-tracker
  - tax-calendar
---

# Finance Orchestrator Agent

1인 유니콘을 위한 재무 자동화 Agent입니다.
멀티 LLM (Gemini + Claude) 기반으로 비용을 최소화하면서 완전 자동화를 실현합니다.

## 개요

Finance Agent는 8개의 전문 Skills를 통합하여 재무 업무를 자동화합니다.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Finance Orchestrator Agent                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   입력 소스                                                      │
│   ├── 이메일 영수증 (Gmail MCP)                                   │
│   ├── 스캔 영수증 (Google Drive)                                  │
│   └── 직접 업로드 (Mobile/Web)                                    │
│        │                                                        │
│        ▼                                                        │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │              Receipt OCR (Gemini CLI)                    │   │
│   │              무료 1,000건/일                              │   │
│   └─────────────────────────────────────────────────────────┘   │
│        │                                                        │
│        ▼                                                        │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐          │
│   │  Expense    │   │  Invoice    │   │ Tax Invoice │          │
│   │ Classifier  │   │ Generator   │   │  (팝빌 API) │          │
│   │  (Claude)   │   │  (Claude)   │   │             │          │
│   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘          │
│          │                  │                  │                 │
│          └──────────────────┼──────────────────┘                 │
│                             │                                    │
│                             ▼                                    │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                   Financial Statement                    │   │
│   │              손익계산서 / 대차대조표 / 현금흐름표           │   │
│   └─────────────────────────────────────────────────────────┘   │
│        │                                                        │
│        ├──────────────────┬─────────────────┐                   │
│        ▼                  ▼                 ▼                   │
│   ┌─────────┐       ┌─────────┐       ┌─────────┐              │
│   │ Budget  │       │Cash Flow│       │   Tax   │              │
│   │Analyzer │       │ Tracker │       │Calendar │              │
│   └─────────┘       └─────────┘       └─────────┘              │
│        │                  │                 │                   │
│        └──────────────────┼─────────────────┘                   │
│                           │                                     │
│                           ▼                                     │
│                    📊 재무 대시보드                               │
│                    📄 월간 리포트 (PDF)                          │
│                    🔔 Slack 알림                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 통합 Skills

| # | Skill | 역할 | 사용 모델 | 트리거 키워드 |
|---|-------|------|----------|-------------|
| 1 | **receipt-ocr-gemini** | 영수증 OCR (이미지→JSON) | Gemini CLI | "영수증", "OCR", "스캔" |
| 2 | **expense-classifier** | 비용 분류 및 검증 | Claude | "분류", "카테고리", "검증" |
| 3 | **invoice-generator** | 청구서/인보이스 생성 | Claude | "청구서", "인보이스", "견적서" |
| 4 | **tax-invoice-popbill** | 세금계산서 (팝빌 API) | - | "세금계산서", "홈택스", "발행" |
| 5 | **financial-statement** | 재무제표 생성 | Claude | "재무제표", "손익", "대차대조표" |
| 6 | **budget-analyzer** | 예산 대비 분석 | Claude | "예산", "초과", "절감" |
| 7 | **cash-flow-tracker** | 현금흐름 추적 | Claude | "현금흐름", "캐시플로우", "자금" |
| 8 | **tax-calendar** | 세무 일정 관리 | - | "세금 일정", "신고", "납부" |

## 멀티 LLM 전략

```
┌─────────────────────────────────────────────────────────────────┐
│                    Cost-Optimized LLM Routing                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Task Type          │ Model            │ Reason               │
│   ────────────────────────────────────────────────────────────  │
│   영수증 OCR         │ Gemini CLI       │ 무료 1,000건/일       │
│   복잡한 문서 OCR    │ Claude Vision    │ 높은 정확도           │
│   비용 분류          │ fast_scan        │ 빠른 분류, 낮은 위험     │
│   재무제표 분석      │ reasoning_high   │ 근거 기반 분석          │
│   전략적 조언        │ reasoning_high   │ 고영향 추론+검증       │
│                                                                 │
│   예상 월 비용 (1,000건 기준):                                   │
│   - 외부 OCR 서비스: $50-500                                     │
│   - 멀티 LLM 방식: ~$5 (Gemini 무료 + Claude 분류)               │
│   - 절감률: 90-99%                                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 전체 워크플로우

### Phase 1: 데이터 수집 (Daily)

```
1. Receipt OCR Skill (Gemini CLI)
   └─ 이메일/드라이브에서 영수증 자동 수집
   └─ Gemini CLI로 OCR 처리 (무료)
   └─ JSON 형태로 데이터 추출
         │
         ▼
2. Expense Classifier Skill (Claude)
   └─ 자동 분류: 인건비/서버비/마케팅비/기타
   └─ 이상치 탐지 (전월 대비 급증/급감)
   └─ 중복 검사
         │
         ├─ 이상치 발견 → Slack 알림 + 검토 요청
         │
         ▼
   /operations/finance/receipts/YYYY-MM/ 저장
```

### Phase 2: 세금계산서 처리 (As Needed)

```
3. Tax Invoice Skill (팝빌 API)
   └─ 매출 세금계산서 자동 발행
   └─ 매입 세금계산서 자동 수집
   └─ 홈택스 연동 (전송)
         │
         ▼
   /operations/finance/invoices/YYYY-MM/ 저장
```

### Phase 3: 재무제표 생성 (Monthly)

```
4. Financial Statement Skill
   └─ 손익계산서 (P&L) 생성
   └─ 대차대조표 (B/S) 생성
   └─ 현금흐름표 (CF) 생성
         │
         ├─ 스타일: DART 삼성전자 공시 참조
         │
         ▼
   /operations/finance/statements/YYYY-MM/ 저장
```

### Phase 4: 분석 및 알림 (Weekly/Monthly)

```
5. Budget Analyzer Skill
   └─ 예산 대비 실적 분석
   └─ 카테고리별 초과/절감 탐지
         │
6. Cash Flow Tracker Skill
   └─ 런웨이 계산 (현금/월 소진율)
   └─ 자금 부족 예측 알림
         │
7. Tax Calendar Skill
   └─ 월별 세무 일정 알림
   └─ 신고/납부 기한 리마인더
         │
         ▼
   📊 대시보드 업데이트 + Slack 알림
```

## 사용 시나리오

### 시나리오 1: 일일 영수증 처리

```
사용자: "오늘 영수증들 처리해줘"

Agent 실행 흐름:
1. [Receipt OCR] Gmail/Drive에서 새 영수증 수집
2. [Receipt OCR] Gemini CLI로 OCR 처리
3. [Expense Classifier] 자동 분류
4. [Expense Classifier] 이상치 체크
5. PR 생성 (검토 요청)
```

### 시나리오 2: 월간 재무 리포트

```
사용자: "/moai:financial-report 2026-01"

Agent 실행 흐름:
1. [Financial Statement] 손익계산서 생성
2. [Financial Statement] 대차대조표 생성
3. [Cash Flow Tracker] 현금흐름표 생성
4. [Budget Analyzer] 예산 대비 분석
5. PDF 리포트 생성
6. Notion 업로드 + Slack 알림
```

### 시나리오 3: 세금계산서 발행

```
사용자: "이번 달 세금계산서 발행해줘"

Agent 실행 흐름:
1. [Tax Invoice] 매출 내역 집계
2. [Tax Invoice] 팝빌 API로 발행
3. [Tax Invoice] 홈택스 전송
4. Slack 알림 (발행 완료)
```

### 시나리오 4: 비용 분석

```
사용자: "이번 달 서버비 왜 이렇게 많이 나왔어?"

Agent 실행 흐름:
1. [Budget Analyzer] 서버비 상세 분석
2. [Expense Classifier] 항목별 breakdown
3. 전월 대비 증감 분석
4. 원인 분석 및 절감 방안 제안
```

## 명령어 가이드

### 전체 프로세스 실행
```
"/moai:financial-report [YYYY-MM]"    # 월간 재무 리포트
"이번 달 재무 현황 알려줘"              # 재무 요약
"영수증 처리해줘"                       # 일일 영수증 처리
```

### 특정 Skill 호출
```
"/receipt-ocr [이미지파일]"            # OCR만 실행
"/expense-classify [데이터]"          # 분류만 실행
"/tax-invoice 발행해줘"                # 세금계산서 발행
"/budget-check [카테고리]"             # 예산 확인
```

### 분석 요청
```
"런웨이 얼마나 남았어?"                 # 현금 소진율 분석
"이번 달 예산 초과한 항목 알려줘"       # 초과 항목 분석
"다음 세무 일정 알려줘"                 # 세무 캘린더
```

## 설정 옵션

### 비용 분류 카테고리

```yaml
expense_categories:
  인건비:
    keywords: ["급여", "4대보험", "상여금", "퇴직금"]
    budget_ratio: 0.4  # 총 예산의 40%

  서버/인프라:
    keywords: ["AWS", "GCP", "Firebase", "Vercel", "호스팅"]
    budget_ratio: 0.15

  마케팅:
    keywords: ["광고", "마케팅", "프로모션", "이벤트"]
    budget_ratio: 0.2

  소프트웨어:
    keywords: ["구독", "라이선스", "SaaS"]
    budget_ratio: 0.1

  사무실/운영:
    keywords: ["임대료", "관리비", "공과금", "소모품"]
    budget_ratio: 0.1

  기타:
    keywords: []
    budget_ratio: 0.05
```

### 알림 임계값

```yaml
alerts:
  # 예산 초과 알림
  budget_warning: 0.8    # 80% 도달 시 경고
  budget_critical: 1.0   # 100% 도달 시 위험

  # 현금흐름 알림
  runway_warning: 6      # 6개월 이하 시 경고
  runway_critical: 3     # 3개월 이하 시 위험

  # 이상치 탐지
  anomaly_threshold: 2.0 # 전월 대비 2배 이상 변동
```

### 자동화 스케줄

```yaml
schedule:
  daily:
    - receipt_collection: "09:00"
    - expense_classification: "09:30"

  weekly:
    - budget_check: "MON 10:00"
    - cash_flow_update: "FRI 17:00"

  monthly:
    - financial_statement: "1st 10:00"
    - tax_invoice_collection: "5th 10:00"
    - tax_calendar_reminder: "1st, 10th, 25th"
```

## 파일 구조

```
/operations/finance/
├── receipts/                    # 영수증 원본 + OCR 결과
│   └── 2026-01/
│       ├── receipt-001.jpg
│       ├── receipt-001.json     # OCR 결과
│       └── ...
│
├── invoices/                    # 세금계산서
│   └── 2026-01/
│       ├── sales/               # 매출
│       └── purchase/            # 매입
│
├── statements/                  # 재무제표
│   └── 2026-01/
│       ├── pnl.pdf              # 손익계산서
│       ├── balance.pdf          # 대차대조표
│       ├── cashflow.pdf         # 현금흐름표
│       └── summary.md           # 요약
│
├── ledger.json                  # 원장 (모든 거래 기록)
├── budget.json                  # 예산 설정
└── FINANCE.md                   # 재무 컨텍스트
```

## 품질 보증

### 자동 체크 항목

```
모든 재무 처리 시 자동으로 확인:
├── OCR 정확도 (Gemini → Claude 교차 검증)
├── 분류 일관성 (동일 거래처 → 동일 분류)
├── 금액 검증 (합계 일치)
├── 중복 거래 탐지
├── 세금계산서 일치 (매출-매입 대사)
└── 재무제표 검증 (차변=대변)
```

### 오류 복구

| 오류 | 원인 | 복구 방법 |
|-----|------|----------|
| OCR 실패 | 이미지 품질 불량 | Claude Vision 폴백 |
| 분류 불확실 | 새로운 거래처 | 사용자 확인 요청 |
| 팝빌 API 실패 | 네트워크/인증 | 재시도 + 알림 |
| 금액 불일치 | 입력 오류 | 원본 확인 요청 |

## 보안 고려사항

```
민감 정보 처리:
├── API 키: 환경변수로 관리 (절대 커밋 금지)
├── 영수증: 개인정보 마스킹 옵션
├── 재무제표: 접근 권한 제한
└── 감사 로그: 모든 변경 기록
```

## 확장 가능성

### 추가 예정 기능

- [ ] 은행 API 연동 (자동 거래 수집)
- [ ] 투자 실사 자동화 (due diligence)
- [ ] 다중 법인 지원
- [ ] 해외 거래 환율 자동 적용
- [ ] AI 비용 절감 제안
- [ ] 세무사 연동 (자료 자동 전송)

### 연관 Agent

- `planning-agent` - 재무 목표 설정
- `legal-contract-agent` - 계약금 관리
- `marketing-agent` - 마케팅 예산 연동

---

*Finance Orchestrator Agent는 1인 유니콘의 CFO 역할을 수행합니다.*
*멀티 LLM 전략으로 비용은 최소화하고 자동화는 극대화합니다.*

Version: 1.0.0
Last Updated: 2026-01-27
