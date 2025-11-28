from typing_extensions import TypedDict
from typing import Annotated, Any, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langchain_core.documents import Document


class AgentState(TypedDict):
    """State for LangGraph agent with user-specific services.

    Services like vectorstore, llm, and embeddings are initialized
    based on user choice and passed through state to tools and nodes.
    """

    # User context
    session_id: str
    user_id: str
    service_id: str
    api_key_id: str

    # LLM configuration
    model: str
    temperature: float
    max_tokens: int
    streaming: bool

    # Service providers
    llm_provider: str
    embeddings_provider: str
    vectorstore_provider: str
    web_search_provider: Optional[str]
    web_scraper_provider: Optional[str]
    memory_provider: Optional[str]
    checkpoint_provider: Optional[str]

    # Source configuration
    source_type: str

    # Services (initialized per user)
    vectorstore: Optional[Any]  # User-specific vectorstore instance
    llm: Optional[Any]  # User-specific LLM instance
    embeddings: Optional[Any]  # User-specific embeddings instance
    web_searcher: Optional[Any]  # User-specific web searcher instance
    web_search_provider: Optional[str]  # User-specific web search provider
    web_scraper: Optional[Any]  # User-specific web scraper instance
    web_scraper_provider: Optional[str]  # User-specific web scraper provider

    # Additional context
    retrieved_docs: Optional[list[Document]]  # Documents retrieved by retriever tool
    fetched_urls: Optional[list[str]]  # URLs fetched by web scrape tool
    scraped_contents: Optional[list[Document]]  # Contents scraped by web scrape tool
