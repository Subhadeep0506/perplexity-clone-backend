"""Centralized application settings using Pydantic BaseSettings."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from src.lib.enums import (
    LLMProvider,
    EmbeddingProvider,
    WebSearcher,
    WebScraper,
    MemoryProvider,
    CheckpointProvider,
)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = ""
    memory_database_url: str = ""
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_session_retries: int = 2
    db_session_retry_delay: float = 0.2

    # LLM Provider (default for testing only, production uses DB per user)
    llm_provider: str = LLMProvider.COHERE.value
    llm_model: Optional[str] = None
    llm_temperature: float = 0.5
    llm_max_tokens: int = 1024
    llm_streaming: bool = False

    # Embeddings (default for testing only, production uses DB per user)
    embedding_provider: str = EmbeddingProvider.HUGGINGFACE_ENDPOINT.value
    embedding_model: str = "intfloat/multilingual-e5-large-instruct"

    # LLM/Search/Scraper API Keys - User-managed via service catalog
    # These are kept for backward compatibility but should not be used in production
    # Production uses encrypted keys from user_api_keys table
    groq_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    cohere_api_key: Optional[str] = None
    mistral_api_key: Optional[str] = None
    nim_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    hf_api_key: Optional[str] = None
    google_search_api_key: Optional[str] = None
    google_custom_search_cx: Optional[str] = None
    tavily_search_api_key: Optional[str] = None
    exa_search_api_key: Optional[str] = None
    serpapi_api_key: Optional[str] = None
    scrapedo_crawler_api_key: Optional[str] = None
    firecrawl_api_key: Optional[str] = None
    scraper_crawler_api_key: Optional[str] = None

    # Vector Store (system-level)
    pinecone_api_key: Optional[str] = None
    pinecone_index_name: str = "perplexity-clone-docstore"
    pinecone_dimension: int = 1024
    pinecone_metric: str = "cosine"
    pinecone_uri: Optional[str] = None

    # Web Search
    web_search_provider: str = WebSearcher.DUCKDUCKGO.value
    google_cse_id: Optional[str] = None  # System-level config

    # Web Scraper
    web_scraper_provider: str = WebScraper.CRAWL4AI.value

    # Storage (S3/Supabase)
    s3_storage_url: Optional[str] = None
    s3_access_key_id: Optional[str] = None
    s3_secret_access_key: Optional[str] = None
    s3_storage_bucket_name: Optional[str] = None
    s3_storage_region: Optional[str] = None
    supabase_service_role_key: Optional[str] = None
    supabase_api_key: Optional[str] = None

    # Memory & Checkpointing
    memory_provider: str = MemoryProvider.POSTGRES.value
    checkpoint_provider: str = CheckpointProvider.POSTGRES.value
    upstash_redis_rest_url: Optional[str] = None
    upstash_redis_rest_token: Optional[str] = None

    # JWT & Auth
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_minutes: int = 10080  # 7 days

    # API Key Encryption
    api_key_encryption_key: Optional[str] = None

    # Google OAuth
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_redirect_uri: Optional[str] = None

    # Server
    workers: int = 1
    host: str = "0.0.0.0"
    port: int = 8089
    reload: bool = False

    # Feature Flags
    enable_logfire: bool = True
    enable_background_tasks: bool = False

    # Logfire
    logfire_token: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
