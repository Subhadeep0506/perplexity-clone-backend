from __future__ import annotations

import os
from typing import TYPE_CHECKING

from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

if TYPE_CHECKING:
    from langchain_core.embeddings import Embeddings


def create_vector_store(
    embeddings: Embeddings,
    *,
    index_name: str = "perplexity-clone-docstore",
    dimension: int = 1024,
    metric: str = "cosine",
    api_key: str | None = None,
) -> PineconeVectorStore:
    """
    Create a Pinecone vector store instance.

    Args:
        embeddings: The embeddings instance to use for the vector store
        index_name: Name of the Pinecone index
        dimension: Dimension of the embeddings
        metric: Distance metric to use (cosine, euclidean, dotproduct)
        api_key: Pinecone API key (defaults to PINECONE_API_KEY env var)

    Returns:
        A configured PineconeVectorStore instance
    """
    if api_key is None:
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("Pinecone API KEY is not set")

    client = Pinecone(
        api_key=api_key,
        ssl_verify=False,
    )

    if not client.has_index(index_name):
        index = client.create_index(
            name=index_name,
            dimension=dimension,
            metric=metric,
            vector_type="dense",
        )
    else:
        index = client.Index(index_name)

    return PineconeVectorStore(
        embedding=embeddings,
        index=index,
    )
