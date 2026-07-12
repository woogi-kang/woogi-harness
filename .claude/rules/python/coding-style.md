---
paths:
  - "**/*.py"
  - "**/*.pyi"
  - "**/pyproject.toml"
---

# Python Coding Style

- 현재 project의 `requires-python`, lockfile, formatter/linter 설정을 우선한다.
- 신규 FastAPI baseline은 `.claude/registry/tech-stacks/python-fastapi.yaml`의 recommended channel을 사용한다. 현재 기준 Python 3.14.6이며 기존 프로젝트를 숫자만 바꿔 강제 migration하지 않는다.
- Python 3.14의 deferred annotation 동작을 고려하고 직접 `__annotations__`를 해석하지 않는다.
- 함수 경계와 public model에 type hint를 사용한다.
- Pydantic 2는 `ConfigDict`/현재 serializer를 사용하며 v1 `class Config`를 새 코드에 만들지 않는다.
- 비동기 I/O는 async-compatible client와 lifecycle을 사용하고 blocking call을 event loop에 넣지 않는다.
- `pathlib.Path`, context manager, 명시적 exception 경계를 선호한다.
- Project가 이미 Ruff/formatter/mypy를 사용하면 해당 설정으로 검증한다. 하네스가 도구를 자동 설치하거나 버전을 추측하지 않는다.
- Dependency 관리는 project의 `uv`/lock workflow를 보존하며 stdlib로 충분한 helper에 새 package를 추가하지 않는다.
