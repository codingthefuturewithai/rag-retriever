#!/usr/bin/env python3
"""Command-line interface for the RAG retriever application."""

import sys
import os
import logging
from pathlib import Path
import argparse

from rag_retriever.main import process_url, search_content
from rag_retriever.vectorstore.store import clean_vectorstore, VectorStore
from rag_retriever.document_processor import LocalDocumentLoader
from rag_retriever.utils.config import initialize_user_files, config

# Configure logging - suppress most output by default
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Set default levels for other modules
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)


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
        logging.getLogger().setLevel(logging.INFO)
        logger.debug("Verbose logging enabled")

    if args.init:
        initialize_user_files()
        sys.exit(0)

    if args.clean:
        clean_vectorstore()
        sys.exit(0)

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
