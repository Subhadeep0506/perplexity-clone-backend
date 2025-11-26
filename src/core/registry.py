"""Service adapter registry for pluggable provider implementations."""

from typing import Any, Callable, Dict, Type, TypeVar
from src.adapters import (
    LLMAdapter,
    EmbeddingsAdapter,
    StorageAdapter,
    VectorStoreAdapter,
    WebSearchAdapter,
    WebScraperAdapter,
)

T = TypeVar("T")


class AdapterRegistry:
    """Registry for adapter implementations."""

    def __init__(self):
        self._llm_adapters: Dict[str, Callable[..., Any]] = {}
        self._embedding_adapters: Dict[str, Callable[..., Any]] = {}
        self._storage_adapters: Dict[str, Callable[..., Any]] = {}
        self._vector_store_adapters: Dict[str, Callable[..., Any]] = {}
        self._web_search_adapters: Dict[str, Callable[..., Any]] = {}
        self._web_scraper_adapters: Dict[str, Callable[..., Any]] = {}

    def register_llm(self, name: str, factory: Callable[..., LLMAdapter]) -> None:
        """Register an LLM adapter factory."""
        self._llm_adapters[name.lower()] = factory

    def register_embeddings(
        self, name: str, factory: Callable[..., EmbeddingsAdapter]
    ) -> None:
        """Register an embeddings adapter factory."""
        self._embedding_adapters[name.lower()] = factory

    def register_storage(
        self, name: str, factory: Callable[..., StorageAdapter]
    ) -> None:
        """Register a storage adapter factory."""
        self._storage_adapters[name.lower()] = factory

    def register_vector_store(
        self, name: str, factory: Callable[..., VectorStoreAdapter]
    ) -> None:
        """Register a vector store adapter factory."""
        self._vector_store_adapters[name.lower()] = factory

    def register_web_search(
        self, name: str, factory: Callable[..., WebSearchAdapter]
    ) -> None:
        """Register a web search adapter factory."""
        self._web_search_adapters[name.lower()] = factory

    def register_web_scraper(
        self, name: str, factory: Callable[..., WebScraperAdapter]
    ) -> None:
        """Register a web scraper adapter factory."""
        self._web_scraper_adapters[name.lower()] = factory

    def get_llm(self, name: str, **kwargs: Any) -> LLMAdapter:
        """Get an LLM adapter instance."""
        factory = self._llm_adapters.get(name.lower())
        if not factory:
            raise ValueError(f"Unknown LLM adapter: {name}")
        return factory(**kwargs)

    def get_embeddings(self, name: str, **kwargs: Any) -> EmbeddingsAdapter:
        """Get an embeddings adapter instance."""
        factory = self._embedding_adapters.get(name.lower())
        if not factory:
            raise ValueError(f"Unknown embeddings adapter: {name}")
        return factory(**kwargs)

    def get_storage(self, name: str, **kwargs: Any) -> StorageAdapter:
        """Get a storage adapter instance."""
        factory = self._storage_adapters.get(name.lower())
        if not factory:
            raise ValueError(f"Unknown storage adapter: {name}")
        return factory(**kwargs)

    def get_vector_store(self, name: str, **kwargs: Any) -> VectorStoreAdapter:
        """Get a vector store adapter instance."""
        factory = self._vector_store_adapters.get(name.lower())
        if not factory:
            raise ValueError(f"Unknown vector store adapter: {name}")
        return factory(**kwargs)

    def get_web_search(self, name: str, **kwargs: Any) -> WebSearchAdapter:
        """Get a web search adapter instance."""
        factory = self._web_search_adapters.get(name.lower())
        if not factory:
            raise ValueError(f"Unknown web search adapter: {name}")
        return factory(**kwargs)

    def get_web_scraper(self, name: str, **kwargs: Any) -> WebScraperAdapter:
        """Get a web scraper adapter instance."""
        factory = self._web_scraper_adapters.get(name.lower())
        if not factory:
            raise ValueError(f"Unknown web scraper adapter: {name}")
        return factory(**kwargs)


# Global registry instance
_registry: AdapterRegistry | None = None


def get_registry() -> AdapterRegistry:
    """Get or create the global adapter registry."""
    global _registry
    if _registry is None:
        _registry = AdapterRegistry()
    return _registry
