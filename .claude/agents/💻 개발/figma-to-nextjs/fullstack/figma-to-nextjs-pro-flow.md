---
name: Figma to Next.js Pro Flow
description: 8-phase pipeline flow documentation for figma-to-nextjs-pro agent with dual-agent verification achieving 95%+ pixel-perfect accuracy
---

# Figma → Next.js Pro 컨버터 플로우

> **버전**: 2.2.0 | **에이전트**: figma-to-nextjs-pro | **품질 클래스**: `reasoning_high`

---

## 개요

8단계 파이프라인과 이중 검증 루프를 통해 Figma 디자인을 **95%+ 정확도**의 Next.js 컴포넌트로 변환합니다.

**핵심 원칙:**
- Code 검증과 Visual 검증 **둘 다 95% 이상**이어야 통과
- 모든 이미지/아이콘은 Figma에서 **100% 다운로드** 필수
- Visual 비교는 **Gemini CLI**에 위임

---

## 메인 파이프라인 플로우

```mermaid
flowchart TB
    subgraph INPUT["📥 입력"]
        A[Figma URL/Frame]
    end

    subgraph P0["Phase 0: CLI 초기화"]
        B1[프로젝트 체크<br/>ls package.json]
        B2[CLI 생성<br/>npx create-next-app]
        B3[shadcn 초기화<br/>npx shadcn init]
        B1 --> B2 --> B3
    end

    subgraph P1["Phase 1: 디자인 분석"]
        C1[get_metadata<br/>80% 토큰 절감]
        C2[노드 선택]
        C3[구조 맵 생성]
        C1 --> C2 --> C3
    end

    subgraph P2["Phase 2: 토큰 추출"]
        D1[get_variable_defs]
        D2[토큰 변환<br/>figma-tokens 스킬]
        D3[Tailwind 생성<br/>Context7 문서]
        D1 --> D2 --> D3
    end

    subgraph P3["Phase 3: 컴포넌트 매핑"]
        E1[Code Connect 맵]
        E2[shadcn 매칭<br/>shadcn-patterns 스킬]
        E3[커스텀 플랜]
        E1 --> E2 --> E3
    end

    subgraph P4["Phase 4: 코드 생성"]
        F1[get_design_context]
        F2[TSX 생성]
        F3[Props 추출]
        F1 --> F2 --> F3
    end

    subgraph P5["Phase 5: 에셋 처리 ⚠️ 필수"]
        G1[get_screenshot]
        G2[100% 다운로드<br/>모든 이미지/아이콘]
        G3[next/image 통합]
        G1 --> G2 --> G3
    end

    subgraph P6["Phase 6: 이중 검증 루프"]
        direction TB
        subgraph PARALLEL["2 에이전트 × 5 반복"]
            direction LR
            subgraph AGENT_A["에이전트 A: 보수적"]
                H1A[Standard Tailwind<br/>temp: 0.3]
            end
            subgraph AGENT_B["에이전트 B: 실험적"]
                H1B[Custom CSS Vars<br/>temp: 0.7]
            end
        end

        subgraph ITERATION["각 반복 - 이중 검증"]
            I1[① Code 검증]
            I2[② Visual 검증<br/>Gemini CLI]
            I3[③ 둘 다 ≥95%?]
            I4[④ 자동 수정 + 재검증]
            I1 --> I3
            I2 --> I3
            I3 --> I4
        end

        PARALLEL --> ITERATION

        subgraph SELECTION["결과 선택"]
            J1{Code ≥95%<br/>AND<br/>Visual ≥95%?}
            J2[✅ 완료<br/>승자 선택]
            J3[수정 적용<br/>다음 반복]
        end

        ITERATION --> J1
        J1 -->|Yes| J2
        J1 -->|No| J3
        J3 --> ITERATION
    end

    subgraph P7["Phase 7: 반응형"]
        K1[브레이크포인트 테스트<br/>sm/md/lg/xl/2xl]
        K2[모바일 퍼스트 체크]
        K3[최종 리포트]
        K1 --> K2 --> K3
    end

    subgraph OUTPUT["📤 출력"]
        L[프로덕션 준비 완료<br/>Next.js 컴포넌트]
    end

    INPUT --> P0 --> P1 --> P2 --> P3 --> P4 --> P5 --> P6
    J2 --> P7
    P7 --> OUTPUT

    style INPUT fill:#e1f5fe
    style OUTPUT fill:#c8e6c9
    style P5 fill:#ffcdd2
    style P6 fill:#fff3e0
    style PARALLEL fill:#fce4ec
    style SELECTION fill:#f3e5f5
```

