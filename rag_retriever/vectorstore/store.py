"""Vector store management module using Chroma."""

import os
import shutil
import time
from datetime import datetime, UTC
from pathlib import Path
import logging
from typing import List, Tuple, Optional, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from rag_retriever.utils.config import (
    config,
    get_data_dir,
    mask_api_key,
    get_user_friendly_config_path,
)

logger = logging.getLogger(__name__)

# Constants
DEFAULT_COLLECTION = "default"
COLLECTION_METADATA_FILE = "collection_metadata.json"


class CollectionMetadata:
    """Collection metadata storage."""

    def __init__(self, name: str):
        self.name = name
        self.created_at = datetime.now(UTC).isoformat()
        self.last_modified = self.created_at
        self.document_count = 0
        self.total_chunks = 0
        self.description = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "name": self.name,
            "created_at": self.created_at,
            "last_modified": self.last_modified,
            "document_count": self.document_count,
            "total_chunks": self.total_chunks,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CollectionMetadata":
        """Create metadata instance from dictionary."""
        instance = cls(data["name"])
        instance.created_at = data["created_at"]
        instance.last_modified = data["last_modified"]
        instance.document_count = data["document_count"]
        instance.total_chunks = data["total_chunks"]
        instance.description = data.get("description", "")
        return instance


def get_vectorstore_path() -> str:
    """Get the vector store directory path using OS-specific locations."""
    # Check for environment variable first
    if "VECTOR_STORE_PATH" in os.environ:
        store_path = Path(os.environ["VECTOR_STORE_PATH"])
        logger.debug(f"Using vector store path from environment variable: {store_path}")
    else:
        store_path = get_data_dir() / "chromadb"
        logger.debug(f"Using default vector store path: {store_path}")

    os.makedirs(store_path, exist_ok=True)
    return str(store_path)


def _delete_collection_files(collection_name: Optional[str] = None) -> None:
    """Internal function to delete collection files without confirmation."""
    vectorstore_path = Path(get_vectorstore_path())

    if collection_name:
        collection_path = vectorstore_path / collection_name
        if collection_path.exists():
            logger.info("Deleting collection at %s", collection_path)
            shutil.rmtree(collection_path)

            # Update metadata file if it exists
            metadata_path = vectorstore_path / COLLECTION_METADATA_FILE
            if metadata_path.exists():
                import json

                try:
                    with open(metadata_path, "r") as f:
                        metadata = json.load(f)
                    if collection_name in metadata:
                        del metadata[collection_name]
                        with open(metadata_path, "w") as f:
                            json.dump(metadata, f, indent=2)
                except Exception as e:
                    logger.error(f"Error updating metadata file: {e}")

            logger.info("Collection deleted successfully")
        else:
            logger.info("Collection not found at %s", collection_path)
    else:
        if vectorstore_path.exists():
            logger.info("Deleting vector store at %s", vectorstore_path)
            shutil.rmtree(vectorstore_path)
            logger.info("Vector store deleted successfully")
        else:
            logger.info("Vector store not found at %s", vectorstore_path)


def clean_vectorstore(collection_name: Optional[str] = None) -> None:
    """Delete the vector store database or a specific collection.

    Args:
        collection_name: Optional name of collection to delete.
                       If None, deletes entire vector store.
    """
    if collection_name:
        # Prompt for confirmation
        print(f"\nWARNING: This will delete the collection '{collection_name}'.")
        response = input("Are you sure you want to proceed? (y/N): ")
        if response.lower() != "y":
            logger.info("Operation cancelled")
            return
    else:
        # Prompt for confirmation
        print("\nWARNING: This will delete the entire vector store database.")
        response = input("Are you sure you want to proceed? (y/N): ")
        if response.lower() != "y":
            logger.info("Operation cancelled")
            return

    _delete_collection_files(collection_name)


