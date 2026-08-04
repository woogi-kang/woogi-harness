# Woogi Harness

최신 모델의 네이티브 판단을 기본값으로 두고, 실제 검증과 이미지 생성 안전 경로만 공통 배포하는 lean agent runtime입니다.

이 저장소에는 비교 실험을 위해 25+ 도메인 에이전트와 활성 skill entrypoint 388개(내부 원본 386개 + exact-vendored `image-prompt`, `img2threejs` 2개)가 남아 있습니다. 다만 default project pack은 이 자산을 자동 배포하거나 라우팅하지 않습니다.

## Lean default

기본 실행은 다음 흐름입니다.

```text
사용자 요청
→ 현재 프로젝트와 기존 패턴 확인
→ 네이티브 모델이 직접 구현
→ 테스트·빌드·실화면·접근성 검증
→ 근거와 남은 위험 보고
```

기본 경로에서 제외한 계층:

- bulk agent/skill catalog와 자동 라우팅
- slash command와 DAG/team template
- registry/context compiler의 선행 context 주입
- routine execution contract와 telemetry
- GBrain 자동 조회
- Design Runtime의 Design Read, 5 dials, register, anti-slop prompt, critic loop

source checkout에는 A/B 비교와 명시적 opt-in을 위해 기존 자산을 보존합니다.

## 유지하는 것

- 프로젝트별 소스·문서·테스트·기존 디자인 시스템
- 실제 브라우저·디바이스·golden·접근성 검증
- read-only formatter/linter quality hook
- git push guard
- exact-vendored Gongnyang `image-prompt`
- Codex `$imagegen` / required `gpt-image-2` 계약과 image generation guard
- exact-vendored `img2threejs`
- dry-run, backup, rollback을 지원하는 sync runtime

## 디자인 실험 기준

`design-harness`는 implicit route에서 비활성화합니다. UI를 만들 때 모델에는 제품 코드, 브랜드 자산, 사용자 요청만 제공합니다. 구현 후 다음 항목만 검증합니다.

- 실제 route/screen 렌더링
- mobile/desktop과 scope 내 주요 상태
- 접근성, overflow, contrast, touch target
- 관련 build, test, golden
- 필요 시 deterministic UI detector

기존 Design Runtime은 source checkout에 opt-in 비교 baseline으로만 남습니다. 동일한 작업을 다음 조건으로 비교할 수 있습니다.

1. Native model only
2. Native model + deterministic QA
3. Explicit legacy `$design-harness`

## 이미지 생성은 별도 유지

디자인 하네스를 비활성화해도 이미지 생성 경로는 제거하지 않습니다.

```text
사용자 이미지 요청
→ image-prompt compile/validate
→ Codex $imagegen
→ artifact 확인
```

이미지의 목적과 배치는 현재 제품 맥락에서 모델이 직접 판단합니다. 허용되지 않은 provider/model fallback은 image guard가 차단합니다.

## 설치

```bash
git clone https://github.com/woogi-kang/woogi-harness.git
cd woogi-harness

# dry-run
./scripts/install.sh --link

# apply
./scripts/install.sh --link --apply
```

기본 설치에는 lean instructions, hooks, runtime verifier, registry contracts, image-generation overlay가 포함됩니다. bulk agents, commands, templates, rules, skills는 포함하지 않으며 `.agents/skills`에는 overlay가 설치한 `image-prompt`와 `img2threejs`만 노출됩니다.

## 다른 프로젝트에 동기화

```bash
bash scripts/sync-to-projects.sh
bash scripts/sync-to-projects.sh ../memoriz
bash scripts/sync-to-projects.sh --canary --apply
python3 scripts/harness-sync.py --rollback <manifest>
```

Sync는 기본적으로 dry-run이며 target-only 파일과 프로젝트별 settings/MCP/env를 보존합니다.

## 검증

```bash
python3 scripts/harness-registry.py validate
python3 scripts/harness-context.py
python3 scripts/harness-doctor.py
python3 scripts/verify-image-generation-policy.py
bash scripts/verify-gongnyang-prompt-kit.sh
bash scripts/verify-img2threejs.sh
```

`harness-doctor.py`는 설치 구조와 deterministic verifier를 확인할 뿐 결과물 품질을 증명하지 않습니다. 디자인 품질 비교는 동일 task와 동일 model 설정에서 실제 화면 결과로 판단합니다.

## Source checkout

기존 agent, skill, command, eval, Design Runtime, memory, orchestration 구현은 삭제하지 않고 source checkout에 보존합니다. 실험 결과가 필요한 계층만 명시적으로 다시 켤 수 있습니다.
