---
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.jsx"
  - "**/*.mjs"
  - "**/*.cjs"
  - "**/package.json"
---

# TypeScript and JavaScript Coding Style

- 현재 `package.json`, lockfile, tsconfig, framework config, lint/format 설정이 우선한다.
- 신규 Next.js baseline은 `.claude/registry/tech-stacks/web-nextjs.yaml`의 recommended channel을 사용한다. TypeScript는 tooling 호환 때문에 6.0.2가 권장이며 7.0.2는 candidate gate를 통과한 뒤 승격한다.
- TypeScript project는 strict typing을 유지하고 `any`/unchecked cast 대신 boundary validation과 narrowing을 사용한다.
- Next.js App Router, server component, server action 규칙은 실제 Next.js 프로젝트에서만 적용한다.
- TanStack Query, Zustand, shadcn/ui, Tailwind, Motion을 하네스 기본값으로 강제하지 않는다. 기존 project pattern 또는 명시적 architecture/design decision이 있을 때만 사용한다.
- Tailwind를 선택한 프로젝트는 v4 CSS-first 구성을 사용하고 v3 config/directive migration gate를 확인한다.
- Formatter/linter는 project-local executable만 사용한다. `npx`를 통한 묵시적 install이나 자동 major upgrade를 실행하지 않는다.
