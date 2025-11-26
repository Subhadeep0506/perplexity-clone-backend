"""
Adapter protocols for external service integrations.
These protocols define contracts that all implementations must follow.
"""

from .llm import LLMAdapter
from .embeddings import EmbeddingsAdapter
from .storage import StorageAdapter
from .vector_store import VectorStoreAdapter
from .web_search import WebSearchAdapter
from .web_scraper import WebScraperAdapter

__all__ = [
    "LLMAdapter",
    "EmbeddingsAdapter",
    "StorageAdapter",
    "VectorStoreAdapter",
    "WebSearchAdapter",
    "WebScraperAdapter",
]
