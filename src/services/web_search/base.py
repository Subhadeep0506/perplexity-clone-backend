from __future__ import annotations

import abc
from typing import List, Dict


class BaseWebSearch(abc.ABC):
    """Abstract base class for web search wrappers.

    Implementations must provide `arun` which performs an async search and
    returns a list of dicts with keys: `title`, `url`, `snippet`.
    """

    @abc.abstractmethod
    async def arun(self, query: str, num: int = 10, **kwargs) -> List[Dict[str, str]]:
        raise NotImplementedError()
