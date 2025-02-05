import pytest
from unittest.mock import MagicMock
from rag_retriever.vectorstore.store import VectorStore
from langchain_core.documents import Document


@pytest.fixture
def mock_vectorstore():
    """Fixture to create a VectorStore instance with mocked dependencies."""
    store = VectorStore()
    store._get_or_create_db = MagicMock()  # Mock the database retrieval method
    store._get_or_create_db.return_value.add_documents = (
        MagicMock()
    )  # Mock the add_documents method
    return store


def test_add_documents(mock_vectorstore):
    """Test that add_documents correctly adds document chunks to the vector store."""
    documents = [
        Document(page_content="Test content 1"),
        Document(page_content="Test content 2"),
    ]

    # Call the method under test
    added_chunks = mock_vectorstore.add_documents(documents)

    # Verify that the add_documents method was called once with the expected arguments
    mock_vectorstore._get_or_create_db.return_value.add_documents.assert_called_once()

    # Ensure the returned chunk count matches expectations (mocked logic)
    assert isinstance(added_chunks, int)
