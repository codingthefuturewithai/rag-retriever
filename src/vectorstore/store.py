"""Vector store management module using Chroma."""

import os
from typing import List, Tuple, Optional

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from src.utils.config import config

def get_vectorstore_path() -> str:
    """Get the vector store directory path."""
    return os.path.join(os.getcwd(), "chromadb")

class VectorStore:
    """Manage vector storage and retrieval using Chroma."""

    def __init__(self, persist_directory: Optional[str] = None):
        """Initialize vector store."""
        self.persist_directory = persist_directory or get_vectorstore_path()
        self.embeddings = self._get_embeddings()
        self._db = None

    def _get_embeddings(self) -> OpenAIEmbeddings:
        """Get OpenAI embeddings instance with configuration."""
        return OpenAIEmbeddings(
            model=config.vector_store["embedding_model"],
            dimensions=config.vector_store["embedding_dimensions"],
        )

    def _get_or_create_db(self, documents: Optional[List[Document]] = None) -> Chroma:
        """Get existing vector store or create a new one."""
        if self._db is not None:
            return self._db

        # Create the directory if it doesn't exist
        os.makedirs(self.persist_directory, exist_ok=True)

        # Load existing DB if it exists
        if os.path.exists(self.persist_directory) and os.listdir(self.persist_directory):
            self._db = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
            )
            # Add new documents if provided
            if documents is not None:
                self._db.add_documents(documents)
            return self._db

        # Create new DB with documents
        if documents is None:
            raise ValueError(
                "No existing vector store found and no documents provided to create one."
            )

        self._db = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
        )
        return self._db

    def add_documents(self, documents: List[Document]) -> int:
        """Add documents to the vector store."""
        db = self._get_or_create_db()  # Get existing DB without documents
        if documents:  # Only add if we have documents
            db.add_documents(documents)
        return len(documents)

    def search(
        self,
        query: str,
        limit: int = 5,
        score_threshold: float = 0.2,
    ) -> List[Tuple[Document, float]]:
        """Search for documents similar to query."""
        db = self._get_or_create_db()
        results = db.similarity_search_with_relevance_scores(
            query,
            k=limit,
            score_threshold=score_threshold,
        )
        return results
