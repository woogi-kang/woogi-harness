---
name: content-pipeline
description: 콘텐츠 생산 자동화 파이프라인 스킬
model: inherit
quality_tier: implementation
triggers:
  - "블로그"
  - "콘텐츠"
  - "파이프라인"
  - "아웃라인"
  - "드래프트"
  - "뉴스레터"
---

# Content Pipeline Skill

콘텐츠 기획부터 생산, 배포까지 자동화하는 스킬입니다.

## 핵심 원칙

| 원칙 | 설명 |
|------|------|
| **속도와 품질** | AI 드래프트 + 인간 검토 |
| **재활용** | 1개 콘텐츠 → 다중 포맷 |
| **데이터 기반** | 성과 분석 → 전략 개선 |

## 콘텐츠 유형

```yaml
content_types:
  pillar_content:
    description: "핵심 주제 종합 가이드"
    length: "3,000-5,000 단어"
    frequency: "월 1-2개"
    purpose: "도메인 권위, 검색 순위"
    example: "SaaS 결제 연동 완벽 가이드"

  cluster_content:
    description: "Pillar 연결 세부 주제"
    length: "1,500-2,500 단어"
    frequency: "주 2-3개"
    purpose: "롱테일 키워드, 내부 링크"
    example: "포트원 API 연동 튜토리얼"

  thought_leadership:
    description: "인사이트, 의견, 트렌드"
    length: "800-1,500 단어"
    frequency: "주 1개"
    purpose: "브랜드, 신뢰, 공유"
    example: "2026년 SaaS 결제 트렌드 전망"

  case_study:
    description: "고객 성공 사례"
    length: "1,000-2,000 단어"
    frequency: "월 1-2개"
    purpose: "신뢰, 전환"
    example: "A사가 결제 연동 시간을 80% 단축한 방법"

  comparison:
    description: "제품/서비스 비교"
    length: "2,000-3,000 단어"
    frequency: "필요시"
    purpose: "구매 고려 단계 타겟"
    example: "포트원 vs Stripe: 어떤 것을 선택해야 할까?"
```

## 콘텐츠 생산 워크플로우

### Phase 1: 기획

```yaml
planning_phase:
  step_1_topic_research:
    input: "키워드 리서치 결과"
    activities:
      - 타겟 키워드 선정
      - 검색 의도 파악
      - 경쟁 콘텐츠 분석
    output: "콘텐츠 브리프"

  step_2_content_brief:
    template: |
      ## 콘텐츠 브리프

      **타겟 키워드**: [주요 키워드]
      **검색 의도**: [정보형/거래형/비교형]
      **타겟 독자**: [페르소나]
      **콘텐츠 목표**: [인지/고려/전환]

      **경쟁 콘텐츠 분석**:
      - Top 1: [URL] - 강점/약점
      - Top 2: [URL] - 강점/약점
      - Top 3: [URL] - 강점/약점

      **우리의 차별점**:
      - [차별점 1]
      - [차별점 2]

      **포함할 내용**:
      - [ ] 서브토픽 1
      - [ ] 서브토픽 2
      - [ ] FAQ 섹션
      - [ ] 실전 예제
```

### Phase 2: 아웃라인 생성

```yaml
outline_generation:
  structure:
    hook:
      purpose: "첫 문단으로 주의 끌기"
      elements:
        - "문제 제기 또는 질문"
        - "통계 또는 사실"
        - "이 글에서 얻을 것"

    body:
      purpose: "핵심 내용 전달"
      h2_count: "5-8개"
      each_section:
        - "서브 헤딩 (H3)"
        - "예시 또는 증거"
        - "실행 가능한 팁"

    conclusion:
      purpose: "요약 및 행동 유도"
      elements:
        - "핵심 포인트 요약"
        - "다음 단계 제안"
        - "CTA"

  example_outline: |
    # SaaS 결제 연동 완벽 가이드 (2026)

    ## 도입
    - Hook: 결제 연동 실패로 매출 손실 사례
    - 이 글에서 배울 것

    ## 1. 결제 연동이란?
    ### 1.1 기본 개념
    ### 1.2 왜 중요한가

    ## 2. 결제 게이트웨이 비교
    ### 2.1 포트원
    ### 2.2 Stripe
    ### 2.3 비교 표

    ## 3. 포트원 연동 단계별 가이드
    ### 3.1 계정 설정
    ### 3.2 API 키 발급
    ### 3.3 코드 구현
    ### 3.4 테스트

    ## 4. 흔한 실수와 해결법
    ### 4.1 실수 1
    ### 4.2 실수 2

    ## 5. 보안 체크리스트

    ## 6. FAQ

    ## 7. 결론 + CTA
```

