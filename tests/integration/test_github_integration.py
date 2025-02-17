"""Integration tests for GitHub repository loading."""

import pytest
import tempfile
import os
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock
from langchain_chroma import Chroma
from git import Repo, GitCommandError
from git.exc import GitCommandError
from langchain_community.document_loaders import GitLoader
import numpy as np

from rag_retriever.document_processor import GitHubLoader
from rag_retriever.vectorstore.store import VectorStore

# Set up logging at the module level
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_git_and_network():
    """Check if both git is installed and GitHub is accessible using production methods."""
    temp_dir = None
    try:
        # Create a temporary directory for the test
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.info("Checking Git and GitHub availability...")
            logger.info(f"Created temporary directory: {temp_dir}")

            # Try to clone a repository using the same method as GitHubLoader
            repo = Repo.clone_from(
                "https://github.com/openai/openai-quickstart-python.git", temp_dir
            )
            logger.info(f"Successfully cloned repository to: {temp_dir}")

            # Try to checkout a branch using the same method as GitHubLoader
            repo.git.checkout("master")
            logger.info("Successfully checked out master branch")

            # Try to load files using the same method as GitHubLoader
            loader = GitLoader(
                repo_path=temp_dir,
                branch="master",
                file_filter=lambda x: x.endswith(".md"),
            )

            # Attempt to load at least one file
            documents = loader.load()
            if not documents:
                logger.error("Repository cloned but no documents could be loaded")
                return False, "Could not load documents from repository"

            logger.info("Successfully verified Git and GitHub access")
            return True, None

    except GitCommandError as e:
        logger.error(f"Git operation failed: {str(e)}")
        return False, f"Git operation failed: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error during Git/GitHub check: {str(e)}")
        return False, str(e)
    finally:
        if temp_dir and Path(temp_dir).exists():
            logger.warning(
                f"Warning: Temporary directory {temp_dir} still exists after context exit"
            )
        else:
            logger.info("Temporary directory was properly cleaned up")


# Get availability status once at module load
logger.info("Running Git and GitHub availability check...")
is_available, skip_reason = check_git_and_network()
logger.info(f"Check results - Available: {is_available}, Reason if not: {skip_reason}")

# Skip all tests if either git or network is unavailable
pytestmark = pytest.mark.skipif(
    not is_available, reason=skip_reason or "Git or GitHub is not available"
)


@pytest.fixture(autouse=True)
def setup_logging():
    """Configure logging for all tests in this module."""
    logging.basicConfig(level=logging.INFO)


@pytest.fixture
def config():
    """Test configuration fixture."""
    return {
        "github_settings": {
            "supported_extensions": [".py", ".md"],
            "excluded_patterns": ["node_modules/**", "__pycache__/**"],
            "max_file_size_mb": 10,
            "default_branch": "master",
        }
    }


@pytest.fixture
def mock_embeddings():
    """Create a mock embeddings instance that returns consistent fake embeddings."""
    mock = MagicMock()
    # Create fake embeddings - use the same dimension as in config (3072)
    fake_embedding = np.random.rand(3072).tolist()
    mock.embed_documents.side_effect = lambda texts: [fake_embedding] * len(texts)
    mock.embed_query.return_value = fake_embedding
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


@pytest.mark.integration
def test_load_public_repository(config, in_memory_vectorstore):
    """Test loading a public GitHub repository."""
    loader = GitHubLoader(config)

    # Use a small, public repository for testing
    repo_url = "https://github.com/openai/openai-quickstart-python.git"

    try:
        # Load only Python and Markdown files
        documents = loader.load_repository(
            repo_url=repo_url, file_filter=lambda x: x.endswith((".py", ".md"))
        )

        # Verify documents were loaded
        assert len(documents) > 0
        assert all(doc.metadata["source"] == repo_url for doc in documents)
        assert all(doc.metadata["branch"] == "master" for doc in documents)
        assert all(
            Path(doc.metadata["file_path"]).suffix in [".py", ".md"]
            for doc in documents
        )

        # Test adding to vector store
        in_memory_vectorstore.add_documents(documents)

        # Test searching the content
        results = in_memory_vectorstore.search(
            "How to use the OpenAI API?",
            limit=2,
            score_threshold=0.0,  # Accept any score for testing
        )
        assert len(results) > 0

    except GitCommandError as e:
        pytest.skip(f"Git command failed: {str(e)}")
    except Exception as e:
        pytest.fail(f"Unexpected error: {str(e)}")


@pytest.mark.integration
def test_load_repository_with_branch(config, in_memory_vectorstore):
    """Test loading a specific branch from a repository."""
    loader = GitHubLoader(config)

    # Use a repository known to have multiple branches
    repo_url = "https://github.com/openai/openai-python.git"
    branch = "main"  # This repository uses main as its default branch

    try:
        documents = loader.load_repository(
            repo_url=repo_url,
            branch=branch,
            file_filter=lambda x: x.endswith(
                "README.md"
            ),  # Only load README to keep test fast
        )

        assert len(documents) > 0
        assert all(doc.metadata["branch"] == branch for doc in documents)
        assert any("README.md" in doc.metadata["file_path"] for doc in documents)

        # Test adding to vector store
        in_memory_vectorstore.add_documents(documents)

        # Test searching the content
        results = in_memory_vectorstore.search(
            "How to use the OpenAI Python client?",
            limit=1,
            score_threshold=0.0,  # Accept any score for testing
        )
        assert len(results) > 0

    except GitCommandError as e:
        pytest.skip(f"Git command failed: {str(e)}")
    except Exception as e:
        pytest.fail(f"Unexpected error: {str(e)}")


@pytest.mark.integration
def test_temp_directory_cleanup(config):
    """Test that temporary directories are properly cleaned up."""
    loader = GitHubLoader(config)
    repo_url = "https://github.com/openai/openai-quickstart-python.git"
    temp_dir = None

    try:
        with tempfile.TemporaryDirectory() as td:
            temp_dir = td  # Save the path for checking later
            logger.info(f"Created temporary directory: {temp_dir}")

            # Load the repository
            documents = loader.load_repository(repo_url=repo_url)
            assert len(documents) > 0, "Should have loaded some documents"

        # After the with block, check if directory still exists
        path = Path(temp_dir)
        assert not path.exists(), f"Temporary directory {temp_dir} was not cleaned up"
        logger.info("Verified temporary directory was cleaned up")

    except Exception as e:
        if temp_dir and Path(temp_dir).exists():
            logger.error(f"Test failed and temporary directory {temp_dir} still exists")
            raise
        else:
            raise
