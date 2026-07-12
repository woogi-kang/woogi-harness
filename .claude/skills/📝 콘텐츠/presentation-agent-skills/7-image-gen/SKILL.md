---
name: ppt-image-gen
description: "PPT 생성형 이미지 오케스트레이션 — Gongnyang image-prompt로 컴파일하고 Codex gpt-image-2로 생성"
metadata:
  category: "📝 콘텐츠"
  version: "3.0.0"
  tags: "presentation, image-generation, gongnyang, gpt-image-2"
---

# PPT Image Generation

프레젠테이션에 필요한 생성형 raster asset의 계획, 생성, 배치, manifest를
관리합니다. Prompt engineering은 이 스킬의 책임이 아닙니다. 모든 prompt는
vendored `image-prompt`가 작성합니다.

## 단일 실행 경로

```text
slide claim + visual contract + deck evidence
→ `.claude/skills/image-prompt/SKILL.md`
→ C6 또는 C12와 필요한 upstream reference
→ `check_prompt.mjs`
→ Codex `$imagegen`
→ `gpt-image-2`
→ visual QA + asset manifest
```

- 다른 생성 provider나 model fallback을 사용하지 않습니다.
- `image-prompt`의 `full_prompt`를 요약, 번역, suffix 추가, negative prompt
  추가 없이 그대로 전달합니다.
- Codex image generation이 없으면 `blocked_imagegen_not_run`으로 중단합니다.
- 투명 배경은 지원하지 않습니다. Opaque 결과로 설계하거나 중단합니다.

## 생성 대상

- cover/chapter hero
- concept metaphor와 scenario visual
- 생성형 infographic 또는 diagram base
- risk/service-flow/product mockup visual
- 반복 가능한 raster motif와 object illustration

## 생성하지 않는 대상

- 실제 제품 UI: browser/app screenshot
- 정확한 숫자, 축, 표, 차트: native chart/table
- 편집 가능한 한국어 본문: PPT/HTML native text
- 기존 logo/icon/source asset: 원본 사용
- deterministic SVG/vector: code/vector tooling

Native text를 생성 raster 위에 덧씌우지 않습니다. 읽어야 하는 정보는 별도
layout region에 두고, 생성 이미지 안의 문구는 Gongnyang text rendering
규칙으로 생성합니다. 문구가 틀리면 prompt를 고쳐 다시 생성합니다.

## Workflow

### 1. Visual contract

이미지마다 다음을 먼저 확정합니다.

```json
{
  "slide": 3,
  "claim": "이 이미지가 증명해야 하는 주장",
  "category_hint": "C6",
  "must_show": ["구체 요소 1", "구체 요소 2"],
  "project_evidence": ["brand token", "source screenshot"],
  "viewport_or_slot": "16:9",
  "acceptance_check": "이미지만 보아도 주장을 설명할 수 있다"
}
```

### 2. Compile

1. `image-prompt`를 활성화합니다.
2. slide/deck이면 C12, 설명 도해이면 C6을 우선 검토하되 최종 라우팅은
   Gongnyang 원본에 맡깁니다.
3. 한 asset마다 하나의 JSONL record를 만듭니다.
4. 배치 record는 다음 명령으로 검증합니다.

```bash
node .claude/skills/image-prompt/scripts/check_prompt.mjs --jsonl prompts.jsonl
```

`ok: false`면 생성하지 않습니다.

### 3. Generate

record의 `full_prompt`를 Codex `$imagegen` host tool의 `prompt` 필드로
매핑합니다. host schema에 없는 `model`, `full_prompt`, `ar`, `size`,
`quality` 인자를 만들지 않습니다. 요청 비율과 크기는 prompt record에
보존하고 실제 결과 크기를 검수합니다. 한 호출은 한 이미지를 생성하며 원문
brief를 다시 붙이지 않습니다.

### 4. Place

- project-bound 파일은 덱의 `images/`에 저장합니다.
- generated-image temp 경로만 문서에서 참조하지 않습니다.
- 정확한 pixel dimension, crop, file size를 확인합니다.
- 생성 raster에 text/logo overlay를 추가하지 않습니다.

### 5. Review

- claim과 must-show 충족
- 깨진 글자, 임의 logo, watermark, 추가 피사체
- deck register, palette, crop 일관성
- 실제 발표 크기의 가독성
- adjacent native text와의 중복/충돌

실패한 asset만 Gongnyang prompt를 수정해 재생성합니다.

## Manifest

```json
{
  "slide": 3,
  "asset_path": "images/03-service-flow.webp",
  "compiler": "image-prompt@2.3.0",
  "upstream_commit": "d1cd1dd3e77f7e12e2fed982fd738cc1ea880598",
  "generator": "image_gen__imagegen",
  "required_model": "gpt-image-2",
  "model_binding": "trusted-host-fixed",
  "local_model_verification": "unavailable",
  "host_reported_model": null,
  "generation_assurance": "generated_under_trusted_host_contract",
  "prompt_record": "prompts.jsonl#C6-SERVICE-001",
  "visual_contract": "visual-contracts.json#slide-3",
  "review_status": "approved"
}
```

`required_model`은 실행 정책이고 `generation_assurance`는 Codex host 계약에
따랐다는 provenance입니다. host가 실제 모델 식별자를 반환하지 않으므로
`model` 필드나 `verified_gpt_image_2` claim을 기록하지 않습니다.

## Verification

```bash
bash scripts/verify-gongnyang-prompt-kit.sh
```

`THEME-PROMPTS.md` 같은 로컬 prompt library는 사용하지 않습니다. Deck
theme은 prompt template이 아니라 `image-prompt`에 전달할 evidence입니다.
