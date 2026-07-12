---
name: receipt-ocr-gemini
description: Gemini CLI 기반 영수증/청구서 OCR 스킬
model: inherit
quality_tier: fast_scan
triggers:
  - "영수증"
  - "OCR"
  - "스캔"
  - "receipt"
---

# Receipt OCR Skill (Gemini CLI)

Gemini CLI를 활용한 무료 영수증 OCR 처리 스킬입니다.

## 핵심 원칙

- **비용 최소화**: Gemini CLI 무료 티어 (1,000건/일) 우선 사용
- **정확도 보장**: 복잡한 문서는 Claude Vision 폴백
- **구조화된 출력**: 항상 JSON 형태로 추출

## 실행 방법

### 1. 단일 영수증 처리

```bash
gemini "이 영수증에서 다음 정보를 JSON으로 추출해줘:
{
  \"vendor\": \"거래처명\",
  \"business_number\": \"사업자번호 (있으면)\",
  \"date\": \"거래일 (YYYY-MM-DD)\",
  \"items\": [
    {\"name\": \"품목명\", \"quantity\": 수량, \"unit_price\": 단가, \"amount\": 금액}
  ],
  \"subtotal\": 공급가액,
  \"vat\": 부가세,
  \"total\": 총액,
  \"payment_method\": \"결제수단 (카드/현금/계좌이체)\",
  \"card_last4\": \"카드 끝 4자리 (카드결제시)\"
}" --image "$IMAGE_PATH"
```

### 2. 배치 처리

```bash
#!/bin/bash
# process-receipts.sh

INPUT_DIR="${1:-./receipts}"
OUTPUT_DIR="${2:-./receipts/processed}"

mkdir -p "$OUTPUT_DIR"

for img in "$INPUT_DIR"/*.{jpg,jpeg,png,pdf}; do
  [ -f "$img" ] || continue

  filename=$(basename "$img")
  output_file="$OUTPUT_DIR/${filename%.*}.json"

  echo "Processing: $filename"

  gemini "영수증 JSON 추출 (vendor, date, items, total, vat)" \
    --image "$img" \
    --output json > "$output_file"

  # 1초 대기 (rate limit 방지)
  sleep 1
done

echo "Processed $(ls -1 $OUTPUT_DIR/*.json 2>/dev/null | wc -l) receipts"
```

### 3. Claude Vision 폴백 (복잡한 문서)

```bash
# OCR 결과가 불완전한 경우 Claude로 재처리
if [ "$CONFIDENCE" -lt 80 ]; then
  claude "이 영수증을 상세히 분석해줘" --file "$IMAGE_PATH"
fi
```

## 출력 스키마

```json
{
  "ocr_metadata": {
    "model": "gemini-cli",
    "timestamp": "2026-01-27T10:30:00Z",
    "confidence": 95,
    "source_file": "receipt-001.jpg"
  },
  "vendor": {
    "name": "스타벅스 강남역점",
    "business_number": "123-45-67890",
    "address": "서울시 강남구..."
  },
  "transaction": {
    "date": "2026-01-27",
    "time": "14:30:00",
    "receipt_number": "R2026012700001"
  },
  "items": [
    {
      "name": "아메리카노 톨",
      "quantity": 2,
      "unit_price": 4500,
      "amount": 9000
    }
  ],
  "amounts": {
    "subtotal": 8182,
    "vat": 818,
    "total": 9000
  },
  "payment": {
    "method": "card",
    "card_company": "삼성카드",
    "card_last4": "1234",
    "approval_number": "12345678"
  },
  "category_suggestion": "복리후생비"
}
```

## 에러 처리

| 에러 | 원인 | 해결 |
|-----|------|------|
| `이미지를 읽을 수 없습니다` | 파일 손상/형식 오류 | 파일 확인 및 재업로드 |
| `텍스트를 인식할 수 없습니다` | 이미지 품질 불량 | 재촬영 또는 Claude Vision 폴백 |
| `Rate limit exceeded` | 일일 한도 초과 | Claude Vision으로 전환 |
| `필수 필드 누락` | OCR 부분 실패 | 수동 입력 요청 |

## 비용 분석

| 방식 | 월 1,000건 | 월 5,000건 |
|-----|-----------|-----------|
| 외부 OCR (CLOVA 등) | $50-500 | $250-2,500 |
| Gemini CLI (무료 티어) | $0 | $0* |
| Claude Vision (폴백) | ~$2 | ~$10 |

*5,000건의 경우 4,000건은 Claude Vision 필요 (~$8)

## 통합 예시

```python
# finance-orchestrator 내부에서 호출
async def process_receipt(image_path: str) -> dict:
    # 1. Gemini CLI로 OCR 시도
    result = await gemini_ocr(image_path)

    # 2. 신뢰도 검증
    if result.get('confidence', 0) < 80:
        # Claude Vision 폴백
        result = await claude_vision_ocr(image_path)

    # 3. 분류 스킬로 전달
    classified = await expense_classifier(result)

    return classified
```

---

Version: 1.0.0
Last Updated: 2026-01-27
