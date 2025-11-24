import asyncio
import os
from typing import List, Dict, Optional

from src.services.logger import SingletonLogger
from .base import BaseWebSearch

from googleapiclient.discovery import build


class GoogleWebSearch(BaseWebSearch):
    """Wrapper for Google Programmable Search (Custom Search) API.

    Usage:
      ```python
      gw = GoogleWebSearch(api_key=..., cx=...)
      results = await gw.arun("your query", num=5)
      ```
    Returns list of dicts with keys: `title`, `url`, `snippet`.
    """

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.cx = os.getenv("GOOGLE_CUSTOM_SEARCH_CX")

    async def arun(self, query: str, num: int = 10) -> List[Dict[str, str]]:
        logger = SingletonLogger().get_logger()
        loop = asyncio.get_event_loop()

        def _call_api():
            service = build("customsearch", "v1", developerKey=self.api_key)
            return (
                service.cse()
                .list(q=query, cx=self.cx, num=min(max(1, num), 10))
                .execute()
            )

        try:
            res = await loop.run_in_executor(None, _call_api)
        except Exception as e:
            logger.exception("Error calling Custom Search API: %s", e)
            return []

        items = res.get("items") or []
        search_results: List[Dict[str, str]] = []

        for it in items:
            title = it.get("title") or "(no title)"
            link = it.get("link") or it.get("formattedUrl") or "(no url)"
            snippet = it.get("snippet") or it.get("htmlSnippet") or "(no snippet)"
            search_results.append({"title": title, "url": link, "snippet": snippet})

        return search_results
