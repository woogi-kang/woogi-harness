# Imagegen Marketing Assets

마케팅 이미지나 제품 소개 이미지를 만들 때 `imagegen`은 "멋진 그림 생성기"가 아니라 산출물의 일부입니다. 실제 UI, 브랜드, 플랫폼 규격, 웹 성능까지 함께 검수합니다.

이 규칙은 `imagegen` 스킬의 실행 정책을 바꾸지 않습니다. 기본은 built-in `image_gen`이고, CLI/API fallback은 사용자가 명시적으로 요청하거나 승인한 경우에만 사용합니다.

출처와 동기화 기준:

- 선별 참고: https://github.com/coreyhaines31/marketingskills/blob/main/skills/image/SKILL.md
- 선별 참고: https://github.com/coreyhaines31/marketingskills/blob/main/skills/image/references/ai-image-prompting.md
- 설치된 시스템 스킬 보강 위치: `/Users/woogi/.codex/skills/.system/imagegen/references/marketing-assets.md`
- 시스템 스킬 설치 경로는 git 저장소가 아니므로, 장기 보존 기준은 이 tracked rule에 둡니다.

## 적용 대상

다음 요청에서 적용합니다.

- 블로그 hero, article cover, OG/social preview 이미지
- X/Twitter, LinkedIn, Instagram, Facebook, Threads 등 소셜 그래픽
- 제품 목업, feature announcement, directory/listing 이미지
- profile banner, cover image, launch gallery
- 마케팅 사이트 hero/section visual
- 브랜드 asset concept, campaign visual, reusable background

## 먼저 확인할 맥락

가능하면 먼저 현재 프로젝트의 맥락을 읽습니다.

- `PRODUCT.md`, `DESIGN.md`
- `.agents/product-marketing.md`, `.claude/product-marketing.md`
- `docs/brand-guidelines.md`, brand tokens, existing assets
- 실제 제품 URL, 로컬 앱 화면, screenshot source

그 다음 부족한 것만 확인합니다.

- 이미지 목적과 배치 위치
- 플랫폼 또는 필요한 크기/비율
- 브랜드 색상, 폰트, 로고, 참고 이미지
- 일회성 이미지인지 반복 템플릿인지
- 최종 format, alt text, 파일 용량/성능 요구

## 생성하지 말아야 할 것

아래는 imagegen에 맡기지 않습니다.

- 실제 제품 UI 스크린샷: 브라우저/앱에서 직접 캡처합니다.
- 대시보드, 표, 차트, UI copy처럼 정확해야 하는 내용: HTML/CSS, SVG, chart, 텍스트 레이어로 만듭니다.
- 긴 문구, 법적 문구, 한국어 본문, 축/라벨/범례: 이미지 안에 넣지 않습니다.
- 로고, favicon, 기존 icon set, 정확한 브랜드 mark: vector/design tooling으로 다룹니다.
- 여러 플랫폼 크기 변형: 같은 master visual을 crop/overlay/export하는 것을 우선합니다.

imagegen은 주로 배경, 장면, 일러스트, 질감, 사진형 hero, 제품 주변 분위기, 추상 concept visual에 사용합니다.

## Prompt 기준

기본 순서는 다음처럼 씁니다.

```text
Use case: <taxonomy slug>
Asset type: <blog hero / OG image / social graphic / profile banner / listing image / product visual>
Primary request: <visual concept>
Scene/backdrop: <setting or abstract environment>
Subject: <main subject>
Style/medium: <photorealistic / commercial photography / flat illustration / 3D render / abstract brand visual>
Composition/framing: <wide / square / vertical / panoramic; negative space if needed>
Lighting/mood: <natural / studio / high key / rim / soft directional>
Text (verbatim): "<short text only, if it must be baked in>"
Constraints: no watermark; no unrelated logos; no fake UI; add exact logos, UI, and long text in post-processing
```

실무 원칙:

