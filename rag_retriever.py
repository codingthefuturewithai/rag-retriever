#!/usr/bin/env python3
"""Entry point script for the RAG retriever application."""

import sys
import logging
import argparse
import shutil
from pathlib import Path

from src.main import process_url, search_content
from src.vectorstore.store import get_vectorstore_path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

def create_parser():
    parser = argparse.ArgumentParser(
        description="RAG Retriever - A tool for crawling, indexing, and searching web content"
    )
    
    # Main arguments group
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--fetch", 
        metavar="URL",
        help="Fetch and index content from a URL"
    )
    group.add_argument(
        "--query", 
        metavar="QUERY",
        help="Query to search for in the documents"
    )
    group.add_argument(
        "--clean",
        action="store_true",
        help="Delete the vector store database"
    )

    # Optional arguments
    parser.add_argument(
        "--max-depth", 
        type=int, 
        default=2,
        help="Maximum depth for recursive URL loading (default: 2)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum number of results to return (default: 5)"
    )
    parser.add_argument(
        "--full", 
        action="store_true",
        help="Show full document content instead of preview"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    parser.add_argument(
        "--score-threshold", 
        type=float, 
        default=0.2,
        help="Only return results with scores above this threshold (default: 0.2)"
    )
    
    return parser

def clean_vectorstore():
    """Delete the vector store database."""
    vectorstore_path = Path(get_vectorstore_path())
    if vectorstore_path.exists():
        # Prompt for confirmation
        print("\nWARNING: This will delete the entire vector store database.")
        response = input("Are you sure you want to proceed? (y/N): ")
        if response.lower() != 'y':
            logger.info("Operation cancelled")
            return
            
        logger.info("Deleting vector store at %s", vectorstore_path)
        shutil.rmtree(vectorstore_path)
        logger.info("Vector store deleted successfully")
    else:
        logger.info("Vector store not found at %s", vectorstore_path)

def confirm_max_depth(max_depth: int) -> bool:
    """Confirm with user if they want to proceed with max_depth > 1."""
    print(f"\nWARNING: You are about to crawl with max_depth={max_depth}.")
    print("This means the crawler will:")
    print("1. Start at the initial URL")
    print("2. Follow links from that page")
    if max_depth > 1:
        print(f"3. Continue following links up to {max_depth} levels deep")
    print("\nThis can potentially crawl many pages and take a long time.")
    response = input("Are you sure you want to proceed? (y/N): ")
    return response.lower() == 'y'

def main():
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        if args.clean:
            clean_vectorstore()
            return 0
            
        if args.fetch:
            # Only prompt once for max_depth > 1
            if args.max_depth > 1 and not confirm_max_depth(args.max_depth):
                logger.info("Operation cancelled")
                return 0
                
            return process_url(
                args.fetch,
                max_depth=args.max_depth
            )
            
        if args.query:
            return search_content(
                args.query,
                limit=args.limit,
                score_threshold=args.score_threshold,
                full_content=args.full,
                json_output=args.json
            )
            
    except Exception as e:
        logger.error("Error: %s", str(e))
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
