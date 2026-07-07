# Presentation Quality Gate

PPT, HTML deck, PDF 발표자료를 생성할 때는 최종 응답 전에 이 게이트를 반드시 통과한다. 목적은 장표가 "파일은 만들어졌지만 실제 발표에 쓰기 어려운" 상태로 전달되는 일을 막는 것이다.

## 완료 기준

### 1. 인포그래픽 적합성

- 각 슬라이드는 시각 요소의 역할을 명확히 정한다: `none`, `imagegen-infographic`, `chart/table`, `screenshot`, `photo/reference`, `native-label-overlay`.
- PPT에서 인포그래픽으로 분류되는 hero visual, concept visual, process visual, service-flow visual, risk visual은 반드시 `imagegen` 스킬의 built-in `image_gen` 또는 승인된 imagegen CLI fallback으로 생성한 raster asset을 사용한다.
- 마케팅/제품 소개 성격의 hero visual, product mockup, OG/social preview 이미지는 `imagegen-marketing-assets.md`를 함께 적용해 실제 screenshot, 텍스트 overlay, 플랫폼 규격, 웹 성능 QA를 분리한다.
- `native-diagram`, HTML/SVG, PPT 도형만으로 만든 그림은 인포그래픽으로 인정하지 않는다. 도형은 한국어 라벨, 콜아웃, 연결선, 데이터 차트, 표, 보조 overlay에만 사용한다.
- 흐름, 비교, 단계, 구조, 의사결정 기준을 설명하는 슬라이드는 먼저 imagegen asset의 visual contract를 작성한 뒤 생성한다. 한국어 본문과 읽어야 하는 라벨은 이미지 안에 넣지 않고 PPT/HTML 텍스트 레이어에 둔다.
- 정확한 순서, 수치, 라벨, 표 구조가 핵심인 단계 카드나 데이터 차트는 `imagegen-infographic`이 아니라 `native-label-overlay` 또는 `chart/table`로 분류한다. 이 경우 imagegen은 배경/상황 비주얼로만 쓰고, 실제 순서와 라벨은 편집 가능한 텍스트와 도형으로 만든다.
- 생성형 이미지는 장식용 채우기가 아니라 메시지 이해를 돕는 경우에만 사용한다.
- 생성형 이미지 안에는 의도하지 않은 읽을 수 있는 텍스트, 로고, 워터마크가 없어야 한다.
- 인포그래픽을 사용한 경우 `slide`, `purpose`, `asset_path`, `generator`, `prompt_or_source`, `visual_contract`, `review_status`를 manifest에 남긴다.
- imagegen을 실행하지 못한 경우 placeholder, native diagram, 임시 SVG를 납품용 인포그래픽처럼 대체하지 않는다. `blocked_imagegen_not_run`으로 기록하고 사용자에게 상태를 알린다.

### 1.1 Imagegen 사용 기준

다음 상황은 imagegen 사용을 우선 검토한다.

- 첫 장이나 챕터 오프너에서 주제를 한눈에 잡아주는 hero/section visual
- 추상 개념을 구체적 장면으로 바꾸는 concept metaphor
- 학습자, 운영자, 서비스 화면의 상황을 보여주는 scenario visual
- 환각, 최신성 부족, 편향, 보안 위험처럼 텍스트만으로 밋밋한 risk visual
- 실제 스크린샷은 아니지만 서비스 구조를 설명하는 product/service mockup
- 여러 슬라이드에서 반복 사용할 텍스트 없는 icon set 또는 visual motif
- 여백이 큰 슬라이드에서 본문을 방해하지 않는 contextual background

다음 상황은 imagegen을 쓰지 않는다.

