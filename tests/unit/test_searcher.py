"""Unit tests for search functionality."""

import pytest
from unittest.mock import MagicMock, patch
from rag_retriever.search.searcher import Searcher, SearchResult
from langchain_core.documents import Document


@pytest.fixture
def mock_vectorstore():
    """Create a mock VectorStore instance."""
    store = MagicMock()
    store.search.return_value = [
        (
            Document(page_content="Test content 1", metadata={"source": "test1.txt"}),
            0.9,
        ),
        (
            Document(page_content="Test content 2", metadata={"source": "test2.txt"}),
            0.8,
        ),
    ]
    return store


@pytest.fixture
def searcher(mock_vectorstore):
    """Create a Searcher instance with mocked dependencies."""
    with patch(
        "rag_retriever.search.searcher.VectorStore", return_value=mock_vectorstore
    ):
        return Searcher()


def test_search_basic(searcher):
    """Test basic search functionality."""
    results = searcher.search("test query")

    assert len(results) == 2
    assert isinstance(results[0], SearchResult)
    assert results[0].content == "Test content 1"
    assert results[0].source == "test1.txt"
    assert results[0].score == 0.9


def test_search_with_limit(searcher, mock_vectorstore):
    """Test search with result limit."""
    results = searcher.search("test query", limit=1)

    mock_vectorstore.search.assert_called_with(
        "test query",
        limit=1,
        score_threshold=searcher.default_score_threshold,
        search_all_collections=False,
    )
    assert len(results) == 2  # Mock returns 2 results


def test_search_with_threshold(searcher, mock_vectorstore):
    """Test search with score threshold."""
    results = searcher.search("test query", score_threshold=0.85)

    mock_vectorstore.search.assert_called_with(
        "test query",
        limit=searcher.default_limit,
        score_threshold=0.85,
        search_all_collections=False,
    )
    assert len(results) == 2  # Mock returns 2 results


def test_search_all_collections(searcher, mock_vectorstore):
    """Test searching across all collections."""
    results = searcher.search("test query", search_all_collections=True)

    mock_vectorstore.search.assert_called_with(
        "test query",
        limit=searcher.default_limit,
        score_threshold=searcher.default_score_threshold,
        search_all_collections=True,
    )
    assert len(results) == 2


def test_search_no_results(searcher, mock_vectorstore):
    """Test search with no results."""
    mock_vectorstore.search.return_value = []
    results = searcher.search("test query")

    assert len(results) == 0


def test_format_result(searcher):
    """Test result formatting."""
    result = SearchResult(
        content="Test content", source="test.txt", score=0.95, metadata={"type": "text"}
    )

    # Test full content formatting
    formatted = searcher.format_result(result, show_full=True)
    assert "Test content" in formatted
    assert "test.txt" in formatted
    assert "0.9500" in formatted

    # Test truncated content formatting
    long_content = "x" * 300
    result.content = long_content
    formatted = searcher.format_result(result, show_full=False)
    # The actual implementation includes formatting overhead, so we just check for truncation
    assert "..." in formatted


def test_format_result_json(searcher):
    """Test JSON result formatting."""
    result = SearchResult(
        content="Test content", source="test.txt", score=0.95, metadata={"type": "text"}
    )

    json_result = searcher.format_result_json(result)
    assert json_result["content"] == "Test content"
    assert json_result["source"] == "test.txt"
    assert json_result["score"] == 0.95
    assert json_result["metadata"]["type"] == "text"
