"""Dependency injection container for service adapters.

Note: LLM and embeddings API keys should be fetched from the database per user.
The container methods here are for testing/system-level defaults only.
For production, create adapters with user-specific credentials from DB.
"""

from typing import Optional
from src.core.settings import Settings
from src.core.registry import AdapterRegistry, get_registry
from src.services.llm.factory import create_llm
from src.services.embedding.factory import create_embeddings
from src.services.vector_store.factory import create_vector_store
from src.services.web_search.factory import create_web_search
from src.services.web_scraper.factory import create_scraper
from src.services.memory.factory import create_memory, create_checkpointer
from src.lib.storage import SupabaseStorage


class ServiceContainer:
    """Container for initialized service adapters.

    WARNING: Methods here are for testing/system defaults only.
    In production, fetch user-specific API keys from DB and create adapters on-demand.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self._llm: Optional[any] = None
        self._embeddings: Optional[any] = None
        self._vector_store: Optional[any] = None
        self._web_search: Optional[any] = None
        self._web_scraper: Optional[any] = None
        self._storage: Optional[SupabaseStorage] = None
        self._memory: Optional[any] = None
        self._checkpointer: Optional[any] = None

    def get_llm(self, api_key: Optional[str] = None):
        """Get or create LLM adapter.

        Args:
            api_key: User-specific API key from DB. If None, uses test key from env.

        Note: In production, always pass api_key from user's DB credentials.
        """
        # For production: don't cache, create new instance with user's api_key
        if api_key:
            return create_llm(
                provider=self.settings.llm_provider,
                model=self.settings.llm_model,
                api_key=api_key,
                temperature=self.settings.llm_temperature,
                max_tokens=self.settings.llm_max_tokens,
                streaming=self.settings.llm_streaming,
            )

        # For testing only: use cached instance with test key
        if self._llm is None:
            test_key = self._get_test_llm_api_key()
            if test_key:
                self._llm = create_llm(
                    provider=self.settings.llm_provider,
                    model=self.settings.llm_model,
                    api_key=test_key,
                    temperature=self.settings.llm_temperature,
                    max_tokens=self.settings.llm_max_tokens,
                    streaming=self.settings.llm_streaming,
                )
        return self._llm

    def get_embeddings(self, api_key: Optional[str] = None):
        """Get or create embeddings adapter.

        Args:
            api_key: User-specific API key from DB. If None, uses test key from env.

        Note: In production, always pass api_key from user's DB credentials.
        """
        # For production: don't cache, create new instance with user's api_key
        if api_key:
            return create_embeddings(
                provider=self.settings.embedding_provider,
                model_name=self.settings.embedding_model,
                api_key=api_key,
            )

        # For testing only: use cached instance with test key
        if self._embeddings is None:
            test_key = self.settings.test_hf_api_key
            if test_key:
                self._embeddings = create_embeddings(
                    provider=self.settings.embedding_provider,
                    model_name=self.settings.embedding_model,
                    api_key=test_key,
                )
        return self._embeddings

    def get_vector_store(self, embeddings=None):
        """Get or create vector store adapter.

        Args:
            embeddings: Optional embeddings instance. If None, uses default.
        """
        if embeddings:
            return create_vector_store(
                embeddings=embeddings,
                index_name=self.settings.pinecone_index_name,
                dimension=self.settings.pinecone_dimension,
                metric=self.settings.pinecone_metric,
                api_key=self.settings.pinecone_api_key,
            )

        if self._vector_store is None:
            default_embeddings = self.get_embeddings()
            if default_embeddings:
                self._vector_store = create_vector_store(
                    embeddings=default_embeddings,
                    index_name=self.settings.pinecone_index_name,
                    dimension=self.settings.pinecone_dimension,
                    metric=self.settings.pinecone_metric,
                    api_key=self.settings.pinecone_api_key,
                )
        return self._vector_store

    def get_web_search(self):
        """Get or create web search adapter."""
        if self._web_search is None:
            self._web_search = create_web_search(
                provider=self.settings.web_search_provider
            )
        return self._web_search

    def get_web_scraper(self):
        """Get or create web scraper adapter."""
        if self._web_scraper is None:
            self._web_scraper = create_scraper(
                provider=self.settings.web_scraper_provider
            )
        return self._web_scraper

    def get_storage(self):
        """Get or create storage adapter."""
        if self._storage is None:
            self._storage = SupabaseStorage()
        return self._storage

    def get_memory(self):
        """Get or create memory store."""
        if self._memory is None:
            self._memory = create_memory(
                provider=self.settings.memory_provider,
                conn_string=self.settings.memory_database_url,
            )
        return self._memory

    def get_checkpointer(self):
        """Get or create checkpointer."""
        if self._checkpointer is None:
            self._checkpointer = create_checkpointer(
                provider=self.settings.checkpoint_provider,
                conn_string=self.settings.memory_database_url,
            )
        return self._checkpointer

    def _get_test_llm_api_key(self) -> Optional[str]:
        """Get test API key for LLM provider (testing only).

        In production, always fetch from user's DB credentials.
        """
        provider = self.settings.llm_provider.lower()
        key_map = {
            "cohere": self.settings.test_cohere_api_key,
            "openai": self.settings.test_openai_api_key,
            "anthropic": self.settings.test_anthropic_api_key,
            "gemini": self.settings.test_gemini_api_key,
            "groq": self.settings.test_groq_api_key,
            "mistral": self.settings.test_mistral_api_key,
        }
        return key_map.get(provider)


def initialize_registry(settings: Settings) -> AdapterRegistry:
    """Initialize and populate the adapter registry with default implementations."""
    registry = get_registry()

    # Register LLM adapters (wrapping existing factories)
    registry.register_llm("cohere", lambda **kw: create_llm("cohere", **kw))
    registry.register_llm("openai", lambda **kw: create_llm("openai", **kw))
    registry.register_llm("anthropic", lambda **kw: create_llm("anthropic", **kw))
    registry.register_llm("gemini", lambda **kw: create_llm("gemini", **kw))
    registry.register_llm("groq", lambda **kw: create_llm("groq", **kw))
    registry.register_llm("mistral", lambda **kw: create_llm("mistral", **kw))

    # Register embeddings adapters
    registry.register_embeddings(
        "huggingface_local", lambda **kw: create_embeddings("huggingface_local", **kw)
    )
    registry.register_embeddings(
        "huggingface_endpoint",
        lambda **kw: create_embeddings("huggingface_endpoint", **kw),
    )

    # Register web search adapters
    registry.register_web_search(
        "duckduckgo", lambda **kw: create_web_search("duckduckgo", **kw)
    )
    registry.register_web_search(
        "google", lambda **kw: create_web_search("google", **kw)
    )
    registry.register_web_search(
        "tavily", lambda **kw: create_web_search("tavily", **kw)
    )
    registry.register_web_search("serp", lambda **kw: create_web_search("serp", **kw))
    registry.register_web_search("exa", lambda **kw: create_web_search("exa", **kw))

    # Register web scraper adapters
    registry.register_web_scraper(
        "crawl4ai", lambda **kw: create_scraper("crawl4ai", **kw)
    )
    registry.register_web_scraper(
        "firecrawl", lambda **kw: create_scraper("firecrawl", **kw)
    )
    registry.register_web_scraper(
        "scrapedo", lambda **kw: create_scraper("scrapedo", **kw)
    )
    registry.register_web_scraper(
        "scraper", lambda **kw: create_scraper("scraper", **kw)
    )

    # Register storage adapter
    registry.register_storage("supabase", lambda **kw: SupabaseStorage())

    # Register vector store adapters
    registry.register_vector_store("pinecone", lambda **kw: create_vector_store(**kw))

    return registry
