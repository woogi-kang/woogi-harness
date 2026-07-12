---
name: scaffold
description: |
  매핑 전략을 기반으로 Next.js 프로젝트 뼈대를 생성합니다.
  nextjs-boilerplate-skill을 활용하여 프로젝트를 초기화합니다.
triggers:
  - "프로젝트 생성"
  - "scaffold"
  - "뼈대 생성"
---

# Next.js Project Scaffold Skill

매핑 전략을 기반으로 Next.js 프로젝트 구조를 생성합니다.

## 입력

- `mapping-strategy.md` (2-mapping 출력)
- 프로젝트 이름

## 출력

- `workspace/flutter-migration/{project-name}/nextjs/{project-name}/`

---

## 스캐폴딩 프로세스

### Step 1: 기본 프로젝트 생성

`nextjs-boilerplate-skill` 활용:
- Clean Architecture (선택적)
- Zustand (상태관리)
- React Query (비동기 데이터)
- shadcn/ui (UI 컴포넌트)

### Step 2: 추가 디렉토리 구조

```
src/
├── app/                      # App Router (라우팅)
│   ├── (auth)/               # 인증 그룹
│   │   ├── login/
│   │   └── register/
│   ├── (main)/               # 메인 그룹
│   │   ├── layout.tsx
│   │   └── page.tsx
│   └── layout.tsx
│
├── components/               # 컴포넌트
│   ├── ui/                   # shadcn/ui
│   ├── common/               # 공통 컴포넌트
│   │   ├── Header.tsx
│   │   ├── Footer.tsx
│   │   └── ...
│   └── features/             # 기능별 컴포넌트
│       ├── auth/
│       ├── product/
│       └── ...
│
├── stores/                   # Zustand 스토어
│   ├── index.ts              # 스토어 export
│   ├── auth.store.ts
│   └── ...
│
├── hooks/                    # 커스텀 훅
│   ├── useAuth.ts
│   ├── useMediaQuery.ts
│   └── ...
│
├── lib/                      # 유틸리티
│   ├── api/                  # API 클라이언트
│   │   ├── client.ts
│   │   └── endpoints.ts
│   ├── utils/
│   │   ├── cn.ts
│   │   └── format.ts
│   └── constants/
│       └── index.ts
│
├── types/                    # TypeScript 타입
│   ├── index.ts
│   ├── user.types.ts
│   └── ...
│
└── styles/                   # 추가 스타일
    └── animations.css
```

### Step 3: 기본 파일 생성

#### stores/index.ts

```typescript
// 모든 스토어 re-export
export { useAuthStore } from './auth.store'
// 추가 스토어는 변환 시 생성
```

#### stores/auth.store.ts (템플릿)

```typescript
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: string
  email: string
  name: string
}

interface AuthState {
  user: User | null
  token: string | null
  isLoading: boolean
  error: string | null
}

interface AuthActions {
  setUser: (user: User | null) => void
  setToken: (token: string | null) => void
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  clearError: () => void
}

export const useAuthStore = create<AuthState & AuthActions>()(
  persist(
    (set) => ({
      // State
      user: null,
      token: null,
      isLoading: false,
      error: null,

      // Actions
      setUser: (user) => set({ user }),
      setToken: (token) => set({ token }),

      login: async (email, password) => {
        set({ isLoading: true, error: null })
        try {
          // TODO: 실제 API 호출로 교체
          const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
          })

          if (!response.ok) {
            throw new Error('Login failed')
          }

          const { user, token } = await response.json()
          set({ user, token, isLoading: false })
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Login failed',
            isLoading: false,
          })
        }
      },

      logout: () => {
        set({ user: null, token: null })
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user, token: state.token }),
    }
  )
)
```

#### lib/api/client.ts

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || ''

