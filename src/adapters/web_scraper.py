"""Web scraper adapter protocol."""

from typing import Protocol
from langchain_core.documents import Document


class WebScraperAdapter(Protocol):
    """Protocol for web scraper adapters."""

    async def aload(self, urls: list[str]) -> list[Document]:
        """Load and scrape web pages asynchronously.

        Args:
            urls: List of URLs to scrape

        Returns:
            List of documents with scraped content
        """
        ...
