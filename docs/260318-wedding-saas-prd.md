# 모바일 청첩장 SaaS - Product Requirements Document (PRD)

> Phase 1: Self-Serve MVP | 작성일: 2026-03-18
> 컨셉 문서: `docs/260316-wedding-invitation-saas-concept.md`

---

## 1. 제품 개요

### 1.1 비전

기존 개인 모바일 청첩장 프로젝트(`wedding-invitation`)의 인터랙티브 차별점을 SaaS로 확장하여, "무료 청첩장과는 차원이 다른" 프리미엄 모바일 청첩장 에디터를 제공한다.

### 1.2 확정 사항

| 항목 | 결정 |
|------|------|
| 가격 | 단일 4.9만원 (Build Free, Pay to Publish) |
| 기술스택 | Next.js + Vercel Pro + Supabase Pro + Cloudflare R2 + Gemini Flash |
| 전략 | A안 (프리미엄 인터랙티브 정액제) |
| 1차 타겟 | IT/개발자 커플 |
| 2차 타겟 | "특별한 청첩장" 원하는 2030 |

### 1.3 Phase 1 범위

Phase 1은 **블록 에디터로 셀프 제작 + 결제 후 퍼블리시**가 가능한 MVP다. AI 커스터마이징(크레딧 시스템)은 Phase 2로 이관한다.

---

## 2. 유저스토리 & 플로우

### 2.1 페르소나

**제작자 (신랑/신부)**
- 이름: 민수 & 지원
- 직업: 백엔드 개발자 & 프로덕트 디자이너
- 니즈: "바른손카드는 너무 평범하고, 직접 만들기엔 시간이 없다. 개발자 감성이 담긴 특별한 청첩장을 원한다."
- 행동: 결혼식 8-12주 전 청첩장 제작 시작, 모바일 우선

**방문자 (하객)**
- 이름: 영호 (30대 직장 동료)
- 니즈: 카카오톡에서 바로 열리고, 빠르고, 계좌번호 복사가 쉬운 청첩장
- 행동: 카카오톡 링크 클릭 -> 30초 내 핵심 정보 확인 -> 축의금 송금 -> RSVP

### 2.2 제작자(신랑/신부) 유저 저니

```
[1] 랜딩페이지 진입
    ├── 데모 청첩장 체험 (실제 인터랙션 확인)
    ├── 가격/기능 확인 (4.9만원 단일가)
    └── "무료로 만들어보기" CTA

[2] 회원가입/로그인
    ├── 소셜 로그인 (카카오 최우선, Google)
    └── 이메일 로그인 (Magic Link)

[3] 대시보드
    ├── "새 청첩장 만들기" 버튼
    └── 기존 청첩장 목록 (수정/미리보기/통계)

[4] 청첩장 제작 (블록 에디터)
    ├── 4a. 테마 선택 (botanical, modern, glitch)
    ├── 4b. 기본 정보 입력 (온보딩 위자드)
    │   ├── 커플 이름/영문명
    │   ├── 결혼식 날짜/시간
    │   ├── 예식장 정보 (주소 검색)
    │   ├── 인사말 (기본 템플릿 제공 + 직접 작성)
    │   └── 계좌 정보
    ├── 4c. 섹션 편집
    │   ├── 섹션 ON/OFF 토글
    │   ├── 섹션 순서 드래그앤드롭
    │   ├── 섹션별 콘텐츠 편집 (텍스트/이미지)
    │   └── 미리보기 (모바일/데스크탑)
    └── 4d. 미디어 업로드
        ├── Hero 이미지 (커플 사진)
        ├── 갤러리 사진 (최대 30장)
        └── BGM 선택 (제공 목록 or 직접 업로드)

[5] 미리보기 & 공유 설정
    ├── 실시간 미리보기 (실제 청첩장과 동일)
    ├── 슬러그 설정 (/invitation/{slug})
    └── OG 이미지 미리보기 (카카오톡 공유 시)

[6] 결제 (포트원)
    ├── 결제 수단 선택 (카카오페이 최우선)
    ├── 4.9만원 결제
    └── 결제 완료 → 공유 링크 활성화

[7] 공유 & 운영
    ├── 카카오톡/SMS/링크 공유
    ├── RSVP 현황 확인
    ├── 방명록 관리 (삭제/신고)
    └── 콘텐츠 수정 (결제 후에도 무제한)
```

### 2.3 방문자(하객) 유저 저니

```
[1] 카카오톡 링크 수신
    └── OG 미리보기 확인 → 탭

[2] 청첩장 로딩 (< 3초)
    ├── 테마별 인트로 애니메이션 (터미널/파티클 등)
    └── 앱 설치/로그인 없이 즉시 접근

[3] 콘텐츠 소비 (스크롤)
    ├── Hero → 인사말 → 커플소개 → (인터뷰) → 갤러리
    ├── 웨딩정보 → 위치(지도) → 계좌
    ├── 방명록 작성
    ├── RSVP 참석 여부 입력
    └── Guest Snap (결혼식 당일 사진 공유)

[4] 핵심 액션
    ├── 계좌번호 복사 (1-tap)
    ├── 카카오페이/토스 송금 연동
    ├── 네이버/카카오 지도 연동
    ├── 캘린더 추가 (Google/Apple)
    └── 친구에게 공유
```

### 2.4 핵심 유저스토리 (INVEST 기준)

| ID | 유저스토리 | 우선순위 | 스토리 포인트 |
|----|-----------|----------|--------------|
| US-01 | 제작자로서 소셜 로그인으로 가입하여 빠르게 시작할 수 있다 | Must | 3 |
| US-02 | 제작자로서 테마를 선택하고 기본 정보를 입력하여 청첩장 초안을 생성할 수 있다 | Must | 8 |
| US-03 | 제작자로서 섹션을 ON/OFF하고 순서를 변경할 수 있다 | Must | 5 |
| US-04 | 제작자로서 각 섹션의 텍스트와 이미지를 편집할 수 있다 | Must | 8 |
| US-05 | 제작자로서 갤러리에 사진을 업로드하고 순서를 조정할 수 있다 | Must | 5 |
| US-06 | 제작자로서 실시간 미리보기로 최종 결과를 확인할 수 있다 | Must | 5 |
| US-07 | 제작자로서 결제(4.9만원) 후 공유 링크를 발행할 수 있다 | Must | 8 |
| US-08 | 제작자로서 카카오톡/SMS로 청첩장을 공유할 수 있다 | Must | 3 |
| US-09 | 제작자로서 RSVP 현황을 대시보드에서 확인할 수 있다 | Must | 3 |
| US-10 | 제작자로서 결제 후에도 콘텐츠를 수정할 수 있다 | Must | 2 |
| US-11 | 하객으로서 앱 설치 없이 카카오톡 링크로 청첩장을 볼 수 있다 | Must | 0 (기본) |
| US-12 | 하객으로서 계좌번호를 1-tap으로 복사할 수 있다 | Must | 1 |
| US-13 | 하객으로서 방명록을 작성하고 실시간으로 확인할 수 있다 | Must | 5 |
| US-14 | 하객으로서 RSVP(참석 여부 + 식사)를 입력할 수 있다 | Must | 3 |
| US-15 | 하객으로서 결혼식 당일 Guest Snap으로 사진을 공유할 수 있다 | Should | 8 |
| US-16 | 제작자로서 커스텀 슬러그를 설정할 수 있다 | Should | 2 |
| US-17 | 제작자로서 BGM을 선택하거나 업로드할 수 있다 | Should | 3 |
| US-18 | 하객으로서 캘린더에 일정을 추가할 수 있다 | Should | 2 |

---

## 3. 기능 스펙 (MoSCoW)

### 3.1 Must Have (MVP 필수)

#### 인증/계정
- 카카오 소셜 로그인
- Google 소셜 로그인
- Magic Link 이메일 로그인
- 로그인 세션 관리 (Supabase Auth)

#### 블록 에디터
- 테마 선택 (3종: botanical, modern, glitch)
- 온보딩 위자드 (커플정보, 예식정보, 인사말, 계좌)
- 13개 섹션 ON/OFF 토글
- 섹션 순서 드래그앤드롭 (dnd-kit)
- 텍스트 내용 입력 폼 (constants.ts의 WEDDING_INFO에 해당하는 필드들)
- 이미지 업로드/교체 (Hero, 갤러리, 커플 사진)
- 실시간 미리보기 (모바일 프레임)

> **Note**: 섹션 내부 레이아웃 편집(텍스트/이미지 자유 배치), 블록 내부 스타일 커스터마이징, AI 커스터마이징(크레딧 시스템)은 Phase 2로 이동.
> 15개 섹션 4,864줄의 하드코딩된 JSX를 데이터 드리븐으로 전환하는 것은 사실상 렌더링 엔진 개발이며, 1인 6-8주에 멀티테넌트+에디터+결제 전부는 비현실적.

