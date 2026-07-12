# Python 3.14 and FastAPI 0.139 migration contract

Verified: 2026-07-13
Registry: `python-fastapi@recommended`

New services target Python 3.14.6 and FastAPI 0.139.0. Existing services remain project-truth first and move through a dependency lock plus contract-test migration.

## Python 3.14

- Annotations are deferred by default. Libraries that inspect annotations must use documented Pydantic, `typing`, or `annotationlib` APIs rather than class namespace internals.
- Review free-threaded and subinterpreter support as explicit experiments. Do not claim compatibility merely because pure-Python tests pass; native extensions need their own evidence.
- Review the process-pool start method, regex behavior, deprecations, C extensions, and packaging support.
- Python 3.14.0-3.14.4의 incremental GC 자료를 현재 기본값으로 가정하지 않는다. 메모리 압력 문제로 3.14.5부터 non-incremental collector로 되돌아갔으므로, 3.14.6에서 RSS/latency baseline을 다시 측정한다.

## FastAPI and Pydantic

- FastAPI 0.128+ is Pydantic 2 only. Replace `class Config`, `.dict()`, `.json()`, `.parse_obj()`, `.from_orm()`, and other v1 forms with `ConfigDict` and current model APIs.
- FastAPI 0.132 enables strict JSON `Content-Type` validation. Test clients that previously sent JSON without a valid header.
- FastAPI 0.137 preserves nested router instances; `router.routes` is no longer a public flat-list contract. Remove code that reads or mutates it as an implementation detail.
- `ORJSONResponse` and `UJSONResponse` are deprecated. Prefer the default Pydantic-backed response serialization unless a measured exception exists.
- Snapshot validation errors, OpenAPI, serialization aliases, bytes schemas, dependency order, exception handling, and lifespan behavior.

## ASGI and infrastructure

- Uvicorn 0.50 selects `websockets-sansio` for `--ws auto`; the legacy websockets implementation is deprecated. Test close codes, subprotocols, fragmentation, ping/pong, and shutdown.
- `uvicorn.workers` is deprecated. Prefer Uvicorn's own worker management in containers. If Gunicorn is required, use the separate `uvicorn-worker` package and test graceful reload.
- redis-py 8 uses RESP3 on the wire by default while preserving common Python response shapes. Test raw protocol assumptions, modules, pubsub, scripts, async pools, and mocks.
- Async Redis clients, pools, Pub/Sub, and clusters must be closed with `await ...aclose()`. The older async `close()` alias is deprecated; make ownership explicit and test that shutdown releases the owned pool without dropping an in-flight Pub/Sub reader.
- Treat OpenTelemetry API/SDK/exporter and instrumentation versions as one BOM. Verify propagation, sampling, exporter shutdown, and emitted spans.

## Mutually exclusive Redis dependency lanes

The base project does not install a Redis client or task broker. Select exactly one optional extra because the direct client and broker ecosystems currently require incompatible redis-py major lines:

| Extra | Intended use | Resolution contract |
|---|---|---|
| `redis-direct` | Direct cache, Pub/Sub, rate limiting, and sessions | `redis>=8.0.1,<9.0` |
| `broker-celery` | Celery worker and Redis transport | `celery[redis]>=5.6.3,<6.0`; Celery/Kombu owns the transport constraint |
| `broker-arq` | ARQ async worker | `arq>=0.28.0,<0.29`; ARQ 0.28 requires `redis[hiredis]>=4.2,<6` |

Declare all three pairings in `[tool.uv].conflicts`. This tells uv to resolve separate universal forks instead of trying to install Redis 8 with Celery/Kombu's `<6.5` transport constraint or ARQ's `<6` constraint. Do not bypass the contract with a transitive override. The 2026-07-13 compile fixture resolved Redis 8.0.1 for `redis-direct`, Redis 6.4.0 for `broker-celery`, and Redis 5.3.1 for `broker-arq`.

```bash
uv lock
uv sync --extra redis-direct
# or, in a separate deployment/environment:
uv sync --extra broker-celery
uv sync --extra broker-arq

uv pip compile pyproject.toml --extra redis-direct --python-version 3.14
uv pip compile pyproject.toml --extra broker-celery --python-version 3.14
uv pip compile pyproject.toml --extra broker-arq --python-version 3.14
```

## Authentication and password migration

- Use PyJWT with an explicit algorithm allowlist, issuer, audience, subject, expiration, rotation, and invalid-token tests.
- Use `pwdlib[argon2]` for new hashes. Passlib is not a current default; retain it only behind a legacy verification adapter.
- A safe migration verifies the old hash, writes a new Argon2 hash on successful login, and preserves timing behavior for nonexistent users.

## Test tooling

- pytest-asyncio 1 removed the deprecated `event_loop` fixture. Use explicit `loop_scope` when async fixture and test lifetimes differ.
- pytest 9 changes collection duplicates, CI detection, deprecated fixture marks, warnings, and plugin internals. Run the complete plugin set with warnings promoted to errors.

## Promotion commands

```bash
uv python install 3.14
uv lock --upgrade
uv sync --frozen
uv pip check
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest -W error::DeprecationWarning
```

Required contract fixtures include strict content type, nested routers, lifespan, WebSockets, Redis RESP3, Argon2 and legacy rehash, Pydantic serialization, OpenAPI, and database upgrade/downgrade.

## Primary sources

- https://www.python.org/downloads/release/python-3146/
- https://docs.python.org/3.14/whatsnew/3.14.html
- https://fastapi.tiangolo.com/release-notes/
- https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
- https://www.uvicorn.org/release-notes/
- https://www.uvicorn.org/deployment/
- https://redis.readthedocs.io/en/stable/
- https://pytest-asyncio.readthedocs.io/en/stable/reference/changelog.html
- https://docs.pytest.org/en/stable/changelog.html
