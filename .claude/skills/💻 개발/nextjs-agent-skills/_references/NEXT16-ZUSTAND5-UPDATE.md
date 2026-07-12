# Next.js 16 + Zustand 5 Update Reference

Last verified: 2026-07-13

> Tech stack registry: `.claude/registry/tech-stacks/web-nextjs.yaml` (`web-nextjs@recommended`). Latest, LTS, stable, and prerelease channels are intentionally separate.

## Version Baseline

| 영역 | 기준 |
|------|------|
| Next.js | 16.2.10 |
| React / React DOM | 19.2.7 |
| Node.js | 24.18.0 LTS |
| TypeScript | 7.0.2 stable (승격 후보) / 6.0.2 기본 권장 |
| Zustand | 5.0.14 |
| TanStack Query | 5.101.2 |
| Zod | 4.4.3 |
| Vitest / Playwright | 4.1.10 / 1.61.1 |

## Next.js 16 Migration Checklist

- `next dev --turbopack`를 제거하고 `next dev`를 기본으로 사용한다. Turbopack은 기본값이다.
- `next lint`를 제거하고 `eslint . --max-warnings=0`처럼 ESLint CLI를 직접 사용한다.
- `middleware.ts`를 `proxy.ts`로 이전한다. Proxy 파일은 default export 또는 named `proxy` 함수 하나만 export한다.
- Proxy는 Node.js Runtime이 기본값이며 `runtime` config를 사용할 수 없다.
- `cookies()`, `headers()`, `draftMode()`, `params`, `searchParams`는 비동기 API로 다룬다.
- `typedRoutes`는 top-level config로 사용한다. `experimental.typedRoutes`를 쓰지 않는다.
- Cache Components 신규 코드는 `cacheComponents: true`, `"use cache"`, `cacheTag`, `cacheLife`를 우선 검토한다.
- `revalidateTag`는 profile 인자가 필요하다. stale-while-revalidate는 `revalidateTag(tag, 'max')`, Server Action 즉시 갱신은 `updateTag(tag)`를 사용한다.
- `serverComponentsExternalPackages` 대신 `serverExternalPackages`를 사용한다.
- `serverRuntimeConfig`/`publicRuntimeConfig`에 의존하지 않는다. 환경 변수 또는 명시적 서버 설정으로 대체한다.

## TypeScript 7 Candidate Checklist

- TypeScript 7.0은 stable이지만 programmatic compiler API를 제공하지 않는다. compiler API를 사용하는 ESLint/plugin/codegen/editor 도구가 모두 통과하기 전에는 기본 생성 버전을 6.0.2로 유지한다.
- 6.0에서 deprecated 옵션을 먼저 제거하고 `stableTypeOrdering` 차이를 정리한다.
- 7.0 기본값인 `strict: true`, `module: esnext`, `noUncheckedSideEffectImports: true`, `rootDir: ./`, `types: []`를 명시적으로 검토한다.
- `baseUrl`, ES5, node/node10/classic module resolution, AMD/UMD/SystemJS/none module, false `esModuleInterop`/`allowSyntheticDefaultImports`를 제거한다.
- CI에서 TypeScript 6과 7을 병렬 실행하고 Next production build 및 editor LSP까지 통과한 뒤 registry `recommended`를 승격한다.

## Package Family Checklist

- Tailwind 4는 `@tailwindcss/postcss`, `@import "tailwindcss"`, CSS-first config와 최신 브라우저 하한을 사용한다. Tailwind 3 설정을 숫자만 바꾸지 않는다.
- Zod 4는 error API, issue shape, optional 내부 default, record/enum/function schema semantics를 변경하므로 error와 parsed output을 함께 snapshot한다.
- `next-auth` stable은 4.24.14이고 v5는 5.0.0-beta.31이다. prerelease 승인 없이 v5 API를 생성하거나 stable로 표기하지 않는다.

## Zustand 5 Checklist

- 서버 상태는 Zustand에 저장하지 않는다. RSC fetch, Server Action, TanStack Query 캐시를 사용한다.
- URL로 공유되어야 하는 상태는 nuqs에 둔다.
- Zustand는 모달, drawer, selected id, 임시 wizard state, 사용자 preference 같은 클라이언트 UI 상태에 한정한다.
- React Server Components에서 Zustand hook/context를 읽거나 쓰지 않는다.
- 요청별 초기값이 필요한 store는 `createStore` factory + Client Provider로 생성한다.
- 객체/배열 selector는 `useShallow(selector)`로 안정적인 참조를 반환한다.
- v4 스타일 `useStore(selector, shallow)`가 필요하면 `createWithEqualityFn`을 `zustand/traditional`에서 가져오고 `use-sync-external-store`를 설치한다.
- `setState(nextState, true)`는 전체 state를 전달한다.
- `persist`는 `partialize`, `version`, `migrate`를 함께 설계하고 민감 정보는 저장하지 않는다.

## Primary Sources

- https://nextjs.org/blog/next-16
- https://nextjs.org/blog/next-16-2
- https://nextjs.org/docs/app/guides/upgrading/version-16
- https://nextjs.org/docs/app/api-reference/file-conventions/proxy
- https://react.dev/blog/2025/10/01/react-19-2
- https://github.com/pmndrs/zustand/blob/main/docs/reference/migrations/migrating-to-v5.md
- https://github.com/pmndrs/zustand/blob/main/docs/learn/guides/nextjs.md
