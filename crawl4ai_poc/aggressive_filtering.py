import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

async def main():
    # More aggressive filtering to remove more navigation
    md_generator = DefaultMarkdownGenerator(
        content_filter=PruningContentFilter(
            threshold=0.7,  # Increased from 0.48 - more aggressive
            threshold_type="fixed"
        )
    )
    
    config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=0,  # Just single page as you wanted
            include_external=False
        ),
        markdown_generator=md_generator,
        word_count_threshold=15,  # Ignore very short text blocks
        stream=True
    )
    
    async with AsyncWebCrawler() as crawler:
        async for result in await crawler.arun("https://docs.anthropic.com/en/docs/claude-code/overview", config=config):
            if result.success:
                print(f"Successfully crawled: {result.url}")
                print(f"Filtered content:\n{result.markdown.fit_markdown}")
            else:
                print(f"Failed to crawl: {result.url}")

asyncio.run(main())