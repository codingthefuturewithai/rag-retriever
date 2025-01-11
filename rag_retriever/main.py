"""Main application logic."""

from typing import Optional, List, Dict, Any
import json
import logging
import os
from pathlib import Path

from rag_retriever.crawling.crawler import Crawler
from rag_retriever.search.searcher import Searcher
from rag_retriever.vectorstore.store import VectorStore, get_vectorstore_path
from rag_retriever.utils.config import config

logger = logging.getLogger(__name__)


def process_url(url: str, max_depth: int = 2) -> int:
    """Crawl and index content from a URL."""
    try:
        # Log startup information
        store_path = get_vectorstore_path()
        logger.info("\nStarting content fetch and indexing process...")
        logger.info("Configuration:")
        logger.info("- Vector store location: %s", store_path)
        logger.info("- OpenAI model: %s", config.vector_store["embedding_model"])
        logger.info("- Max crawl depth: %d", max_depth)
        logger.info("- Chunk size: %d chars", config.content["chunk_size"])
        logger.info("- Chunk overlap: %d chars", config.content["chunk_overlap"])

        if not os.environ.get("OPENAI_API_KEY"):
            logger.warning(
                "No OPENAI_API_KEY found in environment. Make sure you have a .env file with your API key."
            )

        # Create instances
        crawler = Crawler()
        vector_store = VectorStore()

        # Crawl and get documents
        logger.info("\nCrawling content from: %s", url)
        documents = crawler.crawl(url, max_depth=max_depth)

        # Add to vector store
        logger.info("\nIndexing documents...")
        num_chunks = vector_store.add_documents(documents)

        # Calculate sizes
        total_doc_size = sum(len(doc.page_content) for doc in documents)
        avg_chunk_size = total_doc_size / num_chunks if num_chunks > 0 else 0

        logger.info("\nIndexing completed successfully:")
        logger.info("- Source URL: %s", url)
        logger.info("- Documents processed: %d", len(documents))
        logger.info("- Total chunks stored: %d", num_chunks)
        logger.info("- Total content size: %d chars", total_doc_size)
        logger.info("- Average chunk size: %.1f chars", avg_chunk_size)

        logger.info("\nTroubleshooting Info:")
        logger.info("- Vector store location: %s", store_path)

        return 0
    except Exception as e:
        logger.error("\nError processing URL: %s", str(e))
        logger.error("\nTroubleshooting steps:")
        logger.error("1. Check your internet connection")
        logger.error("2. Verify the URL is accessible in your browser")
        logger.error("3. Ensure OPENAI_API_KEY is set in your .env file")
        logger.error("4. Try 'rag-retriever --clean' to reset the vector store")
        logger.error(
            "5. If issues persist, try with --max-depth 0 to only fetch the main page"
        )
        return 1


def search_content(
    query: str,
    limit: int = 5,
    score_threshold: float = 0.2,
    full_content: bool = False,
    json_output: bool = False,
) -> int:
    """Search indexed content."""
    try:
        # Create searcher
        searcher = Searcher()

        # Get results
        results = searcher.search(query, limit=limit, score_threshold=score_threshold)

        # Format and output results
        if json_output:
            formatted = [searcher.format_result_json(r) for r in results]
            print(json.dumps(formatted, indent=2))
        else:
            for result in results:
                print(searcher.format_result(result, show_full=full_content))
        return 0
    except Exception as e:
        print(f"Error searching content: {e}")
        return 1
