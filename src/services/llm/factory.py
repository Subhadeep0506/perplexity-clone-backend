import os
from __future__ import annotations

from typing import Any

from src.lib.enums import LLMProvider

try:
    from langchain_cohere import ChatCohere as _ChatCohere
except Exception as e:
    _ChatCohere = None
    _ChatCohere_err = e

try:
    from langchain_google_genai import ChatGoogleGenerativeAI as _ChatGemini
except Exception as e:  # pragma: no cover
    _ChatGemini = None
    _ChatGemini_err = e

try:
    from langchain_groq import ChatGroq as _ChatGroq
except Exception as e:  # pragma: no cover
    _ChatGroq = None
    _ChatGroq_err = e

try:
    from langchain_mistralai import ChatMistralAI as _ChatMistral
except Exception as e:  # pragma: no cover
    _ChatMistral = None
    _ChatMistral_err = e

try:
    from langchain_openai import ChatOpenAI as _ChatOpenAI
except Exception as e:  # pragma: no cover
    _ChatOpenAI = None
    _ChatOpenAI_err = e

try:
    from langchain_anthropic import ChatAnthropic as _ChatAnthropic
except Exception as e:  # pragma: no cover
    _ChatAnthropic = None
    _ChatAnthropic_err = e


def _lower_key(provider: str | LLMProvider) -> str:
    if isinstance(provider, LLMProvider):
        return provider.value
    return str(provider).lower()


def create_llm(
    provider: str | LLMProvider,
    *,
    model: str | None = None,
    api_key: str | None = None,
    temperature: float | None = 0.5,
    max_tokens: int | None = 1024,
    streaming: bool | None = False,
    base_url: str | None = None,
    **kwargs: Any,
):
    key = _lower_key(provider)
    common = {}
    if model is not None:
        common["model"] = model
    if api_key is not None:
        common.update(
            {
                "api_key": api_key,
                "cohere_api_key": api_key,
                "mistral_api_key": api_key,
                "anthropic_api_key": api_key,
                "google_api_key": api_key,
            }
        )
    if temperature is not None:
        common["temperature"] = temperature
    if max_tokens is not None:
        common["max_tokens"] = max_tokens
    if streaming is not None:
        common["streaming"] = streaming
    if base_url is not None:
        common["base_url"] = base_url

    if key == LLMProvider.COHERE.value:
        if _ChatCohere is None:
            raise ImportError(
                "LangChain Cohere adapter not installed; install 'langchain_cohere'"
            )
        return _ChatCohere(**common, **kwargs)

    if key == LLMProvider.GEMINI.value:
        if _ChatGemini is None:
            raise ImportError(
                "LangChain Google GenAI adapter not installed; install 'langchain_google_genai'"
            )
        return _ChatGemini(**common, **kwargs)

    if key == LLMProvider.GROQ.value:
        if _ChatGroq is None:
            raise ImportError(
                "LangChain Groq adapter not installed; install 'langchain_groq'"
            )
        return _ChatGroq(**common, **kwargs)

    if key == LLMProvider.MISTRAL.value:
        if _ChatMistral is None:
            raise ImportError(
                "LangChain Mistral adapter not installed; install 'langchain_mistralai'"
            )
        return _ChatMistral(**common, **kwargs)

    if key in (LLMProvider.NIM.value, LLMProvider.OPENROUTER.value):
        if _ChatOpenAI is None:
            raise ImportError(
                "LangChain OpenAI adapter not installed; install 'langchain_openai'"
            )
        if key == LLMProvider.NIM.value:
            kwargs["base_url"] = os.getenv("NIM_BASE_URL", "")
        if key == LLMProvider.OPENROUTER.value:
            kwargs["base_url"] = os.getenv("OPENROUTER_BASE_URL", "")
        return _ChatOpenAI(**common, **kwargs)

    if key == LLMProvider.ANTHROPIC.value:
        if _ChatAnthropic is None:
            raise ImportError(
                "LangChain Anthropic adapter not installed; install 'langchain_anthropic'"
            )
        return _ChatAnthropic(**common, **kwargs)

    raise ValueError(
        f"Unknown or unsupported LLM provider for LangChain-only mode: {provider}"
    )
