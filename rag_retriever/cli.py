#!/usr/bin/env python3
"""Command-line interface for the RAG retriever application."""

import sys
import os
import logging
from pathlib import Path
import argparse
import json

# Configure logging first, before any other imports
log_level = os.environ.get("RAG_RETRIEVER_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level), format="%(levelname)s:%(name)s:%(message)s"
)

# Set module log levels
logging.getLogger("rag_retriever").setLevel(getattr(logging, log_level))
# Keep third-party logs at WARNING by default
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# Now import the rest
from rag_retriever.main import process_url, search_content
from rag_retriever.vectorstore.store import clean_vectorstore, VectorStore
from rag_retriever.document_processor import (
    LocalDocumentLoader,
    ImageLoader,
    ConfluenceLoader,
    GitHubLoader,
)
from rag_retriever.utils.config import initialize_user_files, config
from rag_retriever.utils.windows import suppress_asyncio_warnings
from rag_retriever.search.web_search import web_search

logger = logging.getLogger(__name__)
logger.debug("Log level set to: %s", log_level)


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="RAG Retriever - Fetch, index, and search web content"
    )

    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize user configuration files in standard locations",
    )

    parser.add_argument(
        "--fetch",
        type=str,
        help="URL to fetch and index",
    )

    parser.add_argument(
        "--max-depth",
        type=int,
        default=2,
        help="Maximum depth for recursive URL loading (default: 2)",
    )

    parser.add_argument(
        "--query",
        type=str,
        help="Search query to find relevant content",
    )

    parser.add_argument(
        "--limit",
        type=int,
        help="Maximum number of results to return",
    )

    parser.add_argument(
        "--score-threshold",
        type=float,
        help="Minimum relevance score threshold",
    )

    parser.add_argument(
        "--truncate",
        action="store_true",
        help="Truncate content in search results (default: show full content)",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format",
    )

    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean (delete) the vector store",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output for troubleshooting",
    )

    parser.add_argument(
        "--ingest-file",
        type=str,
        help="Path to a local markdown or text file to ingest",
    )

    parser.add_argument(
        "--ingest-directory",
        type=str,
        help="Path to a directory containing markdown and text files to ingest",
    )

    parser.add_argument(
        "--web-search",
        type=str,
        help="Perform a web search using DuckDuckGo",
    )

    parser.add_argument(
        "--results",
        type=int,
        default=5,
        help="Number of results to return for web search (default: 5)",
    )

    parser.add_argument(
        "--confluence",
        action="store_true",
        help="Load content from Confluence using configured settings",
    )

    parser.add_argument(
        "--space-key",
        type=str,
        help="Confluence space key to load content from",
    )

    parser.add_argument(
        "--parent-id",
        type=str,
        help="Confluence parent page ID to start loading from",
    )

    # Add image ingestion arguments
    parser.add_argument(
        "--ingest-image",
        type=str,
        help="Path to an image file or URL to analyze and ingest",
    )

    parser.add_argument(
        "--ingest-image-directory",
        type=str,
        help="Path to a directory containing images to analyze and ingest",
    )

    # Add GitHub repository loading arguments
    parser.add_argument(
        "--github-repo",
        type=str,
        help="URL of the GitHub repository to load",
    )

    parser.add_argument(
        "--branch",
        type=str,
        help="Specific branch to load from the repository",
    )

    parser.add_argument(
        "--file-extensions",
        type=str,
        nargs="+",
        help="Specific file extensions to load (e.g., .py .md .js)",
    )

    return parser


