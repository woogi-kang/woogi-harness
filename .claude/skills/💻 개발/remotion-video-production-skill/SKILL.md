---
name: remotion-video-production
description: "Remotion/FFmpeg 기반 영상 제작 스킬. React 기반 자막, 전환, 오디오, 데이터 시각화, 실제 제품 UI 캡처형 프로모션, prompt-to-video, OpenMontage 스타일 animated explainer, 로컬 TTS 내레이션, 영상 렌더링/검증이 필요할 때 사용한다."
metadata:
  version: 1.1.0
  source: remotion-dev/remotion/packages/skills@4186404 (v4.0.435), adapted
triggers:
  - "remotion"
  - "리모션"
  - "OpenMontage"
  - "openmontage"
  - "animated explainer"
  - "product promo"
  - "제품 프로모션"
  - "UI 데모 영상"
  - "앱 홍보 영상"
  - "prompt-to-video"
  - "비디오 만들어"
  - "영상 만들어"
  - "입장곡"
  - "입장곡 편집"
  - "오디오 페이드"
  - "fade in"
  - "fade out"
  - "bgm 편집"
  - "자막 영상"
  - "Sequence"
  - "TransitionSeries"
  - "calculateMetadata"
  - "voiceover"
updated: 2026-07-23
---

# Remotion Video Production

Remotion으로 만드는 영상 작업 전반을 다룬다. 이 Skill의 목적은 "React로 움직이는 영상 타임라인을 정확하게 구성"하는 것이다.

## 핵심 규칙

1. 모든 애니메이션은 `useCurrentFrame()` 기준으로 만든다.
2. 사람이 이해할 때는 초 단위로 생각해도 되지만, 코드에서는 `fps`를 곱해 프레임으로 변환한다.
3. `public/` 폴더 자산은 항상 `staticFile()`로 참조한다.
4. CSS transition, CSS animation, Tailwind `transition-*` / `animate-*` 클래스에 의존하지 않는다.
5. 오디오만 편집하는 경우에도 타임라인을 "구간" 단위로 설계한 뒤 `Sequence`와 `Audio`로 표현한다.
6. 자연어 영상 요청은 먼저 출력 계약으로 바꾼다: 길이, 해상도, 내레이션 여부, 자막 여부, 사용할 provider, 검증 기준.
7. API 키가 없으면 기본 경로는 로컬 Remotion + Piper TTS + FFmpeg 검증이다. 외부 이미지/영상/음악 provider는 키와 비용을 확인한 뒤에만 약속한다.
8. 제품 UI 영상은 화면을 닮게 다시 그리지 않는다. 실제 앱 런타임이나 제품 코드의 결정론적 golden renderer를 캡처하고 출처·상태·프레임을 manifest로 남긴다.
9. 제품 캡처와 영상 합성을 분리한다. 캡처 단계는 제품 상태 재현만, Remotion 단계는 카메라·전환·타이포·오디오만 소유한다.
10. 레퍼런스 영상이 있으면 보기만 하지 않고 프레임·contact sheet·shot timing을 분석한다. 레퍼런스가 없으면 없다고 기록하고 목표 motion grammar를 별도 선언한다.
11. 제품 UI 장면은 `preset + durationInFrames + params + transition + camera` 계약으로 선언한다.

## 먼저 판단할 것

### 1. 출력물이 무엇인가

- 오디오 파일만 필요함: 간단한 컷/페이드면 FFmpeg가 빠를 수 있다.
- 영상까지 필요함: Remotion composition으로 만든다.
- 둘 다 필요함: Remotion으로 논리를 확정하고, 최종 오디오 추출은 FFmpeg를 함께 쓴다.

### 2. 소스가 어떤 형태인가

- 단일 혼합본 1개: 컷, 스킵, 페이드, 크로스페이드는 가능하다.
- 보컬/반주 stem 분리본 있음: 특정 구간만 MR, 특정 구간만 보컬 강조 같은 편집이 가능하다.
- 단일 혼합본만 있음: "MR만 재생" 같은 요구는 별도 stem separation 없이 불가능하다.

### 3. 길이가 고정인가 가변인가

- 고정 길이: `durationInFrames`를 직접 설정한다.
- 소스 길이에 따라 달라짐: `calculateMetadata`를 사용한다.

## 작업 흐름

