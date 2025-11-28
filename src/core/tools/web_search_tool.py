from langchain.tools import tool
from langgraph.prebuilt import InjectedState
from typing_extensions import Annotated
from typing import Any
from src.services.web_search.factory import create_web_search


@tool(description="Use this tool to search the web based on a query.")
async def web_search_tool(
    query: str, state: Annotated[dict[str, Any], InjectedState]
) -> str:
    """
    A tool that searches the web based on the given query.

    The web searcher is passed through the agent state and is user-specific,
    initialized based on user's service choices and API keys.

    Args:
        query (str): The query string to search for information.
        state (dict): The agent state containing the web search provider.

    Returns:
        str: A message indicating the number of search results found.
    """
    web_searcher = None

    try:
        web_searcher = create_web_search(
            provider=state.get("web_search_provider"),
        )
    except Exception as e:
        return f"Error initializing web searcher: {str(e)}"

    if not web_searcher:
        return "Error: Web searcher not available. Please ensure it is initialized in the state."

    try:
        # Search web for URLs
        fetched_urls = await web_searcher.arun(query=query)
        state["fetched_urls"] = fetched_urls
        if not fetched_urls:
            return f"No relevant search results found for query: {query}"

        return fetched_urls

    except Exception as e:
        return f"Error retrieving information: {str(e)}"
