import asyncio
import os
from typing import List, Dict, Optional

from langchain_community.utilities import SerpAPIWrapper

from src.services.logger import SingletonLogger
from .base import BaseWebSearch


class SerpWebSearch(BaseWebSearch):
    """Wrapper for SerpAPI via langchain_community.SerpAPIWrapper."""

    def __init__(self, engine: str = "google"):
        self.serpapi_api_key = os.getenv("SERPAPI_API_KEY")
        self.engine = engine

    async def arun(
        self, query: str, num: int = 10, engine: Optional[str] = None
    ) -> List[Dict[str, str]]:
        logger = SingletonLogger().get_logger()
        engine = engine or self.engine

        def _call():
            wrapper = SerpAPIWrapper(
                search_engine="google_light",
                params={"engine": engine},
                serpapi_api_key=self.serpapi_api_key,
            )
            return wrapper.results(query)

        loop = asyncio.get_event_loop()
        try:
            raw = await loop.run_in_executor(None, _call)
        except Exception as e:
            logger.exception("Error calling SerpAPI: %s", e)
            return []

        results: List[Dict[str, str]] = []
        for item in raw.get("organic_results", []) if isinstance(raw, dict) else []:
            try:
                title = item.get("title") or "(no title)"
                url = item.get("link") or item.get("url") or "(no url)"
                snippet = (
                    item.get("snippet") or item.get("snippet_text") or "(no snippet)"
                )
                results.append({"title": title, "url": url, "snippet": snippet})
            except Exception:
                logger.exception("Error parsing Serp result: %s", item)

        return results
