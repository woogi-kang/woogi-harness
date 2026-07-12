---
name: social-visual
description: |
  소셜미디어 콘텐츠를 위한 이미지와 영상을 기획합니다.

  활성화 조건:
  - "이미지 기획해줘"
  - "비주얼 만들어줘"
  - "썸네일 디자인"
  - "영상 스토리보드"
  - "캐러셀 디자인"
---

# 5. Visual: 이미지/영상 기획

## 플랫폼별 이미지 사이즈

```yaml
image_specs:
  instagram:
    feed_square: "1080x1080 (1:1)"
    feed_portrait: "1080x1350 (4:5) - 권장"
    feed_landscape: "1080x566 (1.91:1)"
    story_reel: "1080x1920 (9:16)"
    carousel: "1080x1080 또는 1080x1350 (통일)"

  linkedin:
    feed_image: "1200x627 (1.91:1)"
    square: "1080x1080 (1:1)"
    carousel_pdf: "1080x1080 또는 1080x1350"
    cover_image: "1584x396"

  x:
    single_image: "1200x675 (16:9)"
    two_images: "700x800 each"
    header: "1500x500"

  threads:
    flexible: "Instagram과 동일"
    recommended: "1080x1080"
```

## 비주얼 유형별 가이드

### 1. 텍스트 기반 이미지

```yaml
text_image:
  use_cases:
    - 인용문/명언
    - 팁/인사이트
    - 통계/숫자
    - 질문/투표

  design_principles:
    - 텍스트 50% 이하 (Instagram 권장)
    - 폰트 크기: 모바일 가독성 확보
    - 대비: 배경과 텍스트 명확히 구분
    - 여백: 충분한 공간 확보

  layout_options:
    centered: "텍스트 중앙 배치"
    top_bottom: "상단 텍스트 + 하단 CTA"
    left_aligned: "왼쪽 정렬 + 우측 여백"

  font_pairing:
    heading: "Bold Sans-serif (Pretendard, Noto Sans)"
    body: "Regular Sans-serif"
    accent: "Serif 또는 Script (포인트)"
```

### 2. 캐러셀/슬라이드

```yaml
carousel_design:
  structure:
    cover: |
      - 강렬한 헤드라인
      - 시선을 끄는 비주얼
      - 스와이프 힌트 (화살표, "Swipe →")

    content_slides: |
      - 한 슬라이드 = 한 포인트
      - 일관된 레이아웃
      - 진행 표시 (번호, 프로그레스바)

    cta_slide: |
      - 핵심 요약
      - 저장/공유 유도
      - 팔로우 CTA

  design_system:
    colors: "브랜드 컬러 2-3개"
    fonts: "헤드라인 + 본문 2종"
    layout: "일관된 그리드"
    elements: "아이콘, 구분선, 도형"

  templates:
    listicle: "[N]가지 [주제]"
    how_to: "[주제] 하는 방법"
    comparison: "A vs B"
    timeline: "[기간] 동안의 변화"
    checklist: "[주제] 체크리스트"
```

### 3. 인포그래픽

```yaml
infographic:
  types:
    statistical: "데이터/통계 시각화"
    process: "단계별 프로세스"
    comparison: "비교 차트"
    timeline: "타임라인"
    hierarchical: "피라미드/계층"

  design_tips:
    - 데이터 하이라이트
    - 명확한 시각적 계층
    - 컬러로 구분
    - 아이콘 활용
    - 숫자 강조

  chart_selection:
    comparison: "막대 그래프"
    trend: "라인 그래프"
    proportion: "원형 차트 (2-3개만)"
    distribution: "히스토그램"
```

### 4. 영상/릴스 스토리보드

```yaml
video_storyboard:
  structure:
    hook: |
      0-3초
      - 강렬한 시작
      - 텍스트 오버레이
      - 빠른 컷

    body: |
      3-25초
      - 주요 콘텐츠
      - 2-3초 컷
      - 자막 필수

    cta: |
      마지막 5초
      - 행동 유도
      - 팔로우/저장 요청

  template:
    scene_1:
      duration: "3초"
      visual: "[설명]"
      text_overlay: "[텍스트]"
      audio: "[음악/보이스]"
      transition: "컷"

    scene_2:
      # ...

  audio_tips:
    - 트렌딩 오디오 활용
    - 저작권 확인 필수
    - 음소거 시청 고려 → 자막 필수
```

