from __future__ import annotations

import subprocess
from typing import Any

from src.lib.enums import EmbeddingProvider

try:
    from langchain_huggingface import HuggingFaceEmbeddings as _HuggingFaceEmbeddings
except Exception as e:
    _HuggingFaceEmbeddings = None
    _HuggingFaceEmbeddings_err = e

try:
    from langchain_huggingface import (
        HuggingFaceEndpointEmbeddings as _HuggingFaceEndpointEmbeddings,
    )
except Exception as e:
    _HuggingFaceEndpointEmbeddings = None
    _HuggingFaceEndpointEmbeddings_err = e


def _check_gpu_availability() -> bool:
    """Check if NVIDIA GPU is available using nvidia-smi."""
    try:
        result = subprocess.run(
            ["nvidia-smi"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _get_device() -> str:
    """Get the device to use for embeddings (cuda if available, else cpu)."""
    if _check_gpu_availability():
        try:
            import torch  # type: ignore

            if torch.cuda.is_available():
                return "cuda"
        except ImportError:
            pass
    return "cpu"


def _lower_key(provider: str | EmbeddingProvider) -> str:
    if isinstance(provider, EmbeddingProvider):
        return provider.value
    return str(provider).lower()


def create_embeddings(
    provider: str | EmbeddingProvider,
    *,
    model_name: str | None = None,
    api_key: str | None = None,
    device: str | None = None,
    **kwargs: Any,
):
    """
    Create an embeddings instance based on the provider.

    Args:
        provider: The embedding provider (huggingface_local or huggingface_endpoint)
        model_name: The name/repo_id of the embedding model
        api_key: API key for endpoint-based embeddings
        device: Device to use for local embeddings (auto-detected if not provided)
        **kwargs: Additional arguments to pass to the embeddings class

    Returns:
        An embeddings instance
    """
    key = _lower_key(provider)

    # Set default model if not provided
    if model_name is None:
        model_name = "intfloat/multilingual-e5-large-instruct"

    if key == EmbeddingProvider.HUGGINGFACE_LOCAL.value:
        if _HuggingFaceEmbeddings is None:
            raise ImportError(
                "LangChain HuggingFace adapter not installed; install 'langchain_huggingface'"
            ) from _HuggingFaceEmbeddings_err

        # Auto-detect device if not provided
        if device is None:
            device = _get_device()

        model_kwargs = kwargs.pop("model_kwargs", {})
        model_kwargs["device"] = device

        return _HuggingFaceEmbeddings(
            model_name=model_name, model_kwargs=model_kwargs, **kwargs
        )

    if key == EmbeddingProvider.HUGGINGFACE_ENDPOINT.value:
        if _HuggingFaceEndpointEmbeddings is None:
            raise ImportError(
                "LangChain HuggingFace adapter not installed; install 'langchain_huggingface'"
            ) from _HuggingFaceEndpointEmbeddings_err

        common = {"repo_id": model_name}
        if api_key is not None:
            common["huggingfacehub_api_token"] = api_key

        return _HuggingFaceEndpointEmbeddings(**common, **kwargs)

    raise ValueError(f"Unknown or unsupported embedding provider: {provider}")
