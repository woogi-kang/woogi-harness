---
name: nextjs-boilerplate
description: "Next.js 보일러플레이트 생성 — App Router, 인증, DB, 결제 통합 초기 설정"
triggers:
  - "next.js 프로젝트"
  - "nextjs 프로젝트"
  - "보일러플레이트"
  - "boilerplate"
  - "새 프로젝트"
  - "프로젝트 생성"
  - "프로젝트 만들어"
---

# Next.js Boilerplate Generator Skill

AI 시대에 최적화된 Next.js 16 프로젝트 Boilerplate를 생성하는 Skill입니다.

> Tech stack registry: `.claude/registry/tech-stacks/web-nextjs.yaml` (`web-nextjs@recommended`). 템플릿은 검증된 권장 기준을 사용하며 live latest를 무조건 설치하지 않는다.

## 핵심 원칙

1. **최소 시작 + 선택적 확장**: 기본은 가볍게, 필요한 것만 추가
2. **AI-First 설정**: CLAUDE.md, .cursorrules 기본 포함
3. **Best Practices 내장**: TypeScript strict, ESLint, Prettier 기본 설정

---

## 워크플로우

```
[0. 레지스트리 해석] → [1. 요구사항 수집] → [2. 구조 결정] → [3. 파일 생성] → [4. 설치·검증]
```

### Phase 0: 레지스트리 해석

1. 기존 프로젝트라면 package manager, `package.json`, lockfile, Node 설정을 먼저 읽는다.
2. 신규 프로젝트라면 `web-nextjs@recommended`를 사용한다.
3. `latest_observed`나 `prerelease`를 사용하려면 해당 migration guide와 promotion gate를 실행한다.
4. 공식 registry를 다시 조회했다면 작업 중 임의 변경하지 말고 별도 registry 갱신으로 기록한다.

### Phase 1: 요구사항 수집

**필수 질문:**
```
1. 프로젝트 이름은 무엇인가요?
   예: my-awesome-app
```

**선택적 옵션 (다중 선택 가능):**
```
어떤 기능을 포함할까요? (다중 선택 가능)

[ ] Clean Architecture - 레이어 분리된 확장 가능한 구조
[ ] Database (Drizzle ORM) - 타입 안전 데이터베이스
[ ] Supabase - BaaS (Auth + DB + Storage + Realtime)
[ ] Auth (별도, prerelease 명시 동의) - Auth.js v5 beta.31 (Supabase 없이)
[ ] Testing (Vitest + Playwright) - 단위/E2E 테스트
[ ] Docker - 컨테이너화
[ ] MCP 설정 - AI 에이전트 연동
[ ] CI/CD (GitHub Actions) - 자동화 파이프라인
```

### Phase 2: 구조 결정

선택에 따른 구조 결정:

| 선택 | 구조 영향 |
|-----|----------|
| 기본 (아무것도 선택 안함) | Feature-based 단순 구조 |
| Clean Architecture | 5-Layer 구조 (domain/application/infrastructure/presentation/di) |
| Supabase | Supabase 클라이언트 + 타입 생성 + Row Level Security |
| Database | Drizzle + 스키마 + 마이그레이션 설정 |
| Auth | Auth.js v5 beta.31 기반 proxy + 라우트 보호; prerelease 명시 동의 필요 |
| Testing | vitest.config + playwright.config + 예시 테스트 |
| Docker | Dockerfile + docker-compose |
| MCP | .mcp.json 설정 |
| CI/CD | .github/workflows/ |

### Phase 3: 파일 생성

생성 위치: `{현재 디렉토리}/{프로젝트명}/`

### Phase 4: 설치 안내

생성 완료 후 표시:
```bash
cd {프로젝트명}
npm install
npm run dev
```

---

## 생성 파일 목록

### 필수 파일 (항상 생성)

