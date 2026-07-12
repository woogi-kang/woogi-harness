# Next.js 16 and TypeScript 7 migration contract

Verified: 2026-07-13
Registry: `web-nextjs@recommended`

The production baseline is Node 24.18.0 LTS, Next.js 16.2.10, React 19.2.7, TypeScript 6.0.2, and ESLint 9.39.5. TypeScript 7.0.2 and ESLint 10.7.0 are stable and recorded as latest, but remain non-default lanes until their compiler/plugin integration surfaces pass.

## Runtime and framework

- Do not promote Node 26 Current into production templates. Node 18 and Node 20 are EOL; use Node 24 LTS for generated projects.
- Remove `--turbopack` from default scripts because Next 16 uses Turbopack for development and builds by default. Keep an explicit Webpack escape hatch only for a proven compatibility need.
- Replace `middleware.ts` with `proxy.ts` where Node runtime semantics are acceptable. Proxy cannot select the Edge runtime.
- Treat `cookies()`, `headers()`, `draftMode()`, route `params`, and `searchParams` as async APIs.
- Remove `next lint` and run ESLint or Biome directly. `next build` no longer performs linting.
- Review Cache Components, `revalidateTag` profiles, `updateTag`, image defaults, removed runtime config, removed AMP support, browser floors, and custom Webpack behavior.

## ESLint 9 default and ESLint 10 observed lane

- Pin generated Next.js projects to `eslint@^9.39.5`. `eslint-config-next@16.2.10` accepts ESLint 9+, and `typescript-eslint@8.63.0` accepts ESLint 9 and 10, but those peer ranges do not prove that every transitive plugin rule executes correctly on ESLint 10.
- Keep ESLint 10.7.0 as `latest_observed`, not as a generated default. Promote it only after a freshly materialized template completes install, direct ESLint, Next type generation, TypeScript checking, and a production build with zero compatibility patches.
- Keep flat config. Do not restore `.eslintrc` or `next lint` to work around a plugin failure.

## TypeScript 6 to 7 candidate lane

- TypeScript 7 is a native compiler and LSP implementation. It is not a drop-in compiler-library upgrade in 7.0.
- First make TypeScript 6 clean with `stableTypeOrdering` behavior and no ignored deprecated options.
- Account for TypeScript 7 defaults: `strict: true`, `module: esnext`, a modern target, `noUncheckedSideEffectImports: true`, `libReplacement: false`, `stableTypeOrdering: true`, `rootDir: ./`, and `types: []`.
- Remove `baseUrl`; make `paths` relative to the config. Remove ES5, `downlevelIteration`, node/node10/classic resolution, AMD/UMD/SystemJS/none modules, false `esModuleInterop`, false `allowSyntheticDefaultImports`, and import assertions using `assert`.
- TypeScript 7 may be promoted only after Next build, typescript-eslint, every compiler-API consumer, code generation, and editor LSP pass. Until then, run TypeScript 6 and 7 side by side.
- `typescript-eslint` 8.63.0 supports ESLint 10 but declares TypeScript `<6.1.0`. This makes TypeScript 6.0.2 the highest verified lint-compatible default; re-check the peer range before any TypeScript 7 promotion.

## Package-family migrations

- Tailwind 4 uses `@tailwindcss/postcss`, `@import "tailwindcss"`, CSS-first configuration, automatic source detection, and modern browser features. Remove v3-only directives and stale JavaScript config assumptions. Emit `postcss.config.mjs` through a named `const config = { ... }` followed by `export default config` so generated configuration is inspectable and extensible without rewriting an anonymous export.
- Zod 4 changes error customization and precedence, issue types, defaults inside optional fields, enum and record behavior, error formatting, and function schemas. Snapshot both errors and parsed output.
- Zustand 5 requires stable selector references, changes equality APIs and persistence initialization, and makes full replacement typing strict. Server state remains outside Zustand.
- Keep Auth.js channels explicit: `next-auth` stable is 4.24.14; 5.0.0-beta.31 is opt-in prerelease. Never emit v5 code while declaring the stable v4 dependency.

## Promotion commands

```bash
node --version
pnpm install --frozen-lockfile
pnpm outdated
pnpm exec next typegen
pnpm exec tsc --noEmit
pnpm exec eslint . --max-warnings=0
pnpm exec vitest run
pnpm exec playwright test
pnpm build
```

Candidate TypeScript 7 lane:

```bash
pnpm add -D 'typescript@npm:@typescript/typescript6@^6.0.2' '@typescript/native@npm:typescript@^7.0.2'
pnpm exec tsc6 --noEmit
pnpm exec tsc --noEmit
```

`typescript` alias는 programmatic API와 typescript-eslint를 위해 TypeScript 6을
유지하고 `@typescript/native` alias가 TypeScript 7의 `tsc`를 제공한다. Vue,
MDX, Astro, Svelte처럼 compiler API embedding이 필요한 도구는 7.1 API가
검증되기 전까지 TypeScript 6 lane을 기본으로 둔다.

## Primary sources

- https://nodejs.org/en/about/previous-releases
- https://nextjs.org/docs/app/guides/upgrading/version-16
- https://nextjs.org/blog/next-16-2
- https://eslint.org/docs/latest/use/migrate-to-9.0.0
- https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/
- https://tailwindcss.com/docs/upgrade-guide
- https://zod.dev/v4/changelog
- https://zustand.docs.pmnd.rs/reference/migrations/migrating-to-v5
- https://www.npmjs.com/package/next-auth?activeTab=versions
