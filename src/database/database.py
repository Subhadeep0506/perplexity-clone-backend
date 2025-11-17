import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncIterator

from sqlalchemy import func
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

engine = create_async_engine(
    os.getenv("DATABASE_URL"),
    connect_args=(
        {"check_same_thread": False}
        if "sqlite" in os.getenv("DATABASE_URL", "")
        else {}
    ),
)

session_pool: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine, autocommit=False, autoflush=False, expire_on_commit=False
)


class Base(DeclarativeBase):
    """Base class for declarative models."""

    pass


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps to models."""

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

class DatabaseConnectionError(Exception):
    """Raised when the DB connection fails (e.g. psycopg2 OperationalError).

    Routes can catch this and return 503 / log as needed.
    """

@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    """
    Context manager to get a database session.
    Provides a session from the connection pool. The session automatically
    handles transaction lifecycle - commits on success, rolls back on exceptions.
    The session is properly closed after use to return it to the pool.

    Usage:
    ```
    async with get_session() as session:
        result = await session.execute(stmt)
        await session.commit()  # Explicit commit if needed
    ```
    """
    async with session_pool() as session:
        yield session