#### 청첩장 뷰어 (하객용)
- 슬러그 기반 라우팅 (`/invitation/{slug}`)
- 기존 15개 섹션 컴포넌트 멀티테넌트 대응
  - Hero, Greeting, CoupleIntro, Interview, Video, Gallery, Timeline, WeddingInfo, Location, Account, RSVP, Guestbook, GuestSnap, Share, Footer
- 반응형 (모바일 우선)
- 테마별 스타일링 (CSS Variables)
- 파티클 이펙트 (선택적 ON/OFF)
- 계좌번호 복사
- 네이버/카카오 지도 연동
- 카카오톡 공유 (동적 OG 이미지)

#### 방명록
- Supabase Realtime 실시간 구독
- 작성/삭제 (비밀번호 기반)
- 마스터 비밀번호 (제작자용)

> **Realtime 동시 접속 대응**
>
> Supabase Pro Realtime 한도: 500 concurrent connections.
> 결혼 시즌 동일 날 다수 청첩장 피크 시 한도 초과 가능.
>
> 대안:
> - Option A: 방명록을 polling 방식(30초 간격)으로 변경 — connection 부담 대폭 감소
> - Option B: 결혼식 당일 이후에는 Realtime 연결 해제
> - Option C: Supabase Team 플랜 업그레이드 (월 $599, 필요 시)
>
> **Phase 1 MVP: Option A (polling) 권장** — 실시간성은 약간 줄지만 안정성 확보

#### RSVP
- 참석 여부 + 동행 인원 + 식사 선택
- 제작자 대시보드 집계

#### 결제
- 포트원 V2 연동
- 카카오페이 간편결제 (최우선)
- 카드 결제
- 결제 완료 시 공유 링크 활성화
- 결제 웹훅 처리
- 환불 처리 (관리자)

#### 대시보드 (제작자)
- 청첩장 목록 (상태: 편집중/결제완료/공유중)
- RSVP 현황
- 콘텐츠 수정
- 공유 링크 복사

#### 인프라
- 멀티테넌트 동적 라우팅
- 이미지 최적화 (Next.js Image + Supabase Storage)
- CDN 캐싱 (Vercel Edge)
- 동적 OG 이미지 생성 (`@vercel/og`)

### 3.2 Should Have (MVP 포함 권장)

| 기능 | 설명 | 근거 |
|------|------|------|
| Guest Snap | 결혼식 당일 하객 사진 업로드 (R2) | 핵심 차별점, 기존 구현 활용 |
| BGM 시스템 | 제공 목록 선택 + 직접 업로드 | UX 완성도 |
| 커스텀 슬러그 | 사용자가 URL 경로 지정 | 개인화 |
| 캘린더 추가 | Google/Apple Calendar .ics | 하객 편의 |
| 이스터에그 | 아케이드 게임, 글리치 테마 | IT 타겟 차별점 |
| SMS 공유 | SMS로 청첩장 링크 발송 | 카카오톡 미사용자 대응 |
| 어드민 패널 | 전체 주문/고객/매출 관리 | 운영 필수 |

### 3.3 Could Have (Phase 2 이후)

| 기능 | Phase | 설명 |
|------|-------|------|
| AI 커스터마이징 | 2 | Gemini Flash 기반, 크레딧 시스템 (Phase 1에서 이동) |
| AI 이미지 생성 | 2 | 배경/일러스트 생성 |
| 섹션 내부 레이아웃 편집 | 2 | 텍스트/이미지 자유 배치 — 렌더링 엔진 개발 필요 (Phase 1에서 이동) |
| 블록 내부 스타일 커스터마이징 | 2 | 섹션별 폰트/색상/간격 커스터마이징 (Phase 1에서 이동) |
| 분석 대시보드 | 2 | 방문자 수, 공유 통계, UTM |
| 테마 추가 (5-10개) | 2 | 테마 마켓 |
| 카카오톡 알림 연동 | 2 | RSVP 알림, 방명록 알림 |
| 보이스오버 | 2 | 신랑신부 음성 메시지 |
| 커스텀 도메인 연결 | 2 | 1,900원 애드온 |
| A/B 가격 테스트 | 2 | 전환율 최적화 |

### 3.4 Won't Have (제외)

| 기능 | 이유 |
|------|------|
| 종이 청첩장 인쇄 | 사업 범위 밖 |
| 벤더 마켓플레이스 | Phase 3 (B안 전환 시) |
| B2B 화이트라벨 | Phase 3 (C안 전환 시) |
| 다국어 지원 | Phase 3 |
| 앱 (iOS/Android) | 웹 우선, 앱 불필요 |
| 축의금 수수료 | 0원 유지 (수익은 청첩장 판매) |
| 구독 모델 | 1회 결제만 |

---

## 4. 데이터 모델

### 4.1 ER 다이어그램 (논리)

```
users ──1:N──> invitations ──1:N──> sections
                    │                    │
                    ├──1:N──> media       │
                    ├──1:N──> rsvps       │
                    ├──1:N──> guestbook_entries
                    ├──1:1──> payments    │
                    └──1:N──> guestsnap_sessions ──1:N──> guestsnap_files
```

### 4.2 Supabase PostgreSQL 스키마

#### `users` (Supabase Auth 확장)

```sql
-- Supabase Auth의 auth.users를 확장하는 프로필 테이블
CREATE TABLE public.profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  display_name TEXT,
  email TEXT,
  avatar_url TEXT,
  provider TEXT, -- 'kakao' | 'google' | 'email'
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 새 유저 생성 시 자동으로 프로필 생성
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, display_name, email, provider)
  VALUES (
    NEW.id,
    COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'name'),
    NEW.email,
    NEW.raw_app_meta_data->>'provider'
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
```

#### `invitations` (청첩장 메인)

```sql
CREATE TYPE invitation_status AS ENUM ('draft', 'paid', 'published', 'expired');

CREATE TABLE public.invitations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,

  -- 슬러그 & 상태
  slug TEXT NOT NULL UNIQUE,
  status invitation_status NOT NULL DEFAULT 'draft',
  theme TEXT NOT NULL DEFAULT 'botanical', -- 'botanical' | 'modern' | 'glitch'

  -- 신랑 정보
  groom_name TEXT NOT NULL,
  groom_english_name TEXT,
  groom_phone TEXT,
  groom_father TEXT,
  groom_mother TEXT,
  groom_father_deceased BOOLEAN DEFAULT false,
  groom_mother_deceased BOOLEAN DEFAULT false,

  -- 신부 정보
  bride_name TEXT NOT NULL,
  bride_english_name TEXT,
  bride_phone TEXT,
  bride_father TEXT,
  bride_mother TEXT,
  bride_father_deceased BOOLEAN DEFAULT false,
  bride_mother_deceased BOOLEAN DEFAULT false,

  -- 결혼식 정보
  wedding_date TIMESTAMPTZ NOT NULL,
  wedding_date_display JSONB NOT NULL,
  -- { year, month, day, dayOfWeek, time, timeDetail }

  -- 예식장 정보
  venue_name TEXT NOT NULL,
  venue_hall TEXT,
  venue_address TEXT NOT NULL,
  venue_tel TEXT,
  venue_coordinates JSONB, -- { lat, lng }
  venue_navigation JSONB, -- { naver, kakao, tmap }
  venue_parking TEXT,
  venue_subway TEXT,
  venue_bus TEXT,

  -- 셔틀버스
  shuttle JSONB, -- { available, routes: [...] }

  -- 인사말
  greeting_title TEXT DEFAULT '소중한 분들을 초대합니다',
  greeting_message TEXT,

  -- 인터뷰
  interview JSONB, -- [{ question, groomAnswer, brideAnswer }]

  -- 타임라인
  timeline JSONB, -- [{ date, title, description, icon }]

  -- 계좌 정보
  accounts JSONB NOT NULL,
  -- { groom: { bank, number, holder }, groomFather: {...}, groomMother: {...},
  --   bride: { bank, number, holder }, brideFather: {...}, brideMother: {...} }

  -- 미디어 참조
  hero_image_groom TEXT, -- Storage path
  hero_image_bride TEXT,
  hero_image_couple TEXT,
  video_youtube_id TEXT,
  video_enabled BOOLEAN DEFAULT false,

  -- BGM
  music_enabled BOOLEAN DEFAULT true,
  music_src TEXT, -- Storage path or preset key
  music_title TEXT,
  music_artist TEXT,

  -- 기능 토글
  rsvp_enabled BOOLEAN DEFAULT true,
  guestbook_enabled BOOLEAN DEFAULT true,
  guestsnap_enabled BOOLEAN DEFAULT true,
  particle_enabled BOOLEAN DEFAULT true,
  intro_enabled BOOLEAN DEFAULT true,
  easter_egg_enabled BOOLEAN DEFAULT false,

  -- OG 메타
  og_title TEXT,
  og_description TEXT,
  og_image TEXT, -- 생성된 OG 이미지 경로

  -- 메타데이터
  published_at TIMESTAMPTZ,
  expires_at TIMESTAMPTZ, -- 결혼식 6개월 후 자동 만료
  view_count INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 인덱스
CREATE INDEX idx_invitations_user_id ON public.invitations(user_id);
CREATE INDEX idx_invitations_slug ON public.invitations(slug);
CREATE INDEX idx_invitations_status ON public.invitations(status);
```

