---
name: social-compliance
description: |
  소셜미디어 콘텐츠의 법적 준수사항을 검토합니다.

  활성화 조건:
  - "법적 검토해줘"
  - "광고 표시 확인해줘"
  - "저작권 체크해줘"
  - "컴플라이언스 검토"
  - "규정 준수 확인"
---

# 3. Compliance: 법적 준수 검토

## 개요

소셜미디어 콘텐츠 발행 전 법적 리스크를 검토하여 벌금, 소송, 브랜드 신뢰도 하락을 방지합니다.

## 1. 광고 표시 (Disclosure)

### FTC 가이드라인 (미국) / 공정위 지침 (한국)

```yaml
disclosure_requirements:
  sponsored_content:
    required_when:
      - 금전적 보상을 받은 경우
      - 무료 제품/서비스를 제공받은 경우
      - 브랜드와 고용/계약 관계인 경우
      - 제휴 링크를 포함한 경우

    acceptable_hashtags:
      - "#광고"
      - "#ad"
      - "#sponsored"
      - "#유료광고"
      - "#협찬"

    unacceptable_hashtags:
      - "#ambassador"  # 불명확
      - "#partner"     # 불명확
      - "#thanks[브랜드]"  # 불명확
      - "#gifted"      # 일부 국가에서만 인정

    placement:
      - 캡션 첫 부분에 위치 (스크롤 없이 보이게)
      - 영상: 화면에 텍스트로 표시 + 음성 언급
      - 스토리: 각 프레임에 표시
      - 해시태그 뭉치에 숨기지 않기

  affiliate_links:
    disclosure: "제휴 링크가 포함되어 있습니다"
    placement: "링크 앞 또는 캡션 시작 부분"
```

### 플랫폼별 네이티브 도구

| 플랫폼 | 광고 표시 도구 | 사용 방법 |
|--------|---------------|----------|
| Instagram | "Paid partnership" 태그 | 브랜디드 콘텐츠 도구 |
| LinkedIn | "Promoted" 라벨 | 광고 설정 |
| X | "Promoted" 라벨 | 광고 대시보드 |
| Threads | 수동 해시태그 | #ad 표기 |

## 2. 저작권 (Copyright)

### 체크리스트

```yaml
copyright_check:
  images:
    - 직접 촬영한 이미지인가?
    - 스톡 이미지 라이선스가 상업용인가?
    - AI 생성 이미지의 사용 조건을 확인했는가?
    - 다른 사람의 이미지를 허가 없이 사용하지 않았는가?
    - 이미지에 포함된 상표/로고에 대한 허가가 있는가?

  music_audio:
    - 상업용 라이선스가 있는가?
    - 플랫폼 제공 무료 음원인가?
    - 저작권 있는 음악을 무단 사용하지 않았는가?
    - 인터뷰/음성 녹음에 동의를 받았는가?

  video:
    - 모든 출연자에게 동의를 받았는가?
    - 타인의 영상을 무단 사용하지 않았는가?
    - 배경에 저작권 콘텐츠(TV, 음악 등)가 없는가?

  text:
    - 인용문의 출처를 명시했는가?
    - 타인의 글을 무단 복제하지 않았는가?
    - 번역물의 저작권을 확인했는가?
```

### 라이선스 유형

| 라이선스 | 상업적 사용 | 수정 가능 | 출처 표시 |
|----------|------------|----------|----------|
| CC0 (Public Domain) | ✓ | ✓ | 불필요 |
| CC BY | ✓ | ✓ | 필수 |
| CC BY-SA | ✓ | ✓ (동일 조건) | 필수 |
| CC BY-NC | ✗ | ✓ | 필수 |
| Editorial Use Only | ✗ (뉴스만) | ✗ | 필수 |
| Rights Managed | 조건부 | 조건부 | 조건부 |

### 안전한 이미지 소스

```yaml
safe_image_sources:
  free_commercial:
    - Unsplash (대부분 무료)
    - Pexels
    - Pixabay
    - Freepik (출처 표시 필요)

  paid:
    - Shutterstock
    - Getty Images
    - Adobe Stock

  ai_generated:
    - image-prompt → Codex gpt-image-2 (OpenAI 이용약관과 실제 배포 권리 확인)
```

## 3. 상표권 (Trademark)

```yaml
trademark_guidelines:
  do:
    - 상표를 형용사로 사용 ("iPhone 스마트폰")
    - ® 또는 ™ 기호 표시 (첫 언급 시)
    - 공식 명칭 사용

  dont:
    - 상표를 일반 명사처럼 사용
    - 경쟁사 상표를 비방에 사용
    - 상표를 변형/패러디 (허가 없이)
    - 로고를 무단 변형

  competitor_mentions:
    allowed:
      - 사실에 기반한 비교
      - 호환성 설명 ("~와 호환")
    prohibited:
      - 허위/과장 비교
      - 비방/폄하
      - 혼동을 유발하는 사용
```

