"""Web search functionality for RAG Retriever.

This module provides web search capabilities using multiple providers:
1. Google's Programmable Search Engine (requires API key and CSE ID)
2. DuckDuckGo Search (no configuration required)

Provider Selection:
- When no provider specified: Uses default_provider from config
- If Google is default/requested but no credentials:
  - For default: Silently falls back to DuckDuckGo
  - For explicit request: Shows error suggesting DuckDuckGo
- If DuckDuckGo specified: Uses DuckDuckGo directly

Configuration:
1. Google Search credentials can be set via:
   - Environment variables: GOOGLE_API_KEY and GOOGLE_CSE_ID
   - Config file: search.google_search.api_key and search.google_search.cse_id
2. Default provider can be set in config: search.default_provider

Example Usage:
    >>> from rag_retriever.search import web_search
    >>> # Use default provider
    >>> results = web_search("python programming")
    >>> # Use specific provider
    >>> results = web_search("python programming", provider="duckduckgo")
"""

from typing import List, Dict, Protocol, runtime_checkable
from abc import ABC, abstractmethod
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_google_community import GoogleSearchAPIWrapper
from dataclasses import dataclass
import logging
from statistics import mean
import os
from ..utils.config import get_google_search_credentials, config

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str


@runtime_checkable
class SearchProvider(Protocol):
    """Protocol defining the interface for search providers."""

    def search(self, query: str, num_results: int) -> List[SearchResult]:
        """
        Perform a web search and return results.

        Args:
            query: Search query string
            num_results: Number of results to return

        Returns:
            List of SearchResult objects
        """
        ...


class DuckDuckGoSearchProvider:
    """DuckDuckGo search implementation."""

    def __init__(self):
        self.search_wrapper = DuckDuckGoSearchAPIWrapper()

    def search(self, query: str, num_results: int) -> List[SearchResult]:
        logger.debug(f"Performing DuckDuckGo search for query: {query}")
        logger.debug(f"Requested number of results: {num_results}")

        try:
            raw_results = self.search_wrapper.results(query, max_results=num_results)
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return []

        snippet_lengths = [len(result.get("snippet", "")) for result in raw_results]
        logger.debug(f"Number of results returned: {len(raw_results)}")
        if snippet_lengths:
            logger.debug(f"Average snippet length: {mean(snippet_lengths):.1f} chars")
            logger.debug(f"Min snippet length: {min(snippet_lengths)} chars")
            logger.debug(f"Max snippet length: {max(snippet_lengths)} chars")

        return [
            SearchResult(
                title=result.get("title", ""),
                url=result.get("link", ""),
                snippet=result.get("snippet", ""),
            )
            for result in raw_results
        ]


class GoogleSearchProvider:
    """Google Programmable Search Engine implementation."""

    def __init__(self):
        # Get credentials from config or environment
        api_key, cse_id = get_google_search_credentials()

        logger.debug("Google Search credentials check:")
        logger.debug("API Key present: %s", bool(api_key))
        logger.debug("CSE ID present: %s", bool(cse_id))
        logger.debug("Environment variables:")
        logger.debug("GOOGLE_API_KEY: %s", bool(os.getenv("GOOGLE_API_KEY")))
        logger.debug("GOOGLE_CSE_ID: %s", bool(os.getenv("GOOGLE_CSE_ID")))

        if not api_key or not cse_id:
            raise ValueError(
                "Google Search requires GOOGLE_API_KEY and GOOGLE_CSE_ID to be set "
                "via environment variables or config file"
            )

        # Set environment variables for GoogleSearchAPIWrapper
        os.environ["GOOGLE_API_KEY"] = api_key
        os.environ["GOOGLE_CSE_ID"] = cse_id

        try:
            self.search_wrapper = GoogleSearchAPIWrapper()
        except Exception as e:
            logger.error(f"Failed to initialize Google Search wrapper: {e}")
            raise ValueError(f"Failed to initialize Google Search: {e}")

    def search(self, query: str, num_results: int) -> List[SearchResult]:
        logger.debug(f"Performing Google search for query: {query}")
        logger.debug(f"Requested number of results: {num_results}")

        try:
            raw_results = self.search_wrapper.results(query, num_results=num_results)
        except Exception as e:
            logger.error(f"Google search error: {e}")
            return []

        snippet_lengths = [len(result.get("snippet", "")) for result in raw_results]
        logger.debug(f"Number of results returned: {len(raw_results)}")
        if snippet_lengths:
            logger.debug(f"Average snippet length: {mean(snippet_lengths):.1f} chars")
            logger.debug(f"Min snippet length: {min(snippet_lengths)} chars")
            logger.debug(f"Max snippet length: {max(snippet_lengths)} chars")

        return [
            SearchResult(
                title=result.get("title", ""),
                url=result.get("link", ""),
                snippet=result.get("snippet", ""),
            )
            for result in raw_results
        ]


