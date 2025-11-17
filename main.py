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
from typing import Optional
from src.routers.auth import router
from src.routers.profile import router as profile_router
from src.routers.user_settings import router as user_settings_router

from src.models import (
    user,
    profile,
    session,
    query,
    answer,
    sources,
    token,
    user_settings,
    model_memory,
    login_session,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan handler to initialize app state, create DB tables and shutdown cleanup."""
    logger = SingletonLogger().get_logger()
    model = None
    tokenizer = None
    app.state = AppState(model=model, tokenizer=tokenizer, logger=logger)

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


app.include_router(router, prefix="api/v1/auth", tags=["Auth"])
app.include_router(profile_router, prefix="api/v1/profile", tags=["Profile"])
app.include_router(
    user_settings_router, prefix="api/v1/user-settings", tags=["User Settings"]
)


@app.get("/")
def read_root():
    return {"message": "FastAPI is running!"}


@app.get("/health")
def health_check():
    cpu_usage: Optional[float] = psutil.cpu_percent(interval=1)
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
