"""Main application logic."""
from typing import Optional, List, Dict, Any
import json

from src.crawling.crawler import Crawler
from src.search.searcher import Searcher
from src.vectorstore.store import VectorStore
from src.utils.config import config

def process_url(url: str, max_depth: int = 2) -> int:
    """Crawl and index content from a URL."""
    try:
        # Create instances
        crawler = Crawler()
        vector_store = VectorStore()
        
        # Crawl and get documents
        documents = crawler.crawl(url, max_depth=max_depth)
        
        # Add to vector store
        vector_store.add_documents(documents)
        return 0
    except Exception as e:
        print(f"Error processing URL: {e}")
        return 1

def search_content(
    query: str,
    limit: int = 5,
    score_threshold: float = 0.2,
    full_content: bool = False,
    json_output: bool = False
) -> int:
    """Search indexed content."""
    try:
        # Create searcher
        searcher = Searcher()
        
        # Get results
        results = searcher.search(
            query,
            limit=limit,
            score_threshold=score_threshold
        )
        
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
