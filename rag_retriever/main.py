"""Main application logic."""

from typing import Optional, List, Dict, Any
import json
import logging
import os
import time
import platform
from pathlib import Path
from datetime import datetime
import asyncio
import warnings

from playwright.async_api import Error as PlaywrightError
from rag_retriever.crawling.playwright_crawler import PlaywrightCrawler
from rag_retriever.crawling.exceptions import PageLoadError, ContentExtractionError

# Try to import Crawl4AI crawler, fallback if not available
try:
    from rag_retriever.crawling.crawl4ai_crawler import Crawl4AICrawler
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False
from rag_retriever.search.searcher import Searcher
from rag_retriever.vectorstore.store import VectorStore, get_vectorstore_path
from rag_retriever.utils.config import (
    config,
    mask_api_key,
    get_user_friendly_config_path,
)
from rag_retriever.utils.windows import suppress_asyncio_warnings, windows_event_loop
from rag_retriever.utils.system_validation import validate_system_dependencies, SystemValidationError
from openai import OpenAI

logger = logging.getLogger(__name__)

# Maximum number of retries for recoverable errors
MAX_RETRIES = 3
# Delay between retries (in seconds)
RETRY_DELAY = 2


def get_crawler():
    """Get the appropriate crawler based on configuration."""
    crawler_type = config.crawler.get("type", "playwright")
    
    if crawler_type == "crawl4ai":
        logger.info("Using Crawl4AI crawler")
        return Crawl4AICrawler()
    else:
        logger.info("Using Playwright crawler")
        return PlaywrightCrawler()


def get_system_info() -> Dict[str, str]:
    """Get system information for diagnostics."""
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "memory": (
            os.popen("free -h").readlines()[1].split()[1]
            if platform.system() == "Linux"
            else "N/A"
        ),
    }


def get_openai_client() -> OpenAI:
    """Get an authenticated OpenAI client."""
    logger.debug("Getting OpenAI client...")
    api_key = config.get_openai_api_key()
    logger.debug(
        "API key retrieved from config: %s", "Found" if api_key else "Not found"
    )

    if not api_key:
        logger.error("No valid API key found in config or environment")
        raise ValueError(
            "Valid OpenAI API key not found. Please configure it by either:\n"
            "1. Setting OPENAI_API_KEY environment variable\n"
            f"2. Adding it to {get_user_friendly_config_path()} under api.openai_api_key\n"
            "The API key should start with 'sk-'"
        )

    logger.debug("Creating OpenAI client with API key")
    try:
        client = OpenAI(api_key=api_key)
        logger.debug("OpenAI client created successfully")
        return client
    except Exception as e:
        logger.error("Failed to create OpenAI client: %s", str(e))
        raise


