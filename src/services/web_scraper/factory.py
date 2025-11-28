from typing import Any

from src.lib.enums import WebScraper

from .scrape_do import ScrapeDoLoader
from .crawl4ai import Crawl4AILoader
from .firecrawl import FirecrawlLoader
from .scraper import ScraperAPILoader


_MAP = {
    WebScraper.SCRAPEDO.value: ScrapeDoLoader,
    WebScraper.CRAWL4AI.value: Crawl4AILoader,
    WebScraper.FIRECRAWL.value: FirecrawlLoader,
    WebScraper.SCRAPER.value: ScraperAPILoader,
}


def create_scraper(provider: str | WebScraper, **kwargs: Any):
    """Create a web scraper implementation by provider name or enum.
    ```python
    scraper = create_scraper(provider='scrapedo', api_key='your_api_key')
    results = await scraper.aload(url='https://example.com')
    # results = [Document(page_content='...', metadata={...}), ...]
    ```
    Returns:
        Instance of a `BaseWebScraper` implementation.

    """
    if isinstance(provider, WebScraper):
        key = provider.value
    else:
        key = str(provider).lower()

    cls = _MAP.get(key)
    if not cls:
        raise ValueError(f"Unknown scraper provider: {provider}")

    return cls(**kwargs)
