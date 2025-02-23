"""Unit tests for PlaywrightCrawler."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
from playwright.async_api import Browser, Page, Response, BrowserContext
from rag_retriever.crawling.playwright_crawler import PlaywrightCrawler
from rag_retriever.crawling.exceptions import PageLoadError, ContentExtractionError


@pytest.fixture
def mock_browser():
    """Create a mock browser instance."""
    browser = MagicMock(spec=Browser)
    context = MagicMock(spec=BrowserContext)
    page = MagicMock(spec=Page)
    response = MagicMock(spec=Response)

    # Configure mocks
    browser.new_context = AsyncMock(return_value=context)
    context.new_page = AsyncMock(return_value=page)
    page.goto = AsyncMock(return_value=response)
    page.content = AsyncMock(return_value="<html><body>Test content</body></html>")
    page.wait_for_selector = AsyncMock()
    page.close = AsyncMock()
    response.status = 200

    return browser, context, page, response


@pytest.fixture
def crawler():
    """Create a PlaywrightCrawler instance."""
    return PlaywrightCrawler()


def test_init(crawler):
    """Test crawler initialization."""
    assert crawler.visited_urls == set()
    assert crawler._total_chunks == 0
    assert crawler._browser is None
    assert crawler._context is None


def test_is_same_domain(crawler):
    """Test domain comparison."""
    assert crawler._is_same_domain("https://example.com", "https://example.com/page")
    assert crawler._is_same_domain("http://example.com", "https://example.com")
    assert not crawler._is_same_domain("https://example.com", "https://other.com")


def test_extract_links(crawler):
    """Test link extraction from HTML."""
    html = """
    <html>
        <body>
            <a href="https://example.com/page1">Page 1</a>
            <a href="/page2">Page 2</a>
            <a href="#section">Section</a>
            <a href="javascript:void(0)">JS Link</a>
            <a href="https://other.com">External</a>
        </body>
    </html>
    """
    base_url = "https://example.com"
    links = crawler._extract_links(html, base_url)

    assert "https://example.com/page1" in links
    assert "https://example.com/page2" in links
    assert "https://other.com" not in links  # External link
    assert len([l for l in links if "#" in l]) == 0  # No anchor links
    assert len([l for l in links if "javascript:" in l]) == 0  # No javascript links


@pytest.mark.asyncio
async def test_setup_browser(crawler, mock_browser):
    """Test browser setup."""
    browser, context, _, _ = mock_browser

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = MagicMock()
        mock_playwright_instance.chromium.launch = AsyncMock(return_value=browser)
        mock_playwright.return_value.start = AsyncMock(
            return_value=mock_playwright_instance
        )

        result = await crawler._setup_browser()

        assert result == browser
        mock_playwright.assert_called_once()
        mock_playwright_instance.chromium.launch.assert_called_once()
        browser.new_context.assert_called_once()


@pytest.mark.asyncio
async def test_get_page_content_success(crawler, mock_browser):
    """Test successful page content retrieval."""
    browser, _, page, _ = mock_browser

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = MagicMock()
        mock_playwright_instance.chromium.launch = AsyncMock(return_value=browser)
        mock_playwright.return_value.start = AsyncMock(
            return_value=mock_playwright_instance
        )

        content = await crawler.get_page_content("https://example.com")
        assert "Test content" in content
        page.goto.assert_called_once()
        page.content.assert_called_once()
        page.close.assert_called_once()


@pytest.mark.asyncio
async def test_get_page_content_error(crawler, mock_browser):
    """Test page content retrieval with error."""
    browser, _, page, _ = mock_browser
    page.goto = AsyncMock(side_effect=Exception("Failed to load"))

    with (
        patch("playwright.async_api.async_playwright") as mock_playwright,
        pytest.raises(PageLoadError),
    ):
        mock_playwright_instance = MagicMock()
        mock_playwright_instance.chromium.launch = AsyncMock(return_value=browser)
        mock_playwright.return_value.start = AsyncMock(
            return_value=mock_playwright_instance
        )

        await crawler.get_page_content("https://example.com")


@pytest.mark.asyncio
async def test_crawl_recursive_success(crawler):
    """Test recursive crawling."""

    # Mock get_page_content to return different content for different URLs
    async def mock_get_content(url):
        if url == "https://example.com":
            return """
            <html>
                <body>
                    <main>Main page content</main>
                    <a href="https://example.com/page1">Page 1</a>
                    <a href="https://example.com/page2">Page 2</a>
                </body>
            </html>
            """
        return "<html><body><main>Subpage content</main></body></html>"

    crawler.get_page_content = AsyncMock(side_effect=mock_get_content)

    documents = await crawler._crawl_recursive("https://example.com", 0, 1)

    assert len(documents) == 3  # Main page + 2 subpages
    assert any(d.metadata["source"] == "https://example.com" for d in documents)
    assert any(d.metadata["source"] == "https://example.com/page1" for d in documents)
    assert any(d.metadata["source"] == "https://example.com/page2" for d in documents)


@pytest.mark.asyncio
async def test_crawl_recursive_max_depth(crawler):
    """Test recursive crawling respects max depth."""
    crawler.get_page_content = AsyncMock(
        return_value="""
        <html>
            <body>
                <main>Test content</main>
                <a href="https://example.com/page1">Page 1</a>
            </body>
        </html>
    """
    )

    documents = await crawler._crawl_recursive("https://example.com", 2, 1)
    assert len(documents) == 0  # Should not process pages beyond max_depth


@pytest.mark.asyncio
async def test_crawl_recursive_error_handling(crawler):
    """Test error handling during recursive crawling."""

    async def mock_get_content(url):
        if url == "https://example.com":
            return "<html><body><main>Main content</main><a href='https://example.com/error'>Error Page</a></body></html>"
        raise PageLoadError("Failed to load page")

    crawler.get_page_content = AsyncMock(side_effect=mock_get_content)

    documents = await crawler._crawl_recursive("https://example.com", 0, 1)
    assert len(documents) == 1  # Should still get main page despite subpage error
    assert documents[0].metadata["source"] == "https://example.com"


def test_run_crawl(crawler):
    """Test the synchronous crawl wrapper."""

    async def mock_crawl(*args):
        return [MagicMock()]

    crawler.crawl = AsyncMock(side_effect=mock_crawl)

    result = crawler.run_crawl("https://example.com", max_depth=1)
    assert len(result) == 1
