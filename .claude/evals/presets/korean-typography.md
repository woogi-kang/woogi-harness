# Korean Typography Eval Preset

한국어 UI/랜딩/문서/장표 산출물에서 한글 AI slop을 줄이기 위한 평가 루브릭. `eval-harness`와 디자인/콘텐츠 리뷰에서 한국어 결과물을 평가할 때 사용한다.

## 평가 축 (가중치)

### Korean Readability & Wrapping (35%)

한국어가 음절 단위로 어색하게 쪼개지지 않고, 긴 URL/코드/영문 토큰도 레이아웃을 깨지 않는가?

| 점수 | 기준 |
|---|---|
| 9-10 | `word-break: keep-all`, `overflow-wrap`, code/URL 예외가 모두 안정적 |
| 7-8 | 본문/제목 줄바꿈은 안정적이나 일부 긴 토큰 처리 미흡 |
| 5-6 | 기본 가독성은 있으나 카드/제목에서 한글 줄바꿈 어색함 |
| 3-4 | 자주 음절 단위로 끊기거나 overflow 발생 |
| 1-2 | 한국어 읽기 흐름이 심하게 깨짐 |

### Font Fit & Korean Glyph Safety (25%)

폰트가 산출물의 분위기에 맞고 한글 glyph/fallback이 안전한가?

| 점수 | 기준 |
|---|---|
| 9-10 | 한글 지원 명확, 무드 적합, fallback/CDN/self-hosting 정책 명확 |
| 7-8 | 대부분 적합, fallback 또는 delivery note 일부 부족 |
| 5-6 | 무난하지만 영문-first 느낌 또는 fallback 약함 |
| 3-4 | 분위기와 맞지 않거나 한글 glyph 위험 |
| 1-2 | 한글 폰트 정책 부재 |

### Role Consistency (20%)

제목/본문/코드/포인트 역할별 폰트가 화면·슬라이드·섹션 전체에서 일관적인가?

| 점수 | 기준 |
|---|---|
| 9-10 | body/heading/code 역할이 명확하고 전체 산출물에서 고정 |
| 7-8 | 역할은 대체로 고정, 포인트 폰트만 제한적으로 사용 |
| 5-6 | 1-2곳에서 불필요한 폰트 변경 |
| 3-4 | 섹션마다 폰트가 달라 조립된 느낌 |
| 1-2 | 폰트 시스템 부재 |

### Korean Typographic Craft (20%)

한글에 맞는 line-height, letter-spacing, heading balance, paragraph rhythm을 갖췄는가?

| 점수 | 기준 |
|---|---|
| 9-10 | 본문 1.55-1.75, 제목 1.12-1.25 수준으로 안정, 자간 자연스러움 |
| 7-8 | 작은 조정만 필요 |
| 5-6 | 읽을 수는 있으나 빽빽하거나 느슨함 |
| 3-4 | 영문 템플릿 값을 그대로 써 한글 리듬이 어색함 |
| 1-2 | 기본 타이포그래피 품질 실패 |

## 자동 체크리스트

- [ ] 한국어 문맥에 `word-break: keep-all` 적용
- [ ] `overflow-wrap` fallback 존재
- [ ] code/pre/kbd/samp/terminal에는 `overflow-wrap: anywhere` 또는 동등한 처리
- [ ] 한국어 glyph를 지원하는 font-family/fallback 포함
- [ ] body/heading/code role mapping 명시
- [ ] 일반 작업에서 폰트 family 3개 이하
- [ ] 과도한 한글 body letter-spacing 없음
- [ ] 최종 상업 배포 전 공식 라이선스 확인 note 존재

## 합격 기준

```
가중 평균 = (Readability × 0.35) + (FontFit × 0.25) + (RoleConsistency × 0.20) + (Craft × 0.20)

PASS: 가중 평균 ≥ 7.5
FAIL: 가중 평균 < 7.5
FAIL: Korean Readability & Wrapping < 6
FAIL: Font Fit & Korean Glyph Safety < 5
```

## 권장 정적 검증

```bash
python3 .claude/skills/korean-typography-quality/scripts/validate_korean_typography.py path/to/artifact.html --json
```

## 출력 형식

```markdown
## Korean Typography Evaluation

| Axis | Score | Weight | Weighted |
|---|---:|---:|---:|
| Korean Readability & Wrapping | 8 | 35% | 2.80 |
| Font Fit & Korean Glyph Safety | 8 | 25% | 2.00 |
| Role Consistency | 9 | 20% | 1.80 |
| Korean Typographic Craft | 8 | 20% | 1.60 |
| **Total** | | | **8.20** |

**Result**: PASS

### Feedback
- Readability: `keep-all`과 long-token fallback이 모두 있음
- Font Fit: Pretendard/NanumSquare Neo 조합이 한국어 SaaS 톤에 적합
- Role Consistency: 제목/본문/코드 역할 고정
- Craft: 제목 자간과 본문 행간이 자연스러움
```