1. 타임라인을 구간 표로 정리한다.
2. 자산을 `public/`에 두고 파일명을 안정적으로 정한다.
3. 필요한 reference만 읽는다.
4. composition, audio/video/caption 로직을 구현한다.
5. 렌더링 방식과 코덱을 결정한다.

## Reference Map — 제작 워크플로우

- 자연어 프롬프트에서 animated explainer를 만드는 OpenMontage식 로컬 경로: [references/prompt-to-video-explainer.md](references/prompt-to-video-explainer.md)
- 실제 앱 화면을 캡처해 제품 프로모션/워크스루 영상을 만드는 경로: [references/product-ui-promotion.md](references/product-ui-promotion.md)
- 오디오 편집, 페이드, 컷, MR/stem 여부 판단: [references/audio-editing.md](references/audio-editing.md)
- 이미지/영상/오디오/폰트, 메타데이터, 동적 길이 계산: [references/media-assets.md](references/media-assets.md)
- 시퀀스, spring, transition, 트리밍: [references/animation-timing.md](references/animation-timing.md)
- 자막 생성, SRT 가져오기, 단어 하이라이트: [references/captions-subtitles.md](references/captions-subtitles.md)
- 차트, 텍스트 애니메이션, Lottie, light leak: [references/visual-effects.md](references/visual-effects.md)
- 3D, 지도, 투명 비디오, FFmpeg: [references/advanced-scenes-and-export.md](references/advanced-scenes-and-export.md)

## API Rules — Remotion 상세 레퍼런스 (38개)

필요한 API 영역의 rule 파일을 참조한다.

### Core Animation & Composition
- [rules/animations.md](rules/animations.md) — `useCurrentFrame()`, 프레임 기반 애니메이션
- [rules/timing.md](rules/timing.md) — `interpolate()`, `spring()`, easing
- [rules/compositions.md](rules/compositions.md) — `<Composition>`, stills, folders
- [rules/sequencing.md](rules/sequencing.md) — `<Sequence>`, `<Series>`
- [rules/trimming.md](rules/trimming.md) — 구간 컷

### Media
- [rules/audio.md](rules/audio.md) — 오디오 재생, 볼륨, 속도
- [rules/videos.md](rules/videos.md) — 비디오 임베딩, 루핑
- [rules/images.md](rules/images.md) — `<Img>` 컴포넌트
- [rules/gifs.md](rules/gifs.md) — GIF/APNG/AVIF/WebP
- [rules/assets.md](rules/assets.md) — `staticFile()` 자산 관리

### Captions & Subtitles
- [rules/subtitles.md](rules/subtitles.md) — 캡션 JSON 형식
- [rules/display-captions.md](rules/display-captions.md) — 캡션 렌더링
- [rules/transcribe-captions.md](rules/transcribe-captions.md) — Whisper.cpp 전사
- [rules/import-srt-captions.md](rules/import-srt-captions.md) — SRT 임포트

### Visual Effects & Transitions
- [rules/transitions.md](rules/transitions.md) — `<TransitionSeries>`
- [rules/text-animations.md](rules/text-animations.md) — 텍스트 애니메이션
- [rules/light-leaks.md](rules/light-leaks.md) — WebGL 라이트 리크
- [rules/transparent-videos.md](rules/transparent-videos.md) — 알파 채널 (ProRes, VP9)
- [rules/lottie.md](rules/lottie.md) — Lottie 임베딩

### Audio Features
- [rules/audio-visualization.md](rules/audio-visualization.md) — 스펙트럼, 웨이브폼
- [rules/sfx.md](rules/sfx.md) — 효과음
- [rules/voiceover.md](rules/voiceover.md) — ElevenLabs TTS

### Styling & Fonts
- [rules/fonts.md](rules/fonts.md) — Google Fonts, 로컬 폰트
- [rules/tailwind.md](rules/tailwind.md) — TailwindCSS (애니메이션 제한 포함)

### Data & Charts
- [rules/charts.md](rules/charts.md) — Bar, pie, line 차트
- [rules/3d.md](rules/3d.md) — Three.js / React Three Fiber
- [rules/maps.md](rules/maps.md) — Mapbox 지도 애니메이션

