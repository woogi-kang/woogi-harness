# UI Design Agent v3 사용 가이드

UI/UX 구현·리디자인·감사·폴리시는 `design-harness`의 증거 기반 runtime으로 실행한다.

## 요청 예시

```text
"이 Flutter 온보딩을 기존 테마 안에서 리디자인하고 실제 상태별 화면까지 검증해줘"
"B2B 운영 대시보드의 밀도와 오류 복구 UX를 고쳐줘"
"이 랜딩이 AI Slop처럼 보이는 이유를 evidence와 함께 감사해줘"
```

## 처리 흐름

1. 프로젝트 문서, 대표 화면, theme/token, dependency를 읽는다.
2. runtime run을 만들고 Design Read, register, 5 dials, risk를 고정한다.
3. redesign이면 동일 조건의 baseline을 남긴다.
4. Web 또는 Flutter adapter로 구현한다.
5. detector, build/test, route/state/viewport screenshot, a11y/semantics evidence를 등록한다.
6. 독립 critic이 evidence를 리뷰한다.
7. 최대 2회만 수선하고 register별 executable eval을 실행한다.

## Five dials

| 화면 | DISTINCTION | MOTION | DENSITY | EVIDENCE | SYSTEMNESS |
|---|---:|---:|---:|---:|---:|
| Product UI | 3–5 | 1–4 | 5–8 | 7–9 | 7–10 |
| Operational/admin | 2–4 | 1–3 | 7–10 | 7–10 | 8–10 |
| Brand/campaign | 6–9 | 3–8 | 2–5 | 7–10 | 3–7 |
| Public/regulated | 2–4 | 1–3 | 5–8 | 7–10 | 9–10 |

값은 시작점이며 프로젝트 evidence로 조정한다.

## 주요 명령

```bash
python3 .claude/skills/design-harness/scripts/design-runtime.py plan --root .
python3 .claude/skills/design-harness/scripts/design-runtime.py init --help
node .claude/skills/design-harness/scripts/detect-design-slop.mjs --help
python3 .claude/evals/ui-design/grader.py self-test
```

상세 artifact 계약은 `.claude/skills/design-harness/references/runtime-v3.md`를 따른다.

## 완료 상태

- `passed`: 필수 evidence, 독립 critic, register eval 모두 통과.
- `needs_evidence`: 실제 실행/화면/상태 근거 부족.
- `needs_review`: 독립 critic 또는 근거 있는 채점이 부족.
- `failed`: 품질/기능 hard gate 실패.
- `blocked`: tool, asset, permission 같은 외부 조건 때문에 안전하게 진행 불가.

## Legacy

`/fd-*`, 12개 aesthetic template, minimal/modern/bold strategy, 3-dial workflow는 활성 경로가 아니다.
