from typing import List
from crawl4ai.models import CrawlResultContainer
from langchain_core.documents import Document
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
from langchain_core.document_loaders import BaseLoader
from src.services.logger import SingletonLogger
from .base import BaseCrawler


class Crawl4AILoader(BaseLoader, BaseCrawler):
    def __init__(self):
        self.browser_config = BrowserConfig()  # Default browser configuration
        self.run_config = CrawlerRunConfig(prettiify=True)

    async def aload(self, urls: List[str]) -> List[Document]:
        logger = SingletonLogger().get_logger()
        documents = []
        try:
            async with AsyncWebCrawler(config=self.browser_config) as crawler:
                result: CrawlResultContainer = await crawler.arun_many(
                    urls=urls, config=self.run_config
                )
                for res in result:
                    for r in res:
                        documents.append(
                            Document(
                                page_content=r.markdown,
                                metadata={
                                    "url": r.url,
                                    "links": r.links,
                                    "media": r.media,
                                    "session_id": r.session_id,
                                    **r.metadata,
                                },
                            )
                        )
        except Exception:
            logger.exception("Error while crawling urls with crawl4ai: %s", urls)

        return documents