```
{project-name}/
├── .vscode/
│   └── settings.json            # VS Code 설정
│
├── src/
│   ├── app/
│   │   ├── layout.tsx           # 루트 레이아웃
│   │   ├── page.tsx             # 홈 페이지
│   │   ├── globals.css          # 글로벌 스타일
│   │   └── favicon.ico
│   │
│   ├── components/
│   │   └── ui/                  # shadcn/ui 컴포넌트 (비어있음)
│   │
│   └── lib/
│       └── utils.ts             # cn() 유틸리티
│
├── public/
│   └── .gitkeep
│
├── .env.example                 # 환경변수 템플릿
├── .gitignore
├── eslint.config.mjs
├── .prettierrc
├── CLAUDE.md                    # AI 코딩 지침
├── .cursorrules                 # Cursor AI 규칙
├── components.json              # shadcn/ui 설정
├── next.config.ts
├── package.json
├── postcss.config.mjs
├── tsconfig.json
└── README.md
```

### 선택적 파일

#### Clean Architecture 선택 시

```
src/
├── domain/                      # Enterprise Business Rules
│   ├── entities/
│   │   └── .gitkeep
│   ├── value-objects/
│   │   └── .gitkeep
│   └── errors/
│       └── domain.error.ts
│
├── application/                 # Application Business Rules
│   ├── use-cases/
│   │   └── .gitkeep
│   ├── ports/
│   │   └── repositories/
│   │       └── .gitkeep
│   └── dtos/
│       └── .gitkeep
│
├── infrastructure/              # Frameworks & Drivers
│   ├── repositories/
│   │   └── .gitkeep
│   └── services/
│       └── .gitkeep
│
├── presentation/                # Interface Adapters
│   ├── controllers/
│   │   └── .gitkeep
│   └── view-models/
│       └── .gitkeep
│
└── di/                          # Dependency Injection
    └── container.ts
```

#### Supabase 선택 시

```
src/
├── lib/
│   └── supabase/
│       ├── client.ts            # 브라우저 클라이언트
│       ├── server.ts            # 서버 클라이언트
│       ├── proxy.ts             # 세션 갱신 helper
│       └── types.ts             # 생성된 타입 (placeholder)
│
├── app/
│   ├── auth/
│   │   ├── callback/route.ts    # OAuth 콜백
│   │   ├── login/page.tsx       # 로그인 페이지
│   │   └── signup/page.tsx      # 회원가입 페이지
│   └── (protected)/
│       └── dashboard/page.tsx   # 보호된 라우트 예시
│
└── proxy.ts                     # Next.js 16 request proxy
```

추가 파일:
```
supabase/
├── config.toml                  # 로컬 개발 설정
└── migrations/
    └── .gitkeep
```

#### Database (Drizzle) 선택 시 (Supabase 없이)

```
src/
├── infrastructure/
│   └── database/
│       ├── schema.ts            # Drizzle 스키마
│       ├── client.ts            # DB 클라이언트
│       └── migrate.ts           # 마이그레이션 스크립트

drizzle/
└── migrations/
    └── .gitkeep

drizzle.config.ts
```

#### Auth 선택 시 (Supabase 없이)

```
src/
├── lib/
│   └── auth/
│       ├── config.ts            # Auth.js 설정
│       └── providers.ts         # OAuth 프로바이더
│
├── app/
│   ├── api/
│   │   └── auth/
│   │       └── [...nextauth]/
│   │           └── route.ts
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   └── (protected)/
│       └── layout.tsx           # 보호된 레이아웃

proxy.ts
```

#### Testing 선택 시

```
src/
├── __tests__/
│   ├── unit/
│   │   └── example.test.ts      # Vitest 단위 테스트 예시
│   └── e2e/
│       └── home.spec.ts         # Playwright E2E 테스트 예시

vitest.config.ts
playwright.config.ts
```

#### Docker 선택 시

```
Dockerfile
Dockerfile.dev
docker-compose.yml
docker-compose.dev.yml
.dockerignore
```

#### MCP 설정 선택 시

```
.mcp.json                        # MCP 서버 설정
```

#### CI/CD 선택 시

