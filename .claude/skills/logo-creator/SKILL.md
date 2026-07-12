---
name: logo-creator
description: 로고·brand mark·favicon·app icon 제작 오케스트레이션. 생성형 concept은 Gongnyang image-prompt로 컴파일해 Codex gpt-image-2로 만들고, 선택·preview·crop·vector artifact를 관리합니다.
---

# Logo Creator

로고 제작의 discovery, 생성 option 관리, preview, 선택, deterministic
artifact 처리를 담당합니다. 이 스킬은 prompt를 작성하거나 model을 선택하지
않습니다.

## 범위

- 브랜드명, 업종, audience, 사용 surface, reference 수집
- logo/mark/app icon용 visual contract
- 생성 option과 반복 이력 관리
- HTML preview와 사용자 선택
- crop, resize, vector trace 등 후속 artifact 작업

배너는 `banner-design`, CIP는 `design`, UI는 `ui-styling`로 위임합니다.

## 생성형 경로

```text
brand brief + project evidence + exact copy
→ `image-prompt`
→ C8 branding mockup 또는 C9 icon routing
→ upstream validator
→ Codex `$imagegen`
→ `gpt-image-2`
```

- Gongnyang `full_prompt`만 Codex host tool의 `prompt` 필드로 매핑합니다.
- 자체 style keyword, prompt template, negative prompt를 추가하지 않습니다.
- 다른 생성 provider/model로 fallback하지 않습니다.
- 한 option은 한 prompt와 한 호출입니다.
- 투명 배경 생성은 지원하지 않습니다. Opaque 결과를 만들고 최종 사용처가
  필요로 하면 승인된 local artifact 단계에서 별도로 처리합니다.
- 생성 이미지의 글자를 코드로 덧씌우지 않습니다. 틀리면 prompt를 수정해
  다시 생성합니다.

## Workflow

### 1. Discovery

다음을 확인합니다.

1. 브랜드 또는 프로젝트명과 정확한 표기
2. 업종, audience, positioning
3. mark/wordmark/emblem/app icon 중 필요한 surface
4. 기존 brand token과 실제 reference
5. 컬러와 사용 금지 요소
6. 최종 파일 형식과 최소 표시 크기

BM25 검색은 visual contract를 만들기 위한 evidence 수집에만 사용합니다.
검색 결과를 local prompt template로 조립하지 않습니다.

### 2. Compile options

`image-prompt`가 제공하는 category, look preset, concept axis를 그대로
사용합니다. 여러 시안이 필요하면 upstream concept-axis로 각 option을
분리하고 JSONL 한 줄당 한 이미지를 만듭니다.

```bash
node .claude/skills/image-prompt/scripts/check_prompt.mjs --jsonl prompts.jsonl
```

### 3. Generate and preview

검증된 record를 순차적으로 Codex `$imagegen`에 전달합니다. 결과는 다음처럼
project 아래에 둡니다.

```text
.skill-output/logo-creator/<yyyy-mm-dd-brand>/
├── prompts.jsonl
├── asset-manifest.json
├── logo-01.png
├── logo-02.png
└── preview.html
```

`scripts/batch.py`는 이미 생성된 파일의 preview와 manifest만 구성합니다.
이미지 생성이나 prompt 변형을 수행하지 않습니다.

```bash
python3 .claude/skills/logo-creator/scripts/batch.py \
  --output-dir .skill-output/logo-creator/<yyyy-mm-dd-brand> \
  --count 8
```

### 4. Iterate

선택된 option과 구체 피드백을 다시 `image-prompt`에 전달합니다. 기존
`full_prompt`에 임의 suffix를 붙이지 않습니다. 새 record ID로 검증하고
재생성합니다.

### 5. Finalize

사용자 승인 후 필요한 artifact만 만듭니다.

```bash
python3 <skill_dir>/scripts/crop.py logo-05.png logo-05-cropped.png
python3 <skill_dir>/scripts/remove_bg.py logo-05-cropped.png logo-05-nobg.png
python3 <skill_dir>/scripts/vectorize.py logo-05-nobg.png logo-05.svg
```

이 단계는 생성 model이나 prompt를 바꾸지 않는 artifact 처리입니다. 결과는
원본 raster와 함께 보존하고, trace 결과를 사람이 검수합니다.

## Manifest

```json
{
  "compiler": "image-prompt@2.3.0",
  "upstream_commit": "d1cd1dd3e77f7e12e2fed982fd738cc1ea880598",
  "generator": "image_gen__imagegen",
  "required_model": "gpt-image-2",
  "model_binding": "trusted-host-fixed",
  "local_model_verification": "unavailable",
  "host_reported_model": null,
  "generation_assurance": "generated_under_trusted_host_contract",
  "prompt_record": "prompts.jsonl#C8-BRAND-001",
  "source_raster": "logo-01.png",
  "derived_artifacts": ["logo-01-cropped.png", "logo-01.svg"],
  "review_status": "approved"
}
```

## 완료 기준

- upstream validator `ok: true`
- 후보별 prompt record와 source raster 1:1 대응
- 작은 크기와 mono 상태에서 식별 가능
- 의도하지 않은 글자, logo, watermark 없음
- 모든 파생 파일이 선택된 source raster를 추적 가능
- `bash scripts/verify-gongnyang-prompt-kit.sh` 통과
