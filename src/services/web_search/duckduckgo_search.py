import asyncio
from typing import List, Dict

from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

from src.services.logger import SingletonLogger
from .base import BaseWebSearch


class DuckDuckGoWebSearch(BaseWebSearch):
    """Wrapper for DuckDuckGo search via langchain_community."""

    def __init__(self, backend: str = "all", num_results: int = 10):
        self.backend = backend
        self.num_results = min(max(1, num_results), 50)

    async def arun(
        self, query: str, num: int = 10, backend: str = None
    ) -> List[Dict[str, str]]:
        logger = SingletonLogger().get_logger()
        backend = backend or self.backend

        def _call():
            api_wrapper = DuckDuckGoSearchAPIWrapper(backend=backend)
            search = DuckDuckGoSearchResults(
                output_format="list",
                num_results=min(max(1, num), self.num_results),
                api_wrapper=api_wrapper,
            )
            return search.run(tool_input=query)

        loop = asyncio.get_event_loop()
        try:
            raw = await loop.run_in_executor(None, _call)
        except Exception as e:
            logger.exception("Error calling DuckDuckGo search: %s", e)
            return []

        results: List[Dict[str, str]] = []
        # raw may be a list of strings or dicts depending on output_format
        if isinstance(raw, list):
            for item in raw:
                if isinstance(item, dict):
                    title = item.get("title") or item.get("text") or "(no title)"
                    url = item.get("href") or item.get("url") or "(no url)"
                    snippet = item.get("snippet") or item.get("text") or "(no snippet)"
                else:
                    # fallback: treat as plain string
                    title = str(item)
                    url = "(no url)"
                    snippet = str(item)
                results.append({"title": title, "url": url, "snippet": snippet})
        else:
            # fallback: single string
            text = str(raw)
            results.append({"title": text, "url": "(no url)", "snippet": text})

        return results
