import logging
import pytest
from rag_retriever.vectorstore.store import VectorStore
from langchain_core.documents import Document
from unittest.mock import patch, MagicMock
from langchain_chroma import Chroma
import numpy as np

logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def setup_logging():
    """Configure logging for all tests in this module."""
    logging.basicConfig(level=logging.INFO)


@pytest.fixture
def mock_embeddings():
    """Create a mock embeddings instance that returns deterministic but different embeddings."""
    mock = MagicMock()

    def get_embedding_for_text(text):
        # Use text length as a seed for reproducibility
        np.random.seed(len(text))
        return np.random.rand(3072).tolist()

    def embed_documents(texts):
        return [get_embedding_for_text(text) for text in texts]

    def embed_query(text):
        return get_embedding_for_text(text)

    mock.embed_documents.side_effect = embed_documents
    mock.embed_query.side_effect = embed_query
    return mock


@pytest.fixture
def in_memory_vectorstore(mock_embeddings, request):
    """Fixture to create an in-memory VectorStore instance with mocked embeddings."""
    with patch(
        "rag_retriever.vectorstore.store.OpenAIEmbeddings", return_value=mock_embeddings
    ):
        store = VectorStore()

        # Create a unique collection name for this test
        collection_name = f"test_collection_{request.node.name}"

        # Patch _get_or_create_db to force in-memory ChromaDB with unique collection
        def mock_get_or_create_db(documents=None):
            if not hasattr(store, "_db") or store._db is None:
                # Initialize an empty in-memory Chroma database
                store._db = Chroma(
                    embedding_function=store.embeddings,
                    collection_name=collection_name,
                    persist_directory=None,  # Forces in-memory mode
                    collection_metadata={"hnsw:space": "cosine"},
                )
            if documents is not None:
                # Add documents to the DB
                store._db.add_documents(documents)
            return store._db

        store._get_or_create_db = mock_get_or_create_db
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