### Phase 3: AI 드래프트

```yaml
ai_draft:
  prompt_template: |
    다음 브리프와 아웃라인을 바탕으로 블로그 글을 작성해주세요.

    ## 브리프
    {content_brief}

    ## 아웃라인
    {outline}

    ## 작성 가이드라인
    - 톤: 전문적이지만 친근하게
    - 타겟: {target_audience}
    - 길이: {target_length} 단어
    - 주요 키워드: {primary_keyword}
    - 포함할 키워드: {secondary_keywords}

    ## 필수 포함 요소
    - 실제 코드 예제
    - 비교 표
    - 스크린샷 위치 표시 [IMAGE: 설명]
    - 내부 링크 제안 [INTERNAL: /path]
    - 외부 링크 제안 [EXTERNAL: 설명]

  quality_checks:
    - [ ] 타겟 키워드 자연스럽게 포함
    - [ ] H2 마다 가치 전달
    - [ ] 실행 가능한 조언 포함
    - [ ] 코드 예제 정확성
```

### Phase 4: 인간 검토

```yaml
human_review:
  time_estimate: "15분/글"

  checklist:
    accuracy:
      - [ ] 기술적 정확성 확인
      - [ ] 코드 동작 검증
      - [ ] 최신 정보 확인

    brand_voice:
      - [ ] 톤 일관성
      - [ ] 브랜드 가이드라인 준수
      - [ ] 과도한 AI 느낌 제거

    value:
      - [ ] 독자에게 실질적 가치?
      - [ ] 경쟁 콘텐츠 대비 차별점?
      - [ ] 행동 유도 명확?

    legal:
      - [ ] 저작권 이슈 없음
      - [ ] 경쟁사 비방 없음
```

### Phase 5: 발행

```yaml
publishing:
  platforms:
    primary:
      - WordPress
      - Hashnode
      - Notion (공개 페이지)

    syndication:
      - Dev.to
      - Medium
      - LinkedIn Article

  pre_publish_checklist:
    - [ ] SEO 메타 태그 설정
    - [ ] OG 이미지 설정
    - [ ] 내부/외부 링크 확인
    - [ ] 이미지 alt 텍스트
    - [ ] 구조화 데이터
    - [ ] 발행 일시 설정
```

## 콘텐츠 재활용

### 1개 블로그 → 다중 콘텐츠

```yaml
content_repurposing:
  source: "블로그 포스트 1개"

  outputs:
    twitter_thread:
      count: 5
      format: |
        1/ 🧵 {주제} 완벽 가이드

        {핵심 문제 제기}

        ↓ 스레드에서 배울 것들:
        • {포인트 1}
        • {포인트 2}
        • {포인트 3}

        ---
        2/ {포인트 1 상세}
        ...

    linkedin_post:
      count: 3
      format: |
        {훅 - 질문 또는 통찰}

        {3-4 문단 핵심 내용}

        💡 Key takeaways:
        → {테이크어웨이 1}
        → {테이크어웨이 2}

        {CTA}

        #SaaS #결제 #개발

    instagram_carousel:
      slides: 10
      format:
        - slide_1: "커버 - 제목"
        - slide_2-8: "핵심 포인트"
        - slide_9: "요약"
        - slide_10: "CTA + 저장 유도"

    youtube_script:
      format: |
        [INTRO - 30초]
        {훅 + 채널 소개}

        [BODY - 5-8분]
        {아웃라인 기반 스크립트}

        [OUTRO - 30초]
        {요약 + CTA + 구독 유도}

    newsletter_excerpt:
      format: |
        이번 주 하이라이트: {제목}

        {2-3 문단 요약}

        👉 전문 읽기: {링크}

    podcast_talking_points:
      format:
        - intro: "주제 소개"
        - point_1: "핵심 포인트 1"
        - point_2: "핵심 포인트 2"
        - stories: "관련 경험/사례"
        - outro: "요약 + CTA"
```

## 콘텐츠 캘린더

### 주간 스케줄 템플릿

