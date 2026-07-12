---
name: project-setup
description: |
  FastAPI 프로젝트 초기 설정 및 의존성 구성을 수행합니다.
metadata:
  category: "💻 개발"
  version: "1.0.0"
---
# Project Setup Skill

Extends: `../../_shared/project-setup/SKILL.md` (공통 프로세스 참조)

FastAPI 프로젝트 초기 설정 및 의존성 구성을 수행합니다.

> Tech stack registry: `.claude/registry/tech-stacks/python-fastapi.yaml` (`python-fastapi@recommended`). 기존 서비스에서는 Python constraint와 lockfile을 먼저 보존하고 contract test 없이 major family를 치환하지 않는다.

## Triggers

- "프로젝트 생성", "프로젝트 설정", "fastapi init", "fastapi create"

---

## Input

| 항목 | 필수 | 설명 |
|------|------|------|
| `projectName` | ✅ | 프로젝트 이름 (snake_case) |
| `pythonVersion` | ❌ | Python 버전 (신규 기본: 3.14.6, 기존 프로젝트는 현재 constraint) |
| `database` | ❌ | 데이터베이스 종류 (postgresql/mysql/sqlite) |
| `redisLane` | ❌ | `none` / `redis-direct` / `broker-celery` / `broker-arq` (기본: `none`, 최대 1개) |

---

## Output

### pyproject.toml

```toml
[project]
name = "{project_name}"
version = "0.1.0"
description = "A FastAPI application with Clean Architecture"
readme = "README.md"
requires-python = ">=3.14,<3.15"

dependencies = [
    # FastAPI Core
    "fastapi>=0.139.0,<0.140",
    "uvicorn[standard]>=0.51.0,<0.52",
    "gunicorn>=26.0.0,<27.0",       # 외부 process manager가 필요한 배포에서만 사용
    "uvicorn-worker>=0.4.0,<0.5",   # deprecated uvicorn.workers 대체

    # Database
    "sqlalchemy[asyncio]>=2.0.51,<3.0",
    "asyncpg>=0.31.0,<0.32",
    "alembic>=1.18.5,<2.0",
    "sqlalchemy-utils>=0.42.1,<0.43",  # Type utilities

    # Validation & Settings
    "pydantic>=2.13.4,<3.0",
    "pydantic-settings>=2.14.2,<3.0",

    # Authentication
    "PyJWT[crypto]>=2.13.0,<3.0",
    "pwdlib[argon2]>=0.3.0,<0.4",  # 신규 hash. Passlib은 legacy 검증 adapter에만 둔다.

    # HTTP Client
    "httpx>=0.28.1,<0.29",
    "tenacity>=9.1.4,<10.0",  # Retry logic for HTTP clients

    # Rate Limiting
    "slowapi>=0.1.10,<0.2",  # Rate limiting middleware

    # Caching core. Select exactly one Redis/broker lane below.
    "fastapi-cache2>=0.2.2,<0.3",

    # Logging & Observability
    "structlog>=26.1.0,<27.0",
    "opentelemetry-api>=1.43.0,<2.0",
    "opentelemetry-sdk>=1.43.0,<2.0",
    "opentelemetry-exporter-otlp>=1.43.0,<2.0",
    "opentelemetry-instrumentation-fastapi>=0.64b0,<0.65",
    "prometheus-fastapi-instrumentator>=8.0.2,<9.0",

    # Utilities
    "python-multipart>=0.0.32,<0.1",
    "python-dotenv>=1.2.2,<2.0",

    # Security
    "python-magic>=0.4.27",  # MIME type detection for file uploads
]

[project.optional-dependencies]
redis-direct = [
    # Direct cache, Pub/Sub, rate-limit, and session client lane.
    "redis>=8.0.1,<9.0",
]
broker-celery = [
    # Celery owns its Redis transport constraint; do not add redis-direct.
    "celery[redis]>=5.6.3,<6.0",
]
broker-arq = [
    # ARQ 0.28 currently requires redis-py <6; do not add redis-direct.
    "arq>=0.28.0,<0.29",
]
dev = [
    # Testing
    "pytest>=9.1.1,<10.0",
    "pytest-asyncio>=1.4.0,<2.0",
    "pytest-cov>=7.1.0,<8.0",
    "pytest-mock>=3.15.1,<4.0",
    "httpx>=0.28.1,<0.29",
    "factory-boy>=3.3.3,<4.0",
    "faker>=40.28.1,<41.0",

    # Code Quality
    "ruff>=0.15.21,<0.16",
    "mypy>=2.2.0,<3.0",
    "pre-commit>=4.6.0,<5.0",

    # Development
    "ipython>=9.15.0,<10.0",
]

[tool.uv]
# redis-direct targets redis-py 8. Celery/Kombu currently constrains Redis
# below 6.5, while ARQ constrains it below 6. Each app selects one lane.
conflicts = [
    [
        { extra = "redis-direct" },
        { extra = "broker-celery" },
    ],
    [
        { extra = "redis-direct" },
        { extra = "broker-arq" },
    ],
    [
        { extra = "broker-celery" },
        { extra = "broker-arq" },
    ],
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
target-version = "py314"
line-length = 88

[tool.ruff.lint]
extend-select = ["D", "RUF"]  # docstring + ruff rules
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
    "D",   # pydocstyle
    "RUF", # ruff-specific rules
]
ignore = [
    "E501",  # line too long (handled by formatter)
    "B008",  # do not perform function calls in argument defaults
    "D100",  # Missing docstring in public module
    "D104",  # Missing docstring in public package
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

[tool.mypy]
python_version = "3.14"
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
plugins = ["pydantic.mypy"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "-v --cov=app --cov-report=term-missing"
filterwarnings = ["error"]

[tool.coverage.run]
source = ["app"]
omit = ["*/migrations/*", "*/tests/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
]
```

