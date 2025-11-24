import requests
import urllib.parse
import os
import asyncio
from typing import List

from langchain_core.documents import Document
from langchain_core.document_loaders import BaseLoader
from src.services.logger import SingletonLogger
from .base import BaseCrawler


class ScrapeDoLoader(BaseLoader, BaseCrawler):
    """Loader that uses the ScrapeDo API to scrape web pages."""

    def __init__(self):
        """Initialize with URL and API key."""
        self.api_key = os.getenv("SCRAPEDO_CRAWLER_API_KEY")

    async def aload(self, urls: List[str]) -> List[Document]:
        logger = SingletonLogger().get_logger()
        try:
            if not urls:
                return []
            if isinstance(urls, str):
                urls = [urls]

            async def _load_single(u: str) -> List[Document]:
                try:
                    # build request URL for ScrapeDo
                    target = urllib.parse.quote(u)
                    req_url = f"http://api.scrape.do/?token={os.getenv('SCRAPEDO_CRAWLER_API_KEY')}&url={target}&output=markdown"

                    # run blocking request in thread
                    resp = await asyncio.to_thread(requests.get, req_url)
                    if resp is None or resp.status_code != 200:
                        logger.warning(
                            "ScrapeDo returned non-200 for %s: %s",
                            u,
                            getattr(resp, "status_code", None),
                        )
                        return []

                    text = resp.text or ""

                    doc = Document(
                        page_content=text,
                        metadata={
                            "url": u,
                            "source": "scrape.do",
                            "status_code": resp.status_code,
                            "response_url": resp.url,
                        },
                    )
                    return [doc]
                except Exception:
                    logger.exception("Error while loading url with scrape.do: %s", u)
                    return []

            tasks = [_load_single(u) for u in urls]
            results = await asyncio.gather(*tasks)

            documents: List[Document] = []
            for res in results:
                if res:
                    documents.extend(res)

            return documents
        except Exception:
            logger.exception("Error while loading urls with scrape.do: %s", urls)
            return []
