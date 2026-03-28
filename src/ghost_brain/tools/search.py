"""DuckDuckGo Search tool for the LLM."""

import asyncio
import logging
import random

from ddgs import DDGS
from pipecat.frames.frames import TextFrame
from pipecat.services.llm_service import FunctionCallParams

logger = logging.getLogger(__name__)


async def search_web(params: FunctionCallParams, query: str) -> None:
    """Search the web for real-time information, facts, and documentation.

    Args:
        params: Function call parameters injected by Pipecat.
        query: The search query to look up on the web.
    """
    logger.info(f"LLM Tool Call: Searching web for '{query}'")

    try:
        fillers = [
            "Let me check that for you. ",
            "One second, looking that up. ",
            "Searching the web for that. ",
            "Let me find that. ",
        ]
        await params.llm.push_frame(TextFrame(random.choice(fillers)))

        # Run synchronous DDGS search in a background thread
        def _search():
            with DDGS() as ddgs:
                return list(ddgs.text(query, max_results=3))

        results = await asyncio.to_thread(_search)

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