#### `sections` (섹션 순서/설정)

```sql
CREATE TABLE public.sections (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  invitation_id UUID NOT NULL REFERENCES public.invitations(id) ON DELETE CASCADE,

  type TEXT NOT NULL,
  -- 'hero' | 'greeting' | 'couple_intro' | 'interview' | 'video' |
  -- 'gallery' | 'timeline' | 'wedding_info' | 'location' | 'account' |
  -- 'rsvp' | 'guestbook' | 'guestsnap' | 'share' | 'footer'

  sort_order INTEGER NOT NULL,
  enabled BOOLEAN NOT NULL DEFAULT true,
  config JSONB DEFAULT '{}', -- 섹션별 추가 설정 (Phase 2 블록 내부 레이아웃용)

  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

  UNIQUE(invitation_id, type)
);

CREATE INDEX idx_sections_invitation ON public.sections(invitation_id, sort_order);
```

> **JSON 스키마 버전 관리**: 블록 데이터 JSON에 `version` 필드를 포함한다.
> ```json
> { "version": 1, "sections": [...] }
> ```
> 향후 스키마 변경 시 마이그레이션 함수로 하위 호환을 보장한다.

#### `media` (이미지/영상/음악)

```sql
CREATE TYPE media_type AS ENUM ('hero', 'gallery', 'bgm', 'og_image');
CREATE TYPE storage_provider AS ENUM ('supabase', 'r2');

CREATE TABLE public.media (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  invitation_id UUID NOT NULL REFERENCES public.invitations(id) ON DELETE CASCADE,

  type media_type NOT NULL,
  storage_provider storage_provider NOT NULL DEFAULT 'supabase',
  storage_path TEXT NOT NULL, -- Supabase Storage 또는 R2 key
  original_filename TEXT,
  mime_type TEXT NOT NULL,
  file_size BIGINT, -- bytes
  width INTEGER,
  height INTEGER,
  sort_order INTEGER DEFAULT 0, -- 갤러리 순서

  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_media_invitation ON public.media(invitation_id, type, sort_order);
```

#### `rsvps` (참석 여부)

```sql
CREATE TYPE attendance_status AS ENUM ('attending', 'not_attending', 'maybe');
CREATE TYPE meal_type AS ENUM ('adult', 'child', 'none');

CREATE TABLE public.rsvps (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  invitation_id UUID NOT NULL REFERENCES public.invitations(id) ON DELETE CASCADE,

  name TEXT NOT NULL,
  phone TEXT,
  attendance attendance_status NOT NULL,
  party_size INTEGER DEFAULT 1, -- 동행 인원 (본인 포함)
  meal meal_type DEFAULT 'adult',
  message TEXT, -- 한마디

  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_rsvps_invitation ON public.rsvps(invitation_id);
```

#### `guestbook_entries` (방명록)

```sql
CREATE TABLE public.guestbook_entries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  invitation_id UUID NOT NULL REFERENCES public.invitations(id) ON DELETE CASCADE,

  author_name TEXT NOT NULL,
  content TEXT NOT NULL,
  password_hash TEXT NOT NULL, -- bcrypt 해시
  is_hidden BOOLEAN DEFAULT false, -- 제작자가 숨김 처리

  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_guestbook_invitation ON public.guestbook_entries(invitation_id, created_at DESC);
```

#### `payments` (결제)

```sql
CREATE TYPE payment_status AS ENUM (
  'pending', 'paid', 'failed', 'cancelled', 'refunded', 'partial_refunded'
);

CREATE TABLE public.payments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  invitation_id UUID NOT NULL REFERENCES public.invitations(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES public.profiles(id),

  -- 포트원 연동
  portone_payment_id TEXT UNIQUE, -- 포트원 결제 ID
  portone_tx_id TEXT, -- 포트원 트랜잭션 ID

  amount INTEGER NOT NULL DEFAULT 49000, -- 원
  currency TEXT NOT NULL DEFAULT 'KRW',
  status payment_status NOT NULL DEFAULT 'pending',
  method TEXT, -- 'kakaopay' | 'card' | 'transfer'

  paid_at TIMESTAMPTZ,
  refunded_at TIMESTAMPTZ,
  refund_amount INTEGER DEFAULT 0,
  refund_reason TEXT,

  -- 영수증/세금계산서
  receipt_url TEXT,

  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_payments_invitation ON public.payments(invitation_id);
CREATE INDEX idx_payments_portone ON public.payments(portone_payment_id);
```

#### `guestsnap_sessions` & `guestsnap_files` (Guest Snap)

```sql
CREATE TABLE public.guestsnap_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  invitation_id UUID NOT NULL REFERENCES public.invitations(id) ON DELETE CASCADE,

  guest_name TEXT NOT NULL,
  session_token TEXT NOT NULL UNIQUE,
  ip_address INET,
  user_agent TEXT,

  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TYPE guestsnap_file_status AS ENUM ('uploading', 'completed', 'failed');

CREATE TABLE public.guestsnap_files (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID NOT NULL REFERENCES public.guestsnap_sessions(id) ON DELETE CASCADE,
  invitation_id UUID NOT NULL REFERENCES public.invitations(id) ON DELETE CASCADE,

  r2_key TEXT NOT NULL, -- Cloudflare R2 object key
  original_filename TEXT NOT NULL,
  mime_type TEXT NOT NULL,
  file_size BIGINT NOT NULL,
  status guestsnap_file_status NOT NULL DEFAULT 'uploading',

  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_guestsnap_sessions_invitation ON public.guestsnap_sessions(invitation_id);
CREATE INDEX idx_guestsnap_files_session ON public.guestsnap_files(session_id);
```

### 4.3 RLS (Row Level Security) 정책

```sql
-- 모든 테이블에 RLS 활성화
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.invitations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sections ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.media ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.rsvps ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.guestbook_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.guestsnap_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.guestsnap_files ENABLE ROW LEVEL SECURITY;

-- profiles: 본인만 읽기/수정
CREATE POLICY "profiles_select_own" ON public.profiles
  FOR SELECT USING (auth.uid() = id);
CREATE POLICY "profiles_update_own" ON public.profiles
  FOR UPDATE USING (auth.uid() = id);

-- invitations: 소유자 CRUD + 공개된 청첩장은 누구나 읽기
CREATE POLICY "invitations_owner_all" ON public.invitations
  FOR ALL USING (auth.uid() = user_id);
CREATE POLICY "invitations_published_select" ON public.invitations
  FOR SELECT USING (status = 'published');

-- sections: 초대장 소유자 CRUD + 공개 청첩장은 읽기
CREATE POLICY "sections_owner_all" ON public.sections
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM public.invitations
      WHERE id = sections.invitation_id AND user_id = auth.uid()
    )
  );
CREATE POLICY "sections_published_select" ON public.sections
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.invitations
      WHERE id = sections.invitation_id AND status = 'published'
    )
  );

-- media: 초대장 소유자 CRUD + 공개 읽기
CREATE POLICY "media_owner_all" ON public.media
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM public.invitations
      WHERE id = media.invitation_id AND user_id = auth.uid()
    )
  );
CREATE POLICY "media_published_select" ON public.media
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.invitations
      WHERE id = media.invitation_id AND status = 'published'
    )
  );

-- rsvps: 누구나 작성(INSERT) + 초대장 소유자만 읽기
CREATE POLICY "rsvps_insert_anon" ON public.rsvps
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.invitations
      WHERE id = rsvps.invitation_id AND status = 'published'
    )
  );
CREATE POLICY "rsvps_owner_select" ON public.rsvps
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.invitations
      WHERE id = rsvps.invitation_id AND user_id = auth.uid()
    )
  );

-- guestbook_entries: 공개 읽기/작성 + 소유자 숨김 처리
CREATE POLICY "guestbook_published_select" ON public.guestbook_entries
  FOR SELECT USING (
    is_hidden = false AND
    EXISTS (
      SELECT 1 FROM public.invitations
      WHERE id = guestbook_entries.invitation_id AND status = 'published'
    )
  );
CREATE POLICY "guestbook_insert_anon" ON public.guestbook_entries
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.invitations
      WHERE id = guestbook_entries.invitation_id AND status = 'published'
    )
  );
CREATE POLICY "guestbook_owner_all" ON public.guestbook_entries
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM public.invitations
      WHERE id = guestbook_entries.invitation_id AND user_id = auth.uid()
    )
  );

-- payments: 소유자만 읽기 (생성은 Server Action에서)
CREATE POLICY "payments_owner_select" ON public.payments
  FOR SELECT USING (auth.uid() = user_id);

-- guestsnap_sessions/files: 서버에서만 생성, 공개 읽기 없음
CREATE POLICY "guestsnap_sessions_service" ON public.guestsnap_sessions
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM public.invitations
      WHERE id = guestsnap_sessions.invitation_id AND user_id = auth.uid()
    )
  );
CREATE POLICY "guestsnap_files_service" ON public.guestsnap_files
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM public.invitations
      WHERE id = guestsnap_files.invitation_id AND user_id = auth.uid()
    )
  );
```