```
.github/
└── workflows/
    ├── ci.yml                   # 빌드/테스트
    └── deploy.yml               # 배포 (Vercel)
```

---

## 파일 템플릿

### package.json

```json
{
  "name": "{project-name}",
  "version": "0.1.0",
  "private": true,
  "engines": {
    "node": ">=24.18.0 <25"
  },
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint . --max-warnings=0",
    "format": "prettier --write .",
    "typecheck": "next typegen && tsc --noEmit"
  },
  "dependencies": {
    "next": "^16.2.10",
    "react": "^19.2.7",
    "react-dom": "^19.2.7",
    "clsx": "^2.1.1",
    "tailwind-merge": "^3.6.0"
  },
  "devDependencies": {
    "@types/node": "^24.13.3",
    "@types/react": "^19.2.17",
    "@types/react-dom": "^19.2.3",
    "typescript": "^6.0.2",
    "tailwindcss": "^4.3.2",
    "@tailwindcss/postcss": "^4.3.2",
    "postcss": "^8.5.17",
    "eslint": "^9.39.5",
    "eslint-config-next": "^16.2.10",
    "prettier": "^3.9.5",
    "prettier-plugin-tailwindcss": "^0.8.0"
  }
}
```

### CLAUDE.md

```markdown
# CLAUDE.md

## Project Overview

{project-name} - Next.js 16.2 프로젝트

## Architecture

{architecture-description}

## Commands

```bash
npm run dev        # 개발 서버 (Turbopack)
npm run build      # 프로덕션 빌드
npm run lint       # ESLint 검사
npm run format     # Prettier 포맷팅
npm run typecheck  # TypeScript 타입 체크
```

## Conventions

- **컴포넌트**: PascalCase (e.g., `UserProfile.tsx`)
- **유틸리티**: camelCase (e.g., `formatDate.ts`)
- **타입**: PascalCase + interface 선호
- **스타일**: Tailwind CSS utility-first

## Key Files

| Path | Purpose |
|------|---------|
| `src/app/` | Next.js App Router 페이지 |
| `src/components/` | 재사용 가능한 컴포넌트 |
| `src/lib/` | 유틸리티 및 설정 |

{additional-sections}
```

### .cursorrules

```markdown
# Cursor Rules for {project-name}

## Code Style
- Use TypeScript strict mode
- Prefer functional components with hooks
- Use Tailwind CSS for styling
- Follow React Server Components patterns

## File Naming
- Components: PascalCase.tsx
- Utilities: camelCase.ts
- Types: types.ts or *.types.ts

## Imports
- Use absolute imports with @/ prefix
- Group imports: react, next, external, internal, types

## Patterns
- Server Components by default
- 'use client' only when necessary
- Server Actions for mutations
- Zustand for client state (if enabled)

{architecture-rules}
```

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "rootDir": ".",
    "types": ["node"],
    "noUncheckedSideEffectImports": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

### .env.example

```bash
# App
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Database (if Drizzle selected)
# DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Supabase (if Supabase selected)
# NEXT_PUBLIC_SUPABASE_URL=your-project-url
# NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=your-publishable-key
# SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Auth (if Auth selected without Supabase)
# AUTH_SECRET=your-auth-secret
# AUTH_GOOGLE_ID=your-google-client-id
# AUTH_GOOGLE_SECRET=your-google-client-secret
```

---

## 선택 조합별 권장사항

### 조합 1: MVP 빠른 시작
```
선택: Supabase만
결과: Auth + DB + Storage 한 번에 해결
```

### 조합 2: 엔터프라이즈급
```
선택: Clean Architecture + Drizzle + Auth + Testing + CI/CD
결과: 확장 가능한 프로덕션 구조
```

### 조합 3: AI 개발 최적화
```
선택: Clean Architecture + MCP + Testing
결과: AI 코딩에 최적화된 구조
```

### 조합 4: 풀스택
```
선택: Clean Architecture + Supabase + Testing + Docker + CI/CD
결과: 완전한 풀스택 구조
```

---

## 생성 후 추가 설정 안내

