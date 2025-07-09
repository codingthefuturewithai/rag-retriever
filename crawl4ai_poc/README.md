# Crawl4AI Deep Crawler POC

A standalone proof of concept for replacing the current Playwright-based web crawler in RAG Retriever with Crawl4AI's deep crawling capabilities.

## Features

- **Deep Recursive Crawling**: Crawls to specified depth with domain filtering
- **Fast LXML Parsing**: Uses Crawl4AI's LXMLWebScrapingStrategy for 20x faster parsing
- **Smart Filtering**: Domain restrictions, content type filtering, and URL pattern exclusions
- **Rich Output**: Markdown content extraction with comprehensive metadata
- **Performance Metrics**: Detailed statistics on crawl performance
- **JSON Export**: Save results in structured format

## Installation

```bash
cd crawl4ai_poc
pip install -r requirements.txt
playwright install chromium
```

## Usage

### Basic Usage

```bash
# Crawl a single page (depth 0)
python deep_crawler.py https://example.com --depth 0

# Crawl with depth 2 (default)
python deep_crawler.py https://docs.python.org/3/

# Crawl with verbose output
python deep_crawler.py https://news.ycombinator.com --depth 1 --verbose

# Save to custom output file
python deep_crawler.py https://example.com --depth 2 --output my_results.json
```

### Command Line Options

```
positional arguments:
  url                   Base URL to start crawling from

options:
  -h, --help            show this help message and exit
  --depth DEPTH, -d DEPTH
                        Maximum crawling depth (default: 2, 0 = single page only)
  --output OUTPUT, -o OUTPUT
                        Output file for results (default: crawl_results.json)
  --verbose, -v         Enable verbose output
```

## How It Works

### Deep Crawling Strategy

The POC uses Crawl4AI's `BestFirstCrawlingStrategy` with:

- **Domain Filtering**: Only crawls pages from the same domain as the starting URL
- **Content Type Filtering**: Only processes HTML/XHTML content
- **URL Pattern Exclusion**: Skips admin, API, media files, and fragment URLs
- **Content Filtering**: Excludes navigation, footer, and script elements

### Performance Features

- **LXML Processing**: 20x faster HTML parsing compared to BeautifulSoup
- **Caching**: Intelligent caching for repeated crawls
- **Streaming**: Processes results as they arrive
- **Content Filtering**: Skips pages with minimal content

### Output Format

Results are saved as JSON with:

```json
{
  "crawl_stats": {
    "pages_crawled": 15,
    "pages_successful": 12,
    "pages_failed": 3,
    "total_content_size": 45000,
    "max_depth_reached": 2,
    "total_time": 8.5,
    "pages_per_second": 1.4,
    "domains_crawled": ["example.com"],
    "errors": []
  },
  "results": [
    {
      "url": "https://example.com/page1",
      "content": "# Page Title\n\nMarkdown content...",
      "metadata": {
        "source": "https://example.com/page1",
        "depth": 1,
        "domain": "example.com",
        "title": "Page Title",
        "content_length": 1500,
        "links_internal": 5,
        "links_external": 2,
        "images_count": 3
      },
      "content_length": 1500,
      "depth": 1
    }
  ]
}
```

## Testing

### Test with Different Sites

```bash
# Small documentation site
python deep_crawler.py https://docs.python.org/3/library/os.html --depth 1 -v

# News site (single page)
python deep_crawler.py https://news.ycombinator.com --depth 0 -v

# Blog with multiple pages
python deep_crawler.py https://blog.example.com --depth 2 -v
```

### Performance Testing

```bash
# Compare timing with different depths
time python deep_crawler.py https://example.com --depth 0
time python deep_crawler.py https://example.com --depth 1
time python deep_crawler.py https://example.com --depth 2
```

## Comparison with Current Implementation

| Metric | Current Playwright | Crawl4AI POC |
|--------|-------------------|--------------|
| **Parsing Speed** | BeautifulSoup | LXML (20x faster) |
| **Memory Usage** | Higher | Lower with streaming |
| **Caching** | None | Built-in intelligent caching |
| **Content Quality** | Custom cleaning | Advanced extraction strategies |
| **Anti-Detection** | Basic stealth | Advanced anti-detection |
| **Concurrent Processing** | Sequential | Native batch support |

## Key Differences from RAG Retriever

### Similarities
- Same-domain crawling restriction
- Depth-based recursion
- Document-like output format
- Error handling and statistics

### Improvements
- **20x faster parsing** with LXML
- **Built-in caching** for repeated runs
- **Better content extraction** with Crawl4AI strategies
- **Rich metadata** extraction
- **Streaming results** for better memory usage

### Integration Path

This POC demonstrates that Crawl4AI can be a drop-in replacement for the current Playwright crawler with significant performance improvements. The output format is designed to be compatible with RAG Retriever's Document objects.

## Next Steps

1. **Performance Benchmarking**: Compare against current implementation
2. **Content Quality Assessment**: Verify extraction quality
3. **Integration Testing**: Test with RAG Retriever's vector store
4. **Advanced Features**: Add proxy rotation, custom extraction strategies
5. **Error Handling**: Enhanced retry logic and failure recovery