### 4.4 Storage Buckets

```sql
-- Supabase Storage 버킷 설정

-- 1. 갤러리/Hero 이미지 (제작자 업로드)
-- Bucket: invitation-media
-- Path: {invitation_id}/hero/*, {invitation_id}/gallery/*, {invitation_id}/bgm/*
-- RLS: 소유자 업로드, 공개 읽기 (published)

-- 2. OG 이미지 (서버 생성)
-- Bucket: og-images
-- Path: {invitation_id}/og.png
-- RLS: 서비스 롤 생성, 공개 읽기

-- 3. Guest Snap → Cloudflare R2 (별도)
-- Bucket: guestsnap
-- Path: {invitation_id}/{session_id}/{filename}
```

---

## 5. API 설계

### 5.1 아키텍처 원칙

- **Server Actions** (Next.js): 인증된 사용자의 데이터 변경 (CRUD)
- **API Routes** (`/api/*`): 웹훅, 비인증 엔드포인트 (RSVP, 방명록, Guest Snap)
- **서버 컴포넌트**: 데이터 읽기 (RSC로 직접 Supabase 쿼리)

### 5.2 인증/인가 흐름

```
[소셜 로그인 (카카오/Google)]
    │
    ├── Supabase Auth signInWithOAuth()
    │   ├── Provider redirect → callback
    │   └── JWT 발급 (access_token + refresh_token)
    │
    ├── 쿠키 기반 세션 관리
    │   ├── @supabase/ssr createServerClient
    │   └── proxy.ts에서 세션 갱신
    │
    └── RLS가 데이터 접근 제어
        ├── auth.uid() = user_id → 본인 데이터
        └── status = 'published' → 공개 데이터

[Magic Link (이메일)]
    │
    ├── Supabase Auth signInWithOtp({ email })
    │   └── 이메일로 Magic Link 발송
    │
    └── 링크 클릭 → 토큰 교환 → JWT 발급
```

### 5.3 Server Actions

```typescript
// --- 청첩장 CRUD ---

// 청첩장 생성 (온보딩 위자드 완료 시)
'use server'
async function createInvitation(data: CreateInvitationInput): Promise<Invitation>
// 1. auth.uid() 확인
// 2. 슬러그 유니크 검증
// 3. invitations INSERT
// 4. 기본 sections 15개 INSERT (기본 순서, 전부 enabled)
// 5. 청첩장 ID 반환

// 청첩장 수정
async function updateInvitation(id: string, data: Partial<InvitationInput>): Promise<void>
// RLS가 소유권 검증

// 청첩장 삭제
async function deleteInvitation(id: string): Promise<void>
// CASCADE로 관련 데이터 자동 삭제

// --- 섹션 관리 ---

// 섹션 순서/활성화 변경
async function updateSections(
  invitationId: string,
  sections: { id: string; sort_order: number; enabled: boolean }[]
): Promise<void>

// --- 미디어 ---

// 이미지 업로드 (Presigned URL 방식)
async function getUploadUrl(
  invitationId: string,
  fileType: MediaType,
  mimeType: string
): Promise<{ uploadUrl: string; storagePath: string }>

// 업로드 완료 확인 + media 레코드 생성
async function confirmUpload(
  invitationId: string,
  storagePath: string,
  metadata: MediaMetadata
): Promise<Media>

// 미디어 삭제
async function deleteMedia(mediaId: string): Promise<void>

// 갤러리 순서 변경
async function reorderGallery(
  invitationId: string,
  mediaIds: string[]
): Promise<void>

// --- 결제 ---

// 결제 시작 (포트원 결제 요청 생성)
async function initiatePayment(invitationId: string): Promise<{
  paymentId: string
  merchantId: string
  amount: number
}>

// 결제 검증 (클라이언트에서 결제 완료 후)
async function verifyPayment(
  invitationId: string,
  portonePaymentId: string
): Promise<{ success: boolean }>
// 1. 포트원 API로 결제 상태 조회
// 2. 금액 검증 (49,000원)
// 3. payments UPDATE (status = 'paid')
// 4. invitations UPDATE (status = 'paid')

// --- 퍼블리시 ---

// 공유 링크 발행
async function publishInvitation(invitationId: string): Promise<{
  url: string
  slug: string
}>
// 1. 결제 완료 확인
// 2. invitations UPDATE (status = 'published', published_at = now())
// 3. OG 이미지 생성
// 4. 공유 URL 반환

// 슬러그 변경
async function updateSlug(
  invitationId: string,
  newSlug: string
): Promise<void>
// 유니크 검증 필수
```

### 5.4 API Routes

```typescript
// --- 비인증 엔드포인트 (하객용) ---

// RSVP 제출
POST /api/invitation/{slug}/rsvp
Body: { name, phone?, attendance, partySize, meal, message? }
Response: { success: true }
// Rate limit: IP 기반 10req/min

// 방명록 작성
POST /api/invitation/{slug}/guestbook
Body: { authorName, content, password }
Response: { id, authorName, content, createdAt }
// password → bcrypt 해시 저장

// 방명록 삭제
DELETE /api/invitation/{slug}/guestbook/{id}
Body: { password }
// 비밀번호 검증 또는 마스터 비밀번호

// 방명록 목록 (Supabase Realtime 대신 초기 로드용)
GET /api/invitation/{slug}/guestbook
Response: { entries: [...], total: number }

// --- Guest Snap (R2 연동) ---

// 세션 생성
POST /api/invitation/{slug}/guestsnap/session
Body: { guestName }
Response: { sessionToken, expiresAt }
// Rate limit: IP 기반 5req/min

// 업로드 URL 발급 (R2 Presigned URL)
POST /api/invitation/{slug}/guestsnap/upload
Headers: { X-Session-Token }
Body: { filename, mimeType, fileSize }
Response: { uploadUrl, r2Key }
// Magic byte 검증은 클라이언트에서 수행

// 업로드 완료 알림
POST /api/invitation/{slug}/guestsnap/complete
Headers: { X-Session-Token }
Body: { r2Key }
Response: { success: true }

// --- 결제 웹훅 ---

// 포트원 웹훅
POST /api/webhooks/portone
Headers: { x-portone-signature }
Body: PortoneWebhookPayload
// 1. 시그니처 검증
// 2. 결제 상태 업데이트
// 3. 결제 완료 시 invitation status 변경

// --- 동적 OG 이미지 ---

GET /api/og/{slug}
Response: PNG image (1200x630)
// @vercel/og 기반 동적 생성
// 커플 이름, 날짜, 테마별 디자인
```

### 5.5 결제 (포트원) 연동 흐름

```
[클라이언트]                    [서버]                      [포트원]
    │                            │                            │
    │ 1. "결제하기" 클릭          │                            │
    ├──initiatePayment()────────>│                            │
    │                            ├─ payments INSERT (pending) │
    │<───── paymentId ──────────┤                            │
    │                            │                            │
    │ 2. 포트원 SDK 결제창 호출   │                            │
    ├─────────────────────────────────────────────────────────>│
    │                            │                            │
    │ 3. 결제 완료 콜백           │                            │
    │<─────────────────────────────── portonePaymentId ───────┤
    │                            │                            │
    │ 4. 결제 검증 요청           │                            │
    ├──verifyPayment()──────────>│                            │
    │                            ├─── GET /payments/{id} ────>│
    │                            │<── 결제 상태 + 금액 ────────┤
    │                            │                            │
    │                            ├─ 금액 49,000원 검증         │
    │                            ├─ payments UPDATE (paid)     │
    │                            ├─ invitations UPDATE (paid)  │
    │                            │                            │
    │<── { success: true } ──────┤                            │
    │                            │                            │
    │ [동시] 웹훅도 수신          │                            │
    │                            │<── POST /api/webhooks ─────┤
    │                            ├─ 중복 방지 (이미 paid면 무시)│
    │                            │                            │

[환불 플로우]
    │ 관리자 환불 처리            │                            │
    │                            ├─── POST /payments/cancel ──>│
    │                            │<── 취소 결과 ──────────────┤
    │                            ├─ payments UPDATE (refunded) │
    │                            ├─ invitations UPDATE (draft) │
```