- 숫자, 축, 표, 정확한 비교값, 법적/정책 문구처럼 오차가 없어야 하는 정보
- 한국어 문장, UI 라벨, 코드, 명령어처럼 읽어야 하는 텍스트가 이미지 안에 들어가는 경우
- 편집 가능한 PPTX 본문, 발표자가 수정해야 하는 단계명, 연결선, 카드 제목
- 브랜드 로고, 기존 아이콘 시스템, 실제 제품 스크린샷처럼 원본성이 중요한 시각 요소

기본 prompt에는 다음 제약을 포함한다.

```text
No text, no letters, no numbers, no UI labels, no watermark.
Leave clean negative space for Korean PPT text.
Use a restrained educational presentation style.
```

### 2. 슬라이드 기획과 예시 품질

- 각 슬라이드는 생성 전에 `slide_intent`를 정한다: `hook`, `problem`, `definition`, `misconception`, `worked-example`, `before-after`, `workflow`, `diagnostic`, `decision-rule`, `practice`, `summary`, `closing`.
- `slide_intent`와 실제 레이아웃은 맞아야 한다. 예를 들어 `worked-example`은 예시 입력과 개선 결과가 보여야 하고, `diagnostic`은 증상, 원인 후보, 확인 방법, 수정 기준이 보여야 한다.
- 본문 슬라이드는 개념 설명만 반복하지 않는다. 각 챕터에는 최소 1개 이상의 `worked-example`, `before-after`, `diagnostic`, `practice` 중 하나가 있어야 한다.
- 대학생 대상 강의 자료는 예시를 LMS 공지, 과제 마감, 팀플, 미니프로젝트, FAQ, 출결, 제출물, 튜터 피드백처럼 청중이 바로 이해하는 상황으로 만든다.
- 추상 개념을 설명할 때는 "정의 → 수업/서비스 상황 예시 → 판단 기준"을 함께 둔다. 정의만 있는 슬라이드는 실패로 본다.
- 구조화 출력, RAG, LLMOps처럼 운영 개념을 설명할 때는 `질문/입력 → 자연어 답변/문제 상황 → 왜 그대로 쓰면 안 되는가 → 구조화/검증/운영 결과` 흐름을 최소 1장 이상 포함한다.
- "방지 방향", "서비스 데이터", "앱과 서버가 읽는다"처럼 행동이 보이지 않는 추상 표현은 실패로 본다. `출처 확인`, `최신 문서 검색(RAG)`, `편향·형식 오류 평가`, `summary/use_cases/risk 필드 저장`, `재요청/폴백`처럼 실제 시스템 동작으로 바꾼다.
- 위험/편향/운영 실패 사례는 가능하면 실제 사례와 출처를 사용한다. 근거가 없는 실제 사례처럼 보이는 문장은 실패다. 가상 사례는 가상이라고 명시한다.
- 발표 스크립트는 슬라이드 문구를 읽는 방식이 아니라 "왜 이 예시를 보는지 → 무엇을 판단해야 하는지 → 실제 수업/서비스에서 어떻게 쓰는지"를 설명해야 한다.
- 연속 2장을 같은 layout family로 만들지 않는다. 단, 의도적으로 같은 구조를 반복해 비교하는 구간은 `pattern_repeat_reason`을 남긴다.
- 10장 이상 덱은 최소 5개 이상의 layout family를 사용한다. 예: hero, misconception trio, before/after, timeline, workflow, diagnostic table, prompt teardown, exercise, closing.
- 단순 카드 3개/5개 구성은 기본값이 아니다. 카드형을 쓰려면 각 카드가 상호 비교, 선택 기준, 점검 항목처럼 서로 다른 판단 기능을 가져야 한다.
- 최종 QA report 또는 source manifest에는 `slide`, `slide_intent`, `layout_family`, `example_type`, `audience_fit`, `repeat_reason`을 남긴다.

### 3. 레이아웃 전수 검사

