---
name: tax-invoice-popbill
description: 팝빌 API 기반 세금계산서 자동 발행/수집 스킬
model: inherit
quality_tier: implementation
triggers:
  - "세금계산서"
  - "홈택스"
  - "발행"
  - "tax invoice"
---

# Tax Invoice Skill (팝빌 API)

팝빌 API를 활용한 세금계산서 자동 발행 및 수집 스킬입니다.

## 핵심 원칙

- **자동화**: 월말 세금계산서 일괄 발행
- **정확성**: 매출-매입 대사 자동 검증
- **컴플라이언스**: 홈택스 자동 전송

## 사전 준비

### 1. 팝빌 가입 및 API 키 발급

```bash
# 환경변수 설정
export POPBILL_LINK_ID="your_link_id"
export POPBILL_SECRET_KEY="your_secret_key"
export POPBILL_CORP_NUM="1234567890"  # 사업자번호
```

### 2. MCP 설정 (권장)

```json
// .mcp.json
{
  "mcpServers": {
    "popbill": {
      "command": "popbill-mcp",
      "env": {
        "POPBILL_LINK_ID": "${POPBILL_LINK_ID}",
        "POPBILL_SECRET_KEY": "${POPBILL_SECRET_KEY}"
      }
    }
  }
}
```

## 기능

### 1. 매출 세금계산서 발행

```python
# 개념적 구조
def issue_tax_invoice(sale: Sale) -> TaxInvoice:
    """
    매출 세금계산서 발행

    Args:
        sale: 매출 정보 (거래처, 금액, 품목)

    Returns:
        TaxInvoice: 발행된 세금계산서
    """
    invoice = TaxInvoice(
        # 공급자 (우리 회사)
        invoicer_corp_num=COMPANY_CORP_NUM,
        invoicer_corp_name=COMPANY_NAME,
        invoicer_ceo_name=CEO_NAME,

        # 공급받는자 (거래처)
        invoicee_corp_num=sale.customer.corp_num,
        invoicee_corp_name=sale.customer.name,
        invoicee_ceo_name=sale.customer.ceo_name,

        # 거래 정보
        supply_value=sale.amount,  # 공급가액
        tax_amount=sale.amount * 0.1,  # 부가세
        total_amount=sale.amount * 1.1,  # 합계

        # 품목
        items=[
            InvoiceItem(
                name=item.name,
                quantity=item.quantity,
                unit_price=item.price,
                amount=item.total
            )
            for item in sale.items
        ]
    )

    # 팝빌 API로 발행
    result = popbill.issue(invoice)

    # 홈택스 전송
    popbill.send_to_nts(result.nts_confirm_num)

    return result
```

### 2. 매입 세금계산서 수집

```python
def collect_purchase_invoices(year_month: str) -> List[TaxInvoice]:
    """
    홈택스에서 매입 세금계산서 자동 수집

    Args:
        year_month: 수집 대상 월 (YYYY-MM)

    Returns:
        List[TaxInvoice]: 수집된 세금계산서 목록
    """
    start_date = f"{year_month}-01"
    end_date = last_day_of_month(year_month)

    invoices = popbill.get_purchase_invoices(
        corp_num=COMPANY_CORP_NUM,
        start_date=start_date,
        end_date=end_date
    )

    return invoices
```

### 3. 매출-매입 대사

```python
def reconcile_invoices(year_month: str) -> ReconciliationReport:
    """
    매출 세금계산서와 실제 매출 대사

    Returns:
        ReconciliationReport: 대사 결과 리포트
    """
    # 발행한 세금계산서
    issued = get_issued_invoices(year_month)

    # 실제 매출 기록
    sales = get_sales_records(year_month)

    # 대사
    matched = []
    unmatched_invoices = []
    unmatched_sales = []

    for invoice in issued:
        sale = find_matching_sale(invoice, sales)
        if sale:
            matched.append((invoice, sale))
        else:
            unmatched_invoices.append(invoice)

    for sale in sales:
        if not any(s == sale for _, s in matched):
            unmatched_sales.append(sale)

    return ReconciliationReport(
        matched=matched,
        unmatched_invoices=unmatched_invoices,
        unmatched_sales=unmatched_sales,
        discrepancy_amount=calculate_discrepancy(unmatched_invoices, unmatched_sales)
    )
```

