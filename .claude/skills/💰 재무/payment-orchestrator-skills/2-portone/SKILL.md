---
name: portone
description: 포트원(PortOne) 한국 통합 결제 연동 스킬
model: inherit
quality_tier: implementation
triggers:
  - "포트원"
  - "PortOne"
  - "국내 결제"
  - "한국 결제"
  - "PG"
  - "카드 결제"
---

# PortOne Skill

포트원(구 아임포트)을 통한 한국 통합 결제 연동 스킬입니다.

## 핵심 특징

| 특징 | 설명 |
|------|------|
| **PG 통합** | 20+ PG사 단일 API로 연동 |
| **간편결제** | 카카오페이, 네이버페이, 토스 등 |
| **정기결제** | 빌링키 기반 구독 결제 |
| **세금계산서** | 자동 발행 연동 가능 |

## 지원 결제 수단

```yaml
payment_methods:
  card:
    - 신용카드 (국내/해외)
    - 체크카드

  easy_pay:
    - 카카오페이
    - 네이버페이
    - 토스페이
    - 페이코
    - 삼성페이

  bank:
    - 실시간 계좌이체
    - 가상계좌

  mobile:
    - 휴대폰 소액결제

  other:
    - 상품권
    - 포인트
```

## API 구조

### V2 API (권장)

```yaml
base_url: https://api.portone.io

authentication:
  header: Authorization
  format: "PortOne {API_SECRET}"

endpoints:
  # 결제 요청
  payments:
    get: GET /payments/{payment_id}
    cancel: POST /payments/{payment_id}/cancel

  # 빌링키 (정기결제)
  billing_keys:
    get: GET /billing-keys/{billing_key}
    delete: DELETE /billing-keys/{billing_key}
    pay: POST /billing-keys/{billing_key}/payments

  # 본인인증
  identity_verifications:
    get: GET /identity-verifications/{verification_id}

  # 현금영수증
  cash_receipts:
    get: GET /cash-receipts/{cash_receipt_id}
```

## 워크플로우

### 1. SDK 설정

```html
<!-- 포트원 SDK 로드 -->
<script src="https://cdn.portone.io/v2/browser-sdk.js"></script>
```

```javascript
// 초기화
const portone = PortOne.create({
  storeId: "store-xxx",
});
```

### 2. 일반 결제

```javascript
// 결제 요청
async function requestPayment() {
  const response = await portone.requestPayment({
    storeId: "store-xxx",
    channelKey: "channel-xxx",  // PG 채널 키
    paymentId: `payment-${Date.now()}`,
    orderName: "Pro 플랜 구독",
    totalAmount: 29000,
    currency: "KRW",
    payMethod: "CARD",
    customer: {
      email: "customer@example.com",
      phoneNumber: "01012345678",
      fullName: "홍길동",
    },
    redirectUrl: "https://yourapp.com/payment/complete",
  });

  if (response.code) {
    // 에러 처리
    console.error(response.message);
    return;
  }

  // 서버에서 결제 검증
  await verifyPayment(response.paymentId);
}
```

### 3. 정기결제 (빌링키)

```yaml
subscription_flow:
  step_1_issue_billing_key:
    description: "빌링키 발급 (카드 등록)"
    code: |
      const response = await portone.requestIssueBillingKey({
        storeId: "store-xxx",
        channelKey: "channel-xxx",
        billingKeyMethod: "CARD",
        customer: {
          email: "customer@example.com"
        },
        redirectUrl: "https://yourapp.com/billing/complete"
      });

      // 발급된 billingKey 저장
      const billingKey = response.billingKey;

  step_2_store_billing_key:
    description: "빌링키 안전하게 저장"
    note: "billingKey는 민감정보, 암호화 저장 권장"

  step_3_schedule_payment:
    description: "서버에서 정기 결제 실행"
    code: |
      // POST https://api.portone.io/billing-keys/{billingKey}/payments
      {
        "payment": {
          "orderName": "Pro 플랜 월간 구독",
          "amount": {
            "total": 29000
          },
          "currency": "KRW"
        }
      }

  step_4_cron_job:
    description: "매월 결제일에 자동 실행"
    schedule: "0 0 1 * *"  # 매월 1일
```

### 4. 결제 검증 (서버)

```yaml
verification:
  description: "결제 완료 후 서버에서 검증 필수"

  request:
    method: GET
    endpoint: /payments/{paymentId}
    headers:
      Authorization: "PortOne {API_SECRET}"

  response: |
    {
      "id": "payment-xxx",
      "status": "PAID",
      "amount": {
        "total": 29000,
        "paid": 29000
      },
      "method": {
        "type": "PaymentMethodCard",
        "card": {
          "name": "신한카드",
          "number": "****-****-****-1234"
        }
      },
      "channel": {
        "pgProvider": "NICE"
      }
    }

  validation:
    - status == "PAID"
    - amount.paid == expected_amount
    - orderName == expected_order
```

### 5. 결제 취소/환불

