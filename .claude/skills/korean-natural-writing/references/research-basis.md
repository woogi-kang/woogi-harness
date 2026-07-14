# 연구 근거와 자료 사용 경계

이 파일은 일상 윤문 때 읽지 않는다. 평가 체계, 말뭉치, 반복 수정 횟수, 비평자 설계를 바꿀 때 근거를 확인하는 용도다.

## 설계에 반영한 원칙

### 장르와 사용역을 먼저 고정한다

한국어 문체는 하나의 자연스러움 축으로 정리되지 않는다. 장르, 매체, 화자와 독자의 관계, 격식, 정보 밀도에 따라 같은 구문도 다른 역할을 한다.

- Kang & Kim, [Variation across Korean text registers](https://ucrel.lancs.ac.uk/publications/cl2003/CL2001%20conference/papers/kang.pdf)
- 국립국어원, [모두의 말뭉치](https://kli.korean.go.kr/main/requestMain.do?lang=ko)

### 번역투 후보는 금칙어가 아니다

피동, `~에 대한`, `~을 통해`, 대명사, 명사화 같은 표지는 번역문에서 자주 나타날 수 있지만 비번역 한국어와 특정 장르에도 필요하다. 탐지 결과는 문맥 대조를 위한 후보로만 사용한다.

- 최희경, [영한 번역문의 번역투 연구](https://journal.kci.go.kr/kats/archive/articleView?artiId=ART002094440)
- 국립국어원, [번역투에는 공식 판정 기준이 없다는 답변](https://www.korean.go.kr/front/onlineQna/onlineQnaView.do?mn_id=216&pageIndex=1&qna_seq=307425)

### 문체 개선과 내용 보존을 분리한다

텍스트 스타일 변환 평가는 목표 문체, 의미 보존, 자연스러움을 독립적으로 봐야 한다. 이 스킬은 수치·인용·부정·주체 변화 등을 먼저 탈락시키고 문체를 나중에 평가한다.

- Mir et al., [Evaluating Style Transfer for Text](https://aclanthology.org/N19-1049/)
- Briakou et al., [A Review of Human Evaluation for Style Transfer](https://aclanthology.org/2021.gem-1.6/)
- Mukherjee et al., [Evaluating Text Style Transfer Evaluation](https://aclanthology.org/2025.naacl-srw.41/)

### 반복 수정에는 상한과 중단 조건이 필요하다

반복 피드백은 단회 생성보다 나아질 수 있지만, 같은 blind spot을 반복하거나 원래 목소리와 의미를 깎을 수 있다. 중간본을 보존하고 최대 두 번만 수정한다.

- Madaan et al., [Self-Refine](https://proceedings.neurips.cc/paper_files/paper/2023/hash/91edff07232fb1b55a505a9e9f6c0ff3-Abstract-Conference.html)
- Du et al., [Read, Revise, Repeat](https://aclanthology.org/2022.in2writing-1.14/)

### LLM 비평은 블라인드 보조 평가다

LLM judge는 위치, 길이, 권위적인 어조에 흔들릴 수 있다. 후보를 먼저 독립 평가하고, 익명 비교의 A/B 위치를 바꾸며, 불일치하면 사람에게 넘긴다.

- Shi et al., [Judging the Judges](https://aclanthology.org/2025.ijcnlp-long.18/)
- Jeong et al., [The Comparative Trap](https://aclanthology.org/2025.blackboxnlp-1.5/)

## 활용할 수 있는 한국어 자료

- `글쓰기 첨삭 지원을 위한 지시문 기반 생성 말뭉치 2024`: 문서·문단·문장을 내용, 조직, 표현 기준으로 첨삭한 자료
- `문어 말뭉치 2025`: 저작권 문제가 해결된 문학·정보 글의 장르 참조 자료
- `문법성 판단 말뭉치`: 문장 수용성 참고 자료
- `KoSEnd`: 종결어미 자연성 비교 자료

## 라이선스와 공개 저장소 규칙

- 국립국어원 자료는 종류별 신청과 이용 조건을 확인한다.
- 원문 말뭉치를 이 공개 저장소에 재배포하지 않는다.
- 회귀 사례는 사용자 소유 원문, 허가된 자료, 새로 만든 합성 사례만 커밋한다.
- 말뭉치에서 배운 경향은 출처와 관찰 범위를 기록하고 보편적 금칙어로 승격하지 않는다.
