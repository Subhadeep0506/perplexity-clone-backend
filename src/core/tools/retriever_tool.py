from langchain.tools import tool
from langgraph.prebuilt import InjectedState
from typing_extensions import Annotated
from typing import Any


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
    vectorstore = state.get("vectorstore")

    if not vectorstore:
        return "Error: No vectorstore available. Please ensure a vectorstore is initialized in the state."

    try:
        # Retrieve relevant documents using the vectorstore
        # Using similarity_search method (common in LangChain vectorstores)
        docs = await vectorstore.asimilarity_search(query, k=5)

        if not docs:
            return f"No relevant information found for query: {query}"

        # Format the retrieved documents
        retrieved_content = []
        for i, doc in enumerate(docs, 1):
            content = doc.page_content
            metadata = doc.metadata
            retrieved_content.append(
                f"[Document {i}]\n" f"Content: {content}\n" f"Metadata: {metadata}\n"
            )

        # Store retrieved docs in state for reference
        state["retrieved_docs"] = [doc.page_content for doc in docs]

        return "\n".join(retrieved_content)

    except Exception as e:
        return f"Error retrieving information: {str(e)}"
