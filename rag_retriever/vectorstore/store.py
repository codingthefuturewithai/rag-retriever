"""Vector store management module using Chroma."""

import os
import shutil
import time
from pathlib import Path
import logging
from typing import List, Tuple, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from rag_retriever.utils.config import config, get_data_dir, mask_api_key

logger = logging.getLogger(__name__)


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


def clean_vectorstore() -> None:
    """Delete the vector store database."""
    vectorstore_path = Path(get_vectorstore_path())
    if vectorstore_path.exists():
        # Prompt for confirmation
        print("\nWARNING: This will delete the entire vector store database.")
        response = input("Are you sure you want to proceed? (y/N): ")
        if response.lower() != "y":
            logger.info("Operation cancelled")
            return

        logger.info("Deleting vector store at %s", vectorstore_path)
        shutil.rmtree(vectorstore_path)
        logger.info("Vector store deleted successfully")
    else:
        logger.info("Vector store not found at %s", vectorstore_path)


class VectorStore:
    """Manage vector storage and retrieval using Chroma."""

    def __init__(self, persist_directory: Optional[str] = None):
        """Initialize vector store."""
        self.persist_directory = persist_directory or get_vectorstore_path()
        logger.debug("Vector store directory: %s", self.persist_directory)
        self.embeddings = self._get_embeddings()
        self._db = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.vector_store.get("chunk_size", 1000),
            chunk_overlap=config.vector_store.get("chunk_overlap", 200),
        )

    def _get_embeddings(self) -> OpenAIEmbeddings:
        """Get OpenAI embeddings instance."""
        api_key = config.get_openai_api_key()
        if not api_key:
            raise ValueError(
                "OpenAI API key not found. Please configure it in ~/.config/rag-retriever/config.yaml"
            )

        logger.debug("Using OpenAI API key: %s", mask_api_key(api_key))
        return OpenAIEmbeddings(
            model=config.vector_store["embedding_model"],
            openai_api_key=api_key,
            dimensions=config.vector_store["embedding_dimensions"],
        )

    def _get_or_create_db(self, documents: Optional[List[Document]] = None) -> Chroma:
        """Get existing vector store or create a new one."""
        if self._db is not None:
            logger.debug("Using existing database instance")
            return self._db

        # Create the directory if it doesn't exist
        os.makedirs(self.persist_directory, exist_ok=True)
        logger.debug("Created directory: %s", self.persist_directory)

        # Load existing DB if it exists
        if os.path.exists(self.persist_directory) and os.listdir(
            self.persist_directory
        ):
            logger.debug("Loading existing database from: %s", self.persist_directory)
            self._db = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_metadata={"hnsw:space": "cosine"},
            )
            # Add new documents if provided
            if documents is not None:
                logger.debug("Adding %d documents to existing database", len(documents))
                self._db.add_documents(documents)
            return self._db

        # Create new DB with documents
        if documents is None:
            logger.debug("No existing database found and no documents provided")
            raise ValueError(
                "No existing vector store found and no documents provided to create one."
            )

        logger.debug("Creating new database with %d documents", len(documents))
        self._db = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_metadata={"hnsw:space": "cosine"},
        )
        return self._db

    @retry(
        stop=stop_after_attempt(lambda: config.vector_store["batch_processing"]["max_retries"]),
        wait=wait_exponential(
            multiplier=lambda: config.vector_store["batch_processing"]["retry_delay"],
            min=1,
            max=60
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
            config.vector_store["batch_processing"]["retry_delay"]
        )
    )
    def _process_batch(self, batch: List[Document]) -> bool:
        """Process a single batch of documents with retry logic."""
        try:
            db = self._get_or_create_db()
            logger.info("Storing batch of %d chunks to vector database...", len(batch))
            db.add_documents(batch)
            logger.info("Successfully stored batch to vector database")
            return True
        except Exception as e:
            if "rate limit" in str(e).lower() or "quota" in str(e).lower():
                logger.info("Rate limiting error details: %s", str(e))
            else:
                logger.error("Error processing batch: %s", str(e))
            raise

    def add_documents(self, documents: List[Document]) -> int:
        """Add documents to the vector store using batch processing."""
        try:
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
            delay = batch_settings["delay_between_batches"]
            
            successful_chunks = 0
            total_batches = (len(splits) + batch_size - 1) // batch_size
            
            for i in range(0, len(splits), batch_size):
                batch = splits[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                
                logger.info(
                    "Processing batch %d/%d (%d chunks)",
                    batch_num,
                    total_batches,
                    len(batch)
                )
                
                if self._process_batch(batch):
                    successful_chunks += len(batch)
                    logger.info(
                        "Batch %d/%d completed successfully (%d/%d chunks processed)",
                        batch_num,
                        total_batches,
                        successful_chunks,
                        len(splits)
                    )
                else:
                    logger.error(
                        "Batch %d/%d failed (%d/%d chunks processed)",
                        batch_num,
                        total_batches,
                        successful_chunks,
                        len(splits)
                    )
                
                if i + batch_size < len(splits):  # If not the last batch
                    logger.debug("Waiting %.1f seconds before next batch", delay)
                    time.sleep(delay)
            
            if successful_chunks < len(splits):
                logger.warning(
                    "Partial success: %d/%d chunks successfully processed",
                    successful_chunks,
                    len(splits)
                )
            else:
                logger.info(
                    "All %d chunks successfully processed",
                    successful_chunks
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
    ) -> List[Tuple[Document, float]]:
        """Search for documents similar to query."""
        db = self._get_or_create_db()
        results = db.similarity_search_with_relevance_scores(
            query,
            k=limit,
            score_threshold=score_threshold,
        )
        return results
