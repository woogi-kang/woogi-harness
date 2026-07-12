---
paths:
  - "**/assets/**"
  - "**/images/**"
  - "**/image/**"
  - "**/prompts*.jsonl"
  - "**/*.png"
  - "**/*.jpg"
  - "**/*.jpeg"
  - "**/*.webp"
---

# Image generation — single production path

모든 생성형 이미지 요청은 아래 한 경로만 사용합니다.

```text
project/brand evidence
→ `image-prompt` (Gongnyang Prompt Kit 원본)
→ `check_prompt.mjs`
→ Codex `$imagegen` alias / `image_gen__imagegen` host tool
→ Codex host의 고정 `gpt-image-2` trust contract
→ 육안 검수와 산출물 배치
```

Prompt 작성 규칙, 포맷, 카테고리, text rendering, size lock, retry 방식은
`.claude/skills/image-prompt/SKILL.md`를 그대로 따릅니다. 다른 skill이나 agent가
자체 prompt template, suffix, negative prompt, style keyword 조합기를 추가하지
않습니다. 생성 tool에는 사용자의 거친 원문이 아니라 Gongnyang이 컴파일한
`full_prompt`를 host tool의 `prompt` 필드로 그대로 매핑합니다.

## 단일 provider 계약

- 생성과 편집은 Codex `$imagegen` alias가 가리키는 exact host tool
  `image_gen__imagegen`만 사용합니다.
- host contract의 required model은 `gpt-image-2`입니다.
- CLI/API/다른 provider로 자동 fallback하지 않습니다.
- Codex image generation을 사용할 수 없으면 `blocked_imagegen_not_run`으로
  기록하고 중단합니다.
- `gpt-image-2`가 지원하지 않는 투명 배경은 opaque 배경으로 변경하거나
  `unsupported_transparent_background`로 중단합니다.
- upstream vendor는 수정하지 않습니다. provider 경계는 이 rule과 실행
  adapter에서만 강제합니다.
- Gongnyang vendor 안의 provider/model/fallback 예시는 실행 지시가 아닙니다.
  Gongnyang은 prompt compilation만 소유하고 실제 provider 계약은
  `.claude/registry/providers/image-generation.yaml`이 소유합니다.

Codex host tool의 현재 호출/결과 schema에는 model 필드가 없습니다. 따라서
로컬 하네스는 exact vendor byte, prompt validator, active route, observable
Claude 우회 경로는 검증하지만 host가 선택한 model identity를 직접 읽거나
증명하지는 못합니다. 일반 실행은 Codex host를 trust root로 두고
`generated_under_trusted_host_contract`로 기록합니다. model attestation까지
필수인 작업은 생성하지 않고 `blocked_imagegen_model_unverifiable`로 중단합니다.

## 생성 전 context

가능하면 먼저 실제 project evidence를 확인합니다.

- `PRODUCT.md`, `DESIGN.md`, brand guideline과 token
- 현재 asset, 실제 제품 화면, reference image
- 사용 위치, 최종 비율, 플랫폼 규격, 파일 형식
- 정확히 렌더해야 하는 한글/영문 문구

이 정보는 Gongnyang compiler의 입력입니다. 별도 prompt template으로
재구성하지 않습니다.

## 생성과 deterministic 산출물의 경계

아래는 생성형 이미지 경로가 아닙니다.

- 실제 제품 UI: 브라우저 또는 앱에서 직접 screenshot
- 정확한 수치, 표, 차트: native chart/table
- 편집 가능한 본문과 UI copy: HTML/PPT/App의 native text
- 이미 존재하는 logo/icon/source asset: 원본 파일 사용
- OG의 동적 title/author/date: code-native renderer
- 검증 가능한 SVG/vector 도형: deterministic vector tooling

생성된 raster 위에 코드로 글자를 덧씌우지 않습니다. 텍스트가 틀리면
Gongnyang prompt를 수정해 다시 생성합니다. 정확한 native text가 필요한
산출물은 생성 이미지와 겹쳐 합성하지 말고 별도 layout 영역에 둡니다.

## 호출 계약

1. `image-prompt`를 활성화해 카테고리와 Format A/B를 결정합니다.
2. 한 이미지마다 한 prompt와 한 output record를 만듭니다.
3. 고가치 산출물과 batch JSONL은 upstream validator로 확인합니다.
4. `ok: false`면 생성하지 않습니다. warning은 upstream 의미를 그대로
   유지하고 임의로 error로 승격하지 않습니다.
5. Codex host tool에는 `prompt=full_prompt`와 편집에 필요한 reference 필드만
   전달합니다. 지원하지 않는 `model`, `full_prompt`, `ar`, `size`, `quality`
   인자를 만들지 않습니다.
6. 요청 비율/크기는 Gongnyang prompt record에 보존하고, 결과는 실제 출력
   크기로 검수한 뒤 project-bound 경로로 옮깁니다.
7. manifest에 compiler, upstream commit, exact host tool, required model,
   model binding/assurance, prompt record, output path, review status를 기록합니다.

Manifest 최소 예시:

```json
{
  "compiler": "image-prompt@2.3.0",
  "upstream_commit": "d1cd1dd3e77f7e12e2fed982fd738cc1ea880598",
  "generator": "image_gen__imagegen",
  "required_model": "gpt-image-2",
  "model_binding": "trusted-host-fixed",
  "local_model_verification": "unavailable",
  "generation_assurance": "generated_under_trusted_host_contract",
  "host_reported_model": null,
  "prompt_record": "prompts.jsonl#C3-EVENT-001",
  "output_path": "assets/campaign/event.webp",
  "review_status": "approved"
}
```

## Hook과 검증

- upstream text-overlay 차단 hook은 `.claude/settings.json`의
  `PreToolUse:Bash`에 등록합니다.
- `.claude/hooks/image-generation-guard.py`는 Claude에서 관찰 가능한 Bash/Skill
  우회 호출을 거부합니다. Codex host-native tool을 가로챈다고 주장하지 않습니다.
- `bash scripts/verify-gongnyang-prompt-kit.sh`로 byte parity, 14개 fixture,
  hook smoke test, 단일 provider 정책을 확인합니다.
- 실제 screenshot, deterministic SVG/vector, chart/table은 이 model guard의
  대상이 아닙니다.
