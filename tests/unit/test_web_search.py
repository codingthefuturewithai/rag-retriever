"""Unit tests for web search functionality."""

import os
import pytest
from unittest.mock import MagicMock, patch
from rag_retriever.search.web_search import (
    SearchResult,
    DuckDuckGoSearchProvider,
    GoogleSearchProvider,
    get_search_provider,
    web_search,
)


@pytest.fixture
def mock_duckduckgo_results():
    """Mock DuckDuckGo search results."""
    return [
        {
            "title": "Test Title 1",
            "link": "https://example.com/1",
            "snippet": "Test snippet 1",
        },
        {
            "title": "Test Title 2",
            "link": "https://example.com/2",
            "snippet": "Test snippet 2",
        },
    ]


@pytest.fixture
def mock_google_results():
    """Mock Google search results."""
    return [
        {
            "title": "Test Title 1",
            "link": "https://example.com/1",
            "snippet": "Test snippet 1",
        },
        {
            "title": "Test Title 2",
            "link": "https://example.com/2",
            "snippet": "Test snippet 2",
        },
    ]


def test_duckduckgo_search_provider(mock_duckduckgo_results):
    """Test DuckDuckGo search provider."""
    with patch(
        "langchain_community.utilities.DuckDuckGoSearchAPIWrapper"
    ) as mock_wrapper:
        mock_instance = MagicMock()
        mock_instance.results.return_value = mock_duckduckgo_results
        mock_wrapper.return_value = mock_instance

        provider = DuckDuckGoSearchProvider()
        results = provider.search("test query", 2)

        assert len(results) == 2
        assert isinstance(results[0], SearchResult)
        assert results[0].title == "Test Title 1"
        assert results[0].url == "https://example.com/1"
        assert results[0].snippet == "Test snippet 1"

        mock_instance.results.assert_called_once_with("test query", max_results=2)


def test_google_search_provider(mock_google_results):
    """Test Google search provider."""
    with patch.dict(os.environ, {"GOOGLE_API_KEY": "test", "GOOGLE_CSE_ID": "test"}):
        with patch("langchain_google_community.GoogleSearchAPIWrapper") as mock_wrapper:
            mock_instance = MagicMock()
            mock_instance.results.return_value = mock_google_results
            mock_wrapper.return_value = mock_instance

            provider = GoogleSearchProvider()
            results = provider.search("test query", 2)

            assert len(results) == 2
            assert isinstance(results[0], SearchResult)
            assert results[0].title == "Test Title 1"
            assert results[0].url == "https://example.com/1"
            assert results[0].snippet == "Test snippet 1"

            mock_instance.results.assert_called_once_with("test query", num_results=2)


def test_google_search_provider_missing_credentials():
    """Test Google search provider with missing credentials."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError) as exc_info:
            GoogleSearchProvider()
        assert "Google Search requires GOOGLE_API_KEY and GOOGLE_CSE_ID" in str(
            exc_info.value
        )


def test_get_search_provider_duckduckgo():
    """Test getting DuckDuckGo search provider."""
    provider = get_search_provider("duckduckgo")
    assert isinstance(provider, DuckDuckGoSearchProvider)


def test_get_search_provider_google():
    """Test getting Google search provider."""
    with patch.dict(os.environ, {"GOOGLE_API_KEY": "test", "GOOGLE_CSE_ID": "test"}):
        provider = get_search_provider("google")
        assert isinstance(provider, GoogleSearchProvider)


def test_get_search_provider_unknown():
    """Test getting unknown search provider."""
    with pytest.raises(ValueError) as exc_info:
        get_search_provider("unknown")
    assert "Unknown search provider: unknown" in str(exc_info.value)


def test_get_search_provider_fallback():
    """Test fallback to DuckDuckGo when Google fails."""
    with patch.dict(os.environ, {}, clear=True):
        provider = get_search_provider("google")
        assert isinstance(provider, DuckDuckGoSearchProvider)


def test_web_search_integration(mock_duckduckgo_results):
    """Test web_search function integration."""
    with patch(
        "langchain_community.utilities.DuckDuckGoSearchAPIWrapper"
    ) as mock_wrapper:
        mock_instance = MagicMock()
        mock_instance.results.return_value = mock_duckduckgo_results
        mock_wrapper.return_value = mock_instance

        results = web_search("test query", num_results=2)

        assert len(results) == 2
        assert isinstance(results[0], SearchResult)
        assert results[0].title == "Test Title 1"
        assert results[0].url == "https://example.com/1"
        assert results[0].snippet == "Test snippet 1"
