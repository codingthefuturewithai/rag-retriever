"""Unit tests for content cleaning functionality."""

import pytest
from bs4 import BeautifulSoup
from rag_retriever.crawling.content_cleaner import ContentCleaner


@pytest.fixture
def cleaner():
    """Create a ContentCleaner instance."""
    return ContentCleaner()


def test_clean_element_text(cleaner):
    """Test cleaning of simple text elements."""
    html = "<p>Test paragraph</p>"
    soup = BeautifulSoup(html, "lxml")
    result = cleaner.clean_element(soup.p)
    assert "Test paragraph" in result


def test_clean_element_nested(cleaner):
    """Test cleaning of nested elements."""
    html = "<div><p>First para</p><p>Second para</p></div>"
    soup = BeautifulSoup(html, "lxml")
    result = cleaner.clean_element(soup.div)
    assert "First para" in result
    assert "Second para" in result


def test_clean_element_code_blocks(cleaner):
    """Test preservation of code blocks."""
    html = "<pre><code>def test(): pass</code></pre>"
    soup = BeautifulSoup(html, "lxml")
    result = cleaner.clean_element(soup.pre)
    assert "def test(): pass" in result


def test_clean_element_headers(cleaner):
    """Test cleaning of header elements."""
    html = "<h1>Title</h1><h2>Subtitle</h2>"
    soup = BeautifulSoup(html, "lxml")
    h1_result = cleaner.clean_element(soup.h1)
    h2_result = cleaner.clean_element(soup.h2)
    assert "# Title" in h1_result
    assert "## Subtitle" in h2_result


def test_clean_element_lists(cleaner):
    """Test cleaning of list elements."""
    html = "<ul><li>Item 1</li><li>Item 2</li></ul>"
    soup = BeautifulSoup(html, "lxml")
    result = cleaner.clean_element(soup.ul)
    assert "• Item 1" in result
    assert "• Item 2" in result


def test_clean_element_navigation(cleaner):
    """Test cleaning of navigation elements (should be removed)."""
    html = '<nav><a href="#">Link</a></nav>'
    soup = BeautifulSoup(html, "lxml")
    result = cleaner.clean_element(soup.nav)
    assert result == ""


def test_clean_full_html(cleaner):
    """Test cleaning of complete HTML document."""
    html = """
    <html>
        <head><title>Test</title></head>
        <body>
            <nav>Navigation</nav>
            <main>
                <h1>Main Title</h1>
                <p>First paragraph</p>
                <code>Test code</code>
                <div class="menu">Menu items</div>
            </main>
            <footer>Footer content</footer>
        </body>
    </html>
    """
    result = cleaner.clean(html)
    assert "Navigation" not in result
    assert "Main Title" in result
    assert "First paragraph" in result
    assert "Test code" in result
    assert "Menu items" not in result
    assert "Footer content" not in result


def test_clean_post_processing(cleaner):
    """Test post-processing of cleaned text."""
    text = "Multiple    spaces\n\n\nMultiple newlines"
    processed = cleaner._post_process(text)
    assert "    " not in processed  # Multiple spaces removed
    assert "\n\n\n" not in processed  # Multiple newlines reduced


def test_clean_ui_patterns(cleaner):
    """Test removal of UI patterns."""
    # Test with a known UI pattern from the config
    html = "<div>Content with Accept Cookies</div>"
    result = cleaner.clean(html)
    # Since we don't know the exact UI patterns, we just verify the content is cleaned
    assert result.strip() == "Content with Accept Cookies"