---

## Phase 요약

| Phase | 이름 | 주요 작업 | 토큰 영향 |
|-------|------|----------|----------|
| **0** | CLI 초기화 | 프로젝트 체크 → CLI 생성 → shadcn 초기화 | 97% 절감 |
| **1** | 디자인 분석 | get_metadata → 노드 선택 → 구조 맵 | 80% 절감 |
| **2** | 토큰 추출 | get_variable_defs → 변환 → Tailwind 생성 | 중간 |
| **3** | 컴포넌트 매핑 | Code Connect → shadcn 매칭 → 커스텀 플랜 | 낮음 |
| **4** | 코드 생성 | get_design_context → TSX → Props 추출 | 높음 |
| **5** | 에셋 처리 | get_screenshot → **100% 다운로드** → next/image | 중간 |
| **6** | 이중 검증 | 2 에이전트 × 5 반복 → 둘 다 ≥95% → 승자 선택 | 가변 |
| **7** | 반응형 | 브레이크포인트 테스트 → 모바일 퍼스트 → 리포트 | 낮음 |

---

## Phase 5: 에셋 다운로드 규칙

> **⚠️ CRITICAL**: 모든 이미지/아이콘은 반드시 Figma에서 100% 다운로드해야 합니다.

### 반드시 해야 할 것

- Figma에서 모든 이미지 에셋 다운로드
- Figma에서 모든 아이콘 다운로드 (SVG/PNG)
- `public/images/` 또는 `public/icons/`에 저장
- `next/image` 컴포넌트로 최적화 적용

### 절대 금지

- Lucide, Heroicons 등 대체 아이콘 라이브러리 사용 금지
- 임의로 이미지/아이콘 생성 금지
- Placeholder 이미지 사용 금지
- Figma 에셋 다운로드 스킵 금지

```mermaid
flowchart LR
    F[Figma 디자인] -->|get_screenshot| D[100% 다운로드]
    D -->|images| I[public/images/]
    D -->|icons| IC[public/icons/]
    I --> N[next/image]
    IC --> N

    X[❌ Lucide/Heroicons] -.->|금지| N
    Y[❌ 생성된 에셋] -.->|금지| N
```

---

## Phase 6: 이중 검증 (Code + Visual)

**모든 반복에서 Code와 Visual 검증을 동시에 실행합니다** - Fallback이 아닌 필수입니다.

### 통과 조건 (둘 다 통과해야 함)

```
┌────────────────────────────────────────────────────┐
│              둘 다 95% 이상이어야 통과              │
├────────────────────────────────────────────────────┤
│                                                    │
│   Code ≥ 95%  AND  Visual ≥ 95%  →  ✅ 통과      │
│   Code < 95%  OR   Visual < 95%  →  ❌ 계속 반복  │
│                                                    │
└────────────────────────────────────────────────────┘
```

### 예시 시나리오

| Code | Visual | 결과 |
|------|--------|------|
| 97% | 96% | ✅ 통과 - 둘 다 ≥95% |
| 98% | 92% | ❌ 계속 (Visual 미달) |
| 93% | 97% | ❌ 계속 (Code 미달) |
| 94% | 94% | ❌ 계속 (둘 다 미달) |

---

### 이중 검증 플로우