### 5.6 포트원 V2 통합 코드 구조

```typescript
// lib/portone.ts
import PortOne from "@portone/server-sdk";

const portone = PortOne.PortOneClient({
  secret: process.env.PORTONE_API_SECRET!,
});

// 결제 검증
export async function verifyPortonePayment(paymentId: string) {
  const payment = await portone.payment.getPayment({ paymentId });

  if (payment.status !== "PAID") {
    throw new Error(`Payment not completed: ${payment.status}`);
  }

  if (payment.amount.total !== 49000) {
    throw new Error(`Invalid amount: ${payment.amount.total}`);
  }

  return payment;
}

// 결제 취소 (환불)
export async function cancelPortonePayment(
  paymentId: string,
  reason: string,
  amount?: number // partial refund
) {
  return portone.payment.cancelPayment({
    paymentId,
    reason,
    amount: amount ? { total: amount } : undefined,
  });
}
```

---

## 6. 블록 에디터 아키텍처

### 6.1 블록 타입 정의

```typescript
// types/editor.ts

// 섹션 블록 타입 (기존 15개 섹션 기반)
type SectionType =
  | 'hero'
  | 'greeting'
  | 'couple_intro'
  | 'interview'
  | 'video'
  | 'gallery'
  | 'timeline'
  | 'wedding_info'
  | 'location'
  | 'account'
  | 'rsvp'
  | 'guestbook'
  | 'guestsnap'
  | 'share'
  | 'footer';

// 섹션 블록 인터페이스
interface SectionBlock {
  id: string;
  type: SectionType;
  sortOrder: number;
  enabled: boolean;
  config: SectionConfig;
}

// 섹션별 설정 (Phase 1: 기본 ON/OFF + 순서만)
interface SectionConfig {
  // Phase 1: 공통
  // (향후 Phase 2에서 섹션 내부 레이아웃 설정 추가)
}

// 테마
type ThemeId = 'botanical' | 'modern' | 'glitch';

interface Theme {
  id: ThemeId;
  name: string;
  description: string;
  preview: string; // 미리보기 이미지
  colors: ThemeColors;
  fonts: ThemeFonts;
  features: ThemeFeatures;
}

interface ThemeColors {
  primary: string;
  primaryLight: string;
  primaryDark: string;
  secondary: string;
  accent: string;
  text: string;
  textLight: string;
  background: string;
  groom: string;
  bride: string;
}

interface ThemeFonts {
  heading: string;
  body: string;
}

interface ThemeFeatures {
  introAnimation: 'terminal' | 'fade' | 'glitch';
  particleType: 'cherry_blossom' | 'confetti' | 'glitch_pixel';
  hasEasterEgg: boolean;
  easterEggType?: 'arcade' | 'glitch';
}
```

### 6.2 드래그앤드롭 구조

```
┌────────────────────────────────────────────────────┐
│  블록 에디터 레이아웃                                │
├──────────────────────┬─────────────────────────────┤
│                      │                              │
│  [섹션 리스트]        │  [미리보기 패널]              │
│                      │                              │
│  ┌─────────────┐     │  ┌─────────────────────┐    │
│  │ ≡ Hero    ✓ │     │  │  ┌───────────────┐  │    │
│  ├─────────────┤     │  │  │ iPhone 프레임  │  │    │
│  │ ≡ 인사말  ✓ │     │  │  │               │  │    │
│  ├─────────────┤     │  │  │  실시간 렌더링  │  │    │
│  │ ≡ 커플소개 ✓│     │  │  │               │  │    │
│  ├─────────────┤     │  │  │               │  │    │
│  │ ≡ 인터뷰  ✓ │<-클릭│  │  └───────────────┘  │    │
│  ├─────────────┤     │  │                      │    │
│  │ ≡ 영상   ✗ │     │  │  [모바일] [데스크탑]   │    │
│  ├─────────────┤     │  └─────────────────────┘    │
│  │ ≡ 갤러리  ✓ │     │                              │
│  ├─────────────┤     │  ┌─────────────────────┐    │
│  │ ...         │     │  │  [섹션 상세 편집]     │    │
│  └─────────────┘     │  │                      │    │
│                      │  │  제목: [___________]  │    │
│  ✓ = 활성화          │  │  내용: [___________]  │    │
│  ✗ = 비활성화         │  │  이미지: [업로드]     │    │
│  ≡ = 드래그 핸들      │  │                      │    │
│                      │  └─────────────────────┘    │
│                      │                              │
└──────────────────────┴─────────────────────────────┘
```

**기술 스택**:
- `@dnd-kit/core` + `@dnd-kit/sortable`: 드래그앤드롭
- `zustand`: 에디터 상태 관리
- `iframe` or 동일 페이지 렌더링: 미리보기

### 6.3 에디터 상태 관리

```typescript
// stores/editor-store.ts
import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';

interface EditorState {
  // 현재 청첩장 데이터
  invitation: InvitationData | null;
  sections: SectionBlock[];
  theme: ThemeId;

  // UI 상태
  selectedSectionId: string | null;
  previewMode: 'mobile' | 'desktop';
  isDirty: boolean; // 미저장 변경 존재
  isSaving: boolean;

  // 액션
  setInvitation: (data: InvitationData) => void;
  updateField: <K extends keyof InvitationData>(
    field: K,
    value: InvitationData[K]
  ) => void;
  toggleSection: (sectionId: string) => void;
  reorderSections: (fromIndex: number, toIndex: number) => void;
  selectSection: (sectionId: string | null) => void;
  setTheme: (theme: ThemeId) => void;
  setPreviewMode: (mode: 'mobile' | 'desktop') => void;
  markSaved: () => void;
}

export const useEditorStore = create<EditorState>()(
  immer((set) => ({
    invitation: null,
    sections: [],
    theme: 'botanical',
    selectedSectionId: null,
    previewMode: 'mobile',
    isDirty: false,
    isSaving: false,

    setInvitation: (data) =>
      set((state) => {
        state.invitation = data;
        state.isDirty = false;
      }),

    updateField: (field, value) =>
      set((state) => {
        if (state.invitation) {
          (state.invitation as Record<string, unknown>)[field] = value;
          state.isDirty = true;
        }
      }),

    toggleSection: (sectionId) =>
      set((state) => {
        const section = state.sections.find((s) => s.id === sectionId);
        if (section) {
          section.enabled = !section.enabled;
          state.isDirty = true;
        }
      }),

    reorderSections: (fromIndex, toIndex) =>
      set((state) => {
        const [moved] = state.sections.splice(fromIndex, 1);
        state.sections.splice(toIndex, 0, moved);
        state.sections.forEach((s, i) => (s.sortOrder = i));
        state.isDirty = true;
      }),

    selectSection: (sectionId) =>
      set((state) => {
        state.selectedSectionId = sectionId;
      }),

    setTheme: (theme) =>
      set((state) => {
        state.theme = theme;
        state.isDirty = true;
      }),

    setPreviewMode: (mode) =>
      set((state) => {
        state.previewMode = mode;
      }),

    markSaved: () =>
      set((state) => {
        state.isDirty = false;
        state.isSaving = false;
      }),
  }))
);
```

### 6.4 테마 시스템 설계

