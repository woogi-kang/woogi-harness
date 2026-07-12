# Agent Orchestration — Kernel v3

이 파일은 모든 도메인 지식을 담는 목록이 아니다. 요청을 project profile, canonical capability, bounded context, provider adapter, typed outcome으로 연결하는 작은 라우팅 커널이다. 실제 지침은 선택된 agent/skill만 progressive하게 읽는다.

## 1. Runtime order

사용자 요청을 아래 순서로 처리한다.

```text
1. Explicit command/skill/provider request
2. Memory/context lookup when prior people/project/decision truth matters
3. Material ambiguity or approval boundary → native choice UI
4. Project profile + capability resolution
5. Cross-cutting safety/currentness/design/image rules
6. Context compile
7. Direct execution or bounded delegation
8. Evidence-backed verification and typed outcome
9. Telemetry + concise handoff
```

### Clarification

지시가 불명확하거나 선택에 따라 결과가 달라지면 `.claude/rules/common/clarification-protocol.md`를 따른다. 사용 가능한 런타임에서는 native 선택 UI가 기본이다. 같은 세션에서 범위가 이미 확정됐거나 사소한 가정이면 질문을 반복하지 않는다.

하위 agent/skill은 사용자를 직접 붙잡지 않는다. 필요한 값이 없으면 structured blocker를 반환하고, root orchestrator가 1–3개의 실제 선택으로 바꿔 사용자에게 묻는다.

### Approval

Production, destructive git/data operation, 외부 전송, 유료 실행, 사용자 계정의 게시/메시지/구매는 명시 승인 없이 넘지 않는다. Read-only 진단, local test, dry-run, manifest는 계속할 수 있다.

## 2. Capability registry and project profile

기본 profile은 `.claude/registry/projects/default.json`이다. 프로젝트별 profile/overlay가 있으면 그것이 우선한다.

```bash
python3 scripts/harness-registry.py resolve <capability-or-alias>
python3 scripts/harness-context.py \
  --project-profile <profile.json> \
  --capability <capability-or-alias> \
  --output <context-manifest.json>
```

- Registry는 agent/skill 본문을 로드하지 않고 frontmatter만 bounded scan한다.
- Unique 이름은 bare alias로 resolve한다.
- `architecture`, `project-setup`처럼 중복된 이름은 bare alias를 거부하고 `skill:<scope>/<name>` 또는 stable path ID를 사용한다.
- Context manifest의 byte budget을 넘기지 않는다. 필요한 reference는 선택된 SKILL의 progressive-disclosure 지시에 따라 추가한다.
- Registry 경고를 피하려고 임의의 skill을 선택하지 않는다.

## 3. Cross-cutting hard routes

아래 route는 일반 도메인 위임보다 먼저 적용한다.

| Intent | Required route |
|---|---|
| 사람/회사/프로젝트/과거 결정/이전 작업 맥락 | `memory-engine.md`에 따라 GBrain 조회 |
| 최신 SDK/API/library/version 동작 | `official-docs-guide` + local manifest + tech-stack registry |
| 공개 source 차단/검증 | `web-access-ladder` |
| repo context를 외부 model/worker/reviewer에 전달 | `context-pack-gate`; secret/budget PASS 전 전달 금지 |
| 반복/장기/자율 작업 | `execution-contract.md` + 필요 시 `goal-prep-pack`/`autonomous-loops` |
| UI/UX/Web/Flutter visual 변경·audit·AI Slop | `design-harness` Design Runtime v3 |
| 생성형 raster image/편집 | exact-vendored `image-prompt` → validator → Codex `$imagegen`/`gpt-image-2` only |
| 한국어 기술/제출 문서 | path-scoped `korean-writing-style.md` + `copy-editing` |
| PPT/PDF/slide | `presentation-quality-gate.md` + presentation capability |

### Image invariant

모든 생성형 이미지 prompt는 Gongnyang 원본이 단독 소유한다. 기존 skill은 목적, asset placement, artifact QA만 담당한다. 자체 prompt/negative prompt/suffix를 추가하거나 대체 model/provider로 fallback하지 않는다. 실제 screenshot, deterministic SVG/vector, native chart/table/text는 생성형 이미지가 아니다.

### Design invariant

UI 작업은 project fingerprint, Design Read, 5 dials, platform adapter, route/state/viewport evidence, source scan, independent critic, register-specific eval을 따른다. 구현 owner는 `ckm:ui-styling`과 해당 framework skill이며 방향/완료 gate owner는 `design-harness`다. 구현자가 자기 결과를 최종 승인하지 않는다.

## 4. Domain owner selection

Skill의 name/description/trigger가 명시적으로 맞으면 agent보다 먼저 그 skill을 선택한다. 복합 workflow와 여러 skill 조정이 필요할 때만 domain agent를 사용한다.

