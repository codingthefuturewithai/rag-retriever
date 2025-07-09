#!/usr/bin/env python3
"""
Test script to verify Crawl4AI integration with RAG Retriever
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the parent directory to sys.path to import rag_retriever modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag_retriever.crawling.crawl4ai_crawler import Crawl4AICrawler


async def test_crawl4ai_integration():
    """Test the Crawl4AI crawler integration"""
    print("🧪 Testing Crawl4AI integration...")
    
    # Test URL
    test_url = "https://docs.anthropic.com/en/docs/claude-code/overview"
    
    try:
        # Create crawler
        crawler = Crawl4AICrawler()
        print(f"✓ Crawler created successfully")
        
        # Test single page crawl
        print(f"📄 Testing single page crawl: {test_url}")
        document = await crawler.crawl_page(test_url)
        
        print(f"✓ Page crawled successfully")
        print(f"  Content length: {len(document.page_content):,} characters")
        print(f"  Title: {document.metadata.get('title', 'N/A')}")
        print(f"  Source: {document.metadata.get('source', 'N/A')}")
        print(f"  Crawler type: {document.metadata.get('crawler_type', 'N/A')}")
        
        # Show content preview
        content_preview = document.page_content[:500]
        print(f"\n📝 Content preview:")
        print(f"{content_preview}...")
        
        # Check if navigation is filtered out
        has_navigation = "Navigation" in content_preview
        has_main_content = "Get started in 30 seconds" in document.page_content
        
        print(f"\n🔍 Content analysis:")
        print(f"  Contains navigation: {'⚠️  Yes' if has_navigation else '✓ No'}")
        print(f"  Contains main content: {'✓ Yes' if has_main_content else '❌ No'}")
        
        if has_main_content and not has_navigation:
            print("🎉 Content filtering is working perfectly!")
        elif has_main_content:
            print("✅ Main content extracted (some navigation present)")
        else:
            print("❌ Content extraction failed")
        
        # Get stats
        stats = crawler.get_stats()
        print(f"\n📊 Crawler stats: {stats}")
        
        return document
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def test_website_crawl():
    """Test recursive website crawling"""
    print("\n🌐 Testing website crawl (depth 1)...")
    
    test_url = "https://httpbin.org/html"
    
    try:
        crawler = Crawl4AICrawler()
        
        # Test recursive crawl with small depth
        documents = await crawler.crawl_website(test_url, max_depth=1, max_pages=3)
        
        print(f"✓ Website crawled successfully")
        print(f"  Total documents: {len(documents)}")
        
        for i, doc in enumerate(documents):
            print(f"  Document {i+1}: {doc.metadata.get('source', 'N/A')} ({len(doc.page_content)} chars)")
        
        return documents
        
    except Exception as e:
        print(f"❌ Website crawl test failed: {str(e)}")
        return None


async def main():
    """Run all tests"""
    print("🚀 RAG Retriever Crawl4AI Integration Test")
    print("=" * 50)
    
    # Test single page
    single_doc = await test_crawl4ai_integration()
    
    # Test website crawl
    website_docs = await test_website_crawl()
    
    # Summary
    print("\n📋 Test Summary:")
    print(f"  Single page crawl: {'✓ Pass' if single_doc else '❌ Fail'}")
    print(f"  Website crawl: {'✓ Pass' if website_docs else '❌ Fail'}")
    
    if single_doc and website_docs:
        print("\n🎉 All tests passed! Crawl4AI integration is ready.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")


if __name__ == "__main__":
    asyncio.run(main())