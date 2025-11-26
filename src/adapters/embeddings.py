"""Embeddings adapter protocol."""

from typing import Protocol, Any


class EmbeddingsAdapter(Protocol):
    """Protocol for embeddings adapters."""

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of documents asynchronously.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        ...

    async def aembed_query(self, text: str) -> list[float]:
        """Generate embedding for a single query asynchronously.

        Args:
            text: Query text to embed

        Returns:
            Embedding vector
        """
        ...
