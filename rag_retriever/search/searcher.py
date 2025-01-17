"""Search functionality for the RAG retriever."""

import json
import logging
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass
from statistics import mean

from rag_retriever.utils.config import config
from rag_retriever.vectorstore.store import VectorStore

logger = logging.getLogger(__name__)


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
        limit = self.default_limit if limit is None else limit
        score_threshold = (
            self.default_score_threshold if score_threshold is None else score_threshold
        )

        logger.debug(f"Search query: {query}")
        logger.debug(f"Result limit: {limit}")
        logger.debug(f"Score threshold: {score_threshold}")

        # Get raw results from vector store
        raw_results = self.vector_store.search(
            query,
            limit=limit,
            score_threshold=score_threshold,
        )

        scores = [score for _, score in raw_results]
        logger.debug(f"Number of results found: {len(raw_results)}")
        if scores:
            logger.debug(f"Average relevance score: {mean(scores):.4f}")
            logger.debug(f"Max relevance score: {max(scores):.4f}")
            logger.debug(f"Min relevance score: {min(scores):.4f}")

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
            logger.debug(f"Result from source: {result.source}")
            logger.debug(f"Content length: {len(result.content)} chars")

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
