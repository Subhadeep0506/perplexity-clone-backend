## Backend Concurrency Review Todos

This file tracks the review tasks performed to assess whether the FastAPI backend is designed to serve at least 100 concurrent users.

### Completed Tasks

- [x] Review FastAPI entrypoint
- [x] Inspect database layer
- [x] Scan controllers/routers
- [x] Check external services
- [x] Review Dockerfile & pyproject
- [x] Summarize and recommend

### Decoupling & Architecture Improvements (Completed)

- [x] **Define adapter interfaces**: Created protocol interfaces in `src/adapters/` for LLM, embeddings, storage, vector store, web search, and web scraper.
- [x] **Centralize configuration**: Added `src/core/settings.py` with `pydantic.BaseSettings` for all service config.
- [x] **Use dependency injection**: Created `src/core/container.py` service container and wired it in `main.py` lifespan. Added DI helpers in `src/services/dependencies.py`.
- [x] **Make async adapters**: Wrapped blocking boto3 calls in `src/lib/storage.py` with `asyncio.to_thread()`.
- [x] **Provider plugin registry**: Created `src/core/registry.py` with adapter registry for pluggable provider implementations.
- [x] **Run multiple workers**: Updated `Dockerfile` to use `--workers 4` for better concurrency.
- [x] **Fix blocking health check**: Changed `psutil.cpu_percent(interval=1)` to `interval=None` (non-blocking).

### Suggested Fixes (Remaining)

- [ ] Replace blocking external HTTP requests (`requests`) with `httpx.AsyncClient` where possible in scrapers and other services.
- [ ] Increase DB pool sizes via env vars (`DB_POOL_SIZE`, `DB_MAX_OVERFLOW`) and confirm DB can handle higher connections.
- [ ] Offload CPU-bound embeddings/LLM inference to background workers (Celery/RQ) or separate services.
- [ ] Tune asyncio threadpool or provide a custom ThreadPoolExecutor if many to_thread calls are expected.
- [ ] Add contract tests & mocks for adapter interfaces with `pytest` + `pytest-asyncio`.
- [ ] Document adapter interfaces, expected behavior, failure modes, and provide local dev setup with docker-compose.

### Notes

**Important**: To use the new settings and DI system, you need to:
1. Install `pydantic-settings`: `uv add pydantic-settings`
2. Ensure all environment variables are set in `.env` (see `src/core/settings.py` for required vars)
3. Controllers/services can now use `Depends(get_storage)`, `Depends(get_llm)`, etc. from `src/services/dependencies.py`

**Backward compatibility**: Existing code using factories directly (e.g., `create_llm()`) still works. The new DI system is additive and doesn't break existing usage.