class VectorStore:
    """Manage vector storage and retrieval using Chroma."""

    def __init__(
        self,
        persist_directory: Optional[str] = None,
        collection_name: Optional[str] = None,
    ):
        """Initialize vector store.

        Args:
            persist_directory: Optional directory to persist the vector store
            collection_name: Optional name of the collection to use (defaults to 'default')
        """
        self.persist_directory = persist_directory or get_vectorstore_path()
        logger.debug("Vector store directory: %s", self.persist_directory)
        self.embeddings = self._get_embeddings()
        self._collections: Dict[str, Chroma] = {}
        self.current_collection = collection_name or DEFAULT_COLLECTION
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.vector_store.get("chunk_size", 1000),
            chunk_overlap=config.vector_store.get("chunk_overlap", 200),
        )
        self._load_collections()

    def _load_collections(self) -> None:
        """Load existing collections and their metadata."""
        metadata_path = Path(self.persist_directory) / COLLECTION_METADATA_FILE
        if metadata_path.exists():
            import json

            try:
                with open(metadata_path, "r") as f:
                    metadata_dict = json.load(f)
                    for name, data in metadata_dict.items():
                        # Initialize collection metadata
                        self._get_or_create_collection(
                            name, CollectionMetadata.from_dict(data)
                        )
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                logger.error(f"Error parsing collection metadata: {e}")
                # Initialize with default collection
                self._get_or_create_collection(DEFAULT_COLLECTION)
            except OSError as e:
                logger.error(f"Error reading metadata file: {e}")
                # Initialize with default collection
                self._get_or_create_collection(DEFAULT_COLLECTION)
        else:
            # Initialize with default collection
            self._get_or_create_collection(DEFAULT_COLLECTION)

    def _save_collection_metadata(self) -> None:
        """Save collection metadata to disk."""
        metadata_path = Path(self.persist_directory) / COLLECTION_METADATA_FILE
        metadata_dict = {}
        for name, collection in self._collections.items():
            if hasattr(collection, "_collection_metadata"):
                metadata_dict[name] = collection._collection_metadata.to_dict()

        import json

        with open(metadata_path, "w") as f:
            json.dump(metadata_dict, f, indent=2)

    def _get_or_create_collection(
        self, name: str, metadata: Optional[CollectionMetadata] = None
    ) -> Chroma:
        """Get or create a collection by name."""
        if name not in self._collections:
            collection_dir = Path(self.persist_directory) / name
            os.makedirs(collection_dir, exist_ok=True)

            collection = Chroma(
                persist_directory=str(collection_dir),
                embedding_function=self.embeddings,
                collection_name=name,
                collection_metadata={
                    "hnsw:space": "cosine",
                    "description": metadata.description if metadata else "",
                    "created_at": (
                        metadata.created_at
                        if metadata
                        else datetime.now(UTC).isoformat()
                    ),
                },
            )

            # Attach our custom metadata to the collection
            collection._collection_metadata = metadata or CollectionMetadata(name)
            self._collections[name] = collection
            logger.debug(f"Created new collection: {name}")

        return self._collections[name]

    def list_collections(self) -> List[Dict[str, Any]]:
        """List all available collections and their metadata."""
        # First, scan for any collections that might exist on disk but not loaded
        vectorstore_path = Path(self.persist_directory)
        if vectorstore_path.exists():
            for collection_dir in vectorstore_path.iterdir():
                if collection_dir.is_dir() and collection_dir.name != "__pycache__":
                    # Ensure collection is loaded
                    self._get_or_create_collection(collection_dir.name)
        
        # Now return all loaded collections with their metadata
        collections = []
        for name, collection in self._collections.items():
            try:
                # Get actual document count from ChromaDB
                count = collection._collection.count()
                metadata = collection._collection_metadata.to_dict()
                metadata["count"] = count
                collections.append({"name": name, **metadata})
            except Exception as e:
                logger.warning(f"Error getting metadata for collection {name}: {e}")
                # Fallback to basic info
                collections.append({
                    "name": name,
                    "count": 0,
                    "error": str(e)
                })
        
        return collections

    def get_collection_metadata(self, collection_name: str) -> Dict[str, Any]:
        """Get metadata for a specific collection."""
        collection = self._get_or_create_collection(collection_name)
        return collection._collection_metadata.to_dict()

    def set_current_collection(self, collection_name: str) -> None:
        """Set the current working collection."""
        self._get_or_create_collection(collection_name)  # Ensure it exists
        self.current_collection = collection_name
        logger.debug(f"Set current collection to: {collection_name}")

    def _get_embeddings(self) -> OpenAIEmbeddings:
        """Get OpenAI embeddings instance."""
        api_key = config.get_openai_api_key()
        if not api_key:
            raise ValueError(
                f"OpenAI API key not found. Please configure it in {get_user_friendly_config_path()}"
            )

        logger.debug("Using OpenAI API key: %s", mask_api_key(api_key))
        return OpenAIEmbeddings(
            model=config.vector_store["embedding_model"],
            openai_api_key=api_key,
            dimensions=config.vector_store["embedding_dimensions"],
        )

    @retry(
        stop=stop_after_attempt(
            lambda: config.vector_store["batch_processing"]["max_retries"]
        ),
        wait=wait_exponential(
            multiplier=lambda: config.vector_store["batch_processing"]["retry_delay"],
            min=1,
            max=60,
        ),
        retry=lambda e: "rate limit" in str(e).lower() or "quota" in str(e).lower(),
        before_sleep=lambda retry_state: logger.info(
            "Rate limit error encountered. Using exponential backoff strategy:"
            "\n  - Attempt: %d/%d"
            "\n  - Next retry in: %.1f seconds"
            "\n  - Base delay: %.1f seconds"
            "\n  - Max delay: 60 seconds",
            retry_state.attempt_number + 1,
            config.vector_store["batch_processing"]["max_retries"],
            retry_state.next_action.sleep,
            config.vector_store["batch_processing"]["retry_delay"],
        ),
    )
    def _process_batch(
        self, batch: List[Document], collection_name: Optional[str] = None
    ) -> bool:
        """Process a single batch of documents with retry logic."""
        try:
            collection = self._get_or_create_collection(
                collection_name or self.current_collection
            )
            logger.info(
                "Storing batch of %d chunks to collection '%s'...",
                len(batch),
                collection_name or self.current_collection,
            )

            collection.add_documents(batch)

            # Update collection metadata
            collection._collection_metadata.total_chunks += len(batch)
            collection._collection_metadata.last_modified = datetime.now(
                UTC
            ).isoformat()
            self._save_collection_metadata()

            logger.info("Successfully stored batch to collection")
            return True
        except Exception as e:
            if "rate limit" in str(e).lower() or "quota" in str(e).lower():
                logger.info("Rate limiting error details: %s", str(e))
            else:
                logger.error("Error processing batch: %s", str(e))
            raise

    def add_documents(
        self, documents: List[Document], collection_name: Optional[str] = None
    ) -> int:
        """Add documents to the vector store using batch processing.

        Args:
            documents: List of documents to add
            collection_name: Optional name of collection to add documents to
                           (defaults to current collection)

        Returns:
            Number of chunks successfully processed

        Raises:
            ValueError: If documents list is empty or batch_size is invalid
        """
        if not documents:
            raise ValueError("Documents list cannot be empty")

        try:
            target_collection = collection_name or self.current_collection
            logger.info(f"Adding documents to collection: {target_collection}")

            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=config.content["chunk_size"],
                chunk_overlap=config.content["chunk_overlap"],
                separators=config.content["separators"],
                length_function=len,
            )
            logger.debug(
                "Splitting documents with chunk_size=%d, chunk_overlap=%d",
                config.content["chunk_size"],
                config.content["chunk_overlap"],
            )
            splits = text_splitter.split_documents(documents)

            total_content_size = sum(len(doc.page_content) for doc in documents)
            total_chunk_size = sum(len(split.page_content) for split in splits)

            logger.info(
                "Processing %d documents (total size: %d chars) into %d chunks (total size: %d chars)",
                len(documents),
                total_content_size,
                len(splits),
                total_chunk_size,
            )

            # Process in batches
            batch_settings = config.vector_store["batch_processing"]
            batch_size = batch_settings["batch_size"]

            # Validate batch size
            if batch_size <= 0:
                raise ValueError("Batch size must be greater than 0")
            if batch_size > len(splits):
                logger.warning(
                    f"Batch size ({batch_size}) is larger than number of chunks ({len(splits)}). "
                    "Using chunk count as batch size."
                )
                batch_size = len(splits)

            delay = batch_settings["delay_between_batches"]

            successful_chunks = 0
            total_batches = (len(splits) + batch_size - 1) // batch_size

            # Update collection metadata for document count
            collection = self._get_or_create_collection(target_collection)
            collection._collection_metadata.document_count += len(documents)
            collection._collection_metadata.last_modified = datetime.now(
                UTC
            ).isoformat()
            self._save_collection_metadata()

            for i in range(0, len(splits), batch_size):
                batch = splits[i : i + batch_size]
                batch_num = (i // batch_size) + 1

                logger.info(
                    "Processing batch %d/%d (%d chunks) for collection '%s'",
                    batch_num,
                    total_batches,
                    len(batch),
                    target_collection,
                )

                if self._process_batch(batch, target_collection):
                    successful_chunks += len(batch)
                    logger.info(
                        "Batch %d/%d completed successfully (%d/%d chunks processed)",
                        batch_num,
                        total_batches,
                        successful_chunks,
                        len(splits),
                    )
                else:
                    logger.error(
                        "Batch %d/%d failed (%d/%d chunks processed)",
                        batch_num,
                        total_batches,
                        successful_chunks,
                        len(splits),
                    )

                if i + batch_size < len(splits):  # If not the last batch
                    logger.debug("Waiting %.1f seconds before next batch", delay)
                    time.sleep(delay)

            if successful_chunks < len(splits):
                logger.warning(
                    "Partial success: %d/%d chunks successfully processed in collection '%s'",
                    successful_chunks,
                    len(splits),
                    target_collection,
                )
            else:
                logger.info(
                    "All %d chunks successfully processed in collection '%s'",
                    successful_chunks,
                    target_collection,
                )

            return successful_chunks

        except Exception as e:
            logger.error("Error in document processing: %s", str(e))
            raise

    def search(
        self,
        query: str,
        limit: int = 5,
        score_threshold: float = 0.2,
        collection_name: Optional[str] = None,
        search_all_collections: bool = False,
    ) -> List[Tuple[Document, float]]:
        """Search for documents similar to query.

        Args:
            query: Search query string
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score threshold (0.0 to 1.0)
            collection_name: Optional name of collection to search in
                           (defaults to current collection)
            search_all_collections: If True, search across all collections
                                  (ignores collection_name)

        Returns:
            List of (document, score) tuples sorted by relevance

        Raises:
            ValueError: If score_threshold is not between 0 and 1
        """
        # Validate score threshold
        if not 0 <= score_threshold <= 1:
            raise ValueError("score_threshold must be between 0 and 1")

        if search_all_collections:
            # Search across all collections and merge results
            all_results = []
            for name in self._collections:
                try:
                    collection = self._collections[name]
                    results = collection.similarity_search_with_relevance_scores(
                        query,
                        k=limit,
                        score_threshold=score_threshold,
                    )
                    # Add collection name to metadata
                    for doc, score in results:
                        doc.metadata["collection"] = name
                    all_results.extend(results)
                except Exception as e:
                    logger.error(f"Error searching collection '{name}': {e}")
                    continue  # Continue with other collections on error

            # Sort by score and limit results
            all_results.sort(key=lambda x: x[1], reverse=True)
            return all_results[:limit]
        else:
            # Search in specific collection
            collection = self._get_or_create_collection(
                collection_name or self.current_collection
            )
            try:
                results = collection.similarity_search_with_relevance_scores(
                    query,
                    k=limit,
                    score_threshold=score_threshold,
                )
                # Add collection name to metadata
                for doc, score in results:
                    doc.metadata["collection"] = (
                        collection_name or self.current_collection
                    )
                return results
            except Exception as e:
                logger.error(f"Error searching collection: {e}")
                raise

    def clean_collection(self, collection_name: str) -> None:
        """Delete a specific collection.

        Args:
            collection_name: Name of collection to delete
        """
        if collection_name == DEFAULT_COLLECTION:
            raise ValueError("Cannot delete the default collection")

        _delete_collection_files(collection_name)

        # Remove from internal collections dict if present
        if collection_name in self._collections:
            del self._collections[collection_name]
            logger.debug(f"Removed collection '{collection_name}' from memory")

        # If current collection was deleted, switch to default
        if self.current_collection == collection_name:
            self.current_collection = DEFAULT_COLLECTION
            logger.debug("Switched to default collection after deletion")
