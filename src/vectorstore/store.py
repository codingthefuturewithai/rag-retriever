"""Vector store management module using Chroma."""

import os
from typing import List, Tuple, Optional

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from src.utils.config import config


class VectorStore:
    """Manage vector storage and retrieval using Chroma."""

    def __init__(self, persist_directory: Optional[str] = None):
        """Initialize vector store.

        Args:
            persist_directory: Directory to persist vectors.
                             If None, uses config default.
        """
        self.persist_directory = persist_directory or config.get_persist_directory()
        self.embeddings = self._get_embeddings()

    def _get_embeddings(self) -> OpenAIEmbeddings:
        """Get OpenAI embeddings instance with configuration."""
        return OpenAIEmbeddings(
            model=config.vector_store["embedding_model"],
            dimensions=config.vector_store["embedding_dimensions"],
        )

    def _get_or_create_db(self, documents: Optional[List[Document]] = None) -> Chroma:
        """Get existing vector store or create a new one.

        Args:
            documents: Documents to initialize store with if creating new.

        Returns:
            Chroma vector store instance.

        Raises:
            ValueError: If no existing store and no documents provided.
        """
        # Check if the directory exists and has contents
        if os.path.exists(self.persist_directory) and os.listdir(
            self.persist_directory
        ):
            return Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
            )

        if documents is None:
            raise ValueError(
                "No existing vector store found and no documents provided to create one."
            )

        # Create the directory if it doesn't exist
        os.makedirs(self.persist_directory, exist_ok=True)

        # Create and return the database
        return Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
        )

    def add_documents(self, documents: List[Document]) -> int:
        """Add documents to the vector store.

        Args:
            documents: List of documents to add.

        Returns:
            Number of documents added.
        """
        db = self._get_or_create_db(documents)
        return len(documents)

    def search(
        self,
        query: str,
        limit: int = 5,
        score_threshold: float = 0.2,
    ) -> List[Tuple[Document, float]]:
        """Search for documents similar to query.

        Args:
            query: Search query.
            limit: Maximum number of results.
            score_threshold: Minimum relevance score (0-1).

        Returns:
            List of (document, score) tuples.
        """
        db = self._get_or_create_db()

        # Get results with relevance scores
        results = db.similarity_search_with_relevance_scores(
            query,
            k=limit,
            score_threshold=score_threshold,
        )

        return results
