"""DuckDuckGo Search tool for the LLM."""

import logging
from typing import Any

from duckduckgo_search import AsyncDDGS

logger = logging.getLogger(__name__)


async def perform_web_search(params: Any) -> None:
    """Search the web for real-time information, facts, and documentation."""
    query = params.arguments.get("query")
    max_results = params.arguments.get("max_results", 3)

    if not query:
        await params.result_callback("Error: No search query provided.")
        return

    logger.info(f"LLM Tool Call: Searching web for '{query}'")

    try:
        # Use AsyncDDGS for non-blocking search
        results = await AsyncDDGS().text(query, max_results=max_results)

        if not results:
            await params.result_callback(f"No results found for query: {query}")
            return

        # Format the results into a readable string for the LLM
        formatted_results = [f"Search Results for '{query}':\n"]
        for i, r in enumerate(results, 1):
            title = r.get("title", "No Title")
            body = r.get("body", "No Snippet")
            formatted_results.append(f"{i}. {title}\n   {body}\n")

        final_text = "\n".join(formatted_results)
        await params.result_callback(final_text)

    except Exception as e:
        logger.exception(f"Error performing web search: {e}")
        await params.result_callback(f"An error occurred while searching: {str(e)}")
