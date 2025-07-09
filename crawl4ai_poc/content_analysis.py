#!/usr/bin/env python3
"""
Content Analysis Script for Crawl4AI POC
Analyzes the crawl results to show what content was extracted
"""

import json
from pathlib import Path

def analyze_content():
    """Analyze the crawled content and show key sections"""
    results_file = Path("crawl_results.json")
    
    if not results_file.exists():
        print("❌ No crawl_results.json found. Run the crawler first.")
        return
    
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    if not data['results']:
        print("❌ No results found in crawl data")
        return
    
    result = data['results'][0]
    content = result['content']
    
    print("📊 CONTENT ANALYSIS")
    print("=" * 50)
    print(f"URL: {result['url']}")
    print(f"Total content length: {len(content):,} characters")
    print(f"Title: {result['metadata']['title']}")
    print()
    
    # Look for main content sections
    main_sections = [
        "Get started in 30 seconds",
        "What Claude Code does for you", 
        "Why developers love Claude Code",
        "Next steps",
        "Additional resources"
    ]
    
    print("🔍 MAIN CONTENT SECTIONS FOUND:")
    print("-" * 30)
    
    for section in main_sections:
        if section in content:
            start_idx = content.find(section)
            # Get some context around the section
            context_start = max(0, start_idx - 50)
            context_end = min(len(content), start_idx + len(section) + 200)
            context = content[context_start:context_end].replace('\n', ' ')
            print(f"✓ {section}")
            print(f"   Context: ...{context}...")
            print()
        else:
            print(f"✗ {section} - NOT FOUND")
    
    # Check for navigation content
    nav_indicators = [
        "Navigation",
        "Getting started",
        "##### Getting started",
        "##### Build with Claude",
        "##### Deployment",
        "##### Administration"
    ]
    
    print("\n🚨 NAVIGATION CONTENT DETECTED:")
    print("-" * 30)
    
    nav_found = False
    for indicator in nav_indicators:
        if indicator in content:
            nav_found = True
            print(f"⚠️  {indicator}")
    
    if not nav_found:
        print("✓ No navigation content detected")
    
    # Show content distribution
    print(f"\n📈 CONTENT BREAKDOWN:")
    print("-" * 30)
    
    # Rough estimate of content types
    lines = content.split('\n')
    total_lines = len(lines)
    
    # Count different types of content
    link_lines = sum(1 for line in lines if '[' in line and '](' in line)
    heading_lines = sum(1 for line in lines if line.startswith('#'))
    bullet_lines = sum(1 for line in lines if line.strip().startswith('*') or line.strip().startswith('-'))
    
    print(f"Total lines: {total_lines}")
    print(f"Links: {link_lines} ({link_lines/total_lines*100:.1f}%)")
    print(f"Headings: {heading_lines} ({heading_lines/total_lines*100:.1f}%)")
    print(f"Bullet points: {bullet_lines} ({bullet_lines/total_lines*100:.1f}%)")
    
    # Show a sample of the main content (skip navigation)
    print(f"\n📝 SAMPLE OF MAIN CONTENT:")
    print("-" * 30)
    
    # Find the start of main content after navigation
    main_start = content.find("## ")
    if main_start != -1:
        sample_content = content[main_start:main_start+500]
        print(sample_content)
        print("...")
    else:
        print("Could not locate main content start")

if __name__ == "__main__":
    analyze_content()