def process_url(
    url: str,
    max_depth: int = 2,
    verbose: bool = True,
    collection_name: Optional[str] = None,
) -> int:
    """Process a URL, extracting and indexing its content.

    Args:
        url: URL to process
        max_depth: Maximum depth for recursive crawling
        verbose: Whether to show verbose output
        collection_name: Optional name of collection to use (defaults to 'default')
    """
    # Configure asyncio debug mode and logging
    logging.getLogger("asyncio").setLevel(logging.DEBUG)
    warnings.resetwarnings()  # Reset any warning filters
    warnings.filterwarnings(
        "default", category=ResourceWarning
    )  # Show resource warnings

    @windows_event_loop
    def _process():
        # Validate system dependencies first
        try:
            validate_system_dependencies()
        except SystemValidationError as e:
            logger.error("System validation failed:")
            logger.error(str(e))
            return 1
        
        # Enable asyncio debug mode
        loop = asyncio.get_event_loop()
        loop.set_debug(True)
        loop.slow_callback_duration = 0.1  # Log callbacks taking > 100ms

        start_time = time.time()
        crawl_stats = {
            "pages_attempted": 0,
            "pages_successful": 0,
            "pages_failed": 0,
            "total_content_size": 0,
            "retry_count": 0,
            "errors": {},
        }

        # Set third-party logging levels based on verbose mode
        if verbose:
            logging.getLogger("chromadb").setLevel(logging.INFO)
            logging.getLogger("httpx").setLevel(logging.INFO)
            logging.getLogger("urllib3").setLevel(logging.INFO)

        # System diagnostics
        sys_info = get_system_info()
        logger.debug("\nSystem Information:")
        for key, value in sys_info.items():
            logger.debug(f"- {key}: {value}")

        # Log configuration
        logger.debug("\nConfiguration:")
        logger.debug("- URL: %s", url)
        logger.debug("- Max depth: %d", max_depth)
        logger.debug("- Vector store: %s", get_vectorstore_path())
        logger.debug("- Model: %s", config.vector_store["embedding_model"])
        api_key = config.get_openai_api_key()
        logger.debug("- API key: %s", mask_api_key(api_key if api_key else ""))
        logger.debug("- Config file: %s", config.config_path)

        # Browser configuration
        logger.debug("\nBrowser configuration:")
        logger.debug(
            "- Headless mode: %s", config.browser["launch_options"]["headless"]
        )
        logger.debug(
            "- Browser channel: %s",
            config.browser["launch_options"].get("channel", "default"),
        )
        logger.debug("- Wait time: %d seconds", config.browser["wait_time"])
        logger.debug(
            "- Viewport: %dx%d",
            config.browser["viewport"]["width"],
            config.browser["viewport"]["height"],
        )

        try:
            logger.info("\nStarting content fetch and indexing process...")
            logger.debug("Initializing browser...")
            crawler = get_crawler()
            store = VectorStore(collection_name=collection_name)

            retry_count = 0
            while retry_count < MAX_RETRIES:
                try:
                    # Use the synchronous wrapper for the async crawler
                    logger.info("Starting crawl operation...")
                    documents = crawler.run_crawl(url, max_depth=max_depth)

                    # Check if we got any documents
                    if not documents:
                        logger.error(
                            "No documents were retrieved. The crawl operation failed to fetch any content."
                        )
                        return 1

                    # Update statistics
                    crawl_stats["pages_successful"] = len(documents)
                    crawl_stats["total_content_size"] = sum(
                        len(doc.page_content) for doc in documents
                    )

                    if verbose:
                        logger.info("\nCrawl statistics:")
                        logger.info(
                            "- Pages processed successfully: %d",
                            crawl_stats["pages_successful"],
                        )
                        logger.info(
                            "- Total content size: %.2f KB",
                            crawl_stats["total_content_size"] / 1024,
                        )
                        logger.info(
                            "- Average content size: %.2f KB",
                            (
                                crawl_stats["total_content_size"]
                                / len(documents)
                                / 1024
                                if documents
                                else 0
                            ),
                        )
                        logger.info(
                            "- Crawl duration: %.2f seconds", time.time() - start_time
                        )
                        logger.info(
                            "- Pages/second: %.2f",
                            (
                                len(documents) / (time.time() - start_time)
                                if documents
                                else 0
                            ),
                        )
                        if crawl_stats["retry_count"]:
                            logger.info(
                                "- Retry attempts: %d", crawl_stats["retry_count"]
                            )
                            logger.info(
                                "- Error types encountered: %s",
                                ", ".join(crawl_stats["errors"].keys()),
                            )

                    logger.info("\nIndexing documents...")
                    store.add_documents(documents)
                    logger.info("Indexing complete.")

                    return 0

                except (PageLoadError, PlaywrightError) as e:
                    retry_count += 1
                    crawl_stats["retry_count"] += 1
                    error_type = e.__class__.__name__
                    crawl_stats["errors"][error_type] = (
                        crawl_stats["errors"].get(error_type, 0) + 1
                    )

                    if retry_count < MAX_RETRIES:
                        logger.warning(f"Attempt {retry_count} failed: {str(e)}")
                        logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                        time.sleep(RETRY_DELAY * retry_count)  # Exponential backoff
                        continue
                    else:
                        logger.error(f"Failed after {MAX_RETRIES} attempts: {str(e)}")
                        if isinstance(
                            e, PlaywrightError
                        ) and "Chromium revision is not downloaded" in str(e):
                            logger.error(
                                "Try running 'playwright install chromium' to install required browser."
                            )
                        return 1

                except ContentExtractionError as e:
                    logger.error("Failed to extract content: %s", str(e))
                    crawl_stats["errors"]["ContentExtractionError"] = (
                        crawl_stats["errors"].get("ContentExtractionError", 0) + 1
                    )
                    return 1

        except Exception as e:
            logger.error("Unexpected error: %s", str(e))
            crawl_stats["errors"]["UnexpectedError"] = (
                crawl_stats["errors"].get("UnexpectedError", 0) + 1
            )
            return 1

        finally:
            if "crawler" in locals():
                logger.debug("Cleaning up browser resources...")
                if verbose:
                    logger.info("\nFinal Statistics:")
                    logger.info(
                        "- Total execution time: %.2f seconds", time.time() - start_time
                    )
                    logger.info(
                        "- Memory usage: %s",
                        (
                            os.popen("ps -o rss= -p %d" % os.getpid()).read().strip()
                            if platform.system() != "Windows"
                            else "N/A"
                        ),
                    )
                    if crawl_stats["errors"]:
                        logger.info("- Error summary:")
                        for error_type, count in crawl_stats["errors"].items():
                            logger.info(f"  - {error_type}: {count} occurrences")

    return _process()


def search_content(
    query: str,
    limit: Optional[int] = None,
    score_threshold: Optional[float] = None,
    full_content: bool = False,
    json_output: bool = False,
    verbose: bool = False,
    collection_name: Optional[str] = None,
    search_all_collections: bool = False,
) -> int:
    """Search indexed content.

    Args:
        query: Search query string
        limit: Maximum number of results to return
        score_threshold: Minimum similarity score threshold
        full_content: Whether to show full content in results
        json_output: Whether to output results as JSON
        verbose: Whether to show verbose output
        collection_name: Optional name of collection to search in (defaults to 'default')
        search_all_collections: Whether to search across all collections
    """
    # Use default values from config if not specified
    if limit is None:
        limit = config.search["default_limit"]
    if score_threshold is None:
        score_threshold = config.search["default_score_threshold"]

    # Set third-party logging levels based on verbose mode
    if verbose:
        logging.getLogger("chromadb").setLevel(logging.INFO)
        logging.getLogger("httpx").setLevel(logging.INFO)
        logging.getLogger("urllib3").setLevel(logging.INFO)

    # Log configuration
    logger.debug("\nConfiguration:")
    logger.debug("- Query: %s", query)
    logger.debug("- Result limit: %d", limit)
    logger.debug("- Score threshold: %.2f", score_threshold)
    logger.debug("- Vector store: %s", get_vectorstore_path())
    logger.debug("- Model: %s", config.vector_store["embedding_model"])
    api_key = config.get_openai_api_key()
    logger.debug("- API key: %s", mask_api_key(api_key if api_key else ""))
    logger.debug("- Config file: %s", config.config_path)

    try:
        logger.info("\nStarting content search...")
        searcher = Searcher(collection_name=collection_name)
        results = searcher.search(
            query,
            limit=limit,
            score_threshold=score_threshold,
            search_all_collections=search_all_collections,
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
