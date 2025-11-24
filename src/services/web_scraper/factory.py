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


def create_crawler(provider: str | WebScraper, **kwargs: Any):
    if isinstance(provider, WebScraper):
        key = provider.value
    else:
        key = str(provider).lower()

    cls = _MAP.get(key)
    if not cls:
        raise ValueError(f"Unknown crawler provider: {provider}")

    return cls(**kwargs)
