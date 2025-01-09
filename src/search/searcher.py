"""Search functionality for the RAG retriever."""

from typing import List, Dict, Any
from dataclasses import dataclass

from src.utils.config import config
from src.vectorstore.store import VectorStore


@dataclass
class SearchResult:
    """Container for search results with metadata."""

    content: str
    source: str
    score: float
    metadata: Dict[str, Any]


class Searcher:
    """Handle search operations and result formatting."""

    def __init__(self, vector_store: VectorStore | None = None):
        """Initialize searcher with vector store.

        Args:
            vector_store: VectorStore instance to use.
                        If None, creates new instance.
        """
        self.vector_store = vector_store or VectorStore()
        self.default_limit = config.search["default_limit"]
        self.default_score_threshold = config.search["default_score_threshold"]

    def search(
        self,
        query: str,
        limit: int | None = None,
        score_threshold: float | None = None,
    ) -> List[SearchResult]:
        """Search for documents matching query.

        Args:
            query: Search query.
            limit: Maximum number of results.
            score_threshold: Minimum relevance score.

        Returns:
            List of SearchResult objects.
        """
        # Use defaults from config if not specified
        limit = limit or self.default_limit
        score_threshold = score_threshold or self.default_score_threshold

        # Get raw results from vector store
        raw_results = self.vector_store.search(
            query,
            limit=limit,
            score_threshold=score_threshold,
        )

        # Convert to SearchResult objects
        results = []
        for doc, score in raw_results:
            result = SearchResult(
                content=doc.page_content,
                source=doc.metadata.get("source", "Unknown source"),
                score=score,
                metadata=doc.metadata,
            )
            results.append(result)

        return results

    def format_result(self, result: SearchResult, show_full: bool = False) -> str:
        """Format a search result for display.

        Args:
            result: SearchResult to format.
            show_full: Whether to show full content.

        Returns:
            Formatted result string.
        """
        # Show full content or preview
        content = result.content
        if not show_full and len(content) > 200:
            content = content[:200] + "..."

        return (
            f"\nSource: {result.source}"
            f"\nRelevance Score: {result.score:.4f}"
            f"\nContent: {content}\n"
            f"\n{'-' * 80}"
        )

    def format_result_json(self, result: SearchResult) -> Dict[str, Any]:
        """Format a search result as JSON.

        Args:
            result: SearchResult to format.

        Returns:
            Dictionary suitable for JSON serialization.
        """
        return {
            "source": result.source,
            "content": result.content,
            "score": float(result.score),  # Ensure score is JSON serializable
            "metadata": result.metadata,
        }
