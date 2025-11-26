# Adapter Architecture & Dependency Injection

This document describes the new adapter-based architecture and dependency injection system.

## Overview

The application now uses:
- **Protocol-based adapters** for external services (LLM, embeddings, storage, etc.)
- **Centralized settings** using `pydantic.BaseSettings`
- **Service container** for lazy initialization
- **Adapter registry** for pluggable provider implementations
- **FastAPI dependency injection** for clean service access

## Structure

```
src/
├── adapters/               # Protocol interfaces
│   ├── __init__.py
│   ├── llm.py             # LLMAdapter protocol
│   ├── embeddings.py      # EmbeddingsAdapter protocol
│   ├── storage.py         # StorageAdapter protocol
│   ├── vector_store.py    # VectorStoreAdapter protocol
│   ├── web_search.py      # WebSearchAdapter protocol
│   └── web_scraper.py     # WebScraperAdapter protocol
├── core/
│   ├── settings.py        # Centralized Settings class
│   ├── container.py       # ServiceContainer for DI
│   └── registry.py        # AdapterRegistry for plugins
└── services/
    └── dependencies.py    # FastAPI dependency functions
```

## Usage

### 1. Settings

All configuration is centralized in `src/core/settings.py`:

```python
from src.core.settings import get_settings

settings = get_settings()
print(settings.llm_provider)  # Access any setting
```

Environment variables (`.env`):
```bash
# Database
DATABASE_URL=postgresql+asyncpg://...
MEMORY_DATABASE_URL=postgresql://...
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40

# System-level config
LLM_PROVIDER=cohere
EMBEDDING_PROVIDER=huggingface_endpoint
WEB_SEARCH_PROVIDER=duckduckgo
WEB_SCRAPER_PROVIDER=crawl4ai

# Storage (system-level)
S3_STORAGE_URL=https://...
S3_ACCESS_KEY_ID=...
S3_SECRET_ACCESS_KEY=...
S3_STORAGE_BUCKET_NAME=...

# Testing ONLY (production uses DB per user)
TEST_COHERE_API_KEY=your-test-key
TEST_HF_API_KEY=your-test-key
# ... see src/core/settings.py for all available settings
```

**Important**: LLM and embeddings API keys are **fetched from the database per user** in production. Environment variables with `TEST_` prefix are only for local testing.

### 2. Dependency Injection in Routes

Use FastAPI's `Depends()` to inject services:

```python
from fastapi import APIRouter, Depends
from src.services.dependencies import get_storage, get_settings_dep, get_container_dep
from src.lib.auth import get_current_user

router = APIRouter()

@router.post("/generate")
async def generate(
    user_id: int = Depends(get_current_user),
    container = Depends(get_container_dep),
    storage = Depends(get_storage),
    settings = Depends(get_settings_dep)
):
    # Fetch user's API key from database
    user_credentials = await fetch_user_credentials(user_id)  # Your DB query
    
    # Create LLM with user's API key
    llm = container.get_llm(api_key=user_credentials.llm_api_key)
    
    # Use the service
    response = await llm.agenerate([...])
    return {"result": response}
```

Available dependency functions:
- `get_settings_dep()` - Settings instance (system config)
- `get_container_dep()` - ServiceContainer
- `get_registry_dep()` - AdapterRegistry
- `get_llm()` - LLM adapter
- `get_embeddings()` - Embeddings adapter
- `get_vector_store()` - Vector store adapter
- `get_web_search()` - Web search adapter
- `get_web_scraper()` - Web scraper adapter
- `get_storage()` - Storage adapter
- `get_memory()` - Memory store
- `get_checkpointer()` - Checkpointer

### 3. Service Container (Manual Access)

You can also access services directly from the container:

```python
from src.core.settings import get_settings
from src.core.container import ServiceContainer

settings = get_settings()
container = ServiceContainer(settings)

# Get services
llm = container.get_llm()
embeddings = container.get_embeddings()
storage = container.get_storage()
```

