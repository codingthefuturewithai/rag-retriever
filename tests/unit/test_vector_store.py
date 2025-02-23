import pytest
from unittest.mock import MagicMock, patch, ANY
from rag_retriever.vectorstore.store import (
    VectorStore,
    CollectionMetadata,
    clean_vectorstore,
)
from langchain_core.documents import Document


@pytest.fixture
def mock_vectorstore():
    """Fixture to create a VectorStore instance with mocked dependencies."""
    store = VectorStore()
    store._get_or_create_db = MagicMock()  # Mock the database retrieval method
    store._get_or_create_db.return_value.add_documents = MagicMock()
    return store


def test_add_documents(mock_vectorstore):
    """Test that add_documents correctly adds document chunks to the vector store."""
    documents = [
        Document(page_content="Test content 1"),
        Document(page_content="Test content 2"),
    ]

    # Mock the text splitter to return the same documents
    mock_vectorstore.text_splitter.split_documents = MagicMock(return_value=documents)

    # Mock _process_batch to return True
    mock_vectorstore._process_batch = MagicMock(return_value=True)

    # Call the method under test
    added_chunks = mock_vectorstore.add_documents(documents)

    # Verify that _process_batch was called with the documents
    mock_vectorstore._process_batch.assert_called_once()
    assert added_chunks == 2


def test_get_or_create_collection(mock_vectorstore):
    """Test creating and getting a collection."""
    collection_name = "test_collection"
    metadata = CollectionMetadata(collection_name)

    # Mock Chroma instance
    mock_chroma = MagicMock()
    with patch("rag_retriever.vectorstore.store.Chroma", return_value=mock_chroma):
        # Create collection
        collection = mock_vectorstore._get_or_create_collection(
            collection_name, metadata
        )

        # Verify collection was created with correct parameters
        assert collection == mock_chroma
        assert collection._collection_metadata == metadata
        assert mock_vectorstore._collections[collection_name] == collection


def test_list_collections(mock_vectorstore):
    """Test listing all collections."""
    # Create mock collections with metadata
    collection1 = MagicMock()
    collection1._collection_metadata = CollectionMetadata("collection1")
    collection2 = MagicMock()
    collection2._collection_metadata = CollectionMetadata("collection2")

    # Set up collections in the store
    mock_vectorstore._collections = {
        "collection1": collection1,
        "collection2": collection2,
    }

    # Get collections
    collections = mock_vectorstore.list_collections()

    # Verify results
    assert len(collections) == 2
    assert collections[0]["name"] == "collection1"
    assert collections[1]["name"] == "collection2"


def test_clean_vectorstore():
    """Test cleaning/deleting a collection."""
    collection_name = "test_collection"

    with (
        patch("rag_retriever.vectorstore.store.shutil.rmtree") as mock_rmtree,
        patch("rag_retriever.vectorstore.store.Path.exists", return_value=True),
        patch("builtins.input", return_value="y"),
        patch(
            "rag_retriever.vectorstore.store.get_vectorstore_path",
            return_value="/test/path",
        ),
    ):

        # Call the function
        clean_vectorstore(collection_name)

        # Verify rmtree was called with the correct path
        mock_rmtree.assert_called_once_with(ANY)
        # Get the actual argument passed to rmtree
        actual_path = mock_rmtree.call_args[0][0]
        # Verify the path string representation matches what we expect
        assert str(actual_path) == "/test/path/test_collection"


def test_search_all_collections(mock_vectorstore):
    """Test searching across all collections."""
    query = "test query"

    # Create mock collections with search results
    collection1 = MagicMock()
    collection1.similarity_search_with_relevance_scores.return_value = [
        (Document(page_content="result1"), 0.9)
    ]
    collection2 = MagicMock()
    collection2.similarity_search_with_relevance_scores.return_value = [
        (Document(page_content="result2"), 0.8)
    ]

    # Set up collections in the store
    mock_vectorstore._collections = {
        "collection1": collection1,
        "collection2": collection2,
    }

    # Search all collections
    results = mock_vectorstore.search(query, search_all_collections=True)

    # Verify search was called for each collection
    collection1.similarity_search_with_relevance_scores.assert_called_once()
    collection2.similarity_search_with_relevance_scores.assert_called_once()
    assert len(results) == 2
    assert results[0][1] == 0.9  # Check scores are preserved
    assert results[1][1] == 0.8
