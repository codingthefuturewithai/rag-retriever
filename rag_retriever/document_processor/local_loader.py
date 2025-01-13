"""Module for loading local documents into the vector store."""

from pathlib import Path
from typing import List, Optional, Iterator
import logging

from langchain_core.documents import Document
from langchain_community.document_loaders import DirectoryLoader, TextLoader

logger = logging.getLogger(__name__)


class LocalDocumentLoader:
    """Handles loading of local documents (markdown, text) into Document objects."""

    def __init__(self, show_progress: bool = True, use_multithreading: bool = True):
        """Initialize the document loader.

        Args:
            show_progress: Whether to show a progress bar during loading
            use_multithreading: Whether to use multiple threads for directory loading
        """
        self.show_progress = show_progress
        self.use_multithreading = use_multithreading

    def load_file(self, file_path: str) -> List[Document]:
        """Load a single file with appropriate loader based on extension.

        Args:
            file_path: Path to the file to load

        Returns:
            List of Document objects

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file type is not supported
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if path.suffix.lower() in [".md", ".txt"]:
            logger.debug(f"Loading file: {file_path}")
            loader = TextLoader(file_path, autodetect_encoding=True)
            try:
                return list(loader.lazy_load())
            except Exception as e:
                logger.error(f"Error loading file {file_path}: {str(e)}")
                raise

        raise ValueError(f"Unsupported file type: {path.suffix}")

    def load_directory(
        self, directory_path: str, glob_pattern: str = "**/*.md"
    ) -> List[Document]:
        """Load all supported documents from a directory.

        Args:
            directory_path: Path to the directory to load files from
            glob_pattern: Pattern to match files against. Default matches .md files.
                        Use "**/*.txt" for text files or "**/*.[mt][dx][td]" for both.

        Returns:
            List of Document objects

        Raises:
            FileNotFoundError: If the directory doesn't exist
        """
        path = Path(directory_path)
        if not path.exists() or not path.is_dir():
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        logger.info(f"Loading documents from directory: {directory_path}")

        # First check if there are any matching files
        matching_files = list(path.glob(glob_pattern))
        if not matching_files:
            logger.warning(
                f"No matching files found in {directory_path} using pattern {glob_pattern}"
            )
            return []

        logger.debug(
            f"Found {len(matching_files)} matching files: {[f.name for f in matching_files]}"
        )

        loader = DirectoryLoader(
            str(path),  # Convert path to string
            glob=glob_pattern,
            loader_cls=TextLoader,
            loader_kwargs={"autodetect_encoding": True},
            use_multithreading=self.use_multithreading,
            show_progress=self.show_progress,
        )

        try:
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} documents from {directory_path}")
            return documents
        except Exception as e:
            logger.error(f"Error loading directory {directory_path}: {str(e)}")
            raise