```typescript
// lib/themes.ts

// 테마 레지스트리
const themes: Record<ThemeId, Theme> = {
  botanical: {
    id: 'botanical',
    name: 'Botanical Elegance',
    description: '자연 감성의 우아한 보태니컬 테마',
    preview: '/themes/botanical-preview.jpg',
    colors: {
      primary: '#43573a',
      primaryLight: '#5a6f50',
      primaryDark: '#2f3d29',
      secondary: '#faf8f5',
      accent: '#b7a989',
      text: '#3d3d3d',
      textLight: '#6b6b6b',
      background: '#f5f3ed',
      groom: '#5f8b9b',
      bride: '#BB7273',
    },
    fonts: {
      heading: 'Noto Serif KR',
      body: 'Pretendard',
    },
    features: {
      introAnimation: 'terminal',
      particleType: 'cherry_blossom',
      hasEasterEgg: true,
      easterEggType: 'arcade',
    },
  },

  modern: {
    id: 'modern',
    name: 'Modern Minimal',
    description: '깔끔하고 모던한 미니멀 테마',
    preview: '/themes/modern-preview.jpg',
    colors: {
      primary: '#1a1a2e',
      primaryLight: '#16213e',
      primaryDark: '#0f0f1a',
      secondary: '#ffffff',
      accent: '#e94560',
      text: '#1a1a2e',
      textLight: '#666666',
      background: '#f8f9fa',
      groom: '#4a90d9',
      bride: '#e94560',
    },
    fonts: {
      heading: 'Montserrat',
      body: 'Pretendard',
    },
    features: {
      introAnimation: 'fade',
      particleType: 'confetti',
      hasEasterEgg: false,
    },
  },

  glitch: {
    id: 'glitch',
    name: 'Glitch Cyberpunk',
    description: '개발자 감성 글리치 사이버펑크 테마',
    preview: '/themes/glitch-preview.jpg',
    colors: {
      primary: '#0a0a0a',
      primaryLight: '#1a1a1a',
      primaryDark: '#000000',
      secondary: '#0d1117',
      accent: '#00ff41',
      text: '#c9d1d9',
      textLight: '#8b949e',
      background: '#0d1117',
      groom: '#58a6ff',
      bride: '#f778ba',
    },
    fonts: {
      heading: 'JetBrains Mono',
      body: 'IBM Plex Mono',
    },
    features: {
      introAnimation: 'glitch',
      particleType: 'glitch_pixel',
      hasEasterEgg: true,
      easterEggType: 'glitch',
    },
  },
};

// CSS Variables로 테마 적용
export function getThemeCSSVariables(themeId: ThemeId): Record<string, string> {
  const theme = themes[themeId];
  return {
    '--color-primary': theme.colors.primary,
    '--color-primary-light': theme.colors.primaryLight,
    '--color-primary-dark': theme.colors.primaryDark,
    '--color-secondary': theme.colors.secondary,
    '--color-accent': theme.colors.accent,
    '--color-text': theme.colors.text,
    '--color-text-light': theme.colors.textLight,
    '--color-background': theme.colors.background,
    '--color-groom': theme.colors.groom,
    '--color-bride': theme.colors.bride,
    '--font-heading': theme.fonts.heading,
    '--font-body': theme.fonts.body,
  };
}
```

### 6.5 섹션 컴포넌트 멀티테넌트 전환

기존 `constants.ts` 의존성을 props 기반으로 전환하는 전략:

```typescript
// 기존 (Single Tenant)
import { WEDDING_INFO } from '@/lib/constants';
export function Greeting() {
  return <p>{WEDDING_INFO.greeting.message}</p>;
}

// 전환 후 (Multi Tenant)
interface GreetingProps {
  title: string;
  message: string;
  theme: ThemeId;
}
export function Greeting({ title, message, theme }: GreetingProps) {
  return <p>{message}</p>;
}

// 데이터 주입 (서버 컴포넌트)
// app/invitation/[slug]/page.tsx
export default async function InvitationPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const invitation = await getPublishedInvitation(slug);
  const sections = await getSections(invitation.id);

  return (
    <InvitationViewer
      invitation={invitation}
      sections={sections}
    />
  );
}
```

### 6.6 constants.ts 전환 전략 (점진적)

현재: 67개 파일, 274곳에서 `WEDDING_INFO` 직접 import

**1단계: WeddingDataProvider (React Context) 도입**
- 최상위에서 DB 데이터를 fetch → Context로 제공
- 기존 컴포넌트는 import 대신 `useWeddingData()` 훅 사용

**2단계: 점진적 컴포넌트 전환**
- 한 번에 전체 교체하지 않고, 섹션별로 Context 기반으로 전환
- 전환되지 않은 컴포넌트는 Context에서 fallback으로 기존 constants 사용

**3단계: constants.ts 제거**
- 모든 컴포넌트 전환 완료 후 constants.ts 삭제

---

## 7. 인프라 아키텍처

### 7.1 시스템 아키텍처 다이어그램

```
                    ┌──────────────────────────────────────┐
                    │           Vercel (Pro)                │
                    │                                       │
  [카카오톡]        │  ┌─────────────┐  ┌───────────────┐  │
  [브라우저] ────>  │  │ Next.js App │  │ Edge Middleware│  │
                    │  │             │  │ (Auth/Slug)    │  │
                    │  │ - SSR/RSC   │  └───────────────┘  │
                    │  │ - API Routes│                      │
                    │  │ - Server    │  ┌───────────────┐  │
                    │  │   Actions   │  │ @vercel/og    │  │
                    │  │             │  │ (OG Image Gen)│  │
                    │  └──────┬──────┘  └───────────────┘  │
                    │         │                             │
                    └─────────┼─────────────────────────────┘
                              │
              ┌───────────────┼────────────────┐
              │               │                │
              v               v                v
    ┌─────────────────┐ ┌──────────┐  ┌──────────────────┐
    │  Supabase (Pro)  │ │ Portone  │  │ Cloudflare R2    │
    │                  │ │  (PG)    │  │                  │
    │ - PostgreSQL     │ │          │  │ - Guest Snap     │
    │ - Auth (Kakao/   │ │ - 카카오  │  │   사진/영상      │
    │   Google/Email)  │ │   페이    │  │ - Egress 무료    │
    │ - Realtime       │ │ - 카드    │  │ - Presigned URL  │
    │   (방명록)       │ │          │  │                  │
    │ - Storage        │ │ - Webhook │  │                  │
    │   (갤러리/Hero/  │ └──────────┘  └──────────────────┘
    │    BGM/OG)       │
    │ - RLS            │
    └──────────────────┘
```

### 7.2 멀티테넌트 라우팅

```
URL 구조:
  https://domain.com/invitation/{slug}

라우팅 플로우:
  1. Edge Middleware
     ├── /invitation/{slug} 요청 감지
     ├── slug 유효성 검증 (DB 조회 캐시)
     └── 존재하지 않는 slug → 404 페이지

  2. Next.js Dynamic Route
     ├── app/invitation/[slug]/page.tsx (서버 컴포넌트)
     ├── generateMetadata() → 동적 OG 태그
     └── 청첩장 데이터 조회 + 렌더링

  3. 에디터 라우팅 (인증 필요)
     ├── app/dashboard/page.tsx → 청첩장 목록
     ├── app/editor/[id]/page.tsx → 블록 에디터
     └── app/editor/[id]/preview/page.tsx → 미리보기
```

```typescript
// proxy.ts
import { createServerClient } from '@supabase/ssr';
import { NextResponse, type NextRequest } from 'next/server';

export async function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // 인증 필요 경로
  if (pathname.startsWith('/dashboard') || pathname.startsWith('/editor')) {
    const supabase = createServerClient(/* ... */);
    const { data: { user } } = await supabase.auth.getUser();

    if (!user) {
      return NextResponse.redirect(new URL('/login', request.url));
    }
  }

  // 세션 갱신
  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/editor/:path*'],
};
```

### 7.3 CDN / 캐싱 전략

```
┌───────────────────────────────────────────────────────────┐
│                    캐싱 레이어                              │
├───────────────────────────────────────────────────────────┤
│                                                            │
│  Layer 1: Vercel Edge Cache                                │
│  ├── 정적 에셋 (JS/CSS/이미지): immutable, 1년             │
│  ├── 청첩장 페이지: ISR (revalidate: 60)                   │
│  │   └── 제작자가 수정 시 on-demand revalidation           │
│  └── OG 이미지: stale-while-revalidate: 86400             │
│                                                            │
│  Layer 2: Supabase Storage CDN                             │
│  ├── 갤러리/Hero 이미지: public bucket, CDN 자동           │
│  └── 이미지 변환: Supabase Image Transformation            │
│      (리사이즈, WebP 변환, 품질 조절)                       │
│                                                            │
│  Layer 3: Cloudflare R2                                    │
│  ├── Guest Snap 파일: 직접 접근 차단 (Presigned URL only)  │
│  └── Egress 비용 0원                                       │
│                                                            │
│  Layer 4: Browser Cache                                    │
│  ├── Service Worker: 오프라인 Guest Snap 큐                │
│  └── LocalStorage: 에디터 자동저장 (임시)                   │
│                                                            │
└───────────────────────────────────────────────────────────┘
```

### 7.4 ISR + On-Demand Revalidation

```typescript
// app/invitation/[slug]/page.tsx
export const revalidate = 60; // 60초마다 정적 재생성

// 제작자가 콘텐츠 수정 시 즉시 갱신
// lib/revalidation.ts
import { revalidatePath } from 'next/cache';

export async function revalidateInvitation(slug: string) {
  revalidatePath(`/invitation/${slug}`);
  revalidatePath(`/api/og/${slug}`);
}
```

