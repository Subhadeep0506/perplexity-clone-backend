from langchain.tools import tool
from langgraph.prebuilt import InjectedState
from typing_extensions import Annotated
from typing import Any
from src.services.web_scraper.factory import create_scraper


@tool(description="Use this tool to scrape websites based on previously searched URLs.")
async def web_scrape_tool(state: Annotated[dict[str, Any], InjectedState]) -> str:
    """
    A tool that scrapes websites based on the URLs stored in the state from a previous web search.

    The web scraper is passed through the agent state and is user-specific,
    initialized based on user's service choices and API keys.

    Args:
        state (dict): The agent state containing the fetched URLs and scraper provider.

    Returns:
        str: The retrieved information formatted as a string.
    """
    web_scraper = None

    try:
        web_scraper = create_scraper(
            provider=state.get("web_scraper_provider"),
        )
    except Exception as e:
        return f"Error initializing web scraper: {str(e)}"

    if not web_scraper:
        return "Error: Web scraper not available. Please ensure it is initialized in the state."

    fetched_urls = state.get("fetched_urls")
    if not fetched_urls:
        return (
            "Error: No search results available. Please run the web search tool first."
        )

    try:
        # Scrape contents from URLs
        scraped_contents = await web_scraper.arun(
            urls=[res["link"] for res in fetched_urls]
        )
        if not scraped_contents:
            return "No relevant information found from the searched URLs."

        state["scraped_contents"] = scraped_contents
        return "\n".join([doc.page_content for doc in scraped_contents])

    except Exception as e:
        return f"Error retrieving information: {str(e)}"
