from typing import List, Dict
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from dataclasses import dataclass
import logging
from statistics import mean

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str


def web_search(query: str, num_results: int = 5) -> List[SearchResult]:
    """
    Perform a web search using DuckDuckGo.

    Args:
        query: Search query string
        num_results: Number of results to return (default: 5)

    Returns:
        List of SearchResult objects containing title, URL, and snippet
    """
    logger.debug(f"Performing web search for query: {query}")
    logger.debug(f"Requested number of results: {num_results}")

    search = DuckDuckGoSearchAPIWrapper()
    raw_results = search.results(query, max_results=num_results)

    snippet_lengths = [len(result.get("snippet", "")) for result in raw_results]
    logger.debug(f"Number of results returned: {len(raw_results)}")
    if snippet_lengths:
        logger.debug(f"Average snippet length: {mean(snippet_lengths):.1f} chars")
        logger.debug(f"Min snippet length: {min(snippet_lengths)} chars")
        logger.debug(f"Max snippet length: {max(snippet_lengths)} chars")

    processed_results = []
    for result in raw_results:
        processed_results.append(
            SearchResult(
                title=result.get("title", ""),
                url=result.get("link", ""),
                snippet=result.get("snippet", ""),
            )
        )

    return processed_results
