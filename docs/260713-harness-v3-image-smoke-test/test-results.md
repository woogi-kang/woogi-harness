# Image generation smoke-test results

결과: **5장 생성 / 4장 승인 / 1장 거부**.

모든 입력은 exact-vendored Gongnyang `image-prompt@2.3.0`이 만든 JSONL의
`full_prompt`만 사용했다. `check_prompt.mjs` 검증은 5/5 통과했고 경고는
없었다. 생성에는 Codex `$imagegen` host contract만 사용했으며 다른
provider/model fallback이나 사후 텍스트 오버레이는 사용하지 않았다.

| # | 범주 | 결과 | 핵심 판정 |
|---|---|---|---|
| 01 | C3 typographic minimal | 승인 | 한국어/영문 copy 정확, 활판 인쇄 물성 및 위계 우수 |
| 02 | C4 exploded view | 조건부 승인 | copy와 재질은 정확, CONTEXT leader 위치에 경미한 의미 오차 |
| 03 | C9 clay object | 승인 | 단일 아이디어와 재질 분리가 명확하고 불필요한 문자가 없음 |
| 04 | C11 shadow narrative | **거부** | 요청하지 않은 영문·유사 문자와 하단 배너 생성; repair 1회도 실패 |
| 05 | C12 cover slide | 승인 | 두 문구 정확, 물리적 evidence flow와 안전 여백 우수 |

이번 smoke test는 생성 성공률을 품질 통과율로 바꾸어 말하지 않는다.
04번은 AI Slop 회귀를 탐지하는 실패 증거로 그대로 보존한다. 재시도 결과는
더 많은 문자를 만들어 폐기했으며 manifest에는 최초 산출물만 기록했다.

모델 경계도 구분한다. 정책상 required model은 `gpt-image-2`이고 실행은
`generated_under_trusted_host_contract`로 기록된다. 현재 Codex host schema가
실제 model identity를 노출하지 않으므로 로컬 attestation은 `unavailable`이다.
모델 증명이 필수인 실행은 성공으로 가장하지 않고
`blocked_imagegen_model_unverifiable`로 중단해야 한다.

해시, 크기, 픽셀 치수, 4축 QA, 개별 판정은
`image-generation-manifest.json`이 source of truth다.