### shadcn/ui 컴포넌트 추가
```bash
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add input
```

### Supabase 선택 시
```bash
# 로컬 Supabase 시작
npx supabase start

# 타입 생성
npx supabase gen types typescript --local > src/lib/supabase/types.ts
```

### Drizzle 선택 시
```bash
# 마이그레이션 생성
npm run db:generate

# 마이그레이션 적용
npm run db:migrate
```

### Testing 선택 시
```bash
# 단위 테스트
npm run test

# E2E 테스트
npm run test:e2e
```

---

## 템플릿 처리 규칙

### 플레이스홀더

템플릿 파일에서 사용되는 플레이스홀더:

| 플레이스홀더 | 설명 | 예시 |
|-------------|------|------|
| `{{PROJECT_NAME}}` | 프로젝트 이름 (kebab-case) | my-awesome-app |
| `{{PROJECT_NAME_PASCAL}}` | 프로젝트 이름 (PascalCase) | MyAwesomeApp |
| `{{DESCRIPTION}}` | 프로젝트 설명 | My awesome Next.js app |
| `{{AUTHOR}}` | 작성자 | username |
| `{{YEAR}}` | 현재 연도 | 2025 |

### 조건부 섹션 (Mustache 스타일)

```
{{#FEATURE_NAME}}
이 블록은 FEATURE_NAME이 활성화된 경우에만 포함됩니다.
{{/FEATURE_NAME}}
```

지원 조건:
- `{{#CLEAN_ARCHITECTURE}}` - Clean Architecture 선택 시
- `{{#SUPABASE}}` - Supabase 선택 시
- `{{#DRIZZLE}}` - Drizzle 선택 시
- `{{#AUTH}}` - Auth (별도) 선택 시
- `{{#TESTING}}` - Testing 선택 시
- `{{#DOCKER}}` - Docker 선택 시
- `{{#MCP}}` - MCP 선택 시
- `{{#CICD}}` - CI/CD 선택 시

### package.json 병합 규칙

`package.json.additions.template` 파일 처리:
- `dependencies`: 기존에 병합
- `devDependencies`: 기존에 병합
- `scripts`: 기존에 병합 (중복 시 덮어쓰기)

---

## 옵션 의존성 매트릭스

### 충돌 및 자동 처리

| 조합 | 처리 방식 |
|------|----------|
| Supabase + Auth (별도) | Supabase Auth만 사용, 별도 Auth 무시 (경고 표시) |
| Supabase + Drizzle | Supabase DB를 Drizzle로 관리 (호환) |
| Auth (별도) + Drizzle | Drizzle에 사용자 테이블 스키마 추가 |

### 옵션별 필수 환경변수

| 옵션 | 필수 환경변수 |
|------|--------------|
| Supabase | `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` |
| Drizzle (단독) | `DATABASE_URL` |
| Auth (별도) | `AUTH_SECRET`, OAuth 프로바이더별 키 |

### 권장 조합

| 사용 사례 | 권장 옵션 |
|----------|----------|
| MVP/빠른 시작 | Supabase |
| 엔터프라이즈 | Clean Architecture + Drizzle + Auth + Testing + CI/CD |
| AI 개발 | Clean Architecture + MCP + Testing |
| 풀스택 | Clean Architecture + Supabase + Testing + Docker + CI/CD |

---

## 생성 절차 (Claude 실행)

### Step 1: 디렉토리 생성

```bash
mkdir -p {project-name}/src/app
mkdir -p {project-name}/src/components/ui
mkdir -p {project-name}/src/lib
mkdir -p {project-name}/public
mkdir -p {project-name}/.vscode
```

### Step 2: 템플릿 로드 및 치환

1. `templates/base/` 디렉토리의 모든 `.template` 파일 읽기
2. 플레이스홀더 치환 (`{{PROJECT_NAME}}` → 실제 값)
3. 조건부 섹션 처리 (선택된 옵션에 따라)
4. `.template` 확장자 제거하여 파일 생성

### Step 3: 선택 옵션별 파일 추가

