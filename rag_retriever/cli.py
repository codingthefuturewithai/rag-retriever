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
logging.getLogger("googleapiclient").setLevel(logging.WARNING)  # Added for Google API
logging.getLogger("primp").setLevel(logging.WARNING)  # Added for DuckDuckGo
logging.getLogger("google").setLevel(logging.WARNING)  # Added for Google API

# Now import the rest
from rag_retriever.main import process_url, search_content
from rag_retriever.vectorstore.store import clean_vectorstore, VectorStore
from rag_retriever.utils.system_validation import validate_system_dependencies, SystemValidationError
from rag_retriever.document_processor import (
    LocalDocumentLoader,
    ImageLoader,
    ConfluenceDocumentLoader,
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
        "--version",
        action="store_true",
        help="Show version information",
    )

    parser.add_argument(
        "--ui",
        action="store_true",
        help="Launch the RAG Retriever web interface",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8501,
        help="Port to run the web interface on (default: 8501). Only used with --ui",
    )

    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize user configuration files in standard locations",
    )

    parser.add_argument(
        "--list-collections",
        action="store_true",
        help="List all available collections and their metadata",
    )

    parser.add_argument(
        "--fetch-url",
        type=str,
        help="URL to fetch and index",
    )

    parser.add_argument(
        "--max-depth",
        type=int,
        default=2,
        help="Maximum depth for recursive URL loading when using --fetch-url (default: 2). Not applicable to other commands.",
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
        help="Clean (delete) the vector store. Use with --collection to delete a specific collection.",
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
        help="Perform a web search query",
    )

    parser.add_argument(
        "--search-provider",
        type=str,
        choices=["duckduckgo", "google"],
        help="Search provider to use (defaults to duckduckgo if not specified or if Google credentials not configured)",
    )

    parser.add_argument(
        "--google-api-key",
        type=str,
        help="Google API key for search (overrides config and environment variable)",
    )

    parser.add_argument(
        "--google-cse-id",
        type=str,
        help="Google Custom Search Engine ID (overrides config and environment variable)",
    )

    parser.add_argument(
        "--results",
        type=int,
        default=config.search.get("default_web_results", 5),
        help="Number of results to return for web search (default from config)",
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

    parser.add_argument(
        "--collection",
        type=str,
        help="Name of the collection to use (defaults to 'default')",
    )

    parser.add_argument(
        "--search-all-collections",
        action="store_true",
        help="Search across all collections (ignores --collection)",
    )

    return parser


def confirm_max_depth(depth: int) -> bool:
    """Confirm with user before proceeding with high depth crawl."""
    print(f"\nWarning: Using max_depth={depth} will recursively load pages.")
    print("This may take a while and consume significant resources.")
    response = input("Do you want to continue? [y/N] ").lower()
    return response in ["y", "yes"]


def handle_mcp_requests():
    """Handle MCP requests from stdin."""
    server = MCPServer()

    while True:
        try:
            # Read request from stdin
            request = json.loads(input())

            # Extract operation and parameters
            operation = request.get("operation")
            params = request.get("parameters", {})

            # Handle the request
            try:
                result = server.handle_request(operation, **params)
                print(json.dumps(result))
                sys.stdout.flush()
            except Exception as e:
                error_response = {
                    "content": [{"type": "error", "text": str(e)}],
                    "isError": True,
                }
                print(json.dumps(error_response))
                sys.stdout.flush()

        except EOFError:
            break
        except json.JSONDecodeError as e:
            error_response = {
                "content": [
                    {"type": "error", "text": f"Invalid JSON request: {str(e)}"}
                ],
                "isError": True,
            }
            print(json.dumps(error_response))
            sys.stdout.flush()


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

    # Handle version display first
    if args.version:
        import importlib.metadata

        try:
            version = importlib.metadata.version("rag-retriever")
            print(f"RAG Retriever version {version}")
            return 0
        except importlib.metadata.PackageNotFoundError:
            print("RAG Retriever version: development")
            return 0
    
    # Validate system dependencies early (skip for init and version)
    if not args.init:
        try:
            validate_system_dependencies()
        except SystemValidationError as e:
            logger.error("System validation failed:")
            logger.error(str(e))
            return 1

    # Handle UI launch first
    if args.ui:
        import streamlit.web.cli as stcli
        import sys
        import os

        # Get the path to the UI script
        ui_script = os.path.join(os.path.dirname(__file__), "ui", "app.py")
        sys.argv = ["streamlit", "run", ui_script, "--server.port", str(args.port)]
        sys.exit(stcli.main())

    # Validate max-depth usage
    if args.max_depth != 2 and not args.fetch_url:  # 2 is the default value
        logger.error("The --max-depth option can only be used with --fetch-url")
        return 1

    if args.init:
        initialize_user_files()
        return

    if args.list_collections:
        store = VectorStore()
        collections = store.list_collections()
        if not collections:
            print("\nNo collections found.")
            return 0

        print("\nAvailable collections:")
        for collection in collections:
            print(f"\nCollection: {collection['name']}")
            print(f"  Created: {collection['created_at']}")
            print(f"  Last Modified: {collection['last_modified']}")
            print(f"  Documents: {collection['document_count']}")
            print(f"  Total Chunks: {collection['total_chunks']}")
            if collection.get("description"):
                print(f"  Description: {collection['description']}")
        return 0

    if args.clean:
        if args.collection:
            clean_vectorstore(collection_name=args.collection)
        else:
            clean_vectorstore()  # Deletes entire store
        return

    if args.web_search:
        # Set Google Search credentials from command line if provided
        if args.google_api_key:
            os.environ["GOOGLE_API_KEY"] = args.google_api_key
        if args.google_cse_id:
            os.environ["GOOGLE_CSE_ID"] = args.google_cse_id

        try:
            results = web_search(
                args.web_search, args.results, provider=args.search_provider
            )
            if args.json:
                print(
                    json.dumps(
                        [
                            {"title": r.title, "url": r.url, "snippet": r.snippet}
                            for r in results
                        ],
                        indent=2,
                    )
                )
            else:
                print(f"\nSearch results for: {args.web_search}\n")
                for i, result in enumerate(results, 1):
                    print(f"{i}. {result.title}")
                    print(f"   URL: {result.url}")
                    print(f"   {result.snippet}\n")
            return 0
        except ValueError as e:
            print(f"\nError: {str(e)}")
            return 1
        except Exception as e:
            logger.error(f"Unexpected error during web search: {e}")
            print(
                "\nAn unexpected error occurred during the web search. Please try again."
            )
            return 1

    # Handle image ingestion
    if args.ingest_image or args.ingest_image_directory:
        try:
            image_loader = ImageLoader(config=config._config, show_progress=True)
            store = VectorStore(collection_name=args.collection)

            if args.ingest_image:
                logger.info(f"Loading image: {args.ingest_image}")
                document = image_loader.load_image(args.ingest_image)
                if document:
                    documents = [document]
                else:
                    logger.error("Failed to load image")
                    return 1
            else:
                logger.info(
                    f"Loading images from directory: {args.ingest_image_directory}"
                )
                documents = image_loader.load_directory(args.ingest_image_directory)
                if not documents:
                    logger.error("No valid images found in directory")
                    return 1

            store.add_documents(documents)
            logger.info(f"Successfully ingested {len(documents)} image(s)")
            return 0

        except Exception as e:
            logger.error(f"Error ingesting images: {str(e)}")
            return 1

    # Handle local document ingestion
    if args.ingest_file or args.ingest_directory:
        try:
            loader = LocalDocumentLoader(
                config=config._config, show_progress=True, use_multithreading=True
            )
            store = VectorStore(collection_name=args.collection)

            if args.ingest_file:
                logger.info(f"Loading file: {args.ingest_file}")
                documents = loader.load_file(args.ingest_file)
            else:
                logger.info(f"Loading directory: {args.ingest_directory}")
                documents = loader.load_directory(args.ingest_directory)

            store.add_documents(documents)
            logger.info("Successfully ingested local documents")
            return 0

        except Exception as e:
            logger.error(f"Error ingesting documents: {str(e)}")
            return 1

    # Handle Confluence content loading
    if args.confluence:
        try:
            loader = ConfluenceDocumentLoader(config=config._config)
            store = VectorStore(collection_name=args.collection)
            documents = loader.load_pages(
                space_key=args.space_key, parent_id=args.parent_id
            )
            store.add_documents(documents)
            logger.info("Successfully loaded Confluence content")
            return 0

        except Exception as e:
            logger.error(f"Error loading Confluence content: {str(e)}")
            return 1

    # Handle GitHub repository loading
    if args.github_repo:
        try:
            loader = GitHubLoader(config=config._config)
            store = VectorStore(collection_name=args.collection)

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
            return 0

        except Exception as e:
            logger.error(f"Error loading GitHub repository: {str(e)}")
            return 1

    try:
        if args.fetch_url:
            # Only prompt once for max_depth > 1
            if args.max_depth > 1 and not confirm_max_depth(args.max_depth):
                logger.info("Operation cancelled")
                return 0

            return process_url(
                args.fetch_url,
                max_depth=args.max_depth,
                verbose=args.verbose,
                collection_name=args.collection,
            )

        if args.query:
            return search_content(
                args.query,
                limit=args.limit,
                score_threshold=args.score_threshold,
                full_content=not args.truncate,  # Show full content by default
                json_output=args.json,
                verbose=args.verbose,
                collection_name=args.collection,
                search_all_collections=args.search_all_collections,
            )

        # No command specified, show help
        parser.print_help()
        return 0

    except Exception as e:
        logger.error("Error: %s", str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())