## 생성형 이미지

이 스킬은 자체 prompt 구조, style keyword, 플랫폼별 suffix를 만들지 않습니다.
모든 생성형 이미지 요청은 다음 경로를 사용합니다.

```text
platform spec + content claim + brand evidence
→ `image-prompt`
→ upstream validator
→ Codex `$imagegen`
→ `gpt-image-2`
```

- 단일 post, carousel cover, campaign visual은 Gongnyang C3/C5/C7/P 계열
  중 적합한 경로를 원본 compiler가 선택하게 합니다.
- Gongnyang `full_prompt`만 Codex host tool의 `prompt` 필드로 매핑합니다.
- 다른 provider/model fallback과 로컬 prompt library를 사용하지 않습니다.
- 텍스트가 있는 이미지도 생성 raster 위에 후처리로 얹지 않습니다. 정확하지
  않으면 prompt를 수정해 재생성합니다.
- 실제 제품 화면은 browser/app screenshot으로 캡처합니다.
- 정확한 통계, 표, 긴 본문은 HTML/SVG/native chart로 만듭니다.
- deterministic 산출물과 생성형 raster를 하나의 이미지로 합성하지 않습니다.

생성 후 manifest에는 `image-prompt` version, upstream commit, prompt record,
platform size, output path, review status와 아래 host trust contract를 기록합니다.
`required_model: gpt-image-2`, `model_binding: trusted-host-fixed`,
`local_model_verification: unavailable`, `host_reported_model: null`,
`generation_assurance: generated_under_trusted_host_contract`를 사용하고,
실제 모델을 확인한 것처럼 보이는 `model` 필드는 기록하지 않습니다.

## 제작 도구 경계

- 생성형 raster: `image-prompt` + Codex `$imagegen`
- 실제 화면: browser/app screenshot
- 정확한 text/chart: HTML/CSS/SVG/native renderer
- 영상 편집: 사용자가 지정한 편집 도구 또는 기존 영상 workflow

## 비주얼 체크리스트

```yaml
visual_checklist:
  technical:
    - [ ] 해상도 충분 (흐리지 않음)
    - [ ] 올바른 비율
    - [ ] 파일 크기 적정
    - [ ] 모바일 가독성

  brand:
    - [ ] 브랜드 컬러 사용
    - [ ] 폰트 일관성
    - [ ] 로고 배치 (필요시)
    - [ ] 전체 피드 조화

  accessibility:
    - [ ] 충분한 대비
    - [ ] 텍스트 읽기 쉬움
    - [ ] 색맹 고려
    - [ ] Alt 텍스트 준비

  content:
    - [ ] 메시지 명확
    - [ ] CTA 포함
    - [ ] 불필요한 요소 제거
```

## 출력 형식

```yaml
visual_output:
  content_id: "IG-2025-0104-001"

  visual_spec:
    type: "carousel"
    slides: 7
    ratio: "4:5"
    dimensions: "1080x1350"

  slide_details:
    - slide: 1
      description: "표지 - 헤드라인 중앙 배치"
      text: "마케터가 몰랐던 5가지 비밀"
      elements: ["그라데이션 배경", "볼드 타이틀"]

    - slide: 2
      description: "비밀 #1"
      text: "[내용]"
      elements: ["숫자 강조", "아이콘"]

  generative_assets:
    - role: "background"
      compiler: "image-prompt@2.3.0"
      prompt_record: "prompts.jsonl#C3-SOCIAL-001"
      generator: "image_gen__imagegen"
      required_model: "gpt-image-2"
      model_binding: "trusted-host-fixed"
      local_model_verification: "unavailable"
      host_reported_model: null
      generation_assurance: "generated_under_trusted_host_contract"

  design_notes:
    - "브랜드 컬러: #FF6B6B, #4ECDC4"
    - "폰트: Pretendard Bold/Regular"
```