def confirm_max_depth(depth: int) -> bool:
    """Confirm with user before proceeding with high depth crawl."""
    print(f"\nWarning: Using max_depth={depth} will recursively load pages.")
    print("This may take a while and consume significant resources.")
    response = input("Do you want to continue? [y/N] ").lower()
    return response in ["y", "yes"]


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if args.verbose:
        # Set root logger to INFO
        logging.getLogger().setLevel(logging.INFO)
        # Set rag_retriever logger to DEBUG for detailed output
        logging.getLogger("rag_retriever").setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")

    if args.init:
        initialize_user_files()
        sys.exit(0)

    if args.clean:
        clean_vectorstore()
        sys.exit(0)

    if args.web_search:
        results = web_search(args.web_search, args.results)
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.title}")
            print(f"   URL: {result.url}")
            print(f"   {result.snippet}")
        sys.exit(0)

    # Handle image ingestion
    if args.ingest_image or args.ingest_image_directory:
        try:
            image_loader = ImageLoader(config=config._config, show_progress=True)
            store = VectorStore()

            if args.ingest_image:
                logger.info(f"Loading image: {args.ingest_image}")
                document = image_loader.load_image(args.ingest_image)
                if document:
                    documents = [document]
                else:
                    logger.error("Failed to load image")
                    sys.exit(1)
            else:
                logger.info(
                    f"Loading images from directory: {args.ingest_image_directory}"
                )
                documents = image_loader.load_directory(args.ingest_image_directory)
                if not documents:
                    logger.error("No valid images found in directory")
                    sys.exit(1)

            store.add_documents(documents)
            logger.info(f"Successfully ingested {len(documents)} image(s)")
            sys.exit(0)

        except Exception as e:
            logger.error(f"Error ingesting images: {str(e)}")
            sys.exit(1)

    # Handle local document ingestion
    if args.ingest_file or args.ingest_directory:
        try:
            loader = LocalDocumentLoader(
                config=config._config, show_progress=True, use_multithreading=True
            )
            store = VectorStore()

            if args.ingest_file:
                logger.info(f"Loading file: {args.ingest_file}")
                documents = loader.load_file(args.ingest_file)
            else:
                logger.info(f"Loading directory: {args.ingest_directory}")
                documents = loader.load_directory(args.ingest_directory)

            store.add_documents(documents)
            logger.info("Successfully ingested local documents")
            sys.exit(0)

        except Exception as e:
            logger.error(f"Error ingesting documents: {str(e)}")
            sys.exit(1)

    # Handle Confluence content loading
    if args.confluence:
        try:
            loader = ConfluenceLoader(
                config=config._config,
                space_key=args.space_key,
                parent_id=args.parent_id,
            )
            store = VectorStore()
            documents = loader.load_content()
            store.add_documents(documents)
            logger.info("Successfully loaded Confluence content")
            sys.exit(0)

        except Exception as e:
            logger.error(f"Error loading Confluence content: {str(e)}")
            sys.exit(1)

    # Handle GitHub repository loading
    if args.github_repo:
        try:
            loader = GitHubLoader(config=config._config)
            store = VectorStore()

            # Create file filter if extensions specified
            file_filter = None
            if args.file_extensions:
                file_filter = lambda x: any(
                    x.endswith(ext) for ext in args.file_extensions
                )

            logger.info(f"Loading GitHub repository: {args.github_repo}")
            documents = loader.load_repository(
                repo_url=args.github_repo, branch=args.branch, file_filter=file_filter
            )

            store.add_documents(documents)
            logger.info(
                f"Successfully loaded {len(documents)} documents from repository"
            )
            sys.exit(0)

        except Exception as e:
            logger.error(f"Error loading GitHub repository: {str(e)}")
            sys.exit(1)

    try:
        if args.fetch:
            # Only prompt once for max_depth > 1
            if args.max_depth > 1 and not confirm_max_depth(args.max_depth):
                logger.info("Operation cancelled")
                return 0

            return process_url(
                args.fetch, max_depth=args.max_depth, verbose=args.verbose
            )

        if args.query:
            return search_content(
                args.query,
                limit=args.limit,
                score_threshold=args.score_threshold,
                full_content=not args.truncate,  # Show full content by default
                json_output=args.json,
                verbose=args.verbose,
            )

        # No command specified, show help
        parser.print_help()
        return 0

    except Exception as e:
        logger.error("Error: %s", str(e))
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
