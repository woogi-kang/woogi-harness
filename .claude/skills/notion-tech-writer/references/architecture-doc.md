# Architecture Document Template

## Structure

```markdown
# [시스템/서비스명] Architecture

| 속성 | 값 |
|------|-----|
| 🏷️ 태그 | Architecture, System Design |
| 👤 담당자 | @name |
| 📅 상태 | 작성중 / 검토필요 / 배포됨 |
| 📆 최종수정 | YYYY-MM-DD |

## Overview

[시스템 개요 2-3문장: 무엇을, 왜, 어떻게]

[Image: 시스템 전체 아키텍처 다이어그램]

## Tech Stack

| 영역 | 기술 | 버전 | 비고 |
|------|------|------|------|
| Frontend | Flutter | 3.44.6 | 신규 기준; 실제 프로젝트 constraint 기록 |
| Backend | Node.js | 24.18.0 LTS | 신규 기준; 실제 `engines` 기록 |
| Database | PostgreSQL | 15.x | 메인 DB |
| Cache | Redis | 7.x | 세션, 캐시 |
| Cloud | GCP | - | 프로덕션 환경 |

## System Components

### [컴포넌트 1]

**역할**: [1문장 설명]

**책임**:
- 책임 1
- 책임 2

**의존성**: [다른 컴포넌트와의 관계]

[Image: 컴포넌트 상세 다이어그램]

### [컴포넌트 2]

...

## Data Flow

### [주요 플로우 1: 예) 사용자 인증]

```
1. Client → API Gateway: 로그인 요청
2. API Gateway → Auth Service: 토큰 검증
3. Auth Service → DB: 사용자 조회
4. DB → Auth Service: 사용자 정보
5. Auth Service → Client: JWT 발급
```

[Diagram: 시퀀스 다이어그램]

💡 인증 토큰은 Redis에 캐싱되어 후속 요청 시 DB 조회 없이 검증됩니다.

## Database Schema

### [주요 테이블/컬렉션]

```sql
-- 파일: schema/users.sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

▶️ 전체 스키마 보기
   [접힌 내용: 모든 테이블 DDL]

## API Design

| 서비스 | 프로토콜 | 포트 | 용도 |
|--------|----------|------|------|
| API Gateway | REST/HTTP | 443 | 외부 API |
| Internal | gRPC | 50051 | 서비스 간 통신 |
| Events | Kafka | 9092 | 비동기 이벤트 |

## Infrastructure

### 환경 구성

| 환경 | URL | 용도 |
|------|-----|------|
| Development | dev.example.com | 개발 테스트 |
| Staging | staging.example.com | QA/통합 테스트 |
| Production | api.example.com | 프로덕션 |

### 스케일링 전략

[수평/수직 확장 전략 설명]

⚠️ Auto-scaling은 CPU 70% 이상에서 트리거됩니다.

## Security

### 인증/인가

[인증 방식 설명]

### 데이터 보호

- 저장 시 암호화: [방식]
- 전송 시 암호화: TLS 1.3

🚨 민감 정보는 절대 로그에 출력하지 마십시오.

## Monitoring & Logging

| 도구 | 용도 |
|------|------|
| Prometheus | 메트릭 수집 |
| Grafana | 대시보드 |
| Loki | 로그 집계 |
| PagerDuty | 알림 |

### 핵심 메트릭

- Response Time (p99 < 200ms)
- Error Rate (< 0.1%)
- Throughput (> 1000 RPS)

## Decisions & Trade-offs

### ADR-001: [결정 제목]

**상황**: [문제 상황]
**결정**: [선택한 방안]
**대안**: [고려했던 다른 방안]
**이유**: [선택 이유]

---
📝 **유지보수 노트**
- 주요 컴포넌트 변경 시 다이어그램 업데이트
- 기술 스택 버전 업그레이드 시 반영
- 신규 서비스 추가 시 업데이트
```

## Key Elements

1. **다이어그램 필수**: 전체 아키텍처, 컴포넌트별, 시퀀스 다이어그램
2. **Tech Stack 테이블**: 버전 명시 필수
3. **Data Flow**: 번호 매긴 순차적 흐름 + 다이어그램
4. **스키마**: 주요 테이블만 본문에, 전체는 토글
5. **ADR**: 주요 결정사항과 이유 기록
6. **메트릭**: 성능 기준값 명시