```mermaid
flowchart TB
    subgraph DUAL["이중 검증 (둘 다 통과 필수)"]
        direction LR
        subgraph CODE["Code 검증"]
            C1[Tailwind 클래스 비교]
            C2[Layout 30%]
            C3[Spacing 25%]
            C4[Typography 20%]
            C5[Colors 15%]
            C6[Effects 10%]
            C1 --> C2 & C3 & C4 & C5 & C6
        end

        subgraph VISUAL["Visual 검증"]
            V1[Figma 스크린샷]
            V2[Playwright 캡처]
            V3[Gemini CLI 비교]
            V1 --> V3
            V2 --> V3
        end
    end

    subgraph CHECK["통과 체크"]
        M1{Code ≥ 95%?}
        M2{Visual ≥ 95%?}
    end

    CODE --> M1
    VISUAL --> M2

    M1 -->|Yes| M2
    M1 -->|No| FIX[수정 적용 → 다음 반복]
    M2 -->|Yes| PASS[✅ 완료]
    M2 -->|No| FIX
```

---

### 왜 Visual 비교에 Gemini CLI를 사용하나요?

| 항목 | Claude | Gemini |
|------|--------|--------|
| 이미지 diff 정확도 | 좋음 | **우수** |
| 픽셀 단위 분석 | 제한적 | **강력** |
| 색상 매칭 | 근사치 | **정확** |
| 이미지 비용 | 높음 | **낮음** |

---

### Gemini CLI 명령어

```bash
gemini -p "이 두 UI 이미지를 비교하고 모든 차이점을 식별하세요:
1. 레이아웃/위치 차이
2. Spacing/padding/margin 이슈
3. 색상 불일치 (정확한 hex 값)
4. 타이포그래피 차이
5. 누락되거나 잘못된 요소
6. Border/shadow/effect 차이

각 카테고리를 0-100으로 점수화하고 구체적인 CSS 수정안을 제시하세요.

Reference: ./comparison/figma-reference.png
Implemented: ./comparison/implemented.png

JSON 형식으로 출력:
{
  \"visual_score\": number,
  \"categories\": {...},
  \"differences\": [...],
  \"fixes\": [...]
}"
```

---

### 검증 플로우 상세

```mermaid
flowchart LR
    subgraph CAPTURE["1. 캡처"]
        F[Figma<br/>get_screenshot]
        P[Playwright<br/>browser_take_screenshot]
    end

    subgraph GEMINI["2. Gemini CLI 분석"]
        G["gemini -p 'Compare images...'"]
    end

    subgraph OUTPUT["3. JSON 출력"]
        O1[visual_score: 96]
        O2[differences: ...]
        O3[fixes: ...]
    end

    F --> G
    P --> G
    G --> O1 & O2 & O3
```

---

## 자동 수정 레벨

| 레벨 | 카테고리 | 자동 수정 | 예시 |
|------|----------|----------|------|
| L1 | Spacing | ✅ 즉시 | p-5 → p-6 |
| L1 | Colors | ✅ 즉시 | blue-500 → blue-600 |
| L2 | Typography | ✅ 로그 | text-base → text-lg |
| L2 | Shadows | ✅ 로그 | shadow-sm → shadow-md |
| L3 | Layout | ⚠️ 승인 필요 | flex → grid |
| L4 | Structure | ❌ 수동 | 컴포넌트 분리 |

---

## 병렬 검증 상세

```mermaid
flowchart TB
    subgraph AGENTS["이중 에이전트 전략"]
        direction LR
        A1["🔵 에이전트 A<br/>보수적<br/>temp: 0.3"]
        A2["🟠 에이전트 B<br/>실험적<br/>temp: 0.7"]
    end

    subgraph STRATEGY_A["에이전트 A 전략"]
        SA1[표준 Tailwind 유틸리티]
        SA2[커스텀 CSS보다 조합 선호]
        SA3[shadcn/ui 패턴 엄격 준수]
    end

    subgraph STRATEGY_B["에이전트 B 전략"]
        SB1[유연성을 위한 CSS 변수]
        SB2[창의적인 레이아웃 솔루션]
        SB3[성능 최적화 중심]
    end

    A1 --> STRATEGY_A
    A2 --> STRATEGY_B

    subgraph COMPARE["비교 및 선택"]
        C1["에이전트 A<br/>Code: 97%, Visual: 96%"]
        C2["에이전트 B<br/>Code: 94%, Visual: 95%"]
        C3[승자: 에이전트 A<br/>둘 다 ≥95% 통과]
    end

    STRATEGY_A --> C1
    STRATEGY_B --> C2
    C1 --> C3
    C2 --> C3
```

