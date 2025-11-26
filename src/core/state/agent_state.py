from typing_extensions import TypedDict
from typing import Annotated, Any, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


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
    temperature: float
    max_tokens: int
    streaming: bool

    # Source configuration
    source_type: str

    # Messages for conversation
    messages: Annotated[list[BaseMessage], add_messages]

    # Services (initialized per user)
    vectorstore: Optional[Any]  # User-specific vectorstore instance
    llm: Optional[Any]  # User-specific LLM instance
    embeddings: Optional[Any]  # User-specific embeddings instance

    # Additional context
    retrieved_docs: Optional[list[str]]  # Documents retrieved by retriever tool
