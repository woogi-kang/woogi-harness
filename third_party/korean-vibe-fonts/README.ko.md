# Korean Vibe Fonts ✨

한글 웹폰트를 "뭘 쓰지?" 고민하지 않고, 원하는 분위기에 맞게 추천받는 패키지입니다.

## 📣 더 배우고 싶다면

클로드코드를 비개발자의 시각으로 쉽게 배우고 싶다면 아래 강의를 확인해보세요.

👉 [강의 보러 가기](https://inf.run/BgjkJ)

`퇴근후AI (afterworkai.club)`는 퇴근 후에도 AI를 쉽고 재미있게 익히고 싶은 분들을 위한 커뮤니티입니다.

👉 [퇴근후AI 소개 보기](https://afterworkai.club)
👉 [퇴근후AI 단톡방 참여하기](https://open.kakao.com/o/gzdwHNQh)

이 패키지는 AI 도구가:

- 분위기에 맞는 한글 폰트를 고르고
- 상업적으로 써도 비교적 안전한 폰트를 우선 추천하고
- 바로 붙여 넣을 수 있는 코드까지 같이 내주도록 도와줍니다.

## 🙋 이건 누가 쓰면 좋나요?

이런 분께 특히 잘 맞습니다.

- 랜딩 페이지를 빠르게 만들고 싶은 사람
- 포트폴리오 분위기를 한 번에 잡고 싶은 사람
- "좀 더 세련되게", "좀 더 따뜻하게" 같은 감성 요청을 자주 하는 사람
- Codex, Claude Code 같은 AI 코딩 도구를 쓰는 사람
- 개발을 깊게 몰라도 AI에게 폰트 선택을 잘 시키고 싶은 사람

## 💡 이걸 쓰면 뭐가 좋아요?

예전에는 이렇게 막연했을 수 있어요.

> "한글 폰트 뭐 쓰지?"

이제는 이렇게 말하면 됩니다.

> "AI SaaS 느낌으로 해줘"
> "차분한 에디토리얼 무드로 해줘"
> "귀엽고 발랄하게 보여줘"
> "개발자 포트폴리오 느낌으로 추천해줘"

그러면 도구가 보통 아래를 같이 알려줍니다.

- 본문용 폰트
- 제목용 폰트
- 필요하면 코드용 폰트
- 바로 붙여 넣는 `<link>` 태그
- 바로 붙여 넣는 CSS
- 비슷한 대안 폰트

추가로 중요한 원칙이 하나 있습니다.

- 화면이나 장표 구성이 달라져도, 같은 역할의 텍스트는 같은 폰트 계열을 유지합니다.

예를 들면:

- 제목은 계속 제목용 폰트
- 본문, 설명, 캡션, 표 텍스트는 계속 본문용 폰트
- 코드나 터미널은 계속 코드용 폰트

그래야 결과물이 바뀌어도 전체 인상은 한 팀이 만든 것처럼 정리됩니다.

## 🧸 비개발자도 쓸 수 있나요?

네, 충분히 가능합니다.

직접 프로그램을 많이 만지지 않더라도:

- AI 도구에 이 패키지를 붙여 두고
- 원하는 분위기를 말한 뒤
- 나온 코드만 복사해서 쓰거나
- 개발자에게 그대로 전달하면 됩니다.

즉, "폰트를 고르는 기준"과 "적용 코드"를 한 번에 받는 도우미라고 생각하시면 됩니다.

## 📦 안에 들어 있는 것

- [SKILL.md](./SKILL.md): Codex에서 읽는 핵심 스킬 파일
- [agents/openai.yaml](./agents/openai.yaml): Codex 메타데이터
- [references/font_catalog.json](./references/font_catalog.json): 검증된 폰트 목록
- [references/vibe_presets.md](./references/vibe_presets.md): 자주 쓰는 분위기 프리셋
- [scripts/recommend_font.py](./scripts/recommend_font.py): 폰트 추천기
- [scripts/render_claude_agent.py](./scripts/render_claude_agent.py): Claude Code용 파일 생성기
- [adapters/claude-code-agent.template.md](./adapters/claude-code-agent.template.md): Claude Code용 템플릿
- [adapters/generic-system-prompt.md](./adapters/generic-system-prompt.md): 다른 AI 도구용 기본 프롬프트

## 🚀 설치는 이렇게 생각하면 쉬워요

이 부분이 헷갈릴 수 있는데, 핵심은 이겁니다.

- 먼저 이 패키지 폴더를 내 컴퓨터에 둡니다.
- 그 다음 내가 쓰는 AI 도구에 맞게 "연결"만 해주면 됩니다.

즉, 설치는 보통 2단계입니다.

### 1단계. 이 패키지를 내 컴퓨터에 받기

GitHub 저장소라면 보통 이렇게 받습니다.

```bash
git clone <repo-url>
cd korean-vibe-fonts
```

이미 폴더를 받은 상태라면 이 단계는 건너뛰면 됩니다.

### 2단계. 내가 쓰는 도구에 연결하기

#### Codex를 쓴다면

Codex에서는 일반적인 스킬 설치 방식대로, 이 폴더가 `~/.codex/skills/` 아래에 있으면 됩니다.

방법은 2가지입니다.

1. 폴더를 그대로 복사하기
2. 원래 위치를 유지하고 링크만 걸기

예시:

```bash
ln -s /path/to/korean-vibe-fonts ~/.codex/skills/korean-vibe-fonts
```

또는 직접 복사:

```bash
cp -R /path/to/korean-vibe-fonts ~/.codex/skills/korean-vibe-fonts
```

이렇게 두면 Codex가 자동으로 읽습니다.

#### Claude Code를 쓴다면

여기가 Codex와 다른 부분입니다.

하지만 이 패키지가 이상한 게 아니라, **Claude Code의 일반적인 방식 자체가 Codex와 다르기 때문**입니다.

Claude Code는 보통 Codex처럼 "스킬 폴더를 직접 설치"하지 않고, `~/.claude/agents/` 또는 `.claude/agents/` 안에 **서브에이전트 Markdown 파일**을 등록해서 씁니다.

그래서 이 패키지에서는 그 방식에 맞춰, Claude Code용 파일을 자동으로 만들어주는 스크립트를 함께 넣었습니다.

전역으로 쓰고 싶다면:

```bash
python3 /path/to/korean-vibe-fonts/scripts/render_claude_agent.py \
  --output ~/.claude/agents/korean-vibe-fonts.md
```

현재 프로젝트에서만 쓰고 싶다면:

```bash
mkdir -p .claude/agents
python3 /path/to/korean-vibe-fonts/scripts/render_claude_agent.py \
  --output .claude/agents/korean-vibe-fonts.md
```

즉:

- Codex의 일반 방식: `~/.codex/skills/` 안에 폴더 두기
- Claude Code의 일반 방식: `.claude/agents/*.md` 파일 만들기

이 패키지는 두 방식 모두 지원하도록 만든 것입니다.

참고 문서:

- [Claude Code subagents](https://docs.anthropic.com/en/docs/claude-code/sub-agents)

#### 다른 AI 도구를 쓴다면

그 도구가 Codex 스킬이나 Claude Code 서브에이전트를 바로 지원하지 않아도 괜찮습니다.

이 파일부터 시작하면 됩니다.

- [adapters/generic-system-prompt.md](./adapters/generic-system-prompt.md)

가능하면 아래 파일도 같이 보여주면 추천 품질이 더 좋아집니다.

- `references/font_catalog.json`
- `references/vibe_presets.md`
- `scripts/recommend_font.py`

## 🎨 어떤 상황에 잘 맞나요?

예를 들면:

- AI SaaS 랜딩 페이지
- 개발자 포트폴리오
- 프리미엄 브랜드 소개 페이지
- 차분한 에디토리얼 페이지
- 귀엽고 밝은 커뮤니티 서비스
- 강한 이벤트 / 캠페인 페이지

## 🗣️ 이렇게 말하면 됩니다

AI에게 아래처럼 요청해보세요.

- "한글 웹폰트 추천해줘. AI 스타트업 랜딩 느낌이야."
- "브랜드 스토리 페이지에 어울리는 폰트 골라줘."
- "귀엽고 친근한 커뮤니티 앱 느낌으로 추천해줘."
- "개발자 포트폴리오에 맞는 한글 폰트 조합 줘."
- "상업적으로 써도 괜찮은 한글 웹폰트로 골라줘."

## ⚡ 바로 테스트해보고 싶다면

터미널에서 아래처럼 실행할 수 있습니다.

```bash
python3 scripts/recommend_font.py --theme "AI SaaS 랜딩 페이지"
python3 scripts/recommend_font.py --theme "차분한 에디토리얼 포트폴리오"
python3 scripts/recommend_font.py --theme "귀엽고 발랄한 커뮤니티 앱"
```

그러면 보통 이런 결과가 나옵니다.

- 추천 폰트 조합
- 왜 잘 맞는지 짧은 설명
- `<link>` 태그
- CSS 변수
- 대안 폰트 1~3개

## 🔤 전체 폰트 리스트

현재 이 패키지에 들어 있는 전체 폰트는 아래와 같습니다.

### 본문과 제목에 두루 쓰기 좋은 폰트

- `Pretendard Variable`: 가장 무난한 현대적 기본값. 제품형 UI, 랜딩, 포트폴리오에 잘 맞습니다.
- `NanumSquare Neo`: 직선적이고 브랜드 힘이 강합니다. 메인 타이틀과 카드 UI에 특히 좋습니다.
- `NanumSquare`: 반듯하고 친근합니다. 스타트업, 커뮤니티, 모바일 화면에 잘 어울립니다.
- `NanumGothic`: 익숙하고 안정적인 본문용입니다. 공지, 고객지원, 문서형 페이지에 안전합니다.
- `Gmarket Sans`: 세련되고 깔끔한 브랜드 인상입니다. 이커머스, 모바일 프로모션, 스타트업 랜딩에 잘 맞습니다.
- `Spoqa Han Sans Neo`: UI/UX에 특히 강합니다. 숫자와 정보 가독성이 좋아 제품형 서비스와 대시보드에 잘 맞습니다.
- `Goorm Sans`: 한글과 영문의 균형이 좋습니다. 개발자 제품, 테크 랜딩, 깔끔한 서비스 UI에 잘 어울립니다.
- `S-Core Dream`: 9가지 굵기를 쓸 수 있는 깔끔한 고딕체입니다. 상업 사용 자체는 가능하지만 공식 안내상 파일 수정이 제한되고 공식 웹폰트 CSS가 없어, 이 패키지에서는 `수동 검토 필요` 및 `자동 추천 제외` 상태로 보수적으로 취급합니다.
- `IBM Plex Sans KR`: 공학적이고 차분합니다. B2B, 개발자 도구, 데이터 제품에 잘 맞습니다.
- `Noto Sans KR`: 글로벌 서비스에 쓰기 좋은 중립적 기본값입니다. 다국어 환경에서도 안정적입니다.
- `MaruBuri`: 부드럽고 온기 있는 부리체입니다. 브랜드 스토리와 장문 콘텐츠에 좋습니다.
- `Hahmlet`: 문학적이고 우아합니다. 프리미엄 에디토리얼이나 전시형 페이지에 잘 맞습니다.
- `Noto Serif KR`: 정갈하고 공신력 있는 부리체입니다. 기관형, 정책형, 신뢰형 페이지에 좋습니다.
- `Gowun Dodum`: 부드럽고 잔잔합니다. 웰니스, 라이프스타일, 커뮤니티에 잘 어울립니다.
- `Gowun Batang`: 시적인 여백감이 있습니다. 에세이, 감성 브랜드 저널, 차분한 포트폴리오에 좋습니다.
- `NanumSquareRound`: 동글고 경쾌합니다. 교육, 가족형 서비스, 캐주얼 커뮤니티에 잘 맞습니다.

### 제목용으로 특히 강한 폰트

- `Black Han Sans`: 존재감이 강한 타이틀용 폰트입니다. 포스터, 이벤트, 캠페인 히어로에 좋습니다.
- `Do Hyeon`: 좁고 단단하게 밀어붙이는 느낌입니다. 배너, 게임, 이커머스 프로모션에 강합니다.
- `여기어때 잘난체`: 주목도가 높은 제목용 폰트입니다. 여행, 숙박, 생활형 프로모션 타이틀에 특히 잘 붙습니다.
- `Jua`: 명랑하고 친근합니다. 음식, 가족형, 밝은 커뮤니티 서비스에 잘 어울립니다.

### 코드용 폰트

- `NanumGothicCoding (D2Coding)`: 코드 블록과 터미널에 가장 안정적입니다. 한글, 영문, 기호 구분이 좋습니다.

### 포인트용 손글씨/개성 폰트

- `NanumPen`: 메모, 후기, 짧은 강조 문구에 잘 맞습니다.
- `Gaegu`: 낙서 같은 자유로움이 있어서 실험적이고 장난스러운 포인트용으로 좋습니다.
- `Single Day`: 정돈된 손글씨 느낌으로 일기, 후기, 작은 브랜드 메모 섹션에 잘 어울립니다.

더 자세한 메타데이터와 공식 링크는 [references/font_catalog.json](./references/font_catalog.json)에서 볼 수 있습니다.

## ❤️ 이 패키지가 다른 디자인 스킬과 다른 점

일반적인 디자인 스킬은 보통 이렇게 말합니다.

- "예쁜 폰트를 골라라"
- "너무 흔한 폰트는 피하라"

이 패키지는 거기서 한 걸음 더 갑니다.

- 한글 웹폰트에 집중하고
- 상업용 사용 가능성을 직접 체크하고
- 분위기와 폰트를 연결해주고
- 바로 붙여 넣을 코드까지 같이 줍니다.

## 🔒 폰트는 아무거나 넣지 않았어요

현재 폰트 목록은 공식 출처를 보고 직접 확인한 것만 넣었습니다.

참고:

- `S-Core Dream`은 상업 사용 문구는 확인했지만, 공식 hosted webfont CSS가 없고 파일 수정 제한 문구가 있어 `자동 추천용 웹폰트`로는 제외했습니다.

주요 기준:

- NAVER 한글한글 아름답게
- Google Fonts
- Pretendard 공식 저장소와 라이선스

새 폰트를 추가하고 싶다면 꼭 확인하세요.

- 공식 라이선스 문서
- 실제로 적용 가능한 공식 stylesheet URL, CDN 경로, 또는 공식 셀프호스팅 안내

## 🌱 가장 추천하는 시작 방법

가장 쉽게 쓰려면 이렇게 하세요.

1. Codex 또는 Claude Code에 이 패키지를 연결합니다.
2. 원하는 분위기를 한 문장으로 말합니다.
3. 나온 폰트 추천과 코드를 그대로 사용합니다.

정말 이 3단계면 충분합니다.

## 📍 한 줄 요약

이 패키지는 "한글 폰트 감각 좋은 AI 도우미"입니다.  
분위기를 말하면, 어울리는 상업용 한글 웹폰트와 적용 코드까지 같이 줍니다 ✨
