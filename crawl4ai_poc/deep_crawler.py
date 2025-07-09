#!/usr/bin/env python3
"""
Crawl4AI POC - Deep Recursive Web Crawler
A standalone proof of concept for replacing Playwright with Crawl4AI
"""

import asyncio
import argparse
import json
import time
from urllib.parse import urlparse
from typing import List, Dict, Any
from pathlib import Path

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator


class CrawlResult:
    """Container for crawl results matching RAG Retriever's Document format"""
    
    def __init__(self, url: str, content: str, metadata: Dict[str, Any]):
        self.url = url
        self.content = content  # Markdown content
        self.metadata = metadata
        self.depth = metadata.get("depth", 0)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "content": self.content,
            "metadata": self.metadata,
            "content_length": len(self.content),
            "depth": self.depth
        }


class Crawl4AiDeepCrawler:
    """Deep web crawler using Crawl4AI with recursive capabilities"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[CrawlResult] = []
        self.start_time = None
        self.stats = {
            "pages_crawled": 0,
            "pages_successful": 0,
            "pages_failed": 0,
            "total_content_size": 0,
            "max_depth_reached": 0,
            "domains_crawled": set(),
            "errors": []
        }
    
    def _log(self, message: str, level: str = "INFO"):
        """Simple logging with optional verbose mode"""
        if self.verbose or level == "ERROR":
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] {level}: {message}")
    
    def _create_content_config(self, base_url: str) -> CrawlerRunConfig:
        """Create crawler configuration for proper content extraction"""
        
        # Create a content filter to remove low-quality content
        content_filter = PruningContentFilter(
            threshold=0.4,  # More permissive for documentation content
            threshold_type="dynamic",  # Adaptive scoring based on content type
            min_word_threshold=5  # Lower word threshold for documentation
        )
        
        # Create markdown generator with content filtering
        markdown_generator = DefaultMarkdownGenerator(
            content_filter=content_filter,
            options={
                "ignore_links": False,  # Keep links for navigation
                "include_code": True,   # Include code blocks
                "include_tables": True, # Include tables
            }
        )
        
        return CrawlerRunConfig(
            # Focus markdown generation on main content areas
            target_elements=[
                "#content-container",
                ".main-content", 
                "article", 
                "main",
                ".content",
                "#main-content",
                ".prose",
                ".markdown",
                ".documentation"
            ],
            
            # Exclude navigation and other non-content elements
            excluded_tags=[
                "nav", "footer", "header", "aside", "script", "style", 
                "noscript", "form", "button", "input", "textarea", "select",
                "meta", "title", "link", "base"
            ],
            
            # Content filtering
            word_count_threshold=10,  # Lower threshold for documentation content
            exclude_external_links=False,  # Keep external links in documentation
            exclude_social_media_links=True,
            exclude_external_images=True,
            
            # Remove overlays and forms
            remove_overlay_elements=True,
            remove_forms=True,
            
            # Use LXML for faster parsing
            scraping_strategy=LXMLWebScrapingStrategy(),
            
            # Use our custom markdown generator with content filtering
            markdown_generator=markdown_generator,
            
            # Enable caching for better performance
            cache_mode=CacheMode.ENABLED,
            
            # Wait for content to load
            wait_for="css:body",
            
            # Performance settings
            verbose=self.verbose,
        )
    
    async def crawl_deep(self, base_url: str, max_depth: int = 2) -> List[CrawlResult]:
        """
        Perform deep crawling by recursively following links
        
        Args:
            base_url: Starting URL to crawl
            max_depth: Maximum depth to crawl (0 = only base URL)
        
        Returns:
            List of CrawlResult objects
        """
        self.start_time = time.time()
        self.results = []
        self._log(f"Starting deep crawl of {base_url} with max depth {max_depth}")
        
        # Track visited URLs to avoid duplicates
        visited_urls = set()
        
        # Create content configuration
        config = self._create_content_config(base_url)
        
        try:
            async with AsyncWebCrawler(headless=True, verbose=self.verbose) as crawler:
                self._log("Crawler initialized, starting crawl...")
                
                # Start recursive crawling
                await self._crawl_recursive(crawler, base_url, 0, max_depth, visited_urls, config)
                
                self._log(f"Deep crawl completed. Processed {len(self.results)} pages.")
                
        except Exception as e:
            self._log(f"Error during crawl: {str(e)}", "ERROR")
            self.stats["errors"].append(str(e))
        
        # Update final statistics
        self._update_final_stats()
        return self.results
    
    async def _crawl_recursive(self, crawler, url: str, current_depth: int, max_depth: int, 
                              visited_urls: set, config: CrawlerRunConfig):
        """Recursively crawl URLs up to max_depth"""
        self._log(f"Crawling depth {current_depth}: {url}")
        
        # Check if we've reached max depth or already visited this URL
        if current_depth > max_depth or url in visited_urls:
            return
        
        visited_urls.add(url)
        
        try:
            # Crawl the current URL
            result = await crawler.arun(url, config=config)
            
            # Process the result
            await self._process_result(result, current_depth)
            
            # If we haven't reached max depth, extract links and continue
            if current_depth < max_depth and result.success:
                # Extract internal links from the result
                internal_links = result.links.get("internal", []) if result.links else []
                
                # Filter links to same domain
                base_domain = urlparse(url).netloc
                same_domain_links = []
                
                for link_obj in internal_links:
                    if isinstance(link_obj, dict):
                        link_url = link_obj.get("href", "")
                    else:
                        link_url = getattr(link_obj, "href", str(link_obj))
                    
                    if link_url and urlparse(link_url).netloc == base_domain:
                        # Clean up the URL
                        link_url = link_url.rstrip("/")
                        if link_url != url.rstrip("/") and link_url not in visited_urls:
                            same_domain_links.append(link_url)
                
                # Recursively crawl found links
                self._log(f"Found {len(same_domain_links)} same-domain links at depth {current_depth}")
                for link_url in same_domain_links[:10]:  # Limit to first 10 links per page
                    await self._crawl_recursive(crawler, link_url, current_depth + 1, max_depth, visited_urls, config)
                    
        except Exception as e:
            self._log(f"Error crawling {url}: {str(e)}", "ERROR")
            self.stats["errors"].append(f"{url}: {str(e)}")
            self.stats["pages_failed"] += 1
    
    async def _process_result(self, result, depth: int = 0):
        """Process a single crawl result"""
        try:
            self.stats["pages_crawled"] += 1
            
            if result.success:
                # Use fit_markdown for better content extraction - this is the filtered content
                content = ""
                if hasattr(result, 'markdown') and result.markdown:
                    if hasattr(result.markdown, 'fit_markdown') and result.markdown.fit_markdown:
                        content = result.markdown.fit_markdown
                    elif hasattr(result.markdown, 'raw_markdown') and result.markdown.raw_markdown:
                        content = result.markdown.raw_markdown
                    else:
                        content = str(result.markdown)
                
                if content and content.strip():
                    domain = urlparse(result.url).netloc
                    
                    # Create our result object
                    crawl_result = CrawlResult(
                        url=result.url,
                        content=content,
                        metadata={
                            "source": result.url,
                            "depth": depth,
                            "domain": domain,
                            "title": result.metadata.get("title", "") if result.metadata else "",
                            "description": result.metadata.get("description", "") if result.metadata else "",
                            "content_length": len(content),
                            "links_internal": len(result.links.get("internal", [])) if result.links else 0,
                            "links_external": len(result.links.get("external", [])) if result.links else 0,
                            "images_count": len(result.media.get("images", [])) if result.media else 0,
                        }
                    )
                    
                    self.results.append(crawl_result)
                    self.stats["pages_successful"] += 1
                    self.stats["total_content_size"] += len(content)
                    self.stats["max_depth_reached"] = max(self.stats["max_depth_reached"], depth)
                    self.stats["domains_crawled"].add(domain)
                    
                    self._log(f"✓ Depth {depth}: {result.url} ({len(content)} chars)")
                else:
                    self.stats["pages_failed"] += 1
                    self._log(f"✗ No content: {result.url}", "ERROR")
                    self.stats["errors"].append(f"{result.url}: No content extracted")
                
            else:
                self.stats["pages_failed"] += 1
                error_msg = result.error_message if hasattr(result, 'error_message') else "Unknown error"
                self._log(f"✗ Failed: {result.url if hasattr(result, 'url') else 'Unknown URL'} - {error_msg}", "ERROR")
                self.stats["errors"].append(f"{result.url}: {error_msg}")
                
        except Exception as e:
            self.stats["pages_failed"] += 1
            self._log(f"Error processing result: {str(e)}", "ERROR")
            self.stats["errors"].append(f"Processing error: {str(e)}")
    
    def _update_final_stats(self):
        """Update final statistics"""
        if self.start_time:
            self.stats["total_time"] = time.time() - self.start_time
            self.stats["pages_per_second"] = self.stats["pages_successful"] / self.stats["total_time"] if self.stats["total_time"] > 0 else 0
        
        # Convert set to list for JSON serialization
        self.stats["domains_crawled"] = list(self.stats["domains_crawled"])
    
    def print_summary(self):
        """Print a summary of the crawl results"""
        print("\n" + "="*60)
        print("CRAWL4AI DEEP CRAWL SUMMARY")
        print("="*60)
        print(f"Total pages crawled: {self.stats['pages_crawled']}")
        print(f"Successful pages: {self.stats['pages_successful']}")
        print(f"Failed pages: {self.stats['pages_failed']}")
        print(f"Max depth reached: {self.stats['max_depth_reached']}")
        print(f"Total content size: {self.stats['total_content_size']:,} characters")
        print(f"Average content per page: {self.stats['total_content_size'] // max(1, self.stats['pages_successful']):,} characters")
        
        if "total_time" in self.stats:
            print(f"Total time: {self.stats['total_time']:.2f} seconds")
            print(f"Pages per second: {self.stats['pages_per_second']:.2f}")
        
        print(f"Domains crawled: {len(self.stats['domains_crawled'])}")
        for domain in self.stats['domains_crawled']:
            print(f"  - {domain}")
        
        if self.stats['errors']:
            print(f"\nErrors ({len(self.stats['errors'])}):")
            for error in self.stats['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(self.stats['errors']) > 5:
                print(f"  ... and {len(self.stats['errors']) - 5} more")
        
        print("\nResults by depth:")
        depth_counts = {}
        for result in self.results:
            depth = result.depth
            depth_counts[depth] = depth_counts.get(depth, 0) + 1
        
        for depth in sorted(depth_counts.keys()):
            count = depth_counts[depth]
            avg_size = sum(len(r.content) for r in self.results if r.depth == depth) // count
            print(f"  Depth {depth}: {count} pages (avg {avg_size:,} chars)")
    
    def save_results(self, output_file: str):
        """Save results to JSON file"""
        output_data = {
            "crawl_stats": self.stats,
            "results": [result.to_dict() for result in self.results]
        }
        
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nResults saved to: {output_path.absolute()}")


async def main():
    """Main entry point for the POC"""
    parser = argparse.ArgumentParser(
        description="Crawl4AI Deep Crawler POC",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://docs.python.org/3/ --depth 2 --verbose
  %(prog)s https://example.com --depth 1 --output results.json
  %(prog)s https://news.ycombinator.com --depth 0  # Single page only
        """
    )
    
    parser.add_argument(
        "url",
        help="Base URL to start crawling from"
    )
    
    parser.add_argument(
        "--depth", "-d",
        type=int,
        default=2,
        help="Maximum crawling depth (default: 2, 0 = single page only)"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="crawl_results.json",
        help="Output file for results (default: crawl_results.json)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Validate URL
    parsed_url = urlparse(args.url)
    if not parsed_url.scheme or not parsed_url.netloc:
        print("Error: Please provide a valid URL with http:// or https://")
        return 1
    
    # Create crawler and run
    crawler = Crawl4AiDeepCrawler(verbose=args.verbose)
    
    try:
        print(f"Starting Crawl4AI deep crawl...")
        print(f"URL: {args.url}")
        print(f"Max depth: {args.depth}")
        print(f"Output file: {args.output}")
        print("-" * 60)
        
        results = await crawler.crawl_deep(args.url, args.depth)
        
        # Print summary
        crawler.print_summary()
        
        # Save results
        crawler.save_results(args.output)
        
        if results:
            print(f"\n🎉 Successfully crawled {len(results)} pages!")
            return 0
        else:
            print("\n❌ No pages were successfully crawled.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️  Crawl interrupted by user")
        if crawler.results:
            crawler.print_summary()
            crawler.save_results(args.output)
        return 1
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return 1


if __name__ == "__main__":
    asyncio.run(main())