## 4. 개인정보 보호

```yaml
privacy_compliance:
  user_content:
    - UGC 리포스트 시 원작자 동의 필수
    - DM/댓글 캡처 시 개인정보 블라인드
    - 고객 후기 사용 시 동의서 확보

  tagging:
    - 얼굴 태그 전 동의 확인
    - 위치 태그 시 민감 장소 주의
    - 미성년자 태그 보호자 동의

  data_collection:
    - 이벤트 참여 시 개인정보 수집 고지
    - 개인정보 처리방침 링크 제공
    - 동의 철회 방법 안내
```

## 5. 산업별 특수 규정

### 금융/투자

```yaml
financial_compliance:
  required:
    - 투자 위험 고지문
    - "과거 수익이 미래를 보장하지 않음" 문구
    - 금융감독원 등록 정보
    - 이해상충 공시

  prohibited:
    - 확정 수익률 약속
    - 원금 보장 암시
    - 미등록 금융상품 광고
```

### 의료/건강

```yaml
healthcare_compliance:
  required:
    - "의료 전문가와 상담하세요" 문구
    - 효능 주장의 과학적 근거
    - 부작용/주의사항 고지

  prohibited:
    - 의약품 허위 효능 주장
    - 처방전 없이 구매 유도
    - 의료 진단/처방 대체 암시
```

### 주류/담배

```yaml
alcohol_tobacco_compliance:
  age_restriction:
    - 타겟팅: 법정 음주 연령 이상만
    - 콘텐츠에 미성년자 등장 금지
    - 연령 확인 문구 필수

  prohibited:
    - 과음 조장
    - 운전/위험 활동과 연결
    - 건강상 이점 주장
```

### 경품/이벤트

```yaml
contest_compliance:
  required:
    - 참여 자격 명시
    - 당첨 확률 공개 (추첨 시)
    - 경품 내역 상세 기재
    - 개인정보 수집/이용 동의
    - 세금 부담 주체 명시

  regional_rules:
    korea:
      - 경품류 제공 고시 준수
      - 카드사 이벤트: 여신전문금융업법
    us:
      - "No purchase necessary" 문구
      - Void where prohibited
```

## 6. AI 생성 콘텐츠 표시

```yaml
ai_disclosure:
  when_required:
    - AI로 생성/수정된 이미지
    - AI 작성 텍스트 (플랫폼 정책에 따라)
    - 딥페이크/합성 영상

  how_to_disclose:
    - "#AIGenerated" 해시태그
    - "AI로 생성된 이미지입니다" 문구
    - 플랫폼 네이티브 라벨 (있는 경우)

  platform_policies:
    meta: "AI 생성 콘텐츠 라벨링 권장"
    x: "Community Notes로 검증"
    linkedin: "명확한 정책 없음 (투명성 권장)"
```

## 컴플라이언스 체크리스트

```yaml
compliance_checklist:
  pre_publish:
    disclosure:
      - [ ] 광고/협찬 표시 완료
      - [ ] 제휴 링크 고지 완료
    copyright:
      - [ ] 모든 이미지 라이선스 확인
      - [ ] 음악/영상 저작권 확인
      - [ ] 인용 출처 명시
    trademark:
      - [ ] 상표 올바르게 사용
      - [ ] 경쟁사 언급 적절성 확인
    privacy:
      - [ ] 개인정보 동의 확보
      - [ ] 태그/멘션 허가 확인
    industry:
      - [ ] 산업별 규정 준수
      - [ ] 필수 고지문 포함
    ai:
      - [ ] AI 생성 콘텐츠 표시
```

## 위반 시 결과

| 위반 유형 | 잠재적 결과 |
|-----------|-------------|
| FTC 광고 미표시 | 벌금 $50,000+ / 시정 명령 |
| 저작권 침해 | $750-$30,000/건, 형사 처벌 가능 |
| 상표권 침해 | 손해배상, 금지명령 |
| 개인정보 침해 | GDPR: 매출 4% 또는 €20M |
| 금융 규정 위반 | 영업 정지, 벌금 |

## 다음 단계

컴플라이언스 통과 후:
1. → `7-approval`: 최종 승인 워크플로우
2. → `8-schedule`: 발행 스케줄링

컴플라이언스 실패 시:
1. → 콘텐츠 수정
2. → 법무팀 자문 요청
3. → `2-validation`: 재검증