### 7.5 업타임 보장 (결혼식 당일 장애 대응)

```
결혼식 당일 = 장애 시 치명적

대응 전략:
1. ISR 캐시: 최소 60초 캐시 → Supabase 장애에도 캐시된 페이지 제공
2. 정적 폴백: 결제 완료 시 정적 HTML 스냅샷 생성 → CDN에 저장
3. Vercel Status Page 모니터링
4. Supabase Health Check: 5분 간격 크론
5. 방명록/RSVP: Realtime 연결 실패 시 graceful fallback (폴링)
```

---

## 8. 개발 마일스톤

### 8.1 전제 조건

- 개발자: 1인 (풀타임 기준 6-8주, 파트타임 시 8-12주)
- 기존 프로젝트 코드 재활용 비율: 약 60% (섹션 컴포넌트, Guest Snap, 스타일링)
- 사업자등록/PG 심사: 개발과 병렬 진행

### 8.2 스프린트 계획 (7주)

#### Sprint 0: 프로젝트 셋업 (1주)

| 딜리버리블 | 설명 |
|-----------|------|
| 프로젝트 초기화 | Next.js + Supabase + Tailwind + TypeScript 셋업 |
| 인증 구현 | Supabase Auth (카카오/Google/Magic Link) |
| DB 스키마 | 전체 테이블 생성 + RLS 정책 적용 |
| CI/CD | Vercel 자동 배포 + Preview Deployment |
| 기본 레이아웃 | 랜딩/대시보드/에디터 라우팅 + 레이아웃 |

**완료 기준**: 로그인 후 빈 대시보드가 보인다.

##### 카카오톡 인앱 브라우저 호환성 검증 (Sprint 0 필수)

청첩장의 99% 이상이 카카오톡으로 공유되므로, 인앱 브라우저 호환성이 최우선.

검증 항목:
- [ ] Web Audio API (터미널 인트로 신디사이저) — iOS/Android
- [ ] Canvas API (파티클 이펙트) — 성능 테스트
- [ ] 파일 업로드 (Guest Snap) — 인앱 브라우저 제한 확인
- [ ] URL 스킴 (카카오맵/네이버지도 앱 연결)
- [ ] React Three Fiber (3D 이펙트) — 지원 여부
- [ ] OG 미리보기 품질

미동작 기능은 graceful degradation 적용 (기능 비활성화 + 대체 UI)

#### Sprint 1: 블록 에디터 코어 (1주)

| 딜리버리블 | 설명 |
|-----------|------|
| 온보딩 위자드 | 커플정보, 예식정보, 인사말, 계좌 입력 폼 |
| 테마 선택 | 3개 테마 선택 UI |
| 섹션 리스트 | 15개 섹션 ON/OFF 토글 + dnd-kit 드래그앤드롭 |
| 에디터 상태관리 | zustand 스토어 + 자동저장 (debounce) |
| DB 연동 | invitation CRUD Server Actions |

**완료 기준**: 정보 입력 후 섹션 순서를 변경하고 저장할 수 있다.

#### Sprint 2: 섹션 편집 + 미디어 (1주)

| 딜리버리블 | 설명 |
|-----------|------|
| 섹션별 편집 폼 | 인사말, 인터뷰, 타임라인 등 텍스트 편집 |
| 이미지 업로드 | Hero/갤러리 이미지 업로드 (Supabase Storage) |
| 갤러리 관리 | 다중 업로드 + 순서 변경 + 삭제 |
| 미리보기 패널 | 모바일 프레임 실시간 미리보기 |
| 슬러그 설정 | 커스텀 슬러그 입력 + 유니크 검증 |

**완료 기준**: 에디터에서 모든 콘텐츠를 편집하고 미리보기에서 확인할 수 있다.

#### Sprint 3: 청첩장 뷰어 멀티테넌트 (1.5주)

| 딜리버리블 | 설명 |
|-----------|------|
| 섹션 컴포넌트 전환 | constants.ts 의존 -> props 기반 (15개 섹션) |
| 동적 라우팅 | `/invitation/[slug]` 서버 컴포넌트 |
| 테마 시스템 | CSS Variables 기반 3개 테마 적용 |
| 방명록 | Supabase Realtime 실시간 방명록 |
| RSVP | 참석 여부 + 집계 대시보드 |
| 계좌 복사 | 1-tap 복사 + 카카오페이 링크 |
| 지도 연동 | 네이버/카카오/T맵 네비게이션 |
| OG 이미지 | `@vercel/og` 동적 생성 + 카카오톡 미리보기 |

**완료 기준**: slug로 접근한 청첩장이 기존 개인 프로젝트와 동일한 품질로 렌더링된다.

#### Sprint 4: 결제 + 퍼블리시 (1주)

| 딜리버리블 | 설명 |
|-----------|------|
| 포트원 V2 연동 | 결제 SDK + 검증 + 웹훅 |
| 결제 플로우 | 카카오페이/카드 결제 -> 상태 변경 |
| 퍼블리시 | 결제 완료 -> 공유 링크 활성화 |
| 카카오톡 공유 | Kakao SDK 공유 + OG 미리보기 |
| 환불 처리 | 관리자 환불 API |

**완료 기준**: 4.9만원 결제 후 카카오톡으로 청첩장을 공유할 수 있다.

#### Sprint 5: Guest Snap + 부가기능 (1주)

| 딜리버리블 | 설명 |
|-----------|------|
| Guest Snap 전환 | Google Drive -> Cloudflare R2 |
| R2 Presigned URL | 업로드 URL 발급 + 완료 처리 |
| 오프라인 큐 | IndexedDB + Service Worker (기존 코드 재활용) |
| BGM 시스템 | 프리셋 BGM 선택 |
| 캘린더 추가 | Google/Apple .ics 생성 |
| 이스터에그 | 아케이드/글리치 (기존 코드 재활용) |

**완료 기준**: 결혼식 당일 하객이 Guest Snap으로 사진을 업로드할 수 있다.

#### Sprint 6: 랜딩페이지 + 어드민 + QA (0.5주)

| 딜리버리블 | 설명 |
|-----------|------|
| 랜딩페이지 | 데모 체험 + 가격 + CTA |
| 어드민 패널 | 주문/고객/매출 관리 (기본) |
| 법적 페이지 | 이용약관, 개인정보처리방침, 환불정책 |
| E2E 테스트 | 핵심 플로우 (가입 -> 제작 -> 결제 -> 공유 -> 방문) |
| 성능 최적화 | LCP < 2.5s, CLS < 0.1, FID < 100ms |
| 보안 점검 | RLS 검증, XSS 방지, Rate Limiting |

**완료 기준**: 외부 사용자가 처음 방문 -> 결제 -> 카카오톡 공유까지 완료할 수 있다.

### 8.3 의존성 맵

```
Sprint 0 (셋업/인증/DB)
    │
    ├──> Sprint 1 (에디터 코어)
    │       │
    │       └──> Sprint 2 (섹션 편집/미디어)
    │               │
    │               └──> Sprint 3 (뷰어 멀티테넌트)
    │                       │
    │                       ├──> Sprint 4 (결제/퍼블리시) ──> Sprint 6 (런칭)
    │                       │
    │                       └──> Sprint 5 (Guest Snap/부가) ──> Sprint 6
    │
    └──[병렬] 사업자등록 + PG 심사 (Sprint 0~3 기간)
    └──[병렬] 랜딩페이지 디자인 (Sprint 2~3 기간)

의존성 핵심:
- Sprint 4는 Sprint 3 완료 필수 (결제 대상인 청첩장이 렌더링되어야 함)
- Sprint 5는 Sprint 3 완료 필수 (R2 연동이 뷰어에서 동작해야 함)
- Sprint 4, 5는 서로 독립 (병렬 가능하나 1인 개발이므로 순차)
- PG 심사는 Sprint 4 전까지 완료 필요 (2-3주 소요)
```

### 8.4 기술 부채 / Phase 2 이관 항목

| 항목 | 이유 | Phase 2 계획 |
|------|------|-------------|
| AI 커스터마이징 | MVP 범위 초과 | Gemini Flash API + 크레딧 시스템 |
| 섹션 내부 레이아웃 편집 | 렌더링 엔진 개발 필요 (4,864줄 JSX 데이터 드리븐 전환) | 섹션 내부 요소 배치 자유화 |
| 블록 내부 스타일 커스터마이징 | 에디터 복잡도 상승 | 섹션별 폰트/색상/간격 커스터마이징 |
| 분석 대시보드 | 추가 기능 | 방문자 수, UTM 추적, 공유 통계 |
| 테마 마켓 | 디자인 자산 필요 | 5-10개 추가 테마 |
| 커스텀 도메인 | DNS 설정 자동화 | 1,900원 애드온 |
| 카카오톡 알림 | 카카오 비즈니스 채널 필요 | RSVP/방명록 알림 |

