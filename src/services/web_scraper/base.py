from __future__ import annotations

import abc
from typing import List

from langchain_core.documents import Document


class BaseCrawler(abc.ABC):
    """Abstract base for web crawler/loaders.

    Implementations should provide `aload(urls)` which returns
    a list of `Document` objects.
    """

    @abc.abstractmethod
    async def aload(self, urls) -> List[Document]:
        raise NotImplementedError("aload must be implemented by subclasses")