## 워크플로우

### 월말 세금계산서 발행 자동화

```
┌─────────────────────────────────────────────────────────────────┐
│                Monthly Tax Invoice Workflow                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   매월 말일 - 5일                                                │
│        │                                                        │
│        ▼                                                        │
│   ┌─────────────────┐                                           │
│   │ 매출 데이터 집계 │                                           │
│   │ (ledger.json)   │                                           │
│   └────────┬────────┘                                           │
│            │                                                    │
│            ▼                                                    │
│   ┌─────────────────┐                                           │
│   │ 거래처별 그룹핑  │                                           │
│   └────────┬────────┘                                           │
│            │                                                    │
│            ▼                                                    │
│   ┌─────────────────┐                                           │
│   │ 세금계산서 생성  │ ← 팝빌 API                                │
│   └────────┬────────┘                                           │
│            │                                                    │
│            ▼                                                    │
│   ┌─────────────────┐                                           │
│   │ 검토 요청       │ → Slack 알림                              │
│   │ (Draft 상태)    │                                           │
│   └────────┬────────┘                                           │
│            │                                                    │
│            ▼                                                    │
│   [인간 승인] ─── 거부 → 수정 후 재생성                          │
│            │                                                    │
│            ▼                                                    │
│   ┌─────────────────┐                                           │
│   │ 정식 발행       │                                           │
│   └────────┬────────┘                                           │
│            │                                                    │
│            ▼                                                    │
│   ┌─────────────────┐                                           │
│   │ 홈택스 전송     │                                           │
│   └────────┬────────┘                                           │
│            │                                                    │
│            ▼                                                    │
│   발행 완료 알림 (Slack)                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## CLI 사용법

### 세금계산서 발행

```bash
# 특정 거래처에 세금계산서 발행
/tax-invoice issue \
  --customer "거래처명" \
  --amount 1000000 \
  --items "서비스 이용료"

# 월간 일괄 발행 (Draft)
/tax-invoice batch --month 2026-01 --draft

# Draft 검토 후 발행 확정
/tax-invoice confirm --month 2026-01
```

### 매입 세금계산서 수집

```bash
# 홈택스에서 매입 세금계산서 수집
/tax-invoice collect --month 2026-01

# 대사 리포트 생성
/tax-invoice reconcile --month 2026-01
```

## 출력 파일

```
/operations/finance/invoices/2026-01/
├── sales/                      # 매출 세금계산서
│   ├── INV-2026010001.json    # 세금계산서 데이터
│   ├── INV-2026010001.pdf     # PDF 사본
│   └── ...
│
├── purchase/                   # 매입 세금계산서
│   ├── PUR-2026010001.json
│   └── ...
│
├── reconciliation.json         # 대사 결과
└── summary.md                  # 월간 요약
```

## 비용

| 항목 | 팝빌 요금 |
|-----|----------|
| 세금계산서 발행 | 100원/건 |
| 홈택스 전송 | 무료 |
| 매입 수집 | 무료 |

*월 100건 기준: ~10,000원*

## 에러 처리

| 에러 코드 | 원인 | 해결 |
|----------|------|------|
| -11000001 | 인증 실패 | API 키 확인 |
| -12000004 | 사업자번호 오류 | 거래처 정보 확인 |
| -14000002 | 필수 항목 누락 | 입력값 검증 |
| -99999999 | 서버 오류 | 재시도 (3회) |

## 보안 고려사항

```yaml
security:
  # API 키 관리
  - 환경변수로만 관리
  - 절대 소스코드에 하드코딩 금지
  - 정기적 키 로테이션 (분기별)

  # 접근 제어
  - 발행 권한: 관리자만
  - 조회 권한: 재무 담당자

  # 감사 로그
  - 모든 발행/취소 기록
  - IP 주소 기록
  - 승인자 기록
```

---

Version: 1.0.0
Last Updated: 2026-01-27
