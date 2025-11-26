"""LLM adapter protocol."""

from typing import Protocol, Any, AsyncIterator
from langchain_core.messages import BaseMessage


class LLMAdapter(Protocol):
    """Protocol for language model adapters."""

    async def agenerate(
        self, messages: list[BaseMessage], **kwargs: Any
    ) -> BaseMessage:
        """Generate a response from messages asynchronously.

        Args:
            messages: List of messages to send to the model
            **kwargs: Additional generation parameters

        Returns:
            Generated message response
        """
        ...

    async def astream(
        self, messages: list[BaseMessage], **kwargs: Any
    ) -> AsyncIterator[BaseMessage]:
        """Stream response from messages asynchronously.

        Args:
            messages: List of messages to send to the model
            **kwargs: Additional generation parameters

        Yields:
            Message chunks as they are generated
        """
        ...
