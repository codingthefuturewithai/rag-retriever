"""Module for loading GitHub repositories into the vector store."""

import logging
import tempfile
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path

from git import Repo
from langchain_community.document_loaders import GitLoader
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class GitHubLoader:
    """Handles loading of GitHub repositories into Document objects."""

    def __init__(
        self,
        config: Dict[str, Any],
        show_progress: bool = True,
    ):
        """Initialize the GitHub loader.

        Args:
            config: Configuration dictionary containing GitHub settings
            show_progress: Whether to show a progress bar during loading
        """
        self.config = config.get("github_settings", {})
        self.show_progress = show_progress

        # Set default values if not provided in config
        self.supported_extensions = self.config.get(
            "supported_extensions",
            [
                ".py",
                ".js",
                ".java",
                ".cpp",
                ".h",
                ".cs",
                ".rb",
                ".go",
                ".rs",
                ".php",
                ".scala",
                ".kt",
                ".swift",
                ".m",
                ".ts",
                ".jsx",
                ".tsx",
                ".vue",
                ".md",
                ".rst",
            ],
        )
        self.excluded_patterns = self.config.get(
            "excluded_patterns",
            [
                "node_modules/**",
                "__pycache__/**",
                "*.pyc",
                ".git/**",
                "build/**",
                "dist/**",
                ".idea/**",
                ".vscode/**",
            ],
        )
        self.max_file_size = (
            self.config.get("max_file_size_mb", 10) * 1024 * 1024
        )  # Convert to bytes
        self.default_branch = self.config.get("default_branch", "main")

    def load_repository(
        self,
        repo_url: str,
        branch: Optional[str] = None,
        file_filter: Optional[Callable[[str], bool]] = None,
    ) -> List[Document]:
        """Load documents from a GitHub repository.

        Args:
            repo_url (str): URL of the GitHub repository.
            branch (str, optional): Branch to clone. Defaults to the value in config.
            file_filter (callable, optional): Function to filter files. Defaults to None.

        Returns:
            List[Document]: List of documents from the repository.
        """
        logger.info(f"Loading GitHub repository: {repo_url}")

        try:
            # Create a temporary directory for the repository
            with tempfile.TemporaryDirectory() as temp_dir:
                logger.info("Created temporary directory for repository: %s", temp_dir)
                # Clone the repository
                repo = Repo.clone_from(repo_url, temp_dir)

                # Checkout the specified branch or use default
                target_branch = branch or self.default_branch
                repo.git.checkout(target_branch)

                # Create the GitLoader with the file filter
                if file_filter is None:
                    # Default filter: check file extension and excluded patterns
                    def default_filter(file_path: str) -> bool:
                        path = Path(file_path)

                        # Check if file matches any excluded pattern
                        for pattern in self.excluded_patterns:
                            if path.match(pattern):
                                return False

                        # Check file extension and size
                        return (
                            path.suffix in self.supported_extensions
                            and path.stat().st_size <= self.max_file_size
                        )

                    file_filter = default_filter

                loader = GitLoader(
                    repo_path=temp_dir, branch=target_branch, file_filter=file_filter
                )

                # Load and process documents
                documents = loader.load()

                # Update metadata for each document
                for doc in documents:
                    doc.metadata.update(
                        {
                            "source": repo_url,
                            "branch": target_branch,
                            "file_path": doc.metadata.get("file_path", "unknown"),
                        }
                    )

                return documents

        except Exception as e:
            logger.error(f"Error loading GitHub repository: {str(e)}")
            raise
