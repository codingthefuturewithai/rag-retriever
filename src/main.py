"""Command-line interface for the RAG retriever application."""

import argparse
import json
import sys
from typing import List, Optional

from src.crawling.crawler import Crawler
from src.crawling.exceptions import CrawlerError, PageLoadError, ContentExtractionError
from src.search.searcher import Searcher, SearchResult
from src.vectorstore.store import VectorStore
from src.utils.config import config


def fetch_and_store(
    url: str, max_depth: int, json_output: bool = False
) -> Optional[str]:
    """Fetch content from URL and store in vector database.

    Args:
        url: URL to fetch content from.
        max_depth: Maximum depth for recursive crawling.
        json_output: Whether to output in JSON format.

    Returns:
        Error message if any, None on success.
    """
    try:
        # Crawl the URL
        crawler = Crawler()
        docs = crawler.crawl(url, max_depth=max_depth)

        # Store the documents
        store = VectorStore()
        num_chunks = store.add_documents(docs)

        if not json_output:
            print(f"\nVector store location: {store.persist_directory}")
            print(f"Loading content from {url}")
            print(f"Found {len(docs)} documents")
            print(f"Processed into {num_chunks} chunks and stored in vector database")

    except (CrawlerError, PageLoadError, ContentExtractionError) as e:
        return str(e)
    except Exception as e:
        return f"Unexpected error: {str(e)}"

    return None


def search_documents(
    query: str,
    limit: int,
    score_threshold: float,
    show_full: bool = False,
    json_output: bool = False,
) -> Optional[str]:
    """Search for documents matching query.

    Args:
        query: Search query.
        limit: Maximum number of results.
        score_threshold: Minimum relevance score.
        show_full: Whether to show full content.
        json_output: Whether to output in JSON format.

    Returns:
        Error message if any, None on success.
    """
    try:
        # Search for documents
        searcher = Searcher()
        results = searcher.search(
            query,
            limit=limit,
            score_threshold=score_threshold,
        )

        if results:
            if json_output:
                # For JSON output, just print the JSON array
                json_results = [
                    searcher.format_result_json(result) for result in results
                ]
                print(json.dumps(json_results, indent=2))
            else:
                print(
                    f"\nVector store location: {searcher.vector_store.persist_directory}"
                )
                print(f"\nSearching for: '{query}'")
                print(f"Score threshold: {score_threshold}")

                for i, result in enumerate(results):
                    print(searcher.format_result(result, show_full=show_full))
        elif not json_output:
            print("\nNo relevant documents found.")

    except Exception as e:
        return f"Search error: {str(e)}"

    return None


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="Load URL content into vector store and query it",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch and index content from a website
  python main.py --fetch https://example.com --max-depth 2

  # Search the vector store
  python main.py --query "What is discussed?"
        """,
    )

    # Make URL optional and mutually exclusive with fetch/query
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "url", nargs="?", help="URL to process (deprecated: use --fetch instead)"
    )
    group.add_argument("--fetch", help="Fetch and index content from a URL")
    group.add_argument("--query", help="Query to search for in the documents")

    # Other arguments
    parser.add_argument(
        "--max-depth",
        type=int,
        default=2,
        help="Maximum depth for recursive URL loading",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=config.search["default_limit"],
        help=f"Maximum number of results to return (default: {config.search['default_limit']})",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Show full document content instead of preview",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format",
    )
    parser.add_argument(
        "--score-threshold",
        type=float,
        default=config.search["default_score_threshold"],
        help=f"Only return results with scores above this threshold (default: {config.search['default_score_threshold']})",
    )

    args = parser.parse_args()
    error = None

    try:
        # Handle fetch (either from positional URL or --fetch option)
        url_to_fetch = args.url or args.fetch
        if url_to_fetch:
            error = fetch_and_store(url_to_fetch, args.max_depth, args.json)

        # If query is provided, search the vector store
        elif args.query:
            error = search_documents(
                args.query,
                args.limit,
                args.score_threshold,
                args.full,
                args.json,
            )

        # If neither URL nor query is provided, show help
        else:
            parser.print_help()

    except Exception as e:
        error = f"Error: {str(e)}"

    if error and not args.json:
        print(error, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