- 최종 파일은 모든 슬라이드/페이지를 이미지로 렌더링한 뒤 전수 확인한다.
- contact sheet는 전체 흐름을 훑는 보조 자료일 뿐, 통과 근거가 아니다. 최종 통과는 각 slide/page PNG를 실제 읽을 수 있는 크기로 개별 확대 확인한 뒤에만 기록한다.
- 제목, 본문, 각주, 이미지, 도형, 차트가 화면 밖으로 나가거나 서로 겹치면 실패로 본다.
- 텍스트 박스의 overflow, 잘림, 비정상 축소, 불필요한 여백 부족, 페이지 밖 crop을 확인한다.
- 레이아웃 간격은 제목-부제, 제목-핵심문장/lede, 부제-본문, 카드 간 gap, 표 row/column padding, 이미지-텍스트 사이, 하단 핵심 문장 safe area를 항목별로 확인한다.
- 제목과 `핵심 · ...` 문장 사이 간격은 덱 전체에서 같은 기준선을 써야 한다. 한 슬라이드만 핵심문장이 과하게 내려가거나 제목에 붙으면 실패다.
- `핵심 · ...` 문장은 제목 바로 아래의 보조 헤드라인이다. 본문 카드나 플로우 영역처럼 보일 정도로 떨어뜨리면 실패다.
- 표/리스트 셀 안의 텍스트는 수평 정렬만이 아니라 수직 정렬도 확인한다. 셀 높이 대비 텍스트가 상단에 몰려 하단이 비면 실패로 본다. 셀 텍스트 박스는 셀 전체 높이 + middle anchor를 기본값으로 만든다.
- 불릿 리스트는 "• " 같은 텍스트 prefix로 만들지 않는다. 첫 글자가 영문인 줄과 한글인 줄의 폰트 메트릭이 달라 불릿 간격이 줄마다 달라진다. 불릿은 별도 도형 또는 고정 위치 요소로 분리한다.
- 좌우 비교 박스, 상단 예시 바, 하단 지표 바, 프로세스 플로우는 같은 left/right 기준선과 같은 높이 규칙을 사용한다. 같은 위계인데 폭, 높이, baseline이 다르면 실패다.
- 제목 옆 장식 라인, 번호 밑줄, shadow, divider는 의미를 설명하지 않으면 실패다. 연결선은 실제 단계 흐름에만 사용한다.
- 프로세스 카드에서 한 단계만 accent fill이나 강한 색으로 강조되어 있으면 강조 의미가 명시되어야 한다. `현재 단계`, `핵심 위험`, `선택 상태` 같은 이유가 없으면 같은 위계로 통일한다.
- 문장형 설명은 left align을 기본값으로 한다. 라벨은 짧게 분리하고, 설명 문장을 중앙 정렬해 읽기 흐름을 끊으면 실패다.
- 페이드 처리된 배경/장식 이미지도 겹침 검사 대상이다. "배경이니까 괜찮다"로 텍스트 박스와의 겹침을 통과시키지 않는다.
- 텍스트 위계는 `title`, `subtitle`, `section label`, `card title`, `body`, `caption`, `footer takeaway`가 서로 구분되는지 확인한다. 같은 페이지에서 본문이 제목보다 강하거나 보조 카드가 핵심 메시지를 압도하면 실패로 본다.
- 주요 본문은 발표 화면에서 읽히는 크기여야 한다. 작은 meta label을 제외하고 본문을 8-9pt대로 축소해 넣으면 실패다. 글자 크기를 줄이기 전에 문장 수, 카드 수, layout family를 바꾼다.
- 한국어 자간은 기본값을 유지한다. 한글 제목/본문에 negative letter spacing, 과한 condensed 느낌, 의미 단위를 깨는 강제 축소가 보이면 실패로 본다.
- contact sheet를 만들어 전체 흐름과 문제 슬라이드를 한 번에 볼 수 있어야 한다.
- 실패 슬라이드는 수정 후 다시 렌더링하고, 마지막 렌더 결과 기준으로만 전달한다.

### 3.1 피드백 반영 주의사항

