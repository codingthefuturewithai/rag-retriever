#!/bin/bash

# Crawl4AI POC Installation Script

echo "🚀 Installing Crawl4AI POC dependencies..."

# Check if we're in a virtual environment
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo "⚠️  Warning: Not in a virtual environment. Consider activating one first."
    echo "   You can create one with: python -m venv crawl4ai_env && source crawl4ai_env/bin/activate"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Installation cancelled."
        exit 1
    fi
fi

# Install Python dependencies
echo "📦 Installing Python packages from requirements.txt..."
pip install -r requirements.txt

# Install Playwright browsers
echo "🎭 Installing Playwright browsers..."
playwright install chromium

echo "✅ Installation complete!"
echo
echo "📋 Usage examples:"
echo "  python deep_crawler.py https://example.com --depth 2 --verbose"
echo "  python deep_crawler.py https://docs.python.org/3/ --depth 1"
echo "  python deep_crawler.py https://news.ycombinator.com --depth 0"
echo
echo "📖 See README.md for more details."