```yaml
weekly_schedule:
  monday:
    - task: "키워드 리서치 + 주간 기획"
    - output: "이번 주 콘텐츠 브리프 5개"

  tuesday:
    - task: "아웃라인 작성 + AI 드래프트"
    - output: "드래프트 2-3개"

  wednesday:
    - task: "인간 검토 + 수정"
    - output: "발행 준비 완료 2개"

  thursday:
    - task: "발행 + 소셜 콘텐츠 생성"
    - output: "블로그 발행, 소셜 포스트 준비"

  friday:
    - task: "소셜 배포 + 주간 분석"
    - output: "소셜 발행, 성과 리포트"
```

### 월간 콘텐츠 믹스

```yaml
monthly_content_mix:
  total_posts: 20

  distribution:
    pillar_content: 2      # 10%
    cluster_content: 10    # 50%
    thought_leadership: 4  # 20%
    case_studies: 2        # 10%
    comparisons: 2         # 10%

  theme_focus:
    primary: "월별 메인 주제"
    secondary: "보조 주제 2-3개"
```

## CLI 사용법

```bash
# 콘텐츠 브리프 생성
/content brief --keyword "SaaS 결제" --type pillar

# 아웃라인 생성
/content outline --brief {brief_file}

# AI 드래프트 작성
/content draft --outline {outline_file}

# 콘텐츠 재활용
/content repurpose --source {blog_file} --formats twitter,linkedin

# 콘텐츠 캘린더 생성
/content calendar --month 2026-02

# 성과 분석
/content analyze --period 30d
```

## 출력 포맷

### 콘텐츠 브리프

```json
{
  "type": "content_brief",
  "created_at": "2026-01-27",

  "topic": {
    "title": "SaaS 결제 연동 완벽 가이드",
    "primary_keyword": "SaaS 결제 연동",
    "secondary_keywords": ["포트원 연동", "Stripe 연동", "결제 API"],
    "search_intent": "informational",
    "content_type": "pillar"
  },

  "target": {
    "persona": "초기 SaaS 창업자, 백엔드 개발자",
    "pain_points": ["결제 연동 복잡", "어떤 PG 선택?", "보안 우려"],
    "goal": "결제 연동 의사결정 및 구현 지원"
  },

  "competition": {
    "top_results": [
      {
        "url": "competitor1.com/guide",
        "strengths": ["상세한 코드", "최신 정보"],
        "weaknesses": ["한국 PG 부족", "비교 없음"]
      }
    ],
    "our_angle": "한국 시장 중심 + 실전 비교 + 보안 체크리스트"
  },

  "requirements": {
    "word_count": 4000,
    "sections": ["개념", "비교", "튜토리얼", "보안", "FAQ"],
    "must_include": ["코드 예제", "비교 표", "체크리스트"]
  }
}
```

### 재활용 콘텐츠 결과

```json
{
  "source": "/blog/saas-payment-guide.md",
  "generated_at": "2026-01-27",

  "outputs": {
    "twitter_thread": {
      "tweets": 5,
      "content": [
        "1/ 🧵 SaaS 결제 연동, 어디서부터 시작해야 할지 막막하신가요?\n\n3년간 100+ SaaS를 도우며 깨달은 핵심을 공유합니다.\n\n↓",
        "2/ 첫 번째: 결제 게이트웨이 선택\n\n한국 시장: 포트원 (구 아임포트)\n- 모든 국내 PG 통합\n- 간편결제 지원\n\n글로벌: Stripe\n- 135개국 지원\n- 개발자 친화적",
        "..."
      ]
    },
    "linkedin_posts": {
      "count": 3,
      "posts": ["...", "...", "..."]
    },
    "newsletter": {
      "subject": "🔧 이번 주: SaaS 결제 연동 마스터하기",
      "preview": "포트원 vs Stripe, 어떤 것을 선택해야 할까요?",
      "body": "..."
    }
  },

  "publishing_schedule": {
    "twitter": "2026-01-28 09:00",
    "linkedin_1": "2026-01-28 08:00",
    "linkedin_2": "2026-01-30 12:00"
  }
}
```

## 품질 기준

```yaml
quality_standards:
  readability:
    flesch_score: "> 60"
    avg_sentence_length: "< 20 words"
    paragraph_length: "3-4 sentences"

  seo:
    keyword_density: "1-2%"
    internal_links: ">= 3"
    external_links: ">= 2"
    images: ">= 3"

  engagement:
    hook_quality: "문제/질문으로 시작"
    subheadings: "스캔 가능"
    cta_presence: "명확한 행동 유도"

  accuracy:
    code_tested: true
    facts_verified: true
    links_working: true
```

---

Version: 1.0.0
Last Updated: 2026-01-27
