from __future__ import annotations

import os
from typing import Any

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from langgraph.store.postgres import AsyncPostgresStore
from langgraph.store.redis import AsyncRedisStore
from upstash_redis import Redis

from src.lib.enums import CheckpointProvider, MemoryProvider


def _lower_key(provider: str | CheckpointProvider | MemoryProvider) -> str:
    if isinstance(provider, (CheckpointProvider, MemoryProvider)):
        return provider.value
    return str(provider).lower()


def create_checkpointer(
    provider: str | CheckpointProvider = CheckpointProvider.POSTGRES,
    *,
    conn_string: str | None = None,
):
    """
    Create a checkpointer instance.

    Args:
        provider: Type of database to use (postgres or redis)
        conn_string: Database connection string (defaults to env vars)

    Returns:
        An async checkpointer instance (AsyncPostgresSaver or AsyncRedisSaver)
    """
    key = _lower_key(provider)

    if key == CheckpointProvider.POSTGRES.value:
        if conn_string is None:
            conn_string = os.getenv("MEMORY_DATABASE_URL")
            if not conn_string:
                raise ValueError("MEMORY_DATABASE_URL environment variable not set")
        return AsyncPostgresSaver.from_conn_string(conn_string)

    elif key == CheckpointProvider.REDIS.value:
        redis_url = os.getenv("UPSTASH_REDIS_REST_URL")
        redis_token = os.getenv("UPSTASH_REDIS_REST_TOKEN")

        if not redis_url or not redis_token:
            raise ValueError(
                "UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN environment variables must be set"
            )

        redis_client = Redis(url=redis_url, token=redis_token)
        return AsyncRedisSaver(redis_client=redis_client)

    else:
        raise ValueError(f"Unsupported checkpoint provider: {provider}")


def create_memory(
    provider: str | MemoryProvider = MemoryProvider.POSTGRES,
    *,
    conn_string: str | None = None,
):
    """
    Create a memory store instance.

    Args:
        provider: Type of database to use (postgres or redis)
        conn_string: Database connection string (defaults to env vars)

    Returns:
        An async memory store instance (AsyncPostgresStore or AsyncRedisStore)
    """
    key = _lower_key(provider)

    if key == MemoryProvider.POSTGRES.value:
        if conn_string is None:
            conn_string = os.getenv("MEMORY_DATABASE_URL")
            if not conn_string:
                raise ValueError("MEMORY_DATABASE_URL environment variable not set")
        return AsyncPostgresStore.from_conn_string(conn_string)

    elif key == MemoryProvider.REDIS.value:
        redis_url = os.getenv("UPSTASH_REDIS_REST_URL")
        redis_token = os.getenv("UPSTASH_REDIS_REST_TOKEN")

        if not redis_url or not redis_token:
            raise ValueError(
                "UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN environment variables must be set"
            )

        redis_client = Redis(url=redis_url, token=redis_token)
        return AsyncRedisStore(redis_client=redis_client)

    else:
        raise ValueError(f"Unsupported memory provider: {provider}")