def get_search_provider(provider: str | None = None) -> SearchProvider:
    """
    Factory function to get the appropriate search provider.

    The function follows these rules:
    1. If provider is None, use default from config
    2. If provider is unknown, raise ValueError
    3. If Google is requested (explicitly or by default) but credentials missing:
       - For explicit request: Raise ValueError with message suggesting DuckDuckGo
       - For default: Silently fall back to DuckDuckGo
    4. If DuckDuckGo is requested: Return DuckDuckGo provider

    Args:
        provider: Name of the search provider to use ("duckduckgo" or "google")
                 If None, uses default from config

    Returns:
        SearchProvider instance

    Raises:
        ValueError: If unknown provider specified or if Google explicitly requested
                   but credentials not configured
    """
    # Normalize provider name if provided
    if provider:
        provider = provider.lower()
        # Validate provider name
        if provider not in ["google", "duckduckgo"]:
            raise ValueError(
                f"Unknown search provider: {provider}. "
                "Valid options are 'google' or 'duckduckgo'"
            )
    else:
        # Use default from config
        provider = config.search.get("default_provider", "duckduckgo").lower()

    # Handle Google provider
    if provider == "google":
        try:
            return GoogleSearchProvider()
        except ValueError as e:
            # If explicitly requested, show error
            if provider:
                raise ValueError(
                    "Google Search credentials are not configured. Please try again with "
                    "provider='duckduckgo' or configure Google Search credentials."
                )
            # If default, silently fall back
            logger.debug("Google credentials not found, falling back to DuckDuckGo")
            return DuckDuckGoSearchProvider()

    # For all other cases (including DuckDuckGo and Google fallback)
    return DuckDuckGoSearchProvider()


def web_search(
    query: str,
    num_results: int | None = None,
    provider: str | None = None,
) -> List[SearchResult]:
    """
    Perform a web search using the specified provider.

    The function follows these provider selection rules:
    1. When no provider specified:
       - Uses default_provider from config
       - If Google is default but not configured, silently falls back to DuckDuckGo
    2. When Google explicitly requested but not configured:
       - Shows error message suggesting to use DuckDuckGo
    3. When DuckDuckGo requested:
       - Uses DuckDuckGo directly

    Args:
        query: Search query string
        num_results: Number of results to return (if None, uses default from config)
        provider: Search provider to use ("google" or "duckduckgo")
                 If None, uses default from config.
                 Falls back to DuckDuckGo if Google credentials are not configured.

    Returns:
        List of SearchResult objects containing title, URL, and snippet

    Raises:
        ValueError: If Google is explicitly requested but credentials are not configured
    """
    # Set up search provider
    if provider is None:
        # No explicit provider - try config default or fall back to DuckDuckGo
        try:
            if config.search.get("default_provider") == "google":
                search_provider = GoogleSearchProvider()
            else:
                search_provider = DuckDuckGoSearchProvider()
        except ValueError:
            logger.debug("Google credentials not found, using DuckDuckGo")
            search_provider = DuckDuckGoSearchProvider()
    else:
        # Explicit provider requested - use get_search_provider which handles errors
        search_provider = get_search_provider(provider)

    # Get number of results
    if num_results is None:
        num_results = config.search.get("default_web_results", 5)

    return search_provider.search(query, num_results)