```yaml
cancel_payment:
  full_cancel:
    method: POST
    endpoint: /payments/{paymentId}/cancel
    body: |
      {
        "reason": "고객 요청"
      }

  partial_cancel:
    method: POST
    endpoint: /payments/{paymentId}/cancel
    body: |
      {
        "amount": 10000,
        "reason": "부분 환불"
      }

  response: |
    {
      "cancellation": {
        "status": "SUCCEEDED",
        "cancelledAt": "2026-01-27T10:00:00Z",
        "cancelAmount": 29000
      }
    }
```

## Webhook 설정

```yaml
webhook_events:
  # 결제 완료
  payment.paid:
    action:
      - 주문 상태 업데이트
      - 서비스 활성화
      - 알림 발송

  # 결제 실패
  payment.failed:
    action:
      - 실패 로그 기록
      - 고객 알림
      - 재시도 안내

  # 결제 취소
  payment.cancelled:
    action:
      - 환불 처리
      - 서비스 비활성화

  # 가상계좌 입금 대기
  payment.virtual_account.issued:
    action:
      - 입금 안내 발송

  # 가상계좌 입금 완료
  payment.virtual_account.deposited:
    action:
      - 결제 완료 처리

webhook_verification: |
  // Webhook 시그니처 검증
  const crypto = require('crypto');

  function verifyWebhook(body, timestamp, signature, secret) {
    const message = `${timestamp}.${JSON.stringify(body)}`;
    const expected = crypto
      .createHmac('sha256', secret)
      .update(message)
      .digest('base64');
    return signature === expected;
  }
```

## PG사별 채널 설정

```yaml
pg_channels:
  # 신용카드 - 나이스페이먼츠
  nice_card:
    channelKey: "channel-key-xxx"
    pgProvider: "NICE"
    methods: ["CARD"]
    features:
      - 카드 할부
      - 무이자 할부

  # 카카오페이
  kakaopay:
    channelKey: "channel-key-yyy"
    pgProvider: "KAKAOPAY"
    methods: ["EASY_PAY"]
    features:
      - 간편결제
      - 정기결제

  # 토스페이먼츠
  tosspayments:
    channelKey: "channel-key-zzz"
    pgProvider: "TOSSPAYMENTS"
    methods: ["CARD", "EASY_PAY", "VIRTUAL_ACCOUNT"]
    features:
      - 통합 결제
      - 브랜드페이

  # 정기결제 전용
  subscription:
    channelKey: "channel-key-sub"
    pgProvider: "NICE"
    methods: ["CARD"]
    features:
      - 빌링키 발급
      - 자동 결제
```

## 환경 설정

```bash
# .env
PORTONE_STORE_ID=store-xxx
PORTONE_API_SECRET=your_api_secret
PORTONE_WEBHOOK_SECRET=your_webhook_secret

# 채널 키 (PG사별)
PORTONE_CHANNEL_CARD=channel-key-card
PORTONE_CHANNEL_KAKAOPAY=channel-key-kakao
PORTONE_CHANNEL_BILLING=channel-key-billing
```

## CLI 사용법

```bash
# 결제 조회
/portone payment get {payment_id}

# 결제 취소
/portone payment cancel {payment_id} --reason "고객 요청"

# 빌링키 조회
/portone billing-key get {billing_key}

# 정기결제 실행
/portone billing-key pay {billing_key} --amount 29000 --name "Pro 플랜"

# 일간 결제 현황
/portone summary --date 2026-01-27
```

## 세금계산서 연동

```yaml
tax_invoice:
  # 결제 완료 후 세금계산서 발행
  auto_issue:
    trigger: "payment.paid"
    condition: "customer.business_number exists"
    action:
      - 팝빌 API 호출
      - 세금계산서 발행
      - 이메일 발송

  # 필요 정보
  required_fields:
    - business_number   # 사업자번호
    - company_name      # 상호
    - ceo_name          # 대표자명
    - address           # 사업장 주소
    - email             # 수신 이메일
```

## 출력 포맷

```json
{
  "provider": "portone",
  "payment": {
    "id": "payment-xxx",
    "status": "PAID",
    "amount": {
      "total": 29000,
      "paid": 29000,
      "currency": "KRW"
    },
    "method": {
      "type": "CARD",
      "card": {
        "name": "신한카드",
        "number": "****-****-****-1234",
        "installment": 0
      }
    },
    "customer": {
      "email": "customer@example.com",
      "name": "홍길동"
    },
    "order": {
      "name": "Pro 플랜 구독",
      "id": "order-xxx"
    },
    "paid_at": "2026-01-27T10:00:00Z"
  }
}
```

## 에러 처리

```yaml
error_codes:
  # 결제 실패
  CARD_DECLINED:
    message: "카드 승인 거절"
    action: "다른 결제 수단 안내"

  INSUFFICIENT_BALANCE:
    message: "잔액 부족"
    action: "충전 또는 다른 카드 안내"

  CARD_EXPIRED:
    message: "카드 유효기간 만료"
    action: "카드 정보 업데이트 요청"

  # 시스템 에러
  PG_PROVIDER_ERROR:
    message: "PG사 오류"
    action: "잠시 후 재시도"

  NETWORK_ERROR:
    message: "네트워크 오류"
    action: "재시도"
```

---

Version: 1.0.0
Last Updated: 2026-01-27