### Measurement & Metadata
- [rules/measuring-text.md](rules/measuring-text.md) — 텍스트 크기 측정
- [rules/measuring-dom-nodes.md](rules/measuring-dom-nodes.md) — DOM 측정
- [rules/calculate-metadata.md](rules/calculate-metadata.md) — 동적 duration/dimensions
- [rules/parameters.md](rules/parameters.md) — Zod 스키마 파라미터
- [rules/get-video-duration.md](rules/get-video-duration.md) — 비디오 길이 추출
- [rules/get-video-dimensions.md](rules/get-video-dimensions.md) — 비디오 해상도 추출
- [rules/get-audio-duration.md](rules/get-audio-duration.md) — 오디오 길이 추출
- [rules/extract-frames.md](rules/extract-frames.md) — 프레임 추출
- [rules/can-decode.md](rules/can-decode.md) — 코덱 호환성

### Video Processing
- [rules/ffmpeg.md](rules/ffmpeg.md) — FFmpeg/FFprobe 연동

## 결혼식 입장곡 편집 플레이북

입장곡 편집 요청에서는 다음 순서로 판단한다.

1. 실제 사용할 출력이 오디오만인지, 영상까지 포함인지 확인한다.
2. 사용 구간을 `시작`, `끝`, `볼륨`, `fade`, `비고`로 표로 적는다.
3. 단일 곡이면 `Audio`를 여러 구간으로 쪼개 배치한다.
4. 장면 전환이 자연스러워야 하면 앞뒤 구간을 1~3초 정도 겹쳐 크로스페이드한다.
5. MR 구간 요구가 있으면 stem 파일 보유 여부를 먼저 확인한다.

예시 구간 설계:

| 구간 | 처리 |
|------|------|
| 0:00-0:18 | 인트로 유지 |
| 0:18-0:24 | 페이드 다운 |
| 0:24-0:48 | 하이라이트 구간 사용 |
| 0:48-1:12 | 중간 벌스 스킵 |
| 1:12-1:42 | 후렴 연결 |
| 마지막 6초 | 페이드 아웃 |

## 구현 원칙

- 단순 컷 편집은 가능한 한 선언적으로 만든다.
- 반복 계산이 필요한 경우 `const FPS = 30` 같은 상수를 둔다.
- 시퀀스 안에서는 `useCurrentFrame()`이 로컬 프레임으로 바뀐다는 점을 항상 의식한다.
- 영상과 자막, 오디오를 함께 다룰 때는 자막 로직을 별도 컴포넌트/파일로 분리한다.
- OpenMontage식 요청을 처리할 때는 upstream 전체를 vendoring하지 말고, 현재 프로젝트의 Remotion composition과 props/schema로 재현 가능한 최소 경로를 만든다.

## Prompt-to-video 작업 흐름

`"Make a 60-second animated explainer about ..."` 같은 요청에서는 [references/prompt-to-video-explainer.md](references/prompt-to-video-explainer.md)를 먼저 읽고 진행한다.

기본 순서:

1. 요청을 출력 계약으로 바꾼다: 길이, 화면비, 대상 시청자, 톤, 내레이션/자막, provider 제한.
2. provider envelope를 확인한다. 키가 없으면 로컬 Remotion/Piper/FFmpeg 경로로 좁힌다.
3. 내레이션 스크립트를 먼저 작성하고 TTS 파일 길이를 `ffprobe`로 측정한다.
4. 스크립트 길이에 맞춰 6-12개 장면의 타임라인을 만든다.
5. 장면은 텍스트 카드, 차트, 비교, callout, KPI, 이미지/영상 컷 중에서 의미가 있는 컴포넌트만 사용한다.
6. Remotion으로 렌더한 뒤 `ffprobe`, 비경계 프레임 샘플, 오디오 재생 확인으로 검증한다.
7. 결과물, props, 스크립트, 검증 로그 위치를 함께 남긴다.

## 제품 UI 프로모션 작업 흐름

`"우리 앱 화면으로 홍보 영상 만들어줘"` 같은 요청에서는
[references/product-ui-promotion.md](references/product-ui-promotion.md)를 먼저
읽는다. 화면 캡처가 합성 코드와 섞이거나, 실제 제품 대신 유사 UI를 다시 그리거나,
SceneSpec의 다섯 필드가 빠진 상태로 렌더를 시작하지 않는다.

## 빠른 시작 질문

Remotion 작업을 시작할 때는 아래 정보부터 수집한다.

1. 출력물: `오디오만 / 영상 포함`
2. 해상도와 비율: `16:9 / 9:16 / 1:1`
3. fps: 기본 `30` 또는 요구값
4. 자산 목록: `음원`, `영상`, `이미지`, `캡션`, `폰트`
5. 타임라인 구간표
