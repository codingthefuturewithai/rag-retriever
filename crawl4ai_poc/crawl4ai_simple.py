#!/usr/bin/env python3
"""
Simple Crawl4AI Implementation - Reference for RAG Retriever Integration
Based on working solution that properly filters navigation content.
"""

import asyncio
import argparse
import json
from pathlib import Path
from urllib.parse import urlparse
from typing import List, Dict, Any

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator


class SimpleCrawl4AI:
    """Simple Crawl4AI wrapper for clean content extraction"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def _log(self, message: str):
        if self.verbose:
            print(f"[Crawl4AI] {message}")
    
    async def crawl_single_page(self, url: str) -> Dict[str, Any]:
        """
        Crawl a single page with aggressive content filtering
        Returns clean content without navigation elements
        """
        self._log(f"Crawling: {url}")
        
        # Aggressive filtering to remove navigation - this is the key
        md_generator = DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(
                threshold=0.7,  # High threshold = aggressive filtering
                threshold_type="fixed"
            )
        )
        
        config = CrawlerRunConfig(
            deep_crawl_strategy=BFSDeepCrawlStrategy(
                max_depth=0,  # Single page only
                include_external=False
            ),
            markdown_generator=md_generator,
            word_count_threshold=15,  # Ignore very short text blocks
            stream=True
        )
        
        async with AsyncWebCrawler() as crawler:
            async for result in await crawler.arun(url, config=config):
                if result.success:
                    # Use fit_markdown for filtered content
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
                    return {
                        "url": url,
                        "content": "",
                        "title": "",
                        "description": "",
                        "success": False,
                        "error": getattr(result, 'error_message', 'Unknown error')
                    }
    
    async def crawl_recursive(self, url: str, max_depth: int = 2) -> List[Dict[str, Any]]:
        """
        Crawl recursively with clean content extraction
        """
        self._log(f"Recursive crawling: {url} (max_depth: {max_depth})")
        
        # Same aggressive filtering for recursive crawling
        md_generator = DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(
                threshold=0.7,  # High threshold = aggressive filtering
                threshold_type="fixed"
            )
        )
        
        config = CrawlerRunConfig(
            deep_crawl_strategy=BFSDeepCrawlStrategy(
                max_depth=max_depth,
                include_external=False  # Stay within same domain
            ),
            markdown_generator=md_generator,
            word_count_threshold=15,
            stream=True
        )
        
        results = []
        async with AsyncWebCrawler() as crawler:
            async for result in await crawler.arun(url, config=config):
                if result.success:
                    content = result.markdown.fit_markdown
                    
                    results.append({
                        "url": result.url,
                        "content": content,
                        "title": result.metadata.get("title", "") if result.metadata else "",
                        "description": result.metadata.get("description", "") if result.metadata else "",
                        "success": True,
                        "content_length": len(content)
                    })
                    
                    self._log(f"✓ Extracted: {result.url} ({len(content)} chars)")
                else:
                    self._log(f"✗ Failed: {result.url}")
        
        return results


async def main():
    """CLI interface for testing"""
    parser = argparse.ArgumentParser(description="Simple Crawl4AI Content Extractor")
    parser.add_argument("url", help="URL to crawl")
    parser.add_argument("--depth", "-d", type=int, default=0, help="Crawl depth (0=single page)")
    parser.add_argument("--output", "-o", default="simple_results.json", help="Output file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    crawler = SimpleCrawl4AI(verbose=args.verbose)
    
    try:
        if args.depth == 0:
            # Single page crawl
            result = await crawler.crawl_single_page(args.url)
            results = [result] if result["success"] else []
        else:
            # Recursive crawl
            results = await crawler.crawl_recursive(args.url, args.depth)
        
        # Save results
        output_data = {
            "url": args.url,
            "depth": args.depth,
            "total_pages": len(results),
            "successful_pages": sum(1 for r in results if r["success"]),
            "results": results
        }
        
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"✅ Crawled {len(results)} pages")
        print(f"📁 Results saved to: {args.output}")
        
        if results:
            total_content = sum(r["content_length"] for r in results)
            print(f"📊 Total content: {total_content:,} characters")
            print(f"📄 Average per page: {total_content // len(results):,} characters")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))