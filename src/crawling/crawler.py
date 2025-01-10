"""Web page crawling and content extraction module."""

import time
import logging
from typing import List, Set
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from langchain_core.documents import Document

from src.utils.config import config
from src.crawling.exceptions import PageLoadError, ContentExtractionError, CrawlerError
from src.crawling.content_cleaner import ContentCleaner

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Crawler:
    """Web page crawler using Selenium for JavaScript support."""

    def __init__(self):
        """Initialize the crawler with configuration."""
        self.wait_time = config.selenium["wait_time"]
        self.selenium_options = config.selenium["options"]
        self.content_cleaner = ContentCleaner()
        self.visited_urls: Set[str] = set()

    def _setup_driver(self) -> webdriver.Chrome:
        """Set up Chrome WebDriver with configured options.

        Returns:
            Configured Chrome WebDriver instance.

        Raises:
            PageLoadError: If WebDriver setup fails.
        """
        try:
            options = Options()
            for option in self.selenium_options:
                options.add_argument(option)

            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=options)
        except WebDriverException as e:
            raise PageLoadError(f"Failed to setup WebDriver: {str(e)}")

    def _is_same_domain(self, base_url: str, url: str) -> bool:
        """Check if two URLs belong to the same domain.

        Args:
            base_url: The original URL being crawled.
            url: The URL to check.

        Returns:
            True if URLs belong to the same domain, False otherwise.
        """
        base_domain = urlparse(base_url).netloc
        check_domain = urlparse(url).netloc
        logger.debug(f"Comparing domains: {base_domain} vs {check_domain}")
        return base_domain == check_domain

    def _extract_links(self, html_content: str, base_url: str) -> List[str]:
        """Extract links from HTML content.

        Args:
            html_content: Raw HTML content.
            base_url: Base URL for resolving relative links.

        Returns:
            List of absolute URLs found in the content.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        links = []
        logger.info(f"Extracting links from {base_url}")

        # Extract all links, including those in navigation
        for anchor in soup.find_all("a", href=True):
            href = anchor["href"]
            absolute_url = urljoin(base_url, href)

            # Skip fragment identifiers and javascript links
            if "#" in absolute_url or "javascript:" in absolute_url:
                logger.debug(f"Skipping URL: {absolute_url}")
                continue

            # Only include links from the same domain
            if self._is_same_domain(base_url, absolute_url):
                # Remove trailing slashes for consistency
                absolute_url = absolute_url.rstrip("/")
                if absolute_url != base_url.rstrip(
                    "/"
                ):  # Don't include self-references
                    logger.info(f"Found valid link: {absolute_url}")
                    links.append(absolute_url)
            else:
                logger.debug(f"Skipping external link: {absolute_url}")

        unique_links = list(set(links))  # Remove duplicates
        logger.info(f"Found {len(unique_links)} unique links on {base_url}")
        return unique_links

    def get_page_content(self, url: str) -> str:
        """Get page content using Selenium for JavaScript support."""
        logger.info(f"Fetching content from {url}")
        options = Options()
        options.add_argument("--headless")  # Run in headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.get(url)
            
            # Wait for main content to be present
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "main"))
            )
            
            # Additional wait for dynamic content
            time.sleep(3)
            
            content = driver.page_source
            driver.quit()
            return content
        except Exception as e:
            if 'driver' in locals():
                driver.quit()
            raise PageLoadError(f"Failed to load page {url}: {str(e)}")

    def _crawl_recursive(
        self, url: str, current_depth: int, max_depth: int
    ) -> List[Document]:
        """Recursively crawl URLs up to max_depth.

        Args:
            url: Current URL to crawl.
            current_depth: Current crawl depth.
            max_depth: Maximum depth for recursive crawling.

        Returns:
            List of Document objects containing page content.

        Raises:
            PageLoadError: If pages cannot be loaded.
            ContentExtractionError: If content cannot be extracted.
        """
        logger.info(f"Crawling {url} at depth {current_depth}/{max_depth}")

        if current_depth > max_depth:
            logger.info(f"Reached max depth at {url}")
            return []

        if url in self.visited_urls:
            logger.info(f"Already visited {url}")
            return []

        self.visited_urls.add(url)
        documents = []

        try:
            # Get page content
            content = self.get_page_content(url)
            
            # DEBUG: Print raw content
            print("\n\n========= RAW CONTENT FROM", url, "=========")
            print(content[:1000])  # First 1000 chars
            # print(content)
            print("...[content truncated]...")
            print("=========================================\n\n")

            # Extract links before cleaning content
            if current_depth < max_depth:
                links = self._extract_links(content, url)

            # Clean content for storage
            cleaned_text = self.content_cleaner.clean(content)

            # DEBUG: Print cleaned content
            print("\n\n========= CLEANED CONTENT FROM", url, "=========")
            # print(cleaned_text[:1000])  # First 1000 chars
            print(cleaned_text)
            # print("...[content truncated]...")
            print("=========================================\n\n")

            if cleaned_text.strip():
                doc = Document(
                    page_content=cleaned_text,
                    metadata={
                        "source": url,
                        "depth": current_depth,
                    },
                )
                documents.append(doc)
                logger.info(f"Added document from {url}")

                # Follow extracted links if not at max depth
                if current_depth < max_depth and links:
                    logger.info(f"Following {len(links)} links from {url}")
                    for link in links:
                        # Recursively crawl each link
                        sub_docs = self._crawl_recursive(
                            link, current_depth + 1, max_depth
                        )
                        documents.extend(sub_docs)
                        logger.info(f"Added {len(sub_docs)} documents from {link}")

            return documents

        except (PageLoadError, ContentExtractionError) as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            return documents
        except Exception as e:
            logger.error(f"Unexpected error crawling {url}: {str(e)}")
            return documents

    def crawl(self, url: str, max_depth: int = 2) -> List[Document]:
        """Crawl a URL and its linked pages up to max_depth.

        Args:
            url: Starting URL to crawl.
            max_depth: Maximum depth for recursive crawling.

        Returns:
            List of Document objects containing page content.

        Raises:
            PageLoadError: If pages cannot be loaded.
            ContentExtractionError: If content cannot be extracted.
        """
        logger.info(f"Starting crawl from {url} with max depth {max_depth}")
        self.visited_urls.clear()  # Reset visited URLs for new crawl
        return self._crawl_recursive(url, 0, max_depth)
