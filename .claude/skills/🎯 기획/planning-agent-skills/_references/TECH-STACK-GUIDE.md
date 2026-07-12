# Tech Stack Guide

## 스택 선택 기준

### 고려 요소

| 요소 | 질문 |
|------|------|
| 팀 역량 | 팀이 이미 알고 있는 기술은? |
| 제품 요구사항 | 실시간? 대용량? 모바일? |
| 확장성 | 얼마나 커질 수 있는가? |
| 생태계 | 라이브러리, 인력 풀은? |
| 비용 | 라이선스, 인프라 비용은? |
| 유지보수 | 장기 지원은? |

### 선택 프레임워크

```
1. 요구사항 정의
   └─► 기능적/비기능적 요구사항

2. 제약사항 파악
   └─► 팀, 예산, 시간

3. 옵션 비교
   └─► 장단점 분석

4. PoC 수행
   └─► 핵심 기능 검증

5. 결정
   └─► 문서화
```

## Frontend

### 프레임워크 비교

| 기술 | 적합 상황 | 장점 | 단점 |
|------|----------|------|------|
| **Next.js** | 웹앱, SEO 중요 | SSR/SSG, 풀스택 | 학습 곡선 |
| **React** | SPA, 대시보드 | 생태계, 유연성 | 설정 필요 |
| **Vue** | 빠른 개발, 중소 프로젝트 | 쉬운 학습 | 작은 생태계 |
| **Svelte** | 성능 중요, 작은 번들 | 빠른 성능 | 작은 생태계 |

### 추천 조합 (2024-2025)

```
Modern React Stack
─────────────────────────────────────
Framework:    Next.js 16.2.10 (App Router; web registry baseline)
State:        Zustand + TanStack Query
UI:           shadcn/ui + Tailwind CSS v4
Forms:        React Hook Form + Zod
Auth:         Auth.js v5 / Clerk
Animation:    Framer Motion
Testing:      Vitest + Playwright
```

### CSS 접근법

| 접근법 | 적합 상황 |
|--------|----------|
| Tailwind CSS | 빠른 개발, 일관성 |
| CSS Modules | 컴포넌트 격리 |
| styled-components | 동적 스타일링 |
| Vanilla CSS | 간단한 프로젝트 |

## Backend

### 프레임워크 비교

| 기술 | 적합 상황 | 장점 | 단점 |
|------|----------|------|------|
| **FastAPI** | API, ML 연동 | 빠름, 타입 | Python 성능 |
| **Node.js (Express)** | JS 풀스택 | 생태계, 동시성 | 콜백 헬 |
| **Go (Gin)** | 고성능, 마이크로서비스 | 성능, 동시성 | 학습 곡선 |
| **Spring Boot** | 엔터프라이즈 | 안정성, 생태계 | 무거움 |
| **Django** | 빠른 MVP, Admin | 배터리 포함 | 느림 |
| **NestJS** | TS 백엔드 | 구조화, DI | 복잡함 |

### 추천 조합 (2024-2025)

```
Modern Python Stack
─────────────────────────────────────
Framework:    FastAPI
Database:     PostgreSQL + SQLAlchemy 2.0
Cache:        Redis
Queue:        Celery / ARQ
Auth:         OAuth2 + JWT
Testing:      pytest
Docs:         OpenAPI (자동 생성)
```

```
Modern Node Stack
─────────────────────────────────────
Framework:    NestJS / tRPC
Database:     PostgreSQL + Drizzle / Prisma
Cache:        Redis
Queue:        BullMQ
Auth:         Passport / Auth.js
Testing:      Jest / Vitest
```

## Database

### 데이터베이스 선택

| 유형 | 기술 | 적합 상황 |
|------|------|----------|
| **관계형** | PostgreSQL | 일반적, ACID 중요 |
| | MySQL | 읽기 많은 워크로드 |
| | SQLite | 소규모, 임베디드 |
| **NoSQL** | MongoDB | 스키마 유연성 |
| | Redis | 캐시, 세션 |
| | DynamoDB | 서버리스, 확장성 |
| **검색** | Elasticsearch | 풀텍스트 검색 |
| **시계열** | InfluxDB | IoT, 모니터링 |
| **그래프** | Neo4j | 관계 중심 데이터 |

### 추천

```
대부분의 경우: PostgreSQL
─────────────────────────────────────
- 범용적
- JSONB 지원 (NoSQL 기능)
- 확장성 (읽기 복제, 파티셔닝)
- 풍부한 기능

+ Redis (캐시/세션)
```

## Mobile

### 프레임워크 비교