## 🌏 글로벌 비주얼 가이드 (Global Visual Guide)

### TikTok 영상 사양

```yaml
tiktok_video_specs:
  aspect_ratio: "9:16 (세로 필수)"
  resolution: "1080x1920 (Full HD)"
  formats:
    short: "15초 (트렌드 참여, 훅 강조)"
    standard: "60초 (튜토리얼, 스토리텔링)"
    extended: "3분 (심층 콘텐츠)"
    long: "10분 (풀 튜토리얼, 브이로그)"
  file_format: "MP4, MOV"
  max_file_size: "287.6MB (모바일), 500MB (웹)"

  visual_guidelines:
    safe_zone: |
      - 상단 15%: 사용자명/아이콘 영역 — 핵심 텍스트 배치 금지
      - 하단 20%: 캡션/버튼 영역 — 핵심 비주얼 피하기
      - 중앙 65%: 핵심 콘텐츠 영역
    text_overlay:
      font_size: "최소 20pt (모바일 가독성)"
      position: "중앙 또는 중앙 상단"
      style: "Bold, 고대비, 짧은 문구"
    thumbnail:
      importance: "TikTok 프로필 그리드에서 노출"
      tip: "영상 중 가장 임팩트 있는 프레임 선택"

  hook_visual_patterns:
    text_hook: "첫 프레임에 텍스트 오버레이 ('이거 모르면 손해')"
    motion_hook: "빠른 움직임, 줌인으로 시작"
    face_hook: "얼굴 클로즈업 + 표정"
    before_after: "비포/애프터 대비"
```

### 멀티 언어 디자인 고려사항

```yaml
multi_language_design:
  text_in_images:
    principle: "텍스트가 포함된 이미지는 언어별 별도 제작 권장"
    alternatives:
      - "텍스트 최소화, 유니버설 아이콘/이모지 활용"
      - "숫자와 그래프 중심 (언어 무관)"
      - "템플릿화하여 텍스트만 교체"
    font_considerations:
      korean: "Pretendard, Noto Sans KR, Spoqa Han Sans"
      english: "Inter, DM Sans, Plus Jakarta Sans"
      bilingual: "Noto Sans (한/영 모두 지원)"

  universal_visual_elements:
    icons: |
      - 이모지: 전 세계 공통 이해 (🚀 💡 ✅ 📊)
      - 아이콘 라이브러리: Lucide, Phosphor (문화 중립적)
      - 화살표, 숫자, 체크마크: 언어 무관
    imagery: |
      - 다양한 인종/문화 반영 (글로벌 이미지 사용 시)
      - 문화 특정 제스처 주의 (OK 사인, 엄지척 등 국가별 의미 다름)
      - 색상 의미 차이 고려 (빨간색: 한국=열정/축하, 서양=위험/정지)
    layout: |
      - 텍스트 방향: 영어(LTR)와 한국어 모두 좌→우
      - 여백 충분히 확보 (번역 시 텍스트 길이 변화 대비)
      - 핵심 메시지는 비주얼로도 전달 가능하게

  platform_specific_global:
    tiktok: |
      - 자막 필수 (음소거 시청 + 외국어 오디언스)
      - 자동 자막 기능 활용 가능하나, 수동 편집 권장
      - 한국어 콘텐츠에 영어 자막 추가하면 글로벌 도달 확대
    pinterest: |
      - 텍스트 오버레이는 간결하게 (영어 기준 6 단어 이하)
      - 세로 2:3 비율 핀이 피드에서 가장 큰 노출
      - 깔끔한 타이포그래피 + 고품질 이미지
    youtube_shorts: |
      - TikTok과 동일 9:16 비율
      - 썸네일 별도 설정 불가 — 영상 자체가 썸네일
      - 제목에 핵심 키워드 (검색 최적화)
```

## 다음 단계

비주얼 기획 완료 후:
1. → 디자인 도구로 제작
2. → `2-validation`: 브랜드 일관성 검증
3. → `7-approval`: 최종 승인
