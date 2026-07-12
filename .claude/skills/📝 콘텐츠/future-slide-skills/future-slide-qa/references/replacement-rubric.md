# Future Slide Replacement Rubric

기존 `presentation-agent`와 PPT 관련 skills를 Future Slide 계열로 대체할 수 있는지 판단하는 기준입니다.

## 현재 판정

Status: Shadow Mode

근거:
- HTML locked layout 품질은 샘플 3종에서 양호했습니다.
- overflow, padding, Korean word breaking 자동 QA는 동작했습니다.
- 기존 product/brand visual deck의 layout/semantic review는 통과했지만, 과거
  자체 prompt와 CLI provenance는 현재 gate의 통과 증거가 아닙니다. 현행
  `image-prompt` → validator → Codex `$imagegen` trusted-host 계약으로 다시
  생성·검증해야 replacement evidence로 승격할 수 있습니다.
- PPTX/PDF export parity, 리서치/검증 파이프라인 parity, 나머지 archetype은 아직 충분히 검증되지 않았습니다.

## 평가 단계

| 단계 | 의미 | 허용 액션 |
|---|---|---|
| Shadow Mode | 기존 PPT agent는 유지하고 Future Slide를 선택 경로로만 사용 | wrapper 추가, 샘플 QA |
| Partial Default | HTML 비주얼 덱 요청은 Future Slide를 기본 사용 | 라우팅 일부 변경 |
| Export Parity | PDF/PPTX 변환 품질까지 통과 | 제출용 덱 일부 전환 |
| Replacement Candidate | 5개 archetype 모두 통과 | `/skill-audit`로 retire 후보 평가 |
| Replacement Approved | 사용자 확인 완료 | 기존 스킬 retire/merge 실행 |

## 필수 Archetype

1. Executive KPI report
   - 수치, ledger, chart, 요약이 많은 보고용 덱

2. Workshop/framework deck
   - 프레임워크, matrix, process, discussion prompt가 있는 덱

3. Product/brand visual deck
   - hero image, icon set, 제품/브랜드 메시지가 중심인 덱
   - current: layout QA pass; semantic graphic quality pass; legacy image
     provenance는 current manifest gate에서 재검증 필요

4. Dense data/chart deck
   - Chart.js 또는 표/그래프가 중심인 분석 덱

5. PPTX/PDF handoff deck
   - 편집 가능한 PPTX와 발표용 PDF가 모두 필요한 제출용 덱

## Gate

각 archetype은 아래 기준을 통과해야 합니다.

- 자동 QA: FAIL 0건
- vendor validator: error 0건
- QA screenshot/contact sheet 생성
- 한국어 제목 줄바꿈 major issue 0건
- 생성형 raster의 `image-prompt@2.3.0`, `image_gen__imagegen`, `prompt_record`,
  `required_model: gpt-image-2`, `model_binding: trusted-host-fixed`,
  `local_model_verification: unavailable`, `host_reported_model: null`,
  `generation_assurance: generated_under_trusted_host_contract` 누락 0건이며
  로컬 attestation으로 오인되는 `model` 필드 0건
- product screenshot, reference photo, deterministic chart/SVG는 명시적 `kind` 및 `source` provenance 누락 0건
- 생성 이미지 내 읽어야 하는 텍스트 0건
- 의미 없는 decorative/filler graphic 0건
- 모든 이미지에 visual contract 존재
- 이미지 alt/data-image-slot 누락 0건
- export가 필요한 케이스는 PPTX/PDF 육안 검수 통과
- 리서치가 필요한 케이스는 출처/검증 기록 존재

## 대체 금지 조건

아래 중 하나라도 남아 있으면 기존 PPT agent를 제거하지 않습니다.

- `.pptx` 편집 가능성이 핵심인 요청을 안정적으로 처리하지 못함
- 리서치/팩트체크/출처 검증 단계가 누락됨
- 한국어 장문 제목에서 자동 줄바꿈 문제가 반복됨
- 이미지 생성 결과가 텍스트를 대체하거나 오탈자를 만들 가능성이 큼
- QA가 screenshot 기반으로 재현되지 않음
- `/skill-audit`에서 Retire/Merge 확인을 받지 않음
