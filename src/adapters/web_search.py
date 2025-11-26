"""Web search adapter protocol."""

from typing import Protocol, Any


class WebSearchAdapter(Protocol):
    """Protocol for web search adapters."""

    async def asearch(
        self, query: str, num_results: int = 10, **kwargs: Any
    ) -> list[dict[str, Any]]:
        """Perform web search asynchronously.

        Args:
            query: Search query
            num_results: Number of results to return
            **kwargs: Additional search parameters

        Returns:
            List of search results with keys like 'title', 'url', 'snippet'
        """
        ...
