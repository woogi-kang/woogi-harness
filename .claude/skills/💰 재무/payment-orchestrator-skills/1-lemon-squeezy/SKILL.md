---
name: lemon-squeezy
description: Lemon Squeezy 글로벌 결제 및 MoR(Merchant of Record) 연동 스킬
model: inherit
quality_tier: implementation
triggers:
  - "Lemon Squeezy"
  - "레몬"
  - "글로벌 결제"
  - "해외 결제"
  - "MoR"
---

# Lemon Squeezy Skill

Lemon Squeezy를 통한 글로벌 결제 및 구독 관리 스킬입니다.

## 핵심 특징

| 특징 | 설명 |
|------|------|
| **MoR (Merchant of Record)** | 세금 계산/납부를 Lemon Squeezy가 대행 |
| **글로벌 결제** | 100+ 국가, 다중 통화 지원 |
| **자동 세금 처리** | EU VAT, US Sales Tax 자동 |
| **간편 연동** | Checkout Overlay, API |

## Lemon Squeezy vs Stripe

| 항목 | Lemon Squeezy | Stripe |
|------|---------------|--------|
| 한국 사업자 | O (MoR) | X |
| 수수료 | 5% + $0.50 | 2.9% + $0.30 |
| 세금 처리 | 자동 (MoR) | 수동 |
| EU VAT | 자동 납부 | 직접 처리 |
| 설정 복잡도 | 낮음 | 높음 |
| **1인 유니콘 권장** | **O** | X |

## API 구조

### 인증

```bash
# API 요청 헤더
Authorization: Bearer {LEMON_SQUEEZY_API_KEY}
Accept: application/vnd.api+json
Content-Type: application/vnd.api+json
```

### 핵심 엔드포인트

```yaml
base_url: https://api.lemonsqueezy.com/v1

endpoints:
  # 제품
  products:
    list: GET /products
    get: GET /products/{id}

  # 가격 (Variants)
  variants:
    list: GET /variants
    get: GET /variants/{id}

  # 체크아웃
  checkouts:
    create: POST /checkouts
    get: GET /checkouts/{id}

  # 구독
  subscriptions:
    list: GET /subscriptions
    get: GET /subscriptions/{id}
    update: PATCH /subscriptions/{id}
    cancel: DELETE /subscriptions/{id}

  # 고객
  customers:
    list: GET /customers
    get: GET /customers/{id}

  # 주문
  orders:
    list: GET /orders
    get: GET /orders/{id}

  # Webhook
  webhooks:
    list: GET /webhooks
    create: POST /webhooks
```

## 워크플로우

### 1. 제품 및 가격 설정

```yaml
product_setup:
  step_1_create_product:
    - Lemon Squeezy 대시보드 접속
    - Products → New Product
    - 제품명, 설명, 이미지 설정

  step_2_create_variants:
    - 가격 옵션 (Variant) 추가
    - 예: Monthly $19, Annual $190
    - 구독 또는 일회성 선택

  step_3_get_variant_id:
    # API로 Variant ID 조회
    endpoint: GET /variants?filter[product_id]={product_id}
    response: |
      {
        "data": [{
          "id": "123456",
          "attributes": {
            "name": "Pro Monthly",
            "price": 1900,
            "interval": "month"
          }
        }]
      }
```

### 2. 체크아웃 생성

```yaml
checkout_creation:
  # API로 체크아웃 URL 생성
  request:
    method: POST
    endpoint: /checkouts
    body: |
      {
        "data": {
          "type": "checkouts",
          "attributes": {
            "custom_price": null,
            "product_options": {
              "redirect_url": "https://yourapp.com/success",
              "receipt_thank_you_note": "구독해주셔서 감사합니다!"
            },
            "checkout_data": {
              "email": "customer@example.com",
              "custom": {
                "user_id": "usr_123"
              }
            }
          },
          "relationships": {
            "store": {
              "data": {
                "type": "stores",
                "id": "{STORE_ID}"
              }
            },
            "variant": {
              "data": {
                "type": "variants",
                "id": "{VARIANT_ID}"
              }
            }
          }
        }
      }

  response: |
    {
      "data": {
        "attributes": {
          "url": "https://yourstore.lemonsqueezy.com/checkout/..."
        }
      }
    }

  # 프론트엔드에서 URL로 리다이렉트 또는 Overlay 표시
```

### 3. Webhook 처리

```yaml
webhook_events:
  # 중요 이벤트
  subscription_created:
    trigger: 새 구독 시작
    action:
      - 사용자 플랜 업데이트
      - 환영 이메일 발송
      - MRR 기록

  subscription_updated:
    trigger: 플랜 변경/갱신
    action:
      - 플랜 정보 업데이트
      - 알림

  subscription_cancelled:
    trigger: 구독 취소
    action:
      - 서비스 종료 예약
      - 이탈 사유 수집
      - Churn 기록

  subscription_payment_success:
    trigger: 결제 성공
    action:
      - 기간 연장
      - 영수증 발송

  subscription_payment_failed:
    trigger: 결제 실패
    action:
      - Dunning 시작
      - 알림 발송

webhook_verification: |
  # 시그니처 검증
  const crypto = require('crypto');

  function verifyWebhook(payload, signature, secret) {
    const hmac = crypto.createHmac('sha256', secret);
    const digest = hmac.update(payload).digest('hex');
    return crypto.timingSafeEqual(
      Buffer.from(signature),
      Buffer.from(digest)
    );
  }
```

