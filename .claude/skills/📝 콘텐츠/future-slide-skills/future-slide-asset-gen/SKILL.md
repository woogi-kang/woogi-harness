---
name: future-slide-asset-gen
description: "Future Slide 생성형 asset 오케스트레이션 — Gongnyang image-prompt, Codex gpt-image-2, manifest와 QA를 연결하는 스킬."
argument-hint: "[asset-brief]"
metadata:
  category: "📝 콘텐츠"
  version: "0.1.0"
  tags: "presentation, image-generation, gongnyang, gpt-image-2, assets, future-slide"
  author: "woogi"
---

# Future Slide Asset Gen

Future Slide HTML 덱에 들어갈 보조 이미지를 생성합니다. 전체 슬라이드 이미지를 생성하는 스킬이 아닙니다.

## 품질 원칙

이미지는 장식이 아니라 **슬라이드 주장의 증거 또는 설명 장치**여야 합니다.

금지:
- 의미 없는 추상 블록, 랜덤 네트워크, 범용 대시보드 느낌의 filler graphic
- Gongnyang/Codex image generation을 실행하지 않았는데 "생성 이미지"처럼 보이는 local placeholder를 납품용으로 만드는 것
- 텍스트를 제거한 결과, 무엇을 설명하는지 알 수 없는 이미지

대체:
- PPT/HTML 덱에서 생성형 비주얼로 분류되는 asset은 `image-prompt`로 컴파일하고 Codex `$imagegen`(`gpt-image-2`)으로 생성합니다.
- 한국어 라벨, 숫자, 표, 축, 설명문이 편집 가능해야 하면 native layout의 별도 영역으로 분리합니다. 생성 raster 위에는 덧씌우지 않습니다.
- Codex `$imagegen`을 실제 실행할 수 없으면 `status: "blocked_imagegen_not_run"`로 기록하고, 다른 provider나 placeholder로 대체하지 않습니다.
- 장식 이미지가 필요할 정도로 메시지가 약하면, 이미지를 만들지 말고 슬라이드 구조와 카피를 다시 설계합니다.

## 사용 기준

사용:
- S22 hero visual 또는 챕터 오프너
- S15/S16 이미지 slot처럼 텍스트를 방해하지 않는 보조 visual
- 추상 개념을 구체적 장면으로 바꾸는 concept metaphor
- 학습자, 운영자, 서비스 화면의 상황을 보여주는 scenario visual
- 환각, 최신성 부족, 편향, 보안 위험 같은 risk visual
- 실제 스크린샷이 아닌 product/service mockup
- 텍스트 없는 아이콘 세트
- 추상적 시스템 다이어그램 배경
- 제품/상황/개념 illustration

사용하지 않음:
- 한국어 텍스트가 포함된 전체 슬라이드 이미지
- 읽어야 하는 표, 축 라벨, 수치, 주석이 들어간 이미지
- 수정 가능한 PPTX가 필요한 산출물의 본문 영역
- 정확한 단계명, 연결선, 의사결정 기준처럼 발표자가 직접 편집해야 하는 구조
- 브랜드 로고, 기존 아이콘 시스템, 실제 제품 스크린샷처럼 원본성이 중요한 시각 요소

분류 원칙:
- 인포그래픽으로 분류한 시각 요소는 `image-prompt`의 C6/C12 경로로 만든 bitmap asset을 사용합니다.
- 정확한 순서, 수치, 한국어 라벨이 핵심인 단계 카드와 차트는 `native-label-region` 또는 `chart/table`로 분류합니다.
- 생성형 asset과 native 정보는 겹쳐 합성하지 않고 별도 layout region으로 구성합니다.

## Codex Image Generation

생성 경로는 `image-prompt` → validator → Codex `$imagegen` host tool
(`gpt-image-2` required host contract) 하나입니다.

