import requests
import os
import asyncio
from typing import List

from langchain_core.documents import Document
from langchain_core.document_loaders import BaseLoader
from src.services.logger import SingletonLogger
from .base import BaseCrawler


class ScraperAPILoader(BaseLoader, BaseCrawler):
    """Loader that uses ScraperAPI to fetch pages and return Documents."""

    def __init__(self):
        self.api_key = os.getenv("SCRAPER_CRAWLER_API_KEY")

    async def _load_single(self, url: str) -> List[Document]:
        logger = SingletonLogger().get_logger()
        try:
            params = {
                "api_key": self.api_key,
                "url": url,
                "output_format": "markdown",
                "device_type": "desktop",
                "max_cost": "5",
            }

            resp = await asyncio.to_thread(
                requests.get, "https://api.scraperapi.com/", params=params
            )
            if resp is None or resp.status_code != 200:
                logger.warning(
                    "ScraperAPI returned non-200 for %s: %s",
                    url,
                    getattr(resp, "status_code", None),
                )
                return []

            text = resp.text or ""
            doc = Document(
                page_content=text,
                metadata={
                    "url": url,
                    "source": "scraperapi",
                    "status_code": resp.status_code,
                    "response_url": resp.url,
                },
            )
            return [doc]
        except Exception:
            logger.exception("Error while loading url with scraperapi: %s", url)
            return []

    async def aload(self, urls: List[str]) -> List[Document]:
        logger = SingletonLogger().get_logger()
        try:
            if not urls:
                return []
            if isinstance(urls, str):
                urls = [urls]

            tasks = [self._load_single(u) for u in urls]
            results = await asyncio.gather(*tasks)

            documents: List[Document] = []
            for res in results:
                if res:
                    documents.extend(res)

            return documents
        except Exception:
            logger.exception("Error while loading urls with scraperapi: %s", urls)
            return []