| Domain | Primary owner examples |
|---|---|
| Backend/Python/FastAPI | `fastapi-agent`; qualified FastAPI skills |
| Flutter/mobile | `flutter-agent`; qualified Flutter skills |
| Next.js/React/web | `nextjs-agent`; qualified Next.js skills |
| Figma conversion | strict fidelity면 pixel-perfect agent, 아니면 framework converter |
| Product planning/strategy/GTM | `planning-agent` 또는 matching planning skill |
| UI/UX/design | `design-harness` → 필요 시 `ui-design-agent` |
| Presentation/social/blog/content | matching content agent/skill |
| Marketing/SEO | matching marketing/SEO owner |
| Legal/corporate | legal contract/corporate legal owner |
| Finance/payment | finance/payment owner |
| Multi-perspective review | `review-orchestrator`; critic은 implementation owner와 분리 |
| Korean life automation | available k-skill의 exact description; agent 없이 skill direct |

거대한 keyword table을 이 파일에 복제하지 않는다. 현재 available skill catalog와 generated registry가 source of truth다.

## 5. Direct work vs delegation

| Situation | Route |
|---|---|
| 특정 파일/함수 조회, 단일 사실, 1–3개 파일의 좁은 수정 | 직접 처리 |
| 3개 이상의 독립 조사 query | 병렬 read-only worker |
| 한 도메인의 여러 capability 조정 | domain agent |
| 서로 독립적인 여러 도메인 | DAG/team orchestration |
| 위험/주관 품질 최종 판정 | 별도 `independent_critic` quality class |

Delegation은 context를 줄이기 위한 수단이지 책임을 넘기는 수단이 아니다. Root가 결과를 통합하고 검증한다.

## 6. Provider-neutral quality classes

일반 작업에 provider/model 이름을 hardcode하지 않는다. `.claude/registry/providers/core.yaml`의 quality class를 project/provider adapter가 해석한다.

| Quality class | Use |
|---|---|
| `reasoning_high` | architecture, ambiguous diagnosis, high-consequence synthesis |
| `implementation` | repository change + focused verification |
| `fast_scan` | bounded inventory/discovery/classification |
| `independent_critic` | implementation context와 분리된 evidence review |

Agent frontmatter는 `model: inherit`와 quality class를 사용한다. Image generation만 사용자 정책에 따라 `gpt-image-2`를 고정한다. Required tool/capability를 지원하지 않는 provider에서는 fallback model을 추측하지 말고 `blocked`로 반환한다.

## 7. Execution and outcome

반복/병렬 작업은 먼저 typed state record를 만든다.

```bash
python3 scripts/harness-execution.py init ...
python3 scripts/harness-execution.py transition ...
python3 scripts/harness-execution.py validate --file <outcome.json> --final
```

`succeeded`에는 success criteria별 passed check와 실제 evidence가 필요하다. Worker process exit 0만으로 DAG를 complete하지 않는다. 같은 실패를 같은 방식으로 세 번 반복하지 않는다.

## 8. Team orchestration

여러 도메인이 독립적으로 진행될 때만 provider가 지원하는 team/DAG substrate를 사용한다.

- Worker마다 `objective`, `success_criteria`, `stop_condition`, `approval_boundary`, `state_record`를 준다.
- 넓은 repo context에는 PASS한 `context_pack`을 준다.
- 파일 소유 범위를 분리해 shared workspace 충돌을 막는다.
- 의존성이 없는 read-only 작업은 병렬, 의존성이 있는 mutation은 DAG 순서를 따른다.
- 위험도나 주관 품질이 높으면 implementation과 별도 critic node를 둔다.
- Worker가 structured blocker를 반환하면 root가 native 선택 UI로 필요한 값만 묻고 재위임한다.

## 9. Common workflow chains

```text
New product:
planning → execution prep → Design Runtime → framework implementation
→ build/test → independent review → typed outcome

Current technical change:
local version → official docs → tech-stack registry/migration gates
→ implementation → fixture/build evidence

UI redesign:
fingerprint/baseline → design contract → platform capture
→ source/visual gate → independent critic → max-two repair → eval

Generated image:
asset context → image-prompt → check_prompt.mjs
→ $imagegen/gpt-image-2 → artifact QA

External review:
context-pack PASS → explicit approval → external review
→ local evidence reconciliation
```

## 10. Context and telemetry discipline

- 큰 body를 routing 단계에서 읽지 않는다.
- Context manifest에는 포함/제외, byte size, SHA-256, inventory hash를 남긴다.
- 외부 전송 전 secret scan 결과를 확인한다.
- Agent/Skill invocation은 normalized one-object-per-line JSONL로 기록한다.
- 중간 결과를 source dump가 아닌 bounded artifact/manifest로 남긴다.
- 최종 응답은 변경, 검증, waiver, 남은 위험만 요약한다.