### Redis/broker lane 선택

기본 생성물은 Redis client를 설치하지 않는다. 실제 아키텍처에 맞는 lane 하나만
선택하고 `--all-extras`는 사용하지 않는다.

```bash
uv sync --extra redis-direct
# or
uv sync --extra broker-celery
# or
uv sync --extra broker-arq
```

### 디렉토리 구조

```
{project_name}/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── routes/
│   │       │   └── __init__.py
│   │       └── dependencies/
│   │           └── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── exceptions.py
│   │   └── logging.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── entities/
│   │   │   └── __init__.py
│   │   └── repositories/
│   │       └── __init__.py
│   ├── application/
│   │   ├── __init__.py
│   │   └── services/
│   │       └── __init__.py
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── session.py
│   │   │   └── models/
│   │   │       └── __init__.py
│   │   ├── repositories/
│   │   │   └── __init__.py
│   │   └── cache/
│   │       └── __init__.py
│   └── schemas/
│       ├── __init__.py
│       └── base.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   └── __init__.py
│   ├── integration/
│   │   └── __init__.py
│   └── e2e/
│       └── __init__.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

### main.py

```python
# app/main.py
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1 import api_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan events."""
    # Startup
    setup_logging()
    yield
    # Shutdown


def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url=f"{settings.API_V1_PREFIX}/docs",
        redoc_url=f"{settings.API_V1_PREFIX}/redoc",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_app()
```

### .env.example

```bash
# Application
PROJECT_NAME="{project_name}"
VERSION="0.1.0"
DEBUG=true
API_V1_PREFIX="/api/v1"

# Database
DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/{project_name}"

# Redis
REDIS_URL="redis://localhost:6379/0"

# Security
SECRET_KEY="your-secret-key-change-in-production"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=["http://localhost:3000"]
```

### .gitignore

```gitignore
# Byte-compiled
__pycache__/
*.py[cod]
*$py.class

# Virtual environments
.venv/
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Environment
.env
.env.local
.env.*.local

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Build
dist/
build/
*.egg-info/

# Logs
*.log
logs/

# Database
*.db
*.sqlite3

# OS
.DS_Store
Thumbs.db
```

---

## 실행 명령어

```bash
# 프로젝트 디렉토리 생성
mkdir {project_name}
cd {project_name}

# 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 의존성 설치
pip install -e ".[dev]"

# 환경 변수 설정
cp .env.example .env

# 개발 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## References

- `_references/ARCHITECTURE-PATTERN.md`