- baked-in text는 짧게 유지합니다. 긴 문구, 로고, 정확한 타이포그래피는 후처리로 얹습니다.
- 제품 UI가 들어가는 asset은 실제 screenshot을 먼저 만들고, imagegen은 주변 장면/배경에만 씁니다.
- campaign family는 3-4개 style test 후 winning prompt를 저장해 변형에 재사용합니다.
- crop, 색 보정, overlay, logo placement, size variant는 재생성보다 후처리를 우선합니다.
- 사용자 프롬프트가 구체적이면 구조화만 하고, 임의의 소품/브랜드/스토리를 추가하지 않습니다.

## 자주 쓰는 크기

아래는 작업 시작용 기본값입니다. 최종 업로드나 광고 제출 전에는 플랫폼의 최신 규격을 확인합니다.

| 용도 | 기본 크기 | 메모 |
|---|---:|---|
| Blog hero / OG image | 1200x630 | 범용 link preview |
| Website full hero | 1920x1080 | 넓은 crop, 필요 시 copy-safe space |
| X/Twitter feed image | 1200x675 | 16:9 |
| LinkedIn feed image | 1200x627 | OG와 유사 |
| Instagram feed square | 1080x1080 | 작은 글자 금지 |
| Instagram feed tall | 1080x1350 | 모바일 노출 강함 |
| Stories / Reels | 1080x1920 | UI chrome safe zone 고려 |
| LinkedIn personal cover | 1584x396 | 중앙 safe zone |
| X/Twitter header | 1500x500 | avatar/crop 간섭 고려 |
| Product Hunt gallery | 1270x760 | 실제 제품 screenshot 우선 |
| G2 profile image | 1280x720 | 제품 화면 또는 feature visual |
| GitHub social preview | 1280x640 | 카드 크기 가독성 확인 |
| Google Play feature graphic | 1024x500 | 스토어 요구사항 확인 |

## 산출물별 처리

Blog hero / OG:

1. 글의 핵심 metaphor나 subject를 먼저 정합니다.
2. 이미지 자체에는 보통 텍스트를 넣지 않습니다.
3. title, logo, author, date 같은 동적 정보는 코드나 템플릿 레이어로 넣습니다.
4. link preview crop, file weight, alt text, width/height를 확인합니다.

Social graphic:

1. platform과 primary crop을 먼저 고릅니다.
2. master visual을 만든 뒤 플랫폼별 crop/overlay를 만듭니다.
3. 모바일 실제 표시 크기로 제목과 CTA가 읽히는지 확인합니다.

Product mockup / feature announcement:

1. 실제 제품 UI를 고해상도로 캡처합니다.
2. device frame, browser frame, callout, feature label은 HTML/CSS 또는 design tool로 얹습니다.
3. imagegen은 주변 scene, background, texture, illustration에만 씁니다.

Profile / listing banner:

1. 플랫폼 크기와 safe zone을 먼저 정합니다.
2. 텍스트를 최소화하고 핵심 content를 중앙에 둡니다.
3. 추상 그래픽보다 실제 제품/브랜드 증거를 우선합니다.

Brand asset concept:

1. imagegen은 컨셉 탐색까지만 사용합니다.
2. 최종 logo, favicon, icon, brand mark는 vector/design tooling으로 정리합니다.

Programmatic OG:

1. HTML/CSS screenshot, Vercel OG, Satori, Cloudinary-style overlay 같은 code-native template을 우선합니다.
2. imagegen은 재사용 가능한 background, texture, illustration slot에만 사용합니다.
3. title, author, date, logo, metadata는 deterministic text layer로 유지합니다.

## 최종 QA

완료 전 확인합니다.

- 프로젝트에서 참조되는 파일이 `$CODEX_HOME/generated_images`에만 남아 있지 않은가?
- 실제 표시 크기 또는 플랫폼 export 크기로 resize 되었는가?
- WebP/JPEG/PNG/SVG 선택이 목적에 맞는가?
- 파일 용량이 과하지 않은가?
- consuming markup에 `width`/`height`가 있어 CLS를 막는가?
- below-the-fold라면 lazy loading이 적용되는가?
- alt text가 설명적이고 keyword stuffing이 아닌가?
- watermark, unrelated logo, fake UI, 깨진 글자, 읽기 어려운 작은 라벨이 없는가?