- 사용자가 "레이아웃이 깨졌다", "QA가 된 게 맞냐", "텍스트 위계/간격/자간을 보라"고 지적하면 이전 QA는 실패로 간주한다. 변명하거나 기존 PASS를 유지하지 말고 기준을 높여 다시 검수한다.
- 단순히 overflow가 없다는 이유로 통과 처리하지 않는다. 발표용 장표는 읽히는 순서, 여백, 시각 비중, 정보 밀도가 자연스러워야 한다.
- contact sheet에서 작게 괜찮아 보여도 개별 PNG 확대에서 제목이 과밀하거나 카드가 답답하면 실패다.
- 문제 슬라이드만 고치고 끝내지 않는다. 같은 layout family를 쓰는 모든 슬라이드를 함께 확인해 같은 결함이 반복되는지 본다.
- 수정 후에는 PPTX를 다시 생성하고, PPTX 렌더 PNG, PDF, PDF 렌더 PNG를 모두 새로 만든다. 이전 렌더 이미지를 최종 증거로 재사용하지 않는다.
- QA report에는 실제로 본 항목을 슬라이드별로 남긴다. "전수 확인"이라고 쓰려면 페이지 수, PNG 수, PDF 페이지 수, 수동 확인 항목이 함께 있어야 한다.
- 한글 장표에서는 영문 디자인 관성으로 자간을 줄이지 않는다. 한글 제목이 커 보이면 자간이 아니라 제목 길이, 줄바꿈, font size, box width를 조정한다.
- 인포그래픽이 있는 슬라이드는 이미지가 좋다는 이유로 텍스트 레이아웃 검수를 생략하지 않는다. 이미지와 텍스트가 서로 다른 역할을 가져야 한다.

### 4. Korean Word Breaking

- 한국어 본문에는 `word-break: break-all`, `overflow-wrap: anywhere`를 기본값으로 쓰지 않는다.
- 웹/HTML 기반 장표는 한국어 텍스트에 `word-break: keep-all`을 우선 적용하고, 필요한 줄바꿈은 문장 단위로 직접 설계한다.
- PPTX 텍스트 박스는 조사, 어미, 단위가 줄 첫머리에 홀로 남지 않도록 문장을 짧게 나누거나 명시적 줄바꿈을 넣는다.
- 제목과 큰 본문은 한 줄에 의미 단위가 유지되는지 확인한다.
- 한국어 설명문은 직역투, AI 번역투, 어색한 현업 비사용어를 별도 패스로 다듬는다. 코드 식별자, 파일명, API 이름은 바꾸지 않는다.

### 4.1 폰트 지정과 임베드 검증

- python-pptx `font.name`은 latin 폰트만 지정한다. 한글 텍스트는 run 단위로 `<a:ea>`(+`<a:cs>`) typeface를 XML로 직접 지정해야 한다. ea 미지정 상태는 렌더러가 한글 폰트를 임의 대체하므로 실패로 본다.
- 폰트 패밀리명은 렌더러가 실제로 해석하는지 실증한다. macOS 시스템 한글 폰트는 LibreOffice에서 영문 패밀리명("Apple SD Gothic Neo")이 아니라 한글 로컬라이즈 패밀리명("Apple SD 산돌고딕 Neo", "나눔고딕")으로만 정상 해석되는 경우가 있다. 1장짜리 테스트 PPTX → PDF → `pdffonts`로 확인한 뒤 본 덱에 적용한다.
- 최종 PDF는 `pdffonts`로 임베드 폰트 목록을 확인한다. 의도한 패밀리 외의 대체 폰트(Arial Narrow, LiberationSans, STHeiti, NanumBrush 등)가 섞여 있으면 실패다. "시스템 폰트라 대체 없음" 같은 주장은 `pdffonts` 출력 없이 QA 리포트에 쓰지 않는다.
- 한글과 Latin/숫자의 웨이트가 같은 줄에서 달라 보이면(한쪽만 굵거나 좁음) 폰트 대체를 의심하고 임베드 목록부터 확인한다.

