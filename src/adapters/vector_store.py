"""Vector store adapter protocol."""

from typing import Protocol, Any
from langchain_core.documents import Document


class VectorStoreAdapter(Protocol):
    """Protocol for vector store adapters."""

    async def aadd_documents(
        self, documents: list[Document], **kwargs: Any
    ) -> list[str]:
        """Add documents to the vector store asynchronously.

        Args:
            documents: List of documents to add
            **kwargs: Additional parameters

        Returns:
            List of document IDs
        """
        ...

    async def asimilarity_search(
        self, query: str, k: int = 4, **kwargs: Any
    ) -> list[Document]:
        """Search for similar documents asynchronously.

        Args:
            query: Search query
            k: Number of results to return
            **kwargs: Additional search parameters

        Returns:
            List of similar documents
        """
        ...

    async def adelete(self, ids: list[str], **kwargs: Any) -> bool:
        """Delete documents from vector store asynchronously.

        Args:
            ids: List of document IDs to delete
            **kwargs: Additional parameters

        Returns:
            True if successful
        """
        ...
