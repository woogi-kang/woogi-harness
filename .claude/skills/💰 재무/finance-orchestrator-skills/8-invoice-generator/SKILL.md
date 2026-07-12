---
name: invoice-generator
description: 청구서/인보이스/견적서 생성 스킬
model: inherit
quality_tier: implementation
triggers:
  - "청구서"
  - "인보이스"
  - "견적서"
  - "invoice"
  - "quotation"
---

# Invoice Generator Skill

청구서, 인보이스, 견적서를 생성하는 스킬입니다.

## 핵심 원칙

- **전문적 포맷**: 한국 상관례에 맞는 양식
- **자동 계산**: 부가세, 합계 자동 산출
- **다중 출력**: PDF, Markdown, JSON 지원

## 지원 문서 유형

| 유형 | 설명 | 부가세 |
|------|------|--------|
| 견적서 | 거래 전 가격 제시 | 별도 표기 |
| 청구서 | 용역/제품 대금 청구 | 포함 |
| 인보이스 | 해외 거래용 | N/A |
| 거래명세서 | 거래 내역 상세 | 포함 |

## 문서 템플릿

### 견적서 (Quotation)

```yaml
quotation:
  header:
    document_type: "견 적 서"
    document_number: "QT-{YYYY}{MM}{NNNN}"
    issue_date: "{YYYY}-{MM}-{DD}"
    valid_until: "{issue_date + 30 days}"

  supplier:
    company: "Solo Unicorn Corp"
    business_number: "000-00-00000"
    ceo: "대표자명"
    address: "사업장 주소"
    contact: "연락처"

  client:
    company: "{고객사명}"
    attention: "{담당자}"
    email: "{이메일}"

  items:
    - description: "{항목명}"
      quantity: 1
      unit_price: 0
      amount: 0

  totals:
    subtotal: 0
    vat: 0  # 10%
    total: 0

  terms:
    payment: "계약금 50%, 잔금 50%"
    delivery: "착수 후 2주"
    validity: "견적일로부터 30일"

  notes: "본 견적서는 부가세 별도입니다."
```

### 청구서 (Invoice)

```yaml
invoice:
  header:
    document_type: "청 구 서"
    document_number: "INV-{YYYY}{MM}{NNNN}"
    issue_date: "{YYYY}-{MM}-{DD}"
    due_date: "{issue_date + 30 days}"

  supplier:
    company: "Solo Unicorn Corp"
    business_number: "000-00-00000"
    bank_name: "은행명"
    bank_account: "계좌번호"
    account_holder: "예금주"

  client:
    company: "{고객사명}"
    business_number: "{사업자번호}"

  items:
    - description: "{항목명}"
      quantity: 1
      unit_price: 0
      amount: 0

  totals:
    subtotal: 0
    vat: 0  # 10%
    total: 0

  payment_info:
    bank: "은행명"
    account: "계좌번호"
    holder: "예금주"
    due_date: "{due_date}"
```

## 문서 번호 체계

```
문서유형-년월-일련번호
QT-202601-0001  # 견적서
INV-202601-0001  # 청구서
PO-202601-0001   # 발주서
```

## 생성 워크플로우

```
1. 문서 유형 선택
   ↓
2. 고객 정보 입력 (또는 기존 고객 선택)
   ↓
3. 항목 입력
   - 품목명, 수량, 단가
   - 자동: 금액 = 수량 × 단가
   ↓
4. 조건 설정
   - 결제 조건
   - 납품 조건
   - 유효 기간
   ↓
5. 출력 형식 선택
   - PDF (고객 제출용)
   - Markdown (내부 기록용)
   - JSON (시스템 연동용)
   ↓
6. 저장 위치
   operations/finance/invoices/{YYYY-MM}/{type}/
```

## CLI 사용법

```bash
# 견적서 생성
/invoice create --type quotation --client "A Corp"

# 청구서 생성 (기존 견적서 기반)
/invoice create --type invoice --from QT-202601-0001

# 목록 조회
/invoice list --month 2026-01

# PDF 출력
/invoice export --id INV-202601-0001 --format pdf
```

## 자연어 요청 예시

```
"A사에 500만원 견적서 보내줘"
→ 견적서 생성 → PDF → 이메일 발송

"이번 달 청구서 발행해"
→ 미청구 건 조회 → 청구서 일괄 생성

"지난달 견적서를 청구서로 전환해줘"
→ 견적서 조회 → 청구서 변환 → 저장
```

## 출력 포맷

### JSON 출력

```json
{
  "document_type": "invoice",
  "document_number": "INV-202601-0001",
  "issue_date": "2026-01-15",
  "due_date": "2026-02-14",
  "client": {
    "company": "A Corp",
    "business_number": "123-45-67890"
  },
  "items": [
    {
      "description": "서비스 개발 용역",
      "quantity": 1,
      "unit_price": 5000000,
      "amount": 5000000
    }
  ],
  "totals": {
    "subtotal": 5000000,
    "vat": 500000,
    "total": 5500000
  },
  "status": "issued",
  "created_at": "2026-01-15T10:00:00Z"
}
```

### Markdown 출력

```markdown
# 청 구 서

**문서번호**: INV-202601-0001
**발행일**: 2026-01-15
**결제기한**: 2026-02-14

---

## 공급자

| 항목 | 내용 |
|------|------|
| 상호 | Solo Unicorn Corp |
| 사업자번호 | 000-00-00000 |

## 공급받는자

| 항목 | 내용 |
|------|------|
| 상호 | A Corp |
| 사업자번호 | 123-45-67890 |

## 청구 내역

| 품목 | 수량 | 단가 | 금액 |
|------|------|------|------|
| 서비스 개발 용역 | 1 | ₩5,000,000 | ₩5,000,000 |

## 합계

| 항목 | 금액 |
|------|------|
| 공급가액 | ₩5,000,000 |
| 부가세 | ₩500,000 |
| **합계** | **₩5,500,000** |

## 입금 정보

- 은행: OO은행
- 계좌: 000-0000-0000
- 예금주: Solo Unicorn Corp
```

## 연동

- **세금계산서**: 청구서 발행 시 세금계산서 동시 발행 옵션
- **원장**: 청구서 발행 시 매출채권 자동 기록
- **알림**: 결제기한 임박 시 Slack 알림

---

Version: 1.0.0
Last Updated: 2026-01-27
