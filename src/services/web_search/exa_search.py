import asyncio
import os
from typing import List, Dict, Optional

from langchain_exa.tools import ExaSearchResults
from exa_py.api import SearchResponse

from src.services.logger import SingletonLogger
from .base import BaseWebSearch


class ExaWebSearch(BaseWebSearch):
    """Wrapper for Exa search tool.

    Example:
      ex = ExaWebSearch(api_key='...')
      results = await ex.arun('query', num=5)
    """

    def __init__(
        self,
    ):
        self.exa_api_key = os.getenv("EXA_SEARCH_API_KEY")

    async def arun(
        self,
        query: str,
        num: int = 10,
        livecrawl: str = "never",
        highlights: bool = True,
        text_contents_options: bool = False,
    ) -> List[Dict[str, str]]:
        logger = SingletonLogger().get_logger()

        def _call():
            tool = ExaSearchResults(exa_api_key=self.exa_api_key)
            return tool._run(
                query=query,
                num_results=min(max(1, num), 10),
                livecrawl=livecrawl,
                highlights=highlights,
                text_contents_options=text_contents_options,
            )

        loop = asyncio.get_event_loop()
        try:
            res: SearchResponse = await loop.run_in_executor(None, _call)
        except Exception as e:
            logger.exception("Error calling Exa Search API: %s", e)
            return []

        results: List[Dict[str, str]] = []
        for r in getattr(res, "results", []) or []:
            try:
                title = getattr(r, "title", "(no title)")
                url = getattr(r, "url", "(no url)")
                highlights_list = getattr(r, "highlights", []) or []
                snippet = (
                    "\n".join(highlights_list) if highlights_list else "(no snippet)"
                )
                results.append({"title": title, "url": url, "snippet": snippet})
            except Exception:
                logger.exception("Error parsing Exa result: %s", r)
        return results