원칙:
- Gongnyang이 컴파일한 `full_prompt`만 Codex host tool의 `prompt` 필드로 매핑합니다.
- 다른 생성 provider나 model fallback을 사용하지 않습니다.
- imagegen 스킬의 저장 규칙을 따른 뒤, project-bound asset은 반드시 덱의 `images/` 아래로 복사합니다.
- 한 번에 batch 생성하지 않고, asset 또는 page를 하나씩 생성합니다.
- 각 생성물은 육안 검수 후 workspace의 `images/` 아래로 복사합니다.
- 생성하지 않은 placeholder/fallback 이미지는 production visual로 인정하지 않습니다.

저장 규칙:
- asset image: `images/<slide-number>-<semantic-name>.png`
- page image: `page_<n>.png`
- manifest에는 `compiler`, `generator`, `required_model: "gpt-image-2"`,
  `model_binding: "trusted-host-fixed"`, `local_model_verification: "unavailable"`,
  `host_reported_model: null`,
  `generation_assurance: "generated_under_trusted_host_contract"`를 기록합니다.
  `model` 필드는 실제 모델을 로컬에서 확인했다는 오해를 만들므로 금지합니다.
- 실행하지 못한 경우에는 `status: "blocked_imagegen_not_run"`로 기록합니다.

## Prompt 계약

이 스킬은 prompt 문구, suffix, negative prompt, style keyword를 만들지
않습니다. Slot, claim, deck palette, 실제 evidence를 `image-prompt`에 전달하고
원본이 반환한 prompt를 수정 없이 사용합니다. `s22-hero-21x9`,
`s15-grid-21x9`, `s16-brief-16x10` 같은 slot 정보는 Gongnyang compiler의
입력이지 별도 prompt template이 아닙니다.

## Visual Contract

이미지를 만들기 전에 manifest에 들어갈 visual contract를 먼저 작성합니다.

```json
{
  "slide": 3,
  "slot": "s22-hero-21x9",
  "claim": "브랜드 공식 근거가 AI 답변 표면으로 연결된다",
  "must_show": [
    "왼쪽의 근거 저장소",
    "가운데의 연결/인용 경로",
    "오른쪽의 답변 카드 표면"
  ],
  "must_not_show": [
    "읽어야 하는 텍스트",
    "무작위 추상 도형",
    "브랜드 로고처럼 보이는 요소"
  ],
  "acceptance_check": "이미지를 보지 않고 alt만 읽어도 슬라이드 주장을 설명할 수 있어야 한다."
}
```

이 contract를 만족하지 못하면 이미지를 생성하지 않습니다.

## Asset manifest

이미지를 만들면 `asset_manifest.json`을 남깁니다.

```json
[
  {
    "slide": 3,
    "slot": "s22-hero-21x9",
    "file": "images/03-answer-engine-hero.png",
    "kind": "generated-raster",
    "compiler": "image-prompt@2.3.0",
    "generator": "image_gen__imagegen",
    "required_model": "gpt-image-2",
    "model_binding": "trusted-host-fixed",
    "local_model_verification": "unavailable",
    "host_reported_model": null,
    "generation_assurance": "generated_under_trusted_host_contract",
    "prompt_record": "prompts.jsonl#C12-SLIDE-003",
    "alt": "검색 결과가 답변 엔진으로 재구성되는 추상적 네트워크",
    "crop": "center center",
    "status": "generated_via_codex",
    "visual_contract": {
      "claim": "슬라이드에서 증명하려는 주장",
      "must_show": ["이미지 안에 보여야 하는 구체 요소"],
      "acceptance_check": "의미 검수 기준"
    }
  }
]
```

## QA 연결

생성 후 반드시 `future-slide-qa`를 실행합니다. QA에서 다음을 확인합니다.

- 이미지 파일 존재
- `data-image-slot` 존재
- `alt` 존재
- slot 비율과 frame class 일치
- 이미지가 텍스트를 대체하지 않음
