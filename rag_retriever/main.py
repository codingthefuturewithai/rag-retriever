"""Main application logic."""

from typing import Optional, List, Dict, Any
import json
import logging
import os
from pathlib import Path

from rag_retriever.crawling.crawler import Crawler
from rag_retriever.search.searcher import Searcher
from rag_retriever.vectorstore.store import VectorStore, get_vectorstore_path
from rag_retriever.utils.config import config, mask_api_key

logger = logging.getLogger(__name__)


def process_url(url: str, max_depth: int = 2, verbose: bool = True) -> int:
    """Process a URL, extracting and indexing its content."""
    # Set logging levels based on verbose mode
    if verbose:
        logging.getLogger().setLevel(logging.INFO)
        logging.getLogger("chromadb").setLevel(logging.INFO)
        logging.getLogger("httpx").setLevel(logging.INFO)
        # Log configuration
        logger.info("\nStarting content fetch and indexing process...")
        logger.info("Configuration:")
        logger.info("- URL: %s", url)
        logger.info("- Max depth: %d", max_depth)
        logger.info("- Vector store: %s", get_vectorstore_path())
        logger.info("- Model: %s", config.vector_store["embedding_model"])
        logger.info("- API key: %s", mask_api_key(os.getenv("OPENAI_API_KEY", "")))
        logger.info("- Config file: %s", config.config_path)
        logger.info("- Environment file: %s", config.env_path)

    try:
        crawler = Crawler()
        store = VectorStore()
        store.add_documents(crawler.crawl(url, max_depth=max_depth))
        return 0
    except Exception as e:
        logger.error("Error processing URL: %s", str(e))
        return 1


def search_content(
    query: str,
    limit: Optional[int] = None,
    score_threshold: Optional[float] = None,
    full_content: bool = False,
    json_output: bool = False,
    verbose: bool = False,
) -> int:
    """Search indexed content."""
    # Use default values from config if not specified
    if limit is None:
        limit = config.search["default_limit"]
    if score_threshold is None:
        score_threshold = config.search["default_score_threshold"]

    # Set logging levels based on verbose mode
    if verbose:
        logging.getLogger().setLevel(logging.INFO)
        logging.getLogger("chromadb").setLevel(logging.INFO)
        logging.getLogger("httpx").setLevel(logging.INFO)
        # Log configuration
        logger.info("\nStarting content search...")
        logger.info("Configuration:")
        logger.info("- Query: %s", query)
        logger.info("- Result limit: %d", limit)
        logger.info("- Score threshold: %.2f", score_threshold)
        logger.info("- Vector store: %s", get_vectorstore_path())
        logger.info("- Model: %s", config.vector_store["embedding_model"])
        logger.info("- API key: %s", mask_api_key(os.getenv("OPENAI_API_KEY", "")))
        logger.info("- Config file: %s", config.config_path)
        logger.info("- Environment file: %s", config.env_path)

    try:
        searcher = Searcher()
        results = searcher.search(
            query,
            limit=limit,
            score_threshold=score_threshold,
        )

        if not results:
            if verbose:
                logger.info("\nNo results found matching the query.")
            return 0

        if json_output:
            print(
                json.dumps([searcher.format_result_json(r) for r in results], indent=2)
            )
        else:
            if verbose:
                print("\nSearch Results:\n")
            for i, result in enumerate(results, 1):
                print(f"{i}. {searcher.format_result(result, show_full=full_content)}")

        return 0
    except Exception as e:
        logger.error("Error searching content: %s", str(e))
        return 1