| 기술 | 적합 상황 | 장점 | 단점 |
|------|----------|------|------|
| **Flutter** | 크로스플랫폼, 커스텀 UI | 성능, 일관성 | 네이티브 통합 |
| **React Native** | 웹 개발자, 빠른 개발 | 코드 공유, 생태계 | 성능 |
| **Swift (iOS)** | iOS 전용, 고성능 | 네이티브 경험 | iOS만 |
| **Kotlin (Android)** | Android 전용 | 네이티브 경험 | Android만 |

### 추천 조합 (Flutter)

```
Modern Flutter Stack
─────────────────────────────────────
State:        Riverpod 3
Routing:      GoRouter
Network:      Dio + Retrofit
Database:     Drift
Code Gen:     Freezed
Testing:      flutter_test + Patrol
```

## Infrastructure

### 클라우드 비교

| Provider | 장점 | 적합 |
|----------|------|------|
| **AWS** | 가장 풍부한 서비스 | 엔터프라이즈 |
| **GCP** | ML, 데이터 분석 | AI/ML 중심 |
| **Azure** | MS 연동 | 엔터프라이즈 |
| **Vercel** | Next.js 최적화 | 프론트엔드 |
| **Railway** | 간편한 배포 | 스타트업 |
| **Supabase** | Firebase 대안 | BaaS |

### 서버리스 vs 컨테이너

| 접근법 | 적합 상황 |
|--------|----------|
| **Serverless** | 가변적 트래픽, 비용 최적화 |
| **Container (K8s)** | 안정적 트래픽, 제어 필요 |
| **PaaS** | 빠른 시작, 관리 최소화 |

### 추천 인프라

```
스타트업/MVP
─────────────────────────────────────
Frontend:     Vercel
Backend:      Railway / Render
Database:     Supabase / Neon
Cache:        Upstash Redis
File:         Cloudflare R2
CDN:          Cloudflare

성장 단계
─────────────────────────────────────
All:          AWS / GCP
Container:    ECS / GKE
Database:     RDS / Cloud SQL
Cache:        ElastiCache
File:         S3
CDN:          CloudFront
```

## DevOps

### CI/CD

| 도구 | 적합 상황 |
|------|----------|
| **GitHub Actions** | GitHub 사용 시 |
| **GitLab CI** | GitLab 사용 시 |
| **CircleCI** | 복잡한 파이프라인 |
| **Vercel** | Next.js 자동 배포 |

### 모니터링

| 도구 | 용도 |
|------|------|
| **Sentry** | 에러 트래킹 |
| **DataDog** | APM, 인프라 |
| **Grafana** | 대시보드 |
| **Prometheus** | 메트릭 |

## 서비스 유형별 추천

### SaaS B2B

```
Frontend:     Next.js + shadcn/ui
Backend:      FastAPI / NestJS
Database:     PostgreSQL
Auth:         Auth.js / Clerk
Payment:      Stripe
Analytics:    Mixpanel
```

### E-commerce

```
Frontend:     Next.js + Commerce.js
Backend:      Medusa / Custom
Database:     PostgreSQL
Payment:      Stripe / Toss
Search:       Algolia
```

### Real-time App

```
Frontend:     Next.js / React
Backend:      FastAPI + WebSocket / Socket.io
Database:     PostgreSQL + Redis
Real-time:    Pusher / Ably
```

### AI/ML Product

```
Frontend:     Next.js
Backend:      FastAPI
ML:           Python + HuggingFace
Database:     PostgreSQL + Pinecone
Infra:        AWS / GCP (GPU)
```

### Mobile App

```
Framework:    Flutter
Backend:      FastAPI / Firebase
Database:     Supabase / Firebase
Push:         FCM
Analytics:    Firebase Analytics
```

## Build vs Buy

### Buy 권장

| 기능 | 추천 서비스 |
|------|-----------|
| 인증 | Auth.js, Clerk, Supabase Auth |
| 결제 | Stripe, Toss |
| 이메일 | Resend, SendGrid |
| 푸시 | FCM, OneSignal |
| 검색 | Algolia, Typesense |
| 분석 | Mixpanel, Amplitude |
| 모니터링 | Sentry, DataDog |
| 파일 저장 | Cloudflare R2, S3 |

### Build 권장

| 기능 | 이유 |
|------|------|
| 핵심 비즈니스 로직 | 차별화 |
| 사용자 경험 | 커스터마이징 |
| 데이터 처리 | 보안, 제어 |

## 의사결정 체크리스트

```
□ 팀이 경험이 있는 기술인가?
□ 제품 요구사항을 충족하는가?
□ 확장 가능한가?
□ 인력 채용이 용이한가?
□ 장기 지원이 보장되는가?
□ 비용이 합리적인가?
□ 보안 요구사항을 충족하는가?
□ 기존 시스템과 연동 가능한가?
```
