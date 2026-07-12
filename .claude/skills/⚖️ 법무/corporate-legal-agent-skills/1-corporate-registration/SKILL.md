---
name: corporate-registration
description: 법인 설립 및 등기 변경 가이드
model: inherit
quality_tier: implementation
triggers:
  - "등기"
  - "법인설립"
  - "설립등기"
  - "변경등기"
  - "본점이전"
  - "자본금"
  - "상호변경"
---

# Corporate Registration Skill

법인 설립 및 등기 변경에 필요한 서류, 절차, 비용을 안내합니다.

## 핵심 원칙

| 원칙 | 설명 |
|------|------|
| **기한 준수** | 변경일로부터 14일 이내 등기 |
| **서류 완비** | 누락 시 보정 요구로 지연 |
| **최신 법령** | 상법/상업등기법 수시 확인 |

---

## 법인 설립

### 주식회사 설립 절차

```yaml
incorporation_workflow:
  phase_1_preparation:
    duration: "1-2일"
    tasks:
      - task: "상호 결정"
        action: "인터넷등기소에서 중복 검색"
        url: "iros.go.kr"

      - task: "본점 소재지 확정"
        requirements:
          - "실제 사업장 또는 가상오피스"
          - "임대차계약서 준비"

      - task: "자본금 결정"
        minimum: "없음 (1원도 가능)"
        recommendation: "1,000만원 이상 (신뢰도)"

      - task: "발기인 구성"
        minimum: "1인 이상"
        role: "설립 시 초기 주주"

  phase_2_documents:
    duration: "1-2일"
    documents:
      정관:
        mandatory: true
        contents:
          - "목적"
          - "상호"
          - "본점 소재지"
          - "자본금 총액"
          - "발행예정 주식 총수"
          - "액면가액"
          - "설립 시 발행 주식 수"
          - "발기인 성명/주소"

      발기인총회의사록:
        mandatory: true
        agenda:
          - "정관 승인"
          - "이사/감사 선임"
          - "본점 소재지 결정"

      취임승낙서:
        mandatory: true
        who: ["대표이사", "이사", "감사"]

      인감증명서:
        mandatory: true
        who: ["발기인 전원", "취임 임원"]
        validity: "발행일로부터 3개월"

      주민등록등본:
        mandatory: true
        who: ["발기인 전원", "취임 임원"]

  phase_3_capital:
    duration: "1일"
    tasks:
      - task: "자본금 납입"
        method: "발기인 명의 계좌로 입금"
        evidence: "잔액증명서 발급"
        timing: "등기 신청일 기준"

  phase_4_registration:
    duration: "3-5일"
    options:
      온라인:
        service: "startbiz.go.kr"
        discount: "등록면허세 75% 감면"
        process:
          - "회원가입 및 로그인"
          - "법인설립 신청서 작성"
          - "서류 업로드"
          - "수수료 납부"
          - "설립 완료 (3-5일)"

      오프라인:
        where: "관할 등기소"
        documents: "위 서류 원본 지참"

  phase_5_post:
    duration: "1-2일"
    tasks:
      - task: "사업자등록"
        where: "관할 세무서 또는 홈택스"
        deadline: "설립일로부터 20일 이내"

      - task: "4대보험 성립신고"
        deadline: "사업장 성립일로부터 14일 이내"

      - task: "법인통장 개설"
        where: "은행 (대표이사 방문 필수)"
```

### 설립 비용

```yaml
incorporation_costs:
  government_fees:
    등록면허세: "자본금 × 0.4% (최소 112,500원)"
    지방교육세: "등록면허세 × 20%"
    등기신청수수료: "약 20,000원"
    공증비용: "정관 공증 (5,000만원 이상 자본금)"

  example:
    자본금_1000만원:
      등록면허세: "112,500원 (최소)"
      지방교육세: "22,500원"
      등기수수료: "20,000원"
      total: "약 155,000원"

    자본금_1억원:
      등록면허세: "400,000원"
      지방교육세: "80,000원"
      등기수수료: "20,000원"
      공증비용: "약 100,000원"
      total: "약 600,000원"

  온라인_혜택:
    startbiz: "등록면허세 75% 감면"
```

