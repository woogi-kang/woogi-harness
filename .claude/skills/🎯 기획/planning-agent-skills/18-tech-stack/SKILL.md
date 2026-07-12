---
name: plan-tech-stack
description: |
  기술 스택을 추천하는 스킬.
  서비스 유형별 적합한 기술과 Make vs Buy 결정을 지원합니다.
triggers:
  - "기술 스택"
  - "Tech Stack"
  - "기술 선택"
  - "아키텍처"
input:
  - 서비스 유형
  - 팀 역량
  - 제약사항
output:
  - 05-estimation/tech-stack.md
---

# Tech Stack Skill

서비스에 적합한 기술 스택을 추천하고 Make vs Buy 결정을 지원합니다.

## 출력 템플릿

```markdown
# {Project Name} - 기술 스택 추천

## 1. 기술 선택 컨텍스트

### 서비스 유형

| 항목 | 내용 |
|------|------|
| 유형 | {service_type} |
| 플랫폼 | {platform} (Web/Mobile/Both) |
| 예상 사용자 | {user_scale} |
| 복잡도 | {complexity} |

### 팀 역량

| 기술 | 숙련도 | 경험 |
|------|--------|------|
| {tech_1} | ⭐⭐⭐⭐⭐ | {years}년 |
| {tech_2} | ⭐⭐⭐⭐ | {years}년 |
| {tech_3} | ⭐⭐⭐ | {years}년 |

### 제약 조건

- 예산: {budget}
- 일정: {timeline}
- 팀 규모: {team_size}
- 기타: {constraints}

---

## 2. 추천 기술 스택

### 전체 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │    Web      │  │   Mobile    │  │   Desktop   │             │
│  │  (Next.js)  │  │  (Flutter)  │  │  (Electron) │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         │                │                │                     │
└─────────┴────────────────┴────────────────┴─────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API Layer                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    API Gateway                            │   │
│  │                    (REST / GraphQL)                       │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Backend                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Server    │  │    Auth     │  │   Storage   │             │
│  │  (FastAPI)  │  │  (Auth.js)  │  │    (S3)     │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
└─────────┴────────────────┴────────────────┴─────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Database                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  PostgreSQL │  │    Redis    │  │   Vector    │             │
│  │   (Main)    │  │   (Cache)   │  │   (AI/ML)   │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

### 기술 스택 상세

#### Frontend

| 레이어 | 기술 | 버전 | 선택 이유 |
|--------|------|------|----------|
| Framework | {framework} | {version} | {reason} |
| Styling | {styling} | {version} | {reason} |
| State | {state_mgmt} | {version} | {reason} |
| UI Components | {ui_lib} | {version} | {reason} |

#### Backend

| 레이어 | 기술 | 버전 | 선택 이유 |
|--------|------|------|----------|
| Framework | {framework} | {version} | {reason} |
| ORM | {orm} | {version} | {reason} |
| Auth | {auth} | {version} | {reason} |
| API | {api_type} | - | {reason} |

#### Database

| 용도 | 기술 | 서비스 | 선택 이유 |
|------|------|--------|----------|
| Primary | {db} | {service} | {reason} |
| Cache | {cache} | {service} | {reason} |
| Search | {search} | {service} | {reason} |

#### Infrastructure

| 레이어 | 기술 | 서비스 | 선택 이유 |
|--------|------|--------|----------|
| Hosting | {hosting} | {service} | {reason} |
| CDN | {cdn} | {service} | {reason} |
| Storage | {storage} | {service} | {reason} |
| Monitoring | {monitoring} | {service} | {reason} |

---

## 3. Make vs Buy 결정

### 결정 매트릭스

| 영역 | Make | Buy | 결정 | 이유 |
|------|------|-----|------|------|
| 인증 | Custom | Auth.js/Clerk | 🛒 Buy | 보안, 시간 |
| 결제 | Custom | Stripe/Toss | 🛒 Buy | 규제, 복잡도 |
| 이메일 | Custom | Resend | 🛒 Buy | 배달률 |
| 검색 | Custom | Algolia | 🔧 Make | 비용, 간단 |
| 분석 | Custom | Mixpanel | 🛒 Buy | 기능 |
| 파일 저장 | Custom | S3/Cloudflare | 🛒 Buy | 확장성 |

### Buy 권장 (SaaS)

| 영역 | 추천 서비스 | 비용 | 이유 |
|------|-----------|------|------|
| Auth | {service} | {cost} | {reason} |
| Payment | {service} | {cost} | {reason} |
| Email | {service} | {cost} | {reason} |
| Analytics | {service} | {cost} | {reason} |

### Make 권장 (직접 구현)

| 영역 | 이유 | 예상 공수 |
|------|------|----------|
| {area_1} | {reason} | {effort} |
| {area_2} | {reason} | {effort} |

---

## 4. 서비스 유형별 추천

### Web App (SaaS)

**추천 스택 (2025)**
```
Frontend:  Next.js 16.2.10 + TanStack Query 5.101.2 + Zustand 5.0.14 + shadcn/ui
Backend:   Next.js API Routes (또는 FastAPI)
Database:  PostgreSQL (Supabase/Neon)
Auth:      Auth.js v5 또는 Clerk
Hosting:   Vercel
```

### Mobile App

**추천 스택 (2025)**
```
Framework: Flutter 3 + Riverpod 3
Backend:   FastAPI 또는 Supabase
Database:  Supabase (PostgreSQL)
Auth:      Supabase Auth 또는 Firebase Auth
Hosting:   Firebase + Play/App Store
```

### Marketplace/Platform

**추천 스택**
```
Frontend:  Next.js + React Query
Backend:   FastAPI + Celery (비동기 작업)
Database:  PostgreSQL + Redis
Search:    Elasticsearch 또는 Algolia
Payment:   Stripe Connect / Toss
```

---

## 5. 비용 추정

### 월별 인프라 비용

| 서비스 | 무료 티어 | 예상 비용 (성장 시) |
|--------|----------|-------------------|
| Vercel | 무료 | ${cost}/월 |
| Supabase | 무료 | ${cost}/월 |
| Stripe | 2.9% + 30¢ | 거래 기반 |
| Resend | 3,000/월 무료 | ${cost}/월 |
| 모니터링 | 무료 | ${cost}/월 |
| **합계** | **$0** | **${total}/월** |

### 단계별 비용

| 단계 | 사용자 | 월 비용 |
|------|--------|---------|
| MVP | 0-100 | $0-50 |
| 성장 | 100-1,000 | $50-200 |
| 스케일 | 1,000-10,000 | $200-1,000 |

---

## 6. 대안 비교

### Option A: {Stack Name} (권장)

| 장점 | 단점 |
|------|------|
| {pro_1} | {con_1} |
| {pro_2} | {con_2} |
| {pro_3} | {con_3} |

**적합한 경우**: {when_suitable}

### Option B: {Stack Name}

| 장점 | 단점 |
|------|------|
| {pro_1} | {con_1} |
| {pro_2} | {con_2} |
| {pro_3} | {con_3} |

**적합한 경우**: {when_suitable}

### 최종 권장

> **{recommended_stack}**
>
> 이유: {recommendation_reason}

---

## 7. 기술 리스크

### 리스크 평가

| 리스크 | 확률 | 영향 | 대응 |
|--------|------|------|------|
| {risk_1} | 🟡 | 🔴 | {mitigation} |
| {risk_2} | 🟢 | 🟡 | {mitigation} |

### 기술 부채 관리

| 영역 | 허용 가능한 부채 | 향후 개선 |
|------|----------------|----------|
| {area_1} | {acceptable} | {future} |
| {area_2} | {acceptable} | {future} |

---

## 8. 개발 환경

### 로컬 개발

```bash
# 필요 도구
- Node.js {version}
- Python {version}
- Docker
- {other_tools}

