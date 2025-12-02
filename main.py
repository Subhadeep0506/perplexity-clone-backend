from dotenv import load_dotenv
from fastapi.responses import JSONResponse
import logfire
import psutil

load_dotenv(".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import asynccontextmanager
from fastapi.security import HTTPBearer
from src.database.database import engine, Base, DatabaseConnectionError

from src.services.app_state import AppState
from src.services.logger import SingletonLogger
from src.core.settings import get_settings
from src.core.container import ServiceContainer, initialize_registry
from typing import Optional
from src.routers.auth import router
from src.routers.profile import router as profile_router
from src.routers.user_settings import router as user_settings_router
from src.routers.service_catalog import router as service_catalog_router
from src.routers.user_api_keys import router as user_api_keys_router
from src.routers.admin import router as admin_router

from src.models import (
    user,
    profile,
    session,
    message,
    sources,
    token,
    user_settings,
    model_memory,
    login_session,
    service_catalog,
    user_service_credential,
    user_api_keys,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan handler to initialize app state, create DB tables and shutdown cleanup."""
    logger = SingletonLogger().get_logger()

    # Initialize settings and service container
    settings = get_settings()
    container = ServiceContainer(settings)
    registry = initialize_registry(settings)

    model = None
    tokenizer = None
    app.state = AppState(model=model, tokenizer=tokenizer, logger=logger)
    app.state.settings = settings
    app.state.container = container
    app.state.registry = registry

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        try:
            logger = app.state.logger
        except Exception:
            logger = SingletonLogger().get_logger()
        logger.error(f"Error creating database tables: {e}")
        raise

    try:
        yield
    finally:
        logger = getattr(app.state, "logger", SingletonLogger().get_logger())
        if logger:
            logger.info("Shutting down application")
        model = getattr(app.state, "model", None)
        if model and hasattr(model, "close"):
            try:
                model.close()
            except Exception:
                if logger:
                    logger.exception("Error closing model during shutdown")


app = FastAPI(
    title="Perplexity Clone - Backend",
    description="FastAPI backend application for a Perplexity AI clone. Supports user authentication, question answering from various sources, real-time web search and crawling and session management.",
    version="0.0.1",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security_scheme = HTTPBearer()
app.openapi_components = {
    "securitySchemes": {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
}
app.openapi_security = [{"BearerAuth": []}]

logfire.instrument_fastapi(app, capture_headers=True)
logfire.instrument_sqlalchemy(engine)
logfire.instrument_httpx()
logfire.instrument_requests()
logfire.instrument_system_metrics(base="full")


app.include_router(router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(profile_router, prefix="/api/v1/profile", tags=["Profile"])
app.include_router(
    user_settings_router, prefix="/api/v1/user-settings", tags=["User Settings"]
)
app.include_router(
    service_catalog_router, prefix="/api/v1/service-catalog", tags=["Service Catalog"]
)
app.include_router(
    user_api_keys_router, prefix="/api/v1/user-api-keys", tags=["User API Keys"]
)
app.include_router(admin_router, prefix="/admin", tags=["Admin"])


@app.get("/")
def read_root():
    return {"message": "FastAPI is running!"}


@app.get("/health")
def health_check():
    cpu_usage: Optional[float] = psutil.cpu_percent(interval=None)  # Non-blocking
    memory_usage: Optional[float] = psutil.virtual_memory().percent
    num_threads: Optional[int] = psutil.cpu_count()

    return {
        "health": "ok",
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage,
        "num_threads": num_threads,
    }


@app.exception_handler(DatabaseConnectionError)
async def db_connection_exception_handler(request, exc: DatabaseConnectionError):
    logger = getattr(request.app.state, "logger", SingletonLogger().get_logger())
    logger.error("Database connection error: %s", exc)
    return JSONResponse(
        status_code=503,
        content={
            "detail": "Database connection error. Please try again later.",
            "error": str(exc),
        },
    )