### 4.2 문체 일관성

- 슬라이드 본문의 종결 문체를 역할별로 정하고 전수 스캔한다. 기본 규칙: 제목·하단 핵심 문장은 합니다체, 카드/표/리스트 본문은 명사형 개조식, 인용문·질문형 점검표·학습 목표 원문은 원형 유지.
- 같은 슬라이드 안에서 카드 본문이 "~동작"(명사형)과 "~달라집니다"(합니다체)로 섞이면 실패다. `rg "습니다|합니다|한다\."`류 검색으로 본문 문자열을 훑고 역할별 규칙과 대조한다.
- 제목·카피는 문법이 맞아도 의미가 한 번에 잡히지 않으면 실패로 본다. 압축으로 주어/목적어가 생략돼 모호해진 문장(예: "구조화 출력은 서비스가 읽을 수 있어야 합니다")은 청중 언어로 풀어 쓴다.

### 5. PDF 동시 생성

- PPTX 또는 HTML deck을 납품할 때는 발표용 PDF도 함께 생성한다.
- PDF 페이지 수는 원본 슬라이드 수와 일치해야 한다.
- PDF도 페이지별 이미지로 렌더링해 contact sheet를 만들고, PPTX/HTML 렌더와 별도로 잘림과 overflow를 확인한다.
- PDF 생성이 실패하면 최종 응답에 실패 사유와 재현 명령을 적고, PPT만 성공한 상태를 완료로 처리하지 않는다.

## 필수 산출물

- 편집 가능한 원본: `.pptx` 또는 HTML deck source
- 발표용 PDF: `.pdf`
- 전수 렌더 이미지: slide/page별 PNG 또는 screenshot
- contact sheet: 전체 슬라이드를 한 번에 확인할 수 있는 이미지
- QA report 또는 manual review: 슬라이드별 PASS/FAIL과 수정 이력
- slide intent manifest: 슬라이드별 `slide_intent`, `layout_family`, `example_type`, `audience_fit`, 반복 사용 사유
- 이미지 manifest: 생성 이미지나 외부 시각 자료를 사용한 경우. 인포그래픽은 imagegen 실행 기록과 asset path가 필수다.

## 권장 검증 순서

1. 콘텐츠 구조와 슬라이드별 메시지를 확정한다.
2. 각 슬라이드의 `slide_intent`, `layout_family`, `example_type`을 정하고 반복 패턴을 점검한다.
3. 챕터별 예시, 전후 비교, 진단표, 실습 장표가 충분한지 확인한다.
4. 인포그래픽이 필요한 슬라이드를 표시하고 asset manifest를 만든다.
5. PPTX/HTML을 생성한다.
6. 전체 슬라이드를 렌더링하고 contact sheet를 만든다.
7. 각 slide/page PNG를 개별 확대 검수하고 레이아웃 간격, 텍스트 위계, 자간, overflow, Korean word breaking을 수정한다.
8. PDF를 생성한다.
9. PDF 전체 페이지를 렌더링하고 contact sheet를 만든다.
10. 최종 QA report에 산출물 경로, 페이지 수, 남은 리스크를 기록한다.

## 검증 명령 예시

```bash
soffice --headless --convert-to pdf --outdir <out>/pdf <deck>.pptx
pdfinfo <out>/pdf/<deck>.pdf
pdffonts <out>/pdf/<deck>.pdf   # 임베드 폰트가 의도한 패밀리뿐인지 확인
pdftoppm -png -r 150 <out>/pdf/<deck>.pdf <out>/qa_pdf_render/png/slide
```

HTML deck을 사용하는 경우 `future-slide-qa` 또는 동등한 Playwright 기반 렌더 QA를 함께 실행한다. PPTX를 직접 생성하는 경우에도 같은 수준의 전체 슬라이드 이미지 렌더와 contact sheet를 남긴다.