interface RequestConfig extends RequestInit {
  params?: Record<string, string>
}

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  private async request<T>(
    endpoint: string,
    config: RequestConfig = {}
  ): Promise<T> {
    const { params, ...init } = config

    let url = `${this.baseUrl}${endpoint}`
    if (params) {
      const searchParams = new URLSearchParams(params)
      url += `?${searchParams.toString()}`
    }

    const response = await fetch(url, {
      ...init,
      headers: {
        'Content-Type': 'application/json',
        ...init.headers,
      },
    })

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`)
    }

    return response.json()
  }

  async get<T>(endpoint: string, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, { ...config, method: 'GET' })
  }

  async post<T>(
    endpoint: string,
    data?: unknown,
    config?: RequestConfig
  ): Promise<T> {
    return this.request<T>(endpoint, {
      ...config,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async put<T>(
    endpoint: string,
    data?: unknown,
    config?: RequestConfig
  ): Promise<T> {
    return this.request<T>(endpoint, {
      ...config,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async delete<T>(endpoint: string, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, { ...config, method: 'DELETE' })
  }
}

export const apiClient = new ApiClient(API_BASE_URL)
```

#### hooks/useMediaQuery.ts

```typescript
'use client'

import { useState, useEffect } from 'react'

export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(false)

  useEffect(() => {
    const media = window.matchMedia(query)
    setMatches(media.matches)

    const listener = (e: MediaQueryListEvent) => setMatches(e.matches)
    media.addEventListener('change', listener)

    return () => media.removeEventListener('change', listener)
  }, [query])

  return matches
}

// 편의 훅
export function useIsMobile() {
  return useMediaQuery('(max-width: 767px)')
}

export function useIsTablet() {
  return useMediaQuery('(min-width: 768px) and (max-width: 1023px)')
}

export function useIsDesktop() {
  return useMediaQuery('(min-width: 1024px)')
}
```

#### components/common/Header.tsx (템플릿)

```tsx
'use client'

import Link from 'next/link'
import { useAuthStore } from '@/stores'
import { Button } from '@/components/ui/button'
import { useIsMobile } from '@/hooks/useMediaQuery'

export function Header() {
  const { user, logout } = useAuthStore()
  const isMobile = useIsMobile()

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur">
      <div className="container flex h-14 items-center justify-between">
        <Link href="/" className="font-bold">
          {/* TODO: 앱 이름 */}
          App Name
        </Link>

        {isMobile ? (
          <MobileNav user={user} onLogout={logout} />
        ) : (
          <DesktopNav user={user} onLogout={logout} />
        )}
      </div>
    </header>
  )
}

function MobileNav({ user, onLogout }: { user: any; onLogout: () => void }) {
  // TODO: 모바일 네비게이션 구현
  return null
}

function DesktopNav({ user, onLogout }: { user: any; onLogout: () => void }) {
  return (
    <nav className="flex items-center gap-4">
      {user ? (
        <>
          <span className="text-sm">{user.name}</span>
          <Button variant="ghost" onClick={onLogout}>
            로그아웃
          </Button>
        </>
      ) : (
        <>
          <Button variant="ghost" asChild>
            <Link href="/login">로그인</Link>
          </Button>
          <Button asChild>
            <Link href="/register">회원가입</Link>
          </Button>
        </>
      )}
    </nav>
  )
}
```

#### providers/index.tsx

```tsx
'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { useState } from 'react'

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1분
            refetchOnWindowFocus: false,
          },
        },
      })
  )

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}
```

### Step 4: 패키지 추가

```json
{
  "dependencies": {
    "zustand": "^5.0.14",
    "@tanstack/react-query": "^5.101.2",
    "framer-motion": "^12.42.2"
  },
  "devDependencies": {
    "@tanstack/react-query-devtools": "^5.101.2"
  }
}
```

### Step 5: shadcn/ui 컴포넌트 추가

```bash
npx shadcn@latest add button
npx shadcn@latest add input
npx shadcn@latest add card
npx shadcn@latest add dialog
npx shadcn@latest add dropdown-menu
npx shadcn@latest add sheet
npx shadcn@latest add tabs
npx shadcn@latest add toast
npx shadcn@latest add avatar
npx shadcn@latest add badge
```

---

## 출력 확인

생성 완료 후 확인:

```
✅ Next.js 프로젝트 생성 완료

📁 {project-name}/
├── src/
│   ├── app/           ✓
│   ├── components/    ✓
│   ├── stores/        ✓
│   ├── hooks/         ✓
│   ├── lib/           ✓
│   └── types/         ✓
├── package.json       ✓
├── CLAUDE.md          ✓
└── ...

📦 추가된 패키지:
  - zustand
  - @tanstack/react-query
  - framer-motion
  - shadcn/ui components (10개)

🚀 다음 단계: 4-components (UI 변환)
```
