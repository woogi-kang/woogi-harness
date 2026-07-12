---
name: ckm:design
description: "종합 디자인 오케스트레이션 — CIP, slides, deterministic SVG/social assets와 Gongnyang/Codex 생성형 이미지를 올바른 경로로 분리"
argument-hint: "[design-type] [context]"
license: MIT
metadata:
  author: claudekit
  version: "3.0.0"
---

# Design

종합 디자인 요청을 전문 skill로 라우팅하고, 산출물 간 brand evidence와
provenance를 연결합니다. 생성형 이미지 prompt engineering은 이 스킬의
책임이 아닙니다.

## 책임

- 복합 디자인 요청 분해와 순서 결정
- CIP deliverable brief와 실제 source asset 관리
- slides, chart, table, HTML/native layout 연결
- deterministic SVG/vector와 screenshot workflow
- 생성형 raster의 `image-prompt`/Codex 경로 연결
- 최종 asset manifest와 QA

## Delegation

| 요청 | Owner |
|---|---|
| 디자인 방향, anti-slop | `design-harness` |
| logo/brand mark/app icon concept | `logo-creator` |
| banner/cover/header | `banner-design` |
| 브랜드 voice와 token | `brand` / `design-system` |
| UI 구현 | `ui-styling` |
| 생성형 raster | `image-prompt` → Codex `$imagegen` |
| PPT/HTML deck | `slides` / presentation skills |

## 생성형 이미지 단일 경로

```text
design brief + brand evidence + source asset
→ `image-prompt`
→ upstream validator
→ Codex `$imagegen`
→ `gpt-image-2`
```

- 다른 생성 provider/model로 fallback하지 않습니다.
- 로컬 prompt template, style suffix, negative prompt를 만들지 않습니다.
- Gongnyang `full_prompt`를 Codex host tool의 `prompt` 필드로 그대로 매핑합니다.
- transparent generation은 지원하지 않습니다. Opaque 결과 또는
  `unsupported_transparent_background`로 처리합니다.
- 생성 raster의 문구를 코드로 덧씌우지 않습니다.

## Deterministic lane

다음은 `image-prompt` 경로와 별개입니다.

- 실제 product/browser/app screenshot
- existing logo/icon/source file
- 편집 가능한 HTML/PPT text와 chart/table
- 검증 가능한 code-native SVG/vector
- crop, resize, compression, vector trace 같은 artifact transformation

생성 raster와 native text를 한 캔버스로 합성하지 않습니다. 둘 다 필요한
경우 layout의 분리된 region으로 구성합니다.

## Logo

1. `scripts/logo/search.py --design-brief`로 style/color/industry evidence를
   수집합니다.
2. `logo-creator`가 brief를 `image-prompt`에 전달합니다.
3. 각 option을 별도 JSONL record로 검증하고 Codex로 생성합니다.
4. 선택 후 crop/vector artifact를 만들고 source raster를 보존합니다.

검색 결과는 prompt가 아니라 compiler 입력 evidence입니다.

## CIP

1. `scripts/cip/search.py --cip-brief`로 deliverable, context, industry evidence를
   수집합니다.
2. 실제 logo/source asset과 brief를 `image-prompt`의 C8 경로에 전달합니다.
3. `scripts/cip/generate.py`는 generation plan/manifest만 검사합니다.
4. 생성된 asset은 `scripts/cip/render-html.py`로 검토용 presentation에
   배치할 수 있습니다.

실제 logo fidelity가 절대 조건이면 생성 mockup 대신 deterministic template을
사용합니다. 생성 model이 source mark를 정확히 재현한다고 가정하지 않습니다.

## Icon

- Raster/3D/object icon concept: `image-prompt` C9 → Codex `gpt-image-2`.
- Editable SVG icon: existing icon library 또는 deterministic code/vector
  tooling.
- `scripts/icon/generate.py`는 외부 model을 호출하지 않고 SVG source를
  정규화·검증하는 artifact command입니다.

## Banner

`banner-design`이 generative와 deterministic lane을 선택합니다.

- Generative: copy까지 Gongnyang이 이미지 안에서 렌더
- Deterministic: HTML/CSS/native text와 실제 asset으로 전체 banner 작성

생성 배경 위에 HTML text를 얹는 혼합 lane은 사용하지 않습니다.

## Social assets

- 생성형 post/cover: `social-visual` → `image-prompt`
- text-heavy carousel/chart: HTML/SVG/native renderer
- 실제 제품 증거: screenshot

Platform size, safe zone, alt text, file weight는 prompt가 아니라 artifact QA로
관리합니다.

## Slides

Strategic HTML presentation과 Chart.js/native table은 deterministic lane입니다.

1. `references/slides-create.md`로 생성 workflow를 선택합니다.
2. layout, template, copy, strategy reference를 필요한 범위만 읽습니다.
3. 생성형 hero/concept asset이 필요할 때만 presentation image skill을
   통해 `image-prompt`로 라우팅합니다.
4. 정확한 수치, 표, 차트, 본문은 편집 가능한 native element로 유지합니다.

## Complete brand package

1. `logo-creator` → logo option 생성과 선택
2. `design` CIP → deliverable brief, mockup/evidence asset, HTML review
3. `banner-design` → channel-specific banner
4. `brand` → token, asset manifest, usage guideline 동기화

## Asset manifest

생성형 asset:

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
  "prompt_record": "prompts.jsonl#C8-CIP-001",
  "source_evidence": ["brand-guidelines.md", "logo.svg"],
  "output_path": "assets/cip/business-card.webp",
  "review_status": "approved"
}
```

Deterministic asset은 `generator` 대신 source tool, input path, command,
checksum을 기록합니다.

## Completion gate

- owner와 production lane이 명확함
- 생성형 asset은 `image-prompt` validator `ok: true`
- `required_model: gpt-image-2`, `model_binding: trusted-host-fixed`,
  `local_model_verification: unavailable`, `host_reported_model: null`,
  `generation_assurance: generated_under_trusted_host_contract` 기록
- 다른 생성 provider/model fallback 없음
- source evidence와 output provenance 연결
- generated raster text overlay 없음
- 실제 출력 크기와 accessibility 검수
- `bash scripts/verify-gongnyang-prompt-kit.sh` 통과

## References

- `references/design-routing.md`
- `references/logo-design.md`
- `references/logo-style-guide.md`
- `references/logo-color-psychology.md`
- `references/logo-prompt-engineering.md`
- `references/cip-design.md`
- `references/cip-deliverable-guide.md`
- `references/cip-style-guide.md`
- `references/cip-prompt-engineering.md`
- `references/icon-design.md`
- `references/social-photos-design.md`
- `references/banner-sizes-and-styles.md`
- `references/slides-create.md`
- `references/slides-layout-patterns.md`
- `references/slides-html-template.md`
- `references/slides-copywriting-formulas.md`
- `references/slides-strategies.md`

## Scripts

| Script | Purpose |
|---|---|
| `scripts/logo/search.py` | style/color/industry evidence 검색과 design brief |
| `scripts/logo/generate.py` | Gongnyang JSONL 검증과 generation plan 생성 |
| `scripts/cip/search.py` | deliverable/style/industry/mockup evidence 검색 |
| `scripts/cip/generate.py` | Gongnyang JSONL 검증과 CIP plan 생성 |
| `scripts/cip/render-html.py` | 생성/실증 asset을 HTML review deck에 배치 |
| `scripts/icon/generate.py` | existing deterministic SVG 정규화·검증 |

Prompt authoring reference는 vendored
`.claude/skills/image-prompt/SKILL.md`만 사용합니다.