# 시작
git clone {repo}
cd {project}
npm install
npm run dev
```

### CI/CD

| 단계 | 도구 | 설정 |
|------|------|------|
| CI | GitHub Actions | 자동 테스트 |
| CD | Vercel | 자동 배포 |
| Preview | Vercel | PR별 프리뷰 |

---

## 9. 체크리스트

### 기술 선택 완료 확인

- [ ] Frontend 스택 결정
- [ ] Backend 스택 결정
- [ ] Database 선택
- [ ] 인증 방식 결정
- [ ] 호스팅 선택
- [ ] Make vs Buy 결정
- [ ] 비용 추정 완료
- [ ] 팀 동의

---

*다음 단계: Effort Estimation → Team Structure*
```

## 퀄리티 체크리스트

```
□ 팀 역량이 고려되었는가?
□ 제약 조건이 반영되었는가?
□ Make vs Buy 결정이 합리적인가?
□ 비용 추정이 현실적인가?
□ 대안이 비교되었는가?
□ 리스크가 식별되었는가?
□ 개발 환경이 정의되었는가?
```

## 🎯 인터랙티브 가이드

### 작성 전 확인 질문

**Q1. 팀의 기술 역량이 파악되었나요?**
- 파악됨 → 역량 기반 스택 선정
- 미파악 → "팀이 가장 익숙한 언어/프레임워크는?"

**Q2. 서비스 유형이 명확한가요?**
- 명확함 → 유형에 적합한 스택 추천
- 불명확 → "웹앱, 모바일앱, 백오피스 중 무엇이 우선인가요?"

**Q3. 예산 제약이 있나요?**
- 있음 → 비용 효율적인 스택 고려
- 없음 → 성능/생산성 중심 선택

### 의사결정 포인트

| 시점 | 확인 내용 | 사용자 프롬프트 |
|------|----------|----------------|
| 프론트엔드 | 프레임워크 | "React, Vue, Next.js 중 선호하는 것은?" |
| 백엔드 | 언어 선택 | "Node.js, Python, Go 중 팀 역량은?" |
| DB | 데이터 특성 | "관계형(SQL) vs 문서형(NoSQL) 중 적합한 것은?" |
| 인프라 | 복잡도 | "서버리스 vs 컨테이너 중 선호하는 것은?" |

---

## 다음 스킬 연결

Tech Stack 완료 후:

1. **공수 산정** → Effort Estimation Skill
2. **팀 구성** → Team Structure Skill
3. **실제 개발** → Expert Agent 연계

---

*기술 스택은 팀과 서비스에 맞아야 합니다. 트렌드보다 적합성.*