선택된 각 옵션에 대해:
1. `templates/{option}/` 디렉토리의 파일 처리
2. `package.json.additions.template` → base package.json에 병합

### Step 4: 파일 생성 순서

1. 설정 파일 (package.json, tsconfig.json, etc.)
2. src/app/ 파일들
3. src/lib/ 파일들
4. src/components/ 파일들
5. 선택 옵션별 파일들
6. 루트 파일들 (`proxy.ts` 등)

### Step 5: 검증

생성 완료 후 확인:
- [ ] package.json 문법 유효성
- [ ] 필수 파일 존재 여부
- [ ] .env.example에 필요한 환경변수 포함

---

## 버전 관리

### 현재 버전

| 항목 | 버전 |
|------|------|
| Registry | `web-nextjs@recommended` |
| Next.js | 16.2.10 |
| React | 19.2.7 |
| TypeScript | 6.0.2 권장 / 7.0.2 candidate |
| Tailwind CSS | 4.3.2 |
| Node.js | 24.18.0 LTS |

### 버전 정책

- **사실 기록**: 공식 source의 최신 stable/current/prerelease는 registry `latest_observed`에 기록
- **생성 기준**: 실제 템플릿은 검증된 `recommended`만 사용
- **메이저 업데이트**: migration guide와 fixture의 typecheck/lint/test/build evidence가 있어야 승격
- **범위 버전**: 템플릿은 `^`를 쓸 수 있지만 검증 fixture와 실제 프로젝트는 lockfile을 커밋

### 호환성 매트릭스

| Skill 버전 | Next.js | React | Node.js |
|-----------|---------|-------|---------|
| `web-nextjs@recommended` | 16.2.x | 19.2.x | 24.x LTS |

### 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2025-01-09 | 1.0.0 | 초기 버전 |
| 2026-07-13 | registry v1 | Next 16.2, Node 24 LTS, TypeScript 6 권장/7 candidate, Tailwind 4 기준 |

### Registry 갱신과 candidate 승격

- 공식 npm dist-tag와 공식 migration 문서를 조회해 registry를 별도 변경한다.
- Node Current, TypeScript 7, Auth.js v5 beta처럼 최신과 권장이 다른 항목을 생성 중 즉석에서 승격하지 않는다.
- `python scripts/verify-stack-registry.py --all`과 Next fixture 검증을 통과시킨 뒤 `recommended`를 변경한다.
- 공식 source 조회가 막히면 마지막 `sources.lock.json` 기준을 유지하고, 최신이라고 추정하지 않는다.

---

## 주의사항

1. **Supabase vs Auth 선택**: 둘 다 선택하면 Supabase Auth 사용 (별도 Auth 무시)
2. **Supabase vs Drizzle**: 둘 다 선택하면 Supabase + Drizzle 조합 (Supabase DB를 Drizzle로 관리)
3. **Clean Architecture**: 작은 프로젝트에는 오버엔지니어링일 수 있음
4. **Docker**: 로컬 개발용 dev 설정도 함께 생성
5. **Auth.js 채널**: 별도 Auth 템플릿은 v5 beta.31이다. prerelease 동의가 없으면 생성하지 말고 stable v4 API를 별도 설계한다.

---

## 출력 예시

```
✅ Next.js Boilerplate 생성 완료!

📁 생성된 프로젝트: my-awesome-app/

📦 포함된 기능:
  ✓ Next.js 16.2 + React 19.2
  ✓ TypeScript (strict)
  ✓ Tailwind CSS + shadcn/ui
  ✓ ESLint + Prettier
  ✓ CLAUDE.md + .cursorrules
  ✓ Clean Architecture
  ✓ Supabase (Auth + DB)
  ✓ Vitest + Playwright

🚀 시작하기:
  cd my-awesome-app
  npm install
  npm run dev

📚 추가 설정:
  - shadcn/ui: npx shadcn@latest add button
  - Supabase: npx supabase start
  - 타입 생성: npx supabase gen types typescript --local
```
