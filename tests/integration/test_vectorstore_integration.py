import logging
import pytest
from rag_retriever.vectorstore.store import VectorStore, clean_vectorstore
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

        # Initialize an empty collections dict
        store._collections = {}

        # Mock Chroma for in-memory operation
        def mock_chroma(collection_name, **kwargs):
            # Create a new in-memory Chroma instance
            return Chroma(
                embedding_function=store.embeddings,
                collection_name=collection_name,
                persist_directory=None,  # Forces in-memory mode
                collection_metadata={"hnsw:space": "cosine"},
            )

        # Patch Chroma to use in-memory mode
        with patch(
            "rag_retriever.vectorstore.store.Chroma", side_effect=mock_chroma
        ) as mock_chroma_class:
            yield store


def test_add_and_search_documents(in_memory_vectorstore):
    """Integration test using an in-memory ChromaDB instance."""
    # Create test documents
    documents = [
        Document(page_content="AI is transforming software development."),
        Document(page_content="Vector databases help with efficient search."),
    ]

    # Create a test collection
    collection_name = "test_search_collection"
    in_memory_vectorstore._get_or_create_collection(collection_name)
    in_memory_vectorstore.set_current_collection(collection_name)

    # Add documents to the vector store
    num_chunks = in_memory_vectorstore.add_documents(documents)

    # Ensure documents were added successfully
    assert num_chunks > 0, "No chunks were added to the vector store."

    # Perform a search
    search_results = in_memory_vectorstore.search(
        query="AI software", limit=1, score_threshold=0.0
    )

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


def test_collection_management(in_memory_vectorstore):
    """Integration test for collection management operations."""
    # Create test collections
    collection1_name = "test_collection_1"
    collection2_name = "test_collection_2"

    # Create collections
    collection1 = in_memory_vectorstore._get_or_create_collection(collection1_name)
    collection2 = in_memory_vectorstore._get_or_create_collection(collection2_name)

    # List collections and verify
    collections = in_memory_vectorstore.list_collections()
    collection_names = [c["name"] for c in collections]
    assert collection1_name in collection_names
    assert collection2_name in collection_names

    # Add documents to different collections
    docs1 = [Document(page_content="AI document in collection 1")]
    docs2 = [Document(page_content="ML document in collection 2")]

    # Add documents to collection 1
    in_memory_vectorstore.set_current_collection(collection1_name)
    in_memory_vectorstore.add_documents(docs1)

    # Add documents to collection 2
    in_memory_vectorstore.set_current_collection(collection2_name)
    in_memory_vectorstore.add_documents(docs2)

    # Test search in specific collection
    in_memory_vectorstore.set_current_collection(collection1_name)
    results1 = in_memory_vectorstore.search("AI", limit=1, score_threshold=0.0)
    assert len(results1) > 0, "No results found in collection 1"
    assert "AI document" in results1[0][0].page_content

    # Test search across all collections
    all_results = in_memory_vectorstore.search(
        "document", search_all_collections=True, limit=2, score_threshold=0.0
    )
    assert len(all_results) > 0, "No results found across collections"

    # Get all document contents
    contents = [r[0].page_content for r in all_results]
    print("Search results:", contents)  # Debug print

    # Check for documents from both collections
    found_ai = False
    found_ml = False
    for content in contents:
        if "AI document" in content:
            found_ai = True
        if "ML document" in content:
            found_ml = True

    assert found_ai, "AI document not found in search results"
    assert found_ml, "ML document not found in search results"

    # Test collection deletion
    with (
        patch("builtins.input", return_value="y"),
        patch("rag_retriever.vectorstore.store.Path.exists", return_value=True),
        patch("rag_retriever.vectorstore.store.shutil.rmtree"),
        patch(
            "rag_retriever.vectorstore.store.get_vectorstore_path",
            return_value="/test/path",
        ),
    ):
        # Delete collection using VectorStore's clean_collection method
        in_memory_vectorstore.clean_collection(collection1_name)
        remaining_collections = in_memory_vectorstore.list_collections()
        remaining_names = [c["name"] for c in remaining_collections]
        assert collection1_name not in remaining_names
        assert collection2_name in remaining_names


def test_collection_metadata_persistence(in_memory_vectorstore):
    """Integration test for collection metadata persistence."""
    collection_name = "test_metadata_collection"

    # Create collection with metadata
    collection = in_memory_vectorstore._get_or_create_collection(collection_name)

    # Add documents with metadata
    docs = [
        Document(
            page_content="Test document", metadata={"source": "test", "type": "example"}
        )
    ]

    in_memory_vectorstore.set_current_collection(collection_name)
    in_memory_vectorstore.add_documents(docs)

    # Search with metadata
    results = in_memory_vectorstore.search("test", score_threshold=0.0, limit=1)

    assert len(results) > 0
    assert results[0][0].metadata["type"] == "example"