### 4. 구독 관리

```yaml
subscription_management:
  # 구독 조회
  get_subscription:
    endpoint: GET /subscriptions/{subscription_id}
    response_fields:
      - status: active/cancelled/expired/past_due
      - renews_at: 다음 갱신일
      - ends_at: 종료일 (취소 시)
      - card_brand: 카드 종류
      - card_last_four: 카드 마지막 4자리

  # 구독 업데이트 (플랜 변경)
  update_subscription:
    endpoint: PATCH /subscriptions/{id}
    body: |
      {
        "data": {
          "type": "subscriptions",
          "id": "{id}",
          "attributes": {
            "variant_id": "{new_variant_id}",
            "invoice_immediately": true
          }
        }
      }

  # 구독 일시정지
  pause_subscription:
    endpoint: PATCH /subscriptions/{id}
    body: |
      {
        "data": {
          "type": "subscriptions",
          "id": "{id}",
          "attributes": {
            "pause": {
              "mode": "free",
              "resumes_at": "2026-03-01T00:00:00Z"
            }
          }
        }
      }

  # 구독 취소
  cancel_subscription:
    endpoint: DELETE /subscriptions/{id}
    # 기본: 현재 기간 종료 시 취소
    # 즉시 취소하려면 ?immediately=true
```

## 프론트엔드 연동

### Checkout Overlay (권장)

```html
<!-- Lemon Squeezy JS 로드 -->
<script src="https://app.lemonsqueezy.com/js/lemon.js" defer></script>

<!-- 결제 버튼 -->
<a href="https://yourstore.lemonsqueezy.com/checkout/buy/{variant_id}"
   class="lemonsqueezy-button">
  Subscribe Now
</a>

<script>
  // Overlay 모드로 열기
  window.createLemonSqueezy();

  // 또는 커스텀 버튼
  document.getElementById('buy-btn').addEventListener('click', () => {
    LemonSqueezy.Url.Open('https://yourstore.lemonsqueezy.com/checkout/...');
  });
</script>
```

### 커스텀 파라미터 전달

```javascript
// 체크아웃 URL에 파라미터 추가
const checkoutUrl = new URL('https://yourstore.lemonsqueezy.com/checkout/buy/123');
checkoutUrl.searchParams.set('checkout[email]', 'user@example.com');
checkoutUrl.searchParams.set('checkout[custom][user_id]', 'usr_123');
checkoutUrl.searchParams.set('checkout[custom][plan]', 'pro');

// Overlay로 열기
LemonSqueezy.Url.Open(checkoutUrl.toString());
```

## 환경 설정

```bash
# .env
LEMON_SQUEEZY_API_KEY=your_api_key
LEMON_SQUEEZY_STORE_ID=your_store_id
LEMON_SQUEEZY_WEBHOOK_SECRET=your_webhook_secret

# Product/Variant IDs
LEMON_SQUEEZY_PRO_MONTHLY_VARIANT=123456
LEMON_SQUEEZY_PRO_ANNUAL_VARIANT=123457
```

## CLI 사용법

```bash
# 구독 조회
/lemon-squeezy subscriptions list

# 특정 구독 상세
/lemon-squeezy subscription get {id}

# 구독 취소
/lemon-squeezy subscription cancel {id}

# 수익 요약
/lemon-squeezy revenue summary --month 2026-01
```

## 출력 포맷

```json
{
  "provider": "lemon_squeezy",
  "subscription": {
    "id": "sub_123",
    "status": "active",
    "customer": {
      "email": "user@example.com",
      "name": "John Doe"
    },
    "plan": {
      "name": "Pro Monthly",
      "price": 19.00,
      "currency": "USD",
      "interval": "month"
    },
    "billing": {
      "card_brand": "visa",
      "card_last_four": "4242",
      "next_payment_date": "2026-02-27"
    },
    "created_at": "2026-01-27T10:00:00Z"
  }
}
```

## 가격 전략 팁

```yaml
pricing_tips:
  # 연간 할인
  annual_discount:
    monthly: $19/month
    annual: $190/year  # 2개월 무료 (17% 할인)
    reason: "현금흐름 개선 + 이탈 감소"

  # 지역별 가격 (PPP)
  ppp_pricing:
    enabled: true
    # Lemon Squeezy가 자동으로 PPP 적용 가능
    discount_regions:
      - region: "South America"
        discount: 30%
      - region: "Southeast Asia"
        discount: 40%

  # 업그레이드 인센티브
  upgrade_incentive:
    from: "Free"
    to: "Pro"
    offer: "첫 달 50% 할인"
    promo_code: "UPGRADE50"
```

---

Version: 1.0.0
Last Updated: 2026-01-27
