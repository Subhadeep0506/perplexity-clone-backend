from typing import Any

from src.lib.enums import WebSearcher

from .google_search import GoogleWebSearch
from .exa_search import ExaWebSearch
from .duckduckgo_search import DuckDuckGoWebSearch
from .tavily_search import TavilyWebSearch
from .serp_search import SerpWebSearch


_MAP = {
    WebSearcher.GOOGLE.value: GoogleWebSearch,
    WebSearcher.EXA.value: ExaWebSearch,
    WebSearcher.TAVILY.value: TavilyWebSearch,
    WebSearcher.SERP.value: SerpWebSearch,
    WebSearcher.DUCKDUCKGO.value: DuckDuckGoWebSearch,
}


def create_web_search(provider: str | WebSearcher, **kwargs: Any):
    """Create a web search implementation by provider name or enum.

    Args:
        provider: `WebSearcher` enum or string value (e.g. 'google', 'exa').
        kwargs: Passed to the implementation constructor.

    Returns:
        Instance of a `BaseWebSearch` implementation.
    """
    if isinstance(provider, WebSearcher):
        key = provider.value
    else:
        key = str(provider).lower()

    cls = _MAP.get(key)
    if not cls:
        raise ValueError(f"Unknown web search provider: {provider}")

    return cls(**kwargs)
