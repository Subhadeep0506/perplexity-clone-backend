from langchain.tools import tool
from langgraph.prebuilt import InjectedState
from typing_extensions import Annotated
from typing import Any
from src.services.llm.factory import create_llm
from src.services.memory.factory import create_memory

SYSTEM_PROMPT = """You are an advanced AI assistant designed to provide accurate and concise answers based on the context provided from various tools. Use the retrieved documents and scraped contents to formulate your responses. If the information is insufficient, respond with 'Insufficient information to provide an answer.' Always aim to be clear and helpful in your answers.
Always make sure to refer the chat history for better context and make the conversation flow coherent. Below are the chat history and context from various tools.
### Chat History:
{chat_history}

### Retrieved Documents:
{retrieved_docs}

### Scraped Contents:
{scraped_contents}
"""


@tool(
    description="Use this tool to generate final response using context from previous tools based on a query."
)
async def answer_tool(
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
    llm = create_llm(
        provider=state.get("llm_provider"),
        model=state.get("model"),
        temperature=state.get("temperature"),
        max_tokens=state.get("max_tokens"),
        streaming=state.get("streaming"),
    )
    
    if not llm:
        return "Error: There was an error while initializing the LLM."
    

    try:
        # Fetching history from memory
        chat_history = await memory.asearch(
            (state.get("session_id"),),
        )  # TODO: Add fetching chat history and adding to database and memory.

        # TODO: Model Response

        # Adding response to the chat history
        await memory.aput(
            (state.get("session_id"),),
        )  # TODO: Add fetching chat history and adding to database and memory.

    except Exception as e:
        return f"Error retrieving information: {str(e)}"
