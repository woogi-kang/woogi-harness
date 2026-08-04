# Woogi Harness — Lean Default

이 저장소의 기본 실행 기준은 **네이티브 모델 + 현재 프로젝트 맥락 + 실제 검증**이다.
에이전트, 스킬, 커맨드, registry, context compiler, memory, DAG, typed execution contract는 자동으로 로드하거나 호출하지 않는다. 저장소에는 비교와 명시적 opt-in을 위한 기존 자산이 남아 있지만 기본 project pack에는 배포하지 않는다.

## 기본 작업 방식

- 사용자 응답은 현재 대화 언어를 따른다.
- 먼저 현재 소스, 프로젝트 문서, 설치된 의존성, 기존 패턴을 확인한다.
- 요청받은 범위만 직접 구현하고 관련 테스트, 빌드, 정적 분석으로 확인한다.
- 안전한 로컬 조회·편집·검증은 진행하되 외부 전송, 배포, 파괴적 변경, 결제·게시·메시지는 명시 승인 전에 중단한다.
- 결과를 바꾸는 중요한 정보가 없을 때만 질문한다. 사소한 가정은 밝히고 진행한다.
- 최신 SDK/API/library 동작은 로컬 버전과 공식 문서를 확인한다.
- 시크릿, 토큰, 개인정보를 출력하거나 커밋하지 않는다.

## 기본적으로 사용하지 않는 것

- capability registry와 context compiler의 선행 실행
- GBrain의 자동 조회·캡처
- routine 작업의 typed execution state
- 자동 agent/skill routing
- 자동 multi-agent, DAG, independent critic
- Design Runtime, Design Read, 5 dials, register, anti-slop prompt

사용자가 특정 스킬·커맨드·멀티에이전트 실행을 명시했을 때만 해당 자산을 연다. 과거 결정이 실제로 필요한 요청에서는 memory를 명시적으로 조회할 수 있다. 장기·반복·고위험 실행에서는 필요성이 확인된 경우에만 execution contract를 사용한다.

## UI와 디자인

UI 방향은 현재 제품, 실제 브랜드 자산, 기존 디자인 시스템과 사용자 요청에서 모델이 직접 판단한다. `design-harness`는 기본 경로에서 비활성화한다.

디자인 지침 대신 결과를 검증한다.

- 실제 브라우저, 시뮬레이터 또는 디바이스에서 화면을 확인한다.
- scope에 해당하는 mobile/desktop과 loading, empty, error, focus 상태를 확인한다.
- 접근성, overflow, contrast, touch target, build/test/golden을 가능한 범위에서 실행한다.
- `.claude/skills/design-harness/scripts/detect-design-slop.mjs`는 생성 지침이 아니라 구현 후 deterministic 진단으로만 사용할 수 있다.

## 이미지 생성

이미지 생성 경로는 디자인 하네스와 분리해 유지한다.

- 생성형 raster prompt는 exact-vendored Gongnyang `image-prompt`가 compile/validate한다.
- 실제 생성은 Codex `$imagegen` host contract의 required model `gpt-image-2`만 사용하며 fallback하지 않는다.
- `img2threejs`는 별도 exact-vendored opt-in skill로 유지한다.
- 실제 screenshot, deterministic SVG/vector, native chart/table/text는 생성형 이미지가 아니다.

## 저장소 자산

`.claude/agents`, `.claude/skills`, `.claude/commands`, `.claude/templates`, Design Runtime, memory와 orchestration scripts는 비교 실험과 명시적 opt-in을 위해 source checkout에 보존한다. 다른 프로젝트로 동기화되는 lean default에는 bulk agent/skill 자산을 포함하지 않는다.
