import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy

async def main():
    # Configure depth crawling - this is the ONLY configuration you need
    config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=0,  # Configure your depth here (0 = just the starting page)
            include_external=False,  # Stay within the same domain
            max_pages=50  # Optional: limit total pages to prevent runaway crawling
        ),
        stream=True  # Get results as they come in
    )
    
    async with AsyncWebCrawler() as crawler:
        # This will crawl the starting page + 2 levels deep
        async for result in await crawler.arun("https://docs.anthropic.com/en/docs/claude-code/overview", config=config):
            if result.success:
                print(f"Successfully crawled: {result.url}")
                print(f"Depth: {result.metadata.get('depth', 0)}")
                # print(f"Content preview: {result.markdown[:200]}...")
                print(f"Content: {result.markdown}...")
                print("-" * 50)
            else:
                print(f"Failed to crawl: {result.url}")

asyncio.run(main())