---

## 9. 비기능 요구사항

### 9.1 성능

| 지표 | 목표 | 측정 도구 |
|------|------|----------|
| LCP (Largest Contentful Paint) | < 2.5s | Lighthouse, Web Vitals |
| FID (First Input Delay) | < 100ms | Lighthouse |
| CLS (Cumulative Layout Shift) | < 0.1 | Lighthouse |
| TTFB (Time to First Byte) | < 200ms | Vercel Analytics |
| 청첩장 페이지 로드 | < 3s (3G) | Lighthouse (throttled) |
| 이미지 최적화 | WebP, lazy loading | Next.js Image |
| R3F 번들 최적화 | dynamic import + code splitting | Webpack Bundle Analyzer |

> **React Three Fiber 번들 최적화**: `react-three-fiber`, `three.js`, `postprocessing`은 dynamic import + code splitting 적용.
> 이스터에그(아케이드/글리치) 페이지만 lazy loading하여 메인 번들 크기를 최소화한다.

### 9.2 보안

| 항목 | 대응 |
|------|------|
| 인증 | Supabase Auth (JWT, httpOnly cookie) |
| 데이터 접근 | RLS (Row Level Security) |
| 결제 위변조 | 서버 사이드 결제 검증 (포트원 API) |
| XSS | React 자동 이스케이프 + CSP 헤더 |
| CSRF | SameSite cookie + Origin 검증 |
| Rate Limiting | IP 기반 (방명록, RSVP, Guest Snap) |
| 파일 업로드 | Magic byte 검증, 허용 MIME 타입만 |
| 개인정보 | 계좌번호 마스킹 표시, 비밀번호 bcrypt 해시 |

### 9.3 모니터링

| 항목 | 도구 |
|------|------|
| 에러 트래킹 | Sentry (무료 티어) |
| 업타임 | Vercel + BetterUptime (무료) |
| 성능 | Vercel Analytics (Pro 포함) |
| 로그 | Vercel Logs + Supabase Logs |
| 결제 | 포트원 대시보드 |

---

## 10. 환불 정책

| 상황 | 환불 비율 | 근거 |
|------|----------|------|
| 결제 후 공유 링크 미발행 | 100% | 서비스 미이용 |
| 공유 후 7일 이내 | 50% | 전자상거래법 디지털 상품 특례 |
| 공유 후 7일 초과 | 환불 불가 | 서비스 이용 완료 |
| 결혼식 이후 | 환불 불가 | 서비스 목적 달성 |
| 서비스 장애로 인한 피해 | 100% + 보상 검토 | 서비스 책임 |

---

## 11. 성공 지표 (Phase 1)

| KPI | 목표 (런칭 후 1개월) | 목표 (런칭 후 3개월) |
|-----|---------------------|---------------------|
| 가입자 수 | 100명 | 500명 |
| 유료 전환 | 10건 | 30건 |
| 전환율 | 10% | 6% |
| RSVP 사용률 | 80% | 80% |
| 방명록 사용률 | 70% | 70% |
| Guest Snap 사용률 | 30% | 40% |
| NPS | 50+ | 50+ |
| 이탈률 (에디터) | < 40% | < 30% |
| Kill Criteria | 3개월 내 월 5건 미만 | 6개월 후 월 15건 미만 |

---

## 부록

### A. 기존 프로젝트 파일 -> SaaS 매핑

| 기존 파일 | SaaS 전환 |
|-----------|----------|
| `src/lib/constants.ts` | `invitations` 테이블 (DB화) |
| `src/lib/firebase.ts` | 삭제 -> Supabase Realtime |
| `src/lib/gallery.ts` | Supabase Storage API로 교체 |
| `src/lib/guestsnap/` | Cloudflare R2 API로 교체 (로직 재활용) |
| `src/components/sections/*.tsx` | props 기반으로 리팩터링 (15개 전부) |
| `src/app/invitation/page.tsx` | `[slug]/page.tsx` 동적 라우팅 |
| `src/app/invitation/arcade/` | 이스터에그로 유지 (테마 연동) |
| `src/app/invitation/glitch/` | glitch 테마에 통합 |
| `src/types/index.ts` | 확장 (에디터/결제/멀티테넌트 타입) |
| `src/hooks/` | 에디터 + 뷰어용 훅 추가 |

### B. 프로젝트 디렉토리 구조 (SaaS)

```
src/
├── app/
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   └── callback/route.ts
│   ├── (marketing)/
│   │   ├── page.tsx              # 랜딩페이지
│   │   ├── pricing/page.tsx
│   │   └── demo/page.tsx
│   ├── dashboard/
│   │   └── page.tsx              # 청첩장 목록
│   ├── editor/
│   │   └── [id]/
│   │       ├── page.tsx          # 블록 에디터
│   │       └── preview/page.tsx  # 미리보기
│   ├── invitation/
│   │   └── [slug]/
│   │       ├── page.tsx          # 공개 청첩장 (SSR/ISR)
│   │       ├── arcade/page.tsx   # 이스터에그
│   │       └── layout.tsx
│   ├── admin/
│   │   └── page.tsx              # 어드민 패널
│   ├── api/
│   │   ├── invitation/
│   │   │   └── [slug]/
│   │   │       ├── rsvp/route.ts
│   │   │       ├── guestbook/route.ts
│   │   │       └── guestsnap/
│   │   │           ├── session/route.ts
│   │   │           ├── upload/route.ts
│   │   │           └── complete/route.ts
│   │   ├── webhooks/
│   │   │   └── portone/route.ts
│   │   └── og/
│   │       └── [slug]/route.tsx
│   ├── layout.tsx
│   └── globals.css
├── components/
│   ├── editor/
│   │   ├── EditorLayout.tsx
│   │   ├── SectionList.tsx
│   │   ├── SectionEditor.tsx
│   │   ├── PreviewPanel.tsx
│   │   ├── OnboardingWizard.tsx
│   │   └── ThemeSelector.tsx
│   ├── sections/              # 기존 15개 섹션 (props 기반)
│   │   ├── Hero.tsx
│   │   ├── Greeting.tsx
│   │   ├── ... (13개 더)
│   │   └── index.ts
│   ├── dashboard/
│   │   ├── InvitationCard.tsx
│   │   └── RsvpSummary.tsx
│   ├── payment/
│   │   └── PaymentButton.tsx
│   └── ui/                    # 공통 UI 컴포넌트
├── lib/
│   ├── supabase/
│   │   ├── client.ts          # 브라우저 클라이언트
│   │   ├── server.ts          # 서버 클라이언트
│   │   └── admin.ts           # 서비스 롤 클라이언트
│   ├── r2/
│   │   └── client.ts          # R2 Presigned URL 생성
│   ├── portone.ts             # 결제 검증/취소
│   ├── themes.ts              # 테마 레지스트리
│   └── utils.ts
├── stores/
│   └── editor-store.ts        # zustand 에디터 상태
├── actions/
│   ├── invitation.ts          # Server Actions
│   ├── media.ts
│   ├── payment.ts
│   └── publish.ts
├── types/
│   ├── database.ts            # Supabase 생성 타입
│   ├── editor.ts              # 에디터 타입
│   └── index.ts
└── hooks/
    ├── useEditorAutoSave.ts
    ├── useRealtimeGuestbook.ts
    └── useGuestSnapUpload.ts
```

### C. 환경 변수

```env
# Supabase
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

# Supabase Auth (OAuth)
# 카카오: Supabase Dashboard > Auth > Providers > Kakao
# Google: Supabase Dashboard > Auth > Providers > Google

# Cloudflare R2
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=guestsnap
R2_PUBLIC_URL=

# 포트원 V2
PORTONE_API_SECRET=
NEXT_PUBLIC_PORTONE_STORE_ID=
PORTONE_WEBHOOK_SECRET=

# 카카오 SDK (공유)
NEXT_PUBLIC_KAKAO_JS_KEY=

# 네이버 지도 (정적 이미지)
NAVER_MAP_CLIENT_ID=
NAVER_MAP_CLIENT_SECRET=

# Sentry
NEXT_PUBLIC_SENTRY_DSN=
SENTRY_AUTH_TOKEN=

# Site
NEXT_PUBLIC_SITE_URL=https://yourdomain.com
```

---

*문서 버전: 1.0*
*작성일: 2026-03-18*
*기반 문서: docs/260316-wedding-invitation-saas-concept.md*
*다음 단계: Phase 0 (Concierge MVP) 실행 또는 Sprint 0 개발 착수*
