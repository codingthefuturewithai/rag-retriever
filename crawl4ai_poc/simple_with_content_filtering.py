import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

async def main():
    # Add content filtering to remove navigation and sidebars
    md_generator = DefaultMarkdownGenerator(
        content_filter=PruningContentFilter(
            threshold=0.48,  # Adjust this: higher = more aggressive filtering
            threshold_type="fixed"
        )
    )
    
    config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=0,
            include_external=False,
            max_pages=50
        ),
        markdown_generator=md_generator,  # Add the filtering here
        stream=True
    )
    
    async with AsyncWebCrawler() as crawler:
        async for result in await crawler.arun("https://docs.anthropic.com/en/docs/claude-code/overview", config=config):
            if result.success:
                print(f"Successfully crawled: {result.url}")
                print(f"Depth: {result.metadata.get('depth', 0)}")
                # Use fit_markdown instead of raw markdown
                print(f"Filtered content: {result.markdown.fit_markdown}...")
                print("-" * 50)
            else:
                print(f"Failed to crawl: {result.url}")

asyncio.run(main())