---

## 등기 변경

### 본점 이전

```yaml
headquarters_relocation:
  types:
    관내이전:
      description: "같은 등기소 관할 내 이전"
      documents:
        - "이사회 의사록 (이사회 설치 법인)"
        - "주주총회 의사록 (정관에 본점 지번 기재 시)"
        - "본점이전등기신청서"
      fee: "약 40,000원"

    관외이전:
      description: "다른 등기소 관할로 이전"
      documents:
        - "이사회 의사록"
        - "주주총회 특별결의 (정관 변경 필요 시)"
        - "구 소재지: 이전등기신청서"
        - "신 소재지: 설립등기에 준하는 서류"
      fee: "약 80,000원 (양쪽 등기)"

  deadline: "이전일로부터 14일 이내"

  decision_authority:
    이사회_설치: "이사회 결의"
    이사회_미설치: "이사 과반수 결의"
    정관_지번기재: "주주총회 특별결의"
```

### 대표이사 변경

```yaml
ceo_change:
  types:
    신규선임:
      trigger: "공석 발생"
      process:
        - "주주총회에서 이사 선임"
        - "이사회에서 대표이사 선임"
        - "취임승낙서 작성"
        - "등기 신청"

    중임:
      trigger: "임기 만료"
      process:
        - "주주총회에서 이사 중임"
        - "이사회에서 대표이사 중임"
        - "중임등기 신청"

    사임:
      trigger: "자발적 사임"
      process:
        - "사임서 제출"
        - "이사회에서 후임 대표이사 선임"
        - "변경등기 신청"

  documents:
    - "주주총회 의사록 (이사 선임)"
    - "이사회 의사록 (대표이사 선임)"
    - "취임승낙서"
    - "인감증명서 (신임 대표이사)"
    - "주민등록등본 (신임 대표이사)"
    - "법인인감신고서 (인감 변경 시)"

  deadline: "14일 이내"
  fee: "약 40,000원"
```

### 자본금 변경

```yaml
capital_change:
  유상증자:
    description: "신주 발행으로 자본금 증가"
    types:
      주주배정:
        description: "기존 주주에게 지분비율대로"
        approval: "이사회 결의"

      제3자배정:
        description: "외부 투자자 유치"
        approval: "주주총회 특별결의"

      일반공모:
        description: "불특정 다수 대상"
        approval: "주주총회 특별결의"

    documents:
      - "이사회 의사록 / 주주총회 의사록"
      - "주금납입증명서"
      - "주식인수증"
      - "자본금 변경등기신청서"

    deadline: "납입기일로부터 14일 이내"

  무상증자:
    description: "잉여금의 자본 전입"
    approval: "이사회 결의"
    source:
      - "자본준비금"
      - "이익준비금"
      - "주식발행초과금"
    effect: "기존 주주 지분율 변동 없음"

  감자:
    description: "자본금 감소"
    types:
      유상감자:
        description: "주주에게 환급"
        creditor_protection: "채권자 보호절차 필수"
      무상감자:
        description: "결손 보전"
        creditor_protection: "불필요 (1주 금액 감소 시 필요)"

    approval: "주주총회 특별결의"
    process:
      - "주주총회 특별결의"
      - "채권자 이의 공고 (1개월)"
      - "감자 실행"
      - "등기 신청"
```

### 상호/목적 변경

```yaml
name_purpose_change:
  상호변경:
    check: "인터넷등기소에서 중복 검색"
    approval: "주주총회 특별결의"
    documents:
      - "주주총회 의사록"
      - "정관 (변경 후)"
      - "상호변경등기신청서"
    follow_up:
      - "사업자등록 정정"
      - "통장, 카드 명의 변경"
      - "계약서 갱신"
    fee: "약 40,000원"

  목적변경:
    approval: "주주총회 특별결의"
    tip: "실제 영위 사업 + 향후 계획 포함"
    documents:
      - "주주총회 의사록"
      - "정관 (변경 후)"
      - "목적변경등기신청서"
    fee: "약 40,000원"
```

---

## 서류 템플릿

### 정관 필수 기재사항

```markdown
# 정관 필수 기재사항 (상법 제289조)

## 절대적 기재사항 (누락 시 정관 무효)
1. 목적
2. 상호
3. 회사가 발행할 주식의 총수
4. 액면주식 발행 시 1주의 금액
5. 회사 설립 시 발행하는 주식의 총수
6. 본점의 소재지
7. 회사가 공고를 하는 방법
8. 발기인의 성명, 주민등록번호 및 주소

## 상대적 기재사항 (기재해야 효력)
- 현물출자
- 재산인수
- 발기인의 보수/특별이익
- 설립비용
```

### 등기신청서 공통 첨부서류

```yaml
common_attachments:
  all_cases:
    - "등기신청서"
    - "등록면허세 영수증"
    - "위임장 (대리인 신청 시)"

  identity:
    - "법인 등기사항전부증명서"
    - "법인 인감증명서"

  resolution:
    - "주주총회 의사록 (공증 필요한 경우)"
    - "이사회 의사록"

  officer_change:
    - "취임승낙서"
    - "개인 인감증명서"
    - "주민등록등본"
```

---

## CLI 사용법

```bash
# 법인 설립 가이드
/corporate-register incorporation --type 주식회사 --capital 10000000

# 등기 변경 안내
/corporate-register change --type 본점이전 --from 서울 --to 경기

# 필요 서류 체크리스트
/corporate-register checklist --type 대표이사변경

# 비용 계산
/corporate-register cost --type 설립 --capital 100000000

# 기한 확인
/corporate-register deadline --type 자본금변경 --date 2026-01-27
```

---

## 출력 포맷

```json
{
  "type": "registration_guide",
  "registration_type": "본점이전",
  "subtype": "관외이전",

  "current_status": {
    "company": "주식회사 OOO",
    "registration_number": "110111-XXXXXXX",
    "current_address": "서울시 강남구..."
  },

  "target_change": {
    "new_address": "경기도 성남시...",
    "effective_date": "2026-02-01"
  },

  "required_documents": [
    {
      "name": "이사회 의사록",
      "required": true,
      "notarization": false,
      "template_available": true
    },
    {
      "name": "본점이전등기신청서 (구소재지)",
      "required": true,
      "template_available": true
    }
  ],

  "estimated_cost": {
    "registration_tax": 40000,
    "local_education_tax": 8000,
    "application_fee": 20000,
    "total": 68000,
    "note": "관외이전은 양쪽 등기소에 납부"
  },

  "deadline": {
    "base_date": "2026-02-01",
    "deadline": "2026-02-15",
    "remaining_days": 14,
    "penalty_warning": true
  },

  "process_steps": [
    {
      "step": 1,
      "action": "이사회 개최 및 의사록 작성",
      "timeline": "D-14"
    },
    {
      "step": 2,
      "action": "구 소재지 등기소에 이전등기 신청",
      "timeline": "D-7"
    },
    {
      "step": 3,
      "action": "신 소재지 등기소에 설립에 준한 등기",
      "timeline": "D-7"
    }
  ],

  "online_service": {
    "url": "iros.go.kr",
    "available": true
  }
}
```

---

## 자주 묻는 질문

### Q: 1인 법인도 주주총회가 필요한가요?
**A**: 네, 1인 주주여도 주주총회 의사록 작성이 필요합니다. 다만 소집절차 생략이 가능하고, "주주 전원 출석하여" 형식으로 간소화됩니다.

### Q: 이사회 없는 소규모 회사는 어떻게 하나요?
**A**: 이사가 2인 이하인 경우 이사회 설치가 의무가 아닙니다. 이 경우 이사 과반수 결의로 대체하고, "이사 결정서" 형태로 의사록을 작성합니다.

### Q: 정관 공증은 언제 필요한가요?
**A**: 자본금 10억원 이상 법인 설립 시 정관 공증이 필요합니다. 그 미만은 발기인 전원 기명날인/서명으로 가능합니다.

---

⚠️ **면책 조항**
이 가이드는 일반적인 정보 제공 목적이며, 법률 자문을 대체하지 않습니다.
실제 등기 신청 전 법무사 또는 변호사와 상담하시기 바랍니다.
법령은 수시로 개정되므로 최신 법령을 확인하세요.
