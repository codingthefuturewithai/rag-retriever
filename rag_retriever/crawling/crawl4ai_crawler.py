"""Web page crawling and content extraction module using Crawl4AI."""

import time
import logging
import asyncio
from typing import List, Set, Dict, Any
from urllib.parse import urljoin, urlparse

from langchain_core.documents import Document

# Suppress dotenv warnings from crawl4ai
import os
os.environ['SUPPRESS_DOTENV_WARNING'] = 'true'

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

from rag_retriever.utils.config import config
from rag_retriever.utils.windows import suppress_asyncio_warnings, windows_event_loop
from rag_retriever.crawling.exceptions import (
    PageLoadError,
    ContentExtractionError,
    CrawlerError,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Crawl4AICrawler:
    """Web page crawler using Crawl4AI for fast content extraction."""

    def __init__(self):
        """Initialize the crawler with configuration."""
        self.config = config.browser
        self.visited_urls: Set[str] = set()
        self._total_chunks = 0

    def _create_crawler_config(self, max_depth: int = 0) -> CrawlerRunConfig:
        """
        Create Crawl4AI configuration with aggressive content filtering.
        
        Based on working solution that properly filters navigation content.
        Key: BFSDeepCrawlStrategy + high threshold (0.7) = clean content.
        """
        # Aggressive filtering - this removes navigation content
        md_generator = DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(
                threshold=0.7,  # High threshold = aggressive filtering
                threshold_type="fixed"
            )
        )
        
        return CrawlerRunConfig(
            deep_crawl_strategy=BFSDeepCrawlStrategy(
                max_depth=max_depth,
                include_external=False  # Stay within same domain
            ),
            markdown_generator=md_generator,
            word_count_threshold=15,  # Ignore very short text blocks
            stream=True
        )

    async def _crawl_single_page(self, url: str) -> Dict[str, Any]:
        """Crawl a single page and return raw result."""
        logger.info(f"Crawling page: {url}")
        
        config = self._create_crawler_config(max_depth=0)
        
        try:
            async with AsyncWebCrawler() as crawler:
                async for result in await crawler.arun(url, config=config):
                    if result.success:
                        # Use fit_markdown for filtered content - this is key
                        content = result.markdown.fit_markdown
                        
                        return {
                            "url": result.url,
                            "content": content,
                            "title": result.metadata.get("title", "") if result.metadata else "",
                            "description": result.metadata.get("description", "") if result.metadata else "",
                            "success": True,
                            "content_length": len(content)
                        }
                    else:
                        error_msg = getattr(result, 'error_message', 'Unknown error')
                        logger.error(f"Failed to crawl {url}: {error_msg}")
                        raise PageLoadError(f"Failed to load page: {error_msg}")
                        
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            raise CrawlerError(f"Crawler error: {str(e)}")

    async def crawl_page(self, url: str) -> Document:
        """
        Crawl a single page and return a Document object.
        
        This method matches the PlaywrightCrawler interface for easy replacement.
        """
        try:
            result = await self._crawl_single_page(url)
            
            if not result["success"]:
                raise PageLoadError(f"Failed to crawl page: {url}")
            
            content = result["content"]
            if not content or not content.strip():
                raise ContentExtractionError(f"No content extracted from: {url}")
            
            # Create Document with metadata matching PlaywrightCrawler format
            # Filter out None values that ChromaDB can't handle
            metadata = {
                "source": result["url"],
                "title": result["title"] or "",
                "description": result["description"] or "",
                "content_length": result["content_length"],
                "crawler_type": "crawl4ai",
                "timestamp": time.time()
            }
            
            self.visited_urls.add(url)
            self._total_chunks += 1
            
            logger.info(f"Successfully crawled: {url} ({result['content_length']} chars)")
            
            return Document(
                page_content=content,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error in crawl_page: {str(e)}")
            raise

    async def crawl_website(self, base_url: str, max_depth: int = 2, max_pages: int = 50) -> List[Document]:
        """
        Crawl a website recursively and return a list of Documents.
        
        This method matches the PlaywrightCrawler interface for easy replacement.
        """
        logger.info(f"Starting website crawl: {base_url} (max_depth: {max_depth})")
        
        documents = []
        config = self._create_crawler_config(max_depth=max_depth)
        
        try:
            async with AsyncWebCrawler() as crawler:
                page_count = 0
                async for result in await crawler.arun(base_url, config=config):
                    if page_count >= max_pages:
                        logger.info(f"Reached max pages limit: {max_pages}")
                        break
                    
                    if result.success:
                        content = result.markdown.fit_markdown
                        
                        if content and content.strip():
                            # Create Document with metadata
                            # Filter out None values that ChromaDB can't handle
                            metadata = {
                                "source": result.url,
                                "title": (result.metadata.get("title", "") if result.metadata else "") or "",
                                "description": (result.metadata.get("description", "") if result.metadata else "") or "",
                                "content_length": len(content),
                                "crawler_type": "crawl4ai",
                                "timestamp": time.time(),
                                "depth": getattr(result, 'depth', 0) or 0  # If available
                            }
                            
                            document = Document(
                                page_content=content,
                                metadata=metadata
                            )
                            documents.append(document)
                            self.visited_urls.add(result.url)
                            page_count += 1
                            
                            logger.info(f"✓ Crawled: {result.url} ({len(content)} chars)")
                        else:
                            logger.warning(f"✗ No content: {result.url}")
                    else:
                        logger.error(f"✗ Failed: {result.url}")
            
            self._total_chunks = len(documents)
            logger.info(f"Website crawl completed: {len(documents)} pages")
            
            return documents
            
        except Exception as e:
            logger.error(f"Error in crawl_website: {str(e)}")
            raise CrawlerError(f"Website crawl failed: {str(e)}")

    def get_stats(self) -> Dict[str, Any]:
        """Get crawler statistics."""
        return {
            "total_chunks": self._total_chunks,
            "visited_urls": len(self.visited_urls),
            "crawler_type": "crawl4ai"
        }

    def run_crawl(self, url: str, max_depth: int = 2) -> List[Document]:
        """Synchronous wrapper for the async crawl_website method."""
        # Suppress asyncio warnings on Windows
        suppress_asyncio_warnings()

        @windows_event_loop
        def _run():
            return asyncio.run(self.crawl_website(url, max_depth))

        return _run()

    def reset(self):
        """Reset crawler state."""
        self.visited_urls.clear()
        self._total_chunks = 0
        logger.info("Crawler state reset")