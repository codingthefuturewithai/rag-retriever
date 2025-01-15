from typing import List, Dict
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from dataclasses import dataclass


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
    search = DuckDuckGoSearchAPIWrapper()
    raw_results = search.results(query, max_results=num_results)

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
