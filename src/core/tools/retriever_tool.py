from langchain.tools import tool
from langgraph.prebuilt import InjectedState
from typing_extensions import Annotated
from typing import Any
from src.services.vector_store.factory import create_vector_store


@tool(
    description="Use this tool to retrieve relevant chunks from the vector store based on a query."
)
async def retriever_tool(
    query: str, state: Annotated[dict[str, Any], InjectedState]
) -> str:
    """
    A tool that retrieves information from the vectorstore based on the given query.

    The vectorstore is passed through the agent state and is user-specific,
    initialized based on user's service choices and API keys.

    Args:
        query (str): The query string to search for information.
        state (dict): The agent state containing the vectorstore instance.

    Returns:
        str: The retrieved information formatted as a string.
    """
    vectorstore = create_vector_store(embeddings=state.get("embeddings"))

    if not vectorstore:
        return "Error: No vectorstore available. Please ensure a vectorstore is initialized in the state."

    try:
        retriever = vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": 15, "fetch_k": 30}
        )
        docs = await retriever._aget_relevant_documents(query, run_manager=None)

        if not docs:
            return f"No relevant information found for query: {query}"

        state["retrieved_docs"] = docs
        return docs

    except Exception as e:
        return f"Error retrieving information: {str(e)}"
