#!/bin/bash

# Test Examples for Crawl4AI POC

echo "🧪 Running Crawl4AI POC test examples..."
echo "============================================"

# Test 1: Single page crawl
echo
echo "📄 Test 1: Single page crawl (depth 0)"
echo "URL: https://httpbin.org/html"
python deep_crawler.py https://httpbin.org/html --depth 0 --output test1_single.json --verbose

# Test 2: Small depth crawl  
echo
echo "📑 Test 2: Small documentation crawl (depth 1)"
echo "URL: https://docs.python.org/3/library/os.html"
python deep_crawler.py https://docs.python.org/3/library/os.html --depth 1 --output test2_docs.json --verbose

# Test 3: News site single page
echo
echo "📰 Test 3: News site single page (depth 0)"
echo "URL: https://news.ycombinator.com"
python deep_crawler.py https://news.ycombinator.com --depth 0 --output test3_news.json --verbose

echo
echo "✅ All tests completed!"
echo "📁 Check the generated JSON files for results:"
echo "   - test1_single.json"
echo "   - test2_docs.json" 
echo "   - test3_news.json"
echo
echo "📊 Compare file sizes and content quality with your current implementation."