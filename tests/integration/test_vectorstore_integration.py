import logging
import pytest
from rag_retriever.vectorstore.store import VectorStore
from langchain_core.documents import Document
from unittest.mock import patch
from langchain_chroma import Chroma  # Ensure this is the correct import

logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def setup_logging():
    """Configure logging for all tests in this module."""
    logging.basicConfig(level=logging.INFO)


@pytest.fixture
def in_memory_vectorstore():
    """Fixture to create an in-memory VectorStore instance."""
    store = VectorStore()

    # Patch _get_or_create_db to force an in-memory ChromaDB
    def mock_get_or_create_db(documents=None):
        if not hasattr(store, "_db") or store._db is None:
            if documents is None:
                documents = []
            store._db = Chroma.from_documents(
                documents=documents,
                embedding=store.embeddings,
                persist_directory=None,  # Forces in-memory mode
                collection_metadata={"hnsw:space": "cosine"},
            )
        return store._db

    store._get_or_create_db = (
        mock_get_or_create_db  # Replace method with in-memory version
    )
    return store


def test_add_and_search_documents(in_memory_vectorstore):
    """Integration test using an in-memory ChromaDB instance."""
    # Create test documents
    documents = [
        Document(page_content="AI is transforming software development."),
        Document(page_content="Vector databases help with efficient search."),
    ]

    # Add documents to the vector store
    num_chunks = in_memory_vectorstore.add_documents(documents)

    # Ensure documents were added successfully
    assert num_chunks > 0, "No chunks were added to the vector store."

    # Perform a search
    search_results = in_memory_vectorstore.search(query="AI software", limit=1)

    # Ensure search returns results
    assert len(search_results) > 0, "No search results returned."

    # Ensure the retrieved document is relevant
    retrieved_doc, score = search_results[0]
    logger.info(
        f"Retrieved document content: {retrieved_doc.page_content}, score: {score}"
    )
    assert (
        "AI is transforming software development." in retrieved_doc.page_content
    ), "Expected document not found in search results."
