from langchain.tools import tool
from langgraph.prebuilt import InjectedState
from typing_extensions import Annotated
from typing import Any
<<<<<<< HEAD
=======
from src.services.vector_store.factory import create_vector_store
>>>>>>> 5ecda7e (Added few more changes to tables)


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
<<<<<<< HEAD
    vectorstore = state.get("vectorstore")
=======
    vectorstore = create_vector_store(embeddings=state.get("embeddings"))
>>>>>>> 5ecda7e (Added few more changes to tables)

    if not vectorstore:
        return "Error: No vectorstore available. Please ensure a vectorstore is initialized in the state."

    try:
<<<<<<< HEAD
        # Retrieve relevant documents using the vectorstore
        # Using similarity_search method (common in LangChain vectorstores)
        docs = await vectorstore.asimilarity_search(query, k=5)
=======
        retriever = vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": 15, "fetch_k": 30}
        )
        docs = await retriever._aget_relevant_documents(query, run_manager=None)
>>>>>>> 5ecda7e (Added few more changes to tables)

        if not docs:
            return f"No relevant information found for query: {query}"

<<<<<<< HEAD
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
=======
        state["retrieved_docs"] = docs
        return docs
>>>>>>> 5ecda7e (Added few more changes to tables)

    except Exception as e:
        return f"Error retrieving information: {str(e)}"
