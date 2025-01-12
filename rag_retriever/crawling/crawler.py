"""Web page crawling and content extraction module."""

import time
import random
import logging
import platform
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
from selenium_stealth import stealth

from rag_retriever.utils.config import config
from rag_retriever.crawling.exceptions import (
    PageLoadError,
    ContentExtractionError,
    CrawlerError,
)
from rag_retriever.crawling.content_cleaner import ContentCleaner

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
        self._total_chunks = 0
        self._setup_platform_config()

    def _setup_platform_config(self):
        """Set up platform-specific configuration."""
        system = platform.system().lower()
        if system == "darwin":  # macOS
            self.platform_name = "MacIntel"
            self.webgl_vendor = "Apple Inc."
            self.renderer = "Apple GPU"
            self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        elif system == "windows":
            self.platform_name = "Win32"
            self.webgl_vendor = "Google Inc."
            self.renderer = (
                "ANGLE (Intel, Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0)"
            )
            self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        else:  # Linux and others
            self.platform_name = "Linux x86_64"
            self.webgl_vendor = "Google Inc."
            self.renderer = "Mesa/X.org, ANGLE (Intel, Mesa Intel(R) UHD Graphics 620 (KBL GT2), OpenGL 4.6)"
            self.user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    def _setup_driver(self) -> webdriver.Chrome:
        """Set up Chrome WebDriver with configured options."""
        try:
            options = Options()

            # Set platform-specific user agent
            options.add_argument(f"user-agent={self.user_agent}")

            # Add essential options for stealth
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--no-sandbox")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)

            # Add any additional configured options
            for option in self.selenium_options:
                if option not in options.arguments:
                    options.add_argument(option)

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)

            # Apply stealth settings with platform-specific values
            stealth(
                driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform=self.platform_name,
                webgl_vendor=self.webgl_vendor,
                renderer=self.renderer,
                fix_hairline=True,
                run_on_insecure_origins=True,
            )

            # Execute CDP commands to prevent detection
            driver.execute_cdp_cmd(
                "Network.setUserAgentOverride",
                {"userAgent": self.user_agent},
            )

            # Remove webdriver property
            driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )

            return driver
        except WebDriverException as e:
            raise PageLoadError(f"Failed to setup WebDriver: {str(e)}")

    def _is_same_domain(self, base_url: str, url: str) -> bool:
        """Check if two URLs belong to the same domain."""
        base_domain = urlparse(base_url).netloc
        check_domain = urlparse(url).netloc
        logger.debug(f"Comparing domains: {base_domain} vs {check_domain}")
        return base_domain == check_domain

    def _extract_links(self, html_content: str, base_url: str) -> List[str]:
        """Extract links from HTML content."""
        soup = BeautifulSoup(html_content, "html.parser")
        links = []
        logger.debug(f"Extracting links from {base_url}")

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
                    logger.debug(f"Found valid link: {absolute_url}")
                    links.append(absolute_url)
            else:
                logger.debug(f"Skipping external link: {absolute_url}")

        unique_links = list(set(links))  # Remove duplicates
        logger.debug(f"Found {len(unique_links)} unique links on {base_url}")
        return unique_links

    def get_page_content(self, url: str) -> str:
        """Get page content using Selenium for JavaScript support."""
        logger.debug(f"Fetching content from {url}")

        try:
            driver = self._setup_driver()

            # Add random delay before request (1-3 seconds)
            time.sleep(random.uniform(1, 3))

            driver.get(url)

            # Random delay after page load (2-4 seconds)
            time.sleep(random.uniform(2, 4))

            try:
                # Wait for main content with longer timeout
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except Exception as e:
                logger.warning(
                    f"Timeout waiting for main content, proceeding anyway: {str(e)}"
                )

            # Additional random delay for dynamic content (1-2 seconds)
            time.sleep(random.uniform(1, 2))

            content = driver.page_source
            driver.quit()
            return content
        except Exception as e:
            if "driver" in locals():
                driver.quit()
            raise PageLoadError(f"Failed to load page {url}: {str(e)}")

    def _crawl_recursive(
        self, url: str, current_depth: int, max_depth: int
    ) -> List[Document]:
        """Recursively crawl URLs up to max_depth."""
        logger.debug(f"Crawling {url} at depth {current_depth}/{max_depth}")

        if current_depth > max_depth:
            logger.debug(f"Reached max depth at {url}")
            return []

        if url in self.visited_urls:
            logger.debug(f"Already visited {url}")
            return []

        self.visited_urls.add(url)
        documents = []

        try:
            # Get page content
            content = self.get_page_content(url)

            # Extract links before cleaning content
            if current_depth < max_depth:
                links = self._extract_links(content, url)

            # Clean content for storage
            cleaned_text = self.content_cleaner.clean(content)

            if cleaned_text.strip():
                doc = Document(
                    page_content=cleaned_text,
                    metadata={
                        "source": url,
                        "depth": current_depth,
                    },
                )
                documents.append(doc)
                logger.info(f"Processed document: {url}")

                # Follow extracted links if not at max depth
                if current_depth < max_depth and links:
                    logger.debug(f"Following {len(links)} links from {url}")
                    for link in links:
                        # Recursively crawl each link
                        sub_docs = self._crawl_recursive(
                            link, current_depth + 1, max_depth
                        )
                        documents.extend(sub_docs)

            return documents

        except (PageLoadError, ContentExtractionError) as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            return documents
        except Exception as e:
            logger.error(f"Unexpected error crawling {url}: {str(e)}")
            return documents

    def crawl(self, url: str, max_depth: int = 2) -> List[Document]:
        """Crawl a URL and its linked pages up to max_depth."""
        logger.info(f"Starting crawl of {url}")
        self.visited_urls.clear()  # Reset visited URLs for new crawl
        documents = self._crawl_recursive(url, 0, max_depth)
        logger.info(f"Completed crawl: processed {len(documents)} documents")
        return documents