---

## 사용된 MCP 도구

| 도구 | Phase | 용도 |
|------|-------|------|
| `get_metadata` | P1 | 구조 분석 (토큰 절감) |
| `get_variable_defs` | P2 | 디자인 토큰 추출 |
| `get_code_connect_map` | P3 | 기존 매핑 조회 |
| `add_code_connect_map` | P3 | 새 매핑 등록 |
| `get_design_context` | P4 | 코드 생성용 전체 컨텍스트 |
| `get_screenshot` | P5, P6 | 이미지 & 시각적 비교 |
| `resolve-library-id` | P2, P4 | Context7 라이브러리 조회 |
| `get-library-docs` | P2, P4 | Context7 문서 |
| `browser_navigate` | P6 | Playwright: 개발 서버로 이동 |
| `browser_snapshot` | P6 | Playwright: DOM 스냅샷 |
| `browser_take_screenshot` | P6 | Playwright: 구현된 UI 캡처 |
| `browser_click` | P6 | Playwright: 인터랙션 테스트 |

---

## 빠른 명령어

```bash
# 전체 변환
@figma-to-nextjs-pro convert [FIGMA_URL]

# 개별 Phase 실행
@figma-to-nextjs-pro phase:0 init      # CLI 초기화
@figma-to-nextjs-pro phase:1 analyze   # 디자인 분석
@figma-to-nextjs-pro phase:2 tokens    # 토큰 추출
@figma-to-nextjs-pro phase:3 map       # 컴포넌트 매핑
@figma-to-nextjs-pro phase:4 generate  # 코드 생성
@figma-to-nextjs-pro phase:5 assets    # 에셋 처리
@figma-to-nextjs-pro phase:6 verify    # 이중 검증
@figma-to-nextjs-pro phase:7 responsive # 반응형 체크
```

---

## 출력 구조

```
src/
├── components/
│   ├── ui/              # shadcn/ui 컴포넌트
│   ├── layout/          # Header, Footer, Nav
│   ├── sections/        # 페이지 섹션
│   └── [feature]/       # 기능별 컴포넌트
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── globals.css
├── public/
│   ├── images/          # Figma에서 다운로드한 이미지
│   └── icons/           # Figma에서 다운로드한 아이콘
├── styles/
│   └── variables.css    # Figma 토큰
└── lib/
    └── utils.ts         # cn() 유틸리티
```

---

## PRO vs Modular 비교

| 기능 | Modular | PRO |
|------|---------|-----|
| **품질 클래스** | `implementation` | `reasoning_high` |
| **검증** | 단일 에이전트 | 이중 에이전트 (병렬) |
| **최대 반복** | 5 | 5 × 2 에이전트 |
| **전략** | 표준만 | 보수적 + 실험적 |
| **결과 선택** | 단일 결과 | 둘 중 최고 |
| **사용 사례** | 간단한 컴포넌트 | 복잡한 페이지, 프로덕션 |

---

## 종료 조건

```yaml
success:
  - code_score >= 95% AND visual_score >= 95%  # 둘 다 통과 필수
  - all_categories >= 90%
  - completion_marker: "## ✓ VERIFICATION COMPLETE"

stop:
  - 두 에이전트 모두 최대 반복 도달 (각 5회)
  - 두 에이전트 모두 2회 연속 개선 없음
```

---

*figma-to-nextjs-pro.md v2.2.0에서 생성됨 | 최종 업데이트: 2026-01-23*