### 4. Adapter Registry (Plugin System)

Register new provider implementations without modifying core code:

```python
from src.core.registry import get_registry

registry = get_registry()

# Register a custom LLM adapter
def my_custom_llm_factory(**kwargs):
    return MyCustomLLM(**kwargs)

registry.register_llm("custom", my_custom_llm_factory)

# Use it
llm = registry.get_llm("custom", model="my-model")
```

## Adapter Protocols

All adapters implement protocol interfaces. Example for LLM:

```python
from src.adapters import LLMAdapter

class MyLLMAdapter(LLMAdapter):
    async def agenerate(self, messages, **kwargs):
        # Implementation
        ...
    
    async def astream(self, messages, **kwargs):
        # Implementation
        ...
```

## Benefits

1. **Decoupling**: Business logic depends on protocols, not concrete implementations
2. **Testability**: Easy to mock adapters for unit tests
3. **Flexibility**: Swap providers via environment variables
4. **Discoverability**: All system config in one place (`settings.py`)
5. **Type safety**: Protocol-based design with type hints
6. **Pluggability**: Add new providers via registry without code changes
7. **Security**: User API keys stored in DB, not env vars

## API Key Strategy

**System-level keys** (from `.env`):
- Storage (S3/Supabase)
- Vector store (Pinecone)
- Memory/checkpoint (Redis/Postgres)
- OAuth secrets

**User-level keys** (from database):
- LLM providers (Cohere, OpenAI, Anthropic, etc.)
- Embeddings (HuggingFace)
- Web search (Tavily, SerpAPI, Exa)
- Web scraper (Firecrawl, ScrapeDo)

**Testing keys** (from `.env` with `TEST_` prefix):
- Only for local development/testing
- Never used in production

## Migration Guide

**Backward compatibility**: Existing code using factories directly still works:

```python
# Old way (still works)
from src.services.llm.factory import create_llm
llm = create_llm("cohere", api_key="...")

# New way for production (fetch API key from DB)
from fastapi import Depends
from src.services.dependencies import get_container_dep

@app.post("/endpoint")
async def handler(
    user_id: int = Depends(get_current_user),
    container = Depends(get_container_dep)
):
    # Fetch user's credentials from database
    user_creds = await get_user_service_credentials(user_id, "llm")
    
    # Create adapter with user's API key
    llm = container.get_llm(api_key=user_creds.api_key)
    
    # Use llm
    response = await llm.agenerate([...])
    return {"result": response}
```

## Installation

Install required dependency:
```bash
uv add pydantic-settings
```

## Configuration

Set environment variables in `.env`. See `src/core/settings.py` for all available settings.

**Required (system-level)**:
- `DATABASE_URL` - Main application database
- `MEMORY_DATABASE_URL` - Memory/checkpoint database
- `JWT_SECRET_KEY` - JWT signing secret
- `S3_STORAGE_URL`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`, `S3_STORAGE_BUCKET_NAME` - Storage
- `PINECONE_API_KEY` - Vector store (if using Pinecone)

**Testing only** (prefix with `TEST_`, not used in production):
- `TEST_COHERE_API_KEY`, `TEST_OPENAI_API_KEY`, etc. - For local testing without DB
- `TEST_HF_API_KEY` - For embeddings testing

**User-level** (stored in database, NOT in .env):
- LLM provider API keys (per user)
- Embeddings API keys (per user)
- Web search API keys (per user)
- Web scraper API keys (per user)

Use the `user_service_credential` table to store and retrieve user-specific API keys.

## Next Steps

- [ ] Migrate controllers to fetch user API keys from DB and use container methods
- [ ] Add contract tests for adapter protocols
- [ ] Create mock adapters for testing
- [ ] Document each adapter's behavior and failure modes
- [ ] Add docker-compose for local dev with all services
