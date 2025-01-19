"""Web page crawling and content extraction module using Playwright."""

import time
import random
import logging
import asyncio
import platform
from typing import List, Set, Dict, Any
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser, Page
from langchain_core.documents import Document

from rag_retriever.utils.config import config
from rag_retriever.utils.windows import suppress_asyncio_warnings, windows_event_loop
from rag_retriever.crawling.exceptions import (
    PageLoadError,
    ContentExtractionError,
    CrawlerError,
)
from rag_retriever.crawling.content_cleaner import ContentCleaner

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlaywrightCrawler:
    """Web page crawler using Playwright for JavaScript support."""

    def __init__(self):
        """Initialize the crawler with configuration."""
        self.config = config.browser
        self.content_cleaner = ContentCleaner()
        self.visited_urls: Set[str] = set()
        self._total_chunks = 0
        self._browser = None
        self._context = None
        self._setup_platform_config()

    def _setup_platform_config(self):
        """Set up platform-specific configuration."""
        # Initialize stealth config if it doesn't exist
        if "stealth" not in self.config:
            self.config["stealth"] = {}

        system = platform.system().lower()
        if system == "darwin":  # macOS
            self.config["stealth"].update(
                {
                    "platform": "MacIntel",
                    "webgl_vendor": "Apple Inc.",
                    "renderer": "Apple GPU",
                    "vendor": "Google Inc.",
                }
            )
        elif system == "windows":
            self.config["stealth"].update(
                {
                    "platform": "Win32",
                    "webgl_vendor": "Google Inc.",
                    "renderer": "ANGLE (Intel, Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0)",
                    "vendor": "Google Inc.",
                }
            )
        else:  # Linux and others
            self.config["stealth"].update(
                {
                    "platform": "Linux x86_64",
                    "webgl_vendor": "Google Inc.",
                    "renderer": "Mesa/X.org, ANGLE (Intel, Mesa Intel(R) UHD Graphics 620 (KBL GT2), OpenGL 4.6)",
                    "vendor": "Google Inc.",
                }
            )

        # Ensure all required config sections exist with optimized values
        if "launch_options" not in self.config:
            self.config["launch_options"] = {
                "headless": True,
                "timeout": 30000,  # 30 second timeout
            }
        if "viewport" not in self.config:
            self.config["viewport"] = {"width": 1920, "height": 1080}
        if "context_options" not in self.config:
            self.config["context_options"] = {
                "bypass_csp": True,
                "java_script_enabled": True,
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            }
        if "delays" not in self.config:
            self.config["delays"] = {
                "before_request": [0.1, 0.3],  # Reduced delays
                "after_load": [0.2, 0.5],
                "after_dynamic": [0.1, 0.2],
            }
        if "wait_time" not in self.config:
            self.config["wait_time"] = 10  # 10 seconds

    async def _setup_browser(self) -> Browser:
        """Set up Playwright browser with stealth configuration."""
        try:
            playwright = await async_playwright().start()
            try:
                browser = await playwright.chromium.launch(
                    **self.config["launch_options"]
                )
            except Exception as e:
                if "Executable doesn't exist" in str(e):
                    logger.warning(
                        "Chromium browser not found, attempting to install..."
                    )
                    import subprocess
                    import sys

                    try:
                        # Install chromium using the current Python executable
                        subprocess.run(
                            [sys.executable, "-m", "playwright", "install", "chromium"],
                            check=True,
                            capture_output=True,
                            text=True,
                        )
                        # Try launching again after installation
                        browser = await playwright.chromium.launch(
                            **self.config["launch_options"]
                        )
                    except subprocess.CalledProcessError as install_error:
                        raise PageLoadError(
                            f"Failed to install Chromium browser. Please run '{sys.executable} -m playwright install chromium' manually."
                        ) from install_error
                else:
                    raise

            # Create a new context with specific configurations
            context = await browser.new_context(
                viewport=self.config["viewport"],
                user_agent=self.config["context_options"]["user_agent"],
                java_script_enabled=self.config["context_options"][
                    "java_script_enabled"
                ],
                bypass_csp=self.config["context_options"]["bypass_csp"],
            )

            # Add stealth scripts
            await context.add_init_script(
                """
                // Override properties that detect automation
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Add language preferences
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });

                // Override platform
                Object.defineProperty(navigator, 'platform', {
                    get: () => '%s'
                });

                // Override vendor
                Object.defineProperty(navigator, 'vendor', {
                    get: () => '%s'
                });
            """
                % (
                    self.config["stealth"]["platform"],
                    self.config["stealth"]["vendor"],
                )
            )

            self._browser = browser
            self._context = context
            return browser

        except Exception as e:
            logger.error("Browser config: %s", self.config)
            raise PageLoadError(f"Failed to setup Playwright browser: {str(e)}")

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

        for anchor in soup.find_all("a", href=True):
            href = anchor["href"]
            absolute_url = urljoin(base_url, href)

            if "#" in absolute_url or "javascript:" in absolute_url:
                logger.debug(f"Skipping URL: {absolute_url}")
                continue

            if self._is_same_domain(base_url, absolute_url):
                absolute_url = absolute_url.rstrip("/")
                if absolute_url != base_url.rstrip("/"):
                    logger.debug(f"Found valid link: {absolute_url}")
                    links.append(absolute_url)
            else:
                logger.debug(f"Skipping external link: {absolute_url}")

        unique_links = list(set(links))
        logger.debug(f"Found {len(unique_links)} unique links on {base_url}")
        return unique_links

    async def get_page_content(self, url: str) -> str:
        """Get page content using Playwright."""
        logger.debug(f"Fetching content from {url}")

        if not self._browser:
            await self._setup_browser()

        try:
            # Minimal delay before request
            delay_min, delay_max = self.config["delays"]["before_request"]
            await asyncio.sleep(random.uniform(delay_min, delay_max))

            page = await self._context.new_page()

            # Set reasonable timeouts
            page.set_default_timeout(30000)  # 30 seconds timeout
            page.set_default_navigation_timeout(30000)

            try:
                # Try loading with domcontentloaded first (faster)
                response = await page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=30000,
                )

                # Quick check for body element
                await page.wait_for_selector(
                    "body",
                    timeout=5000,
                    state="attached",
                )

            except Exception as e:
                logger.warning(
                    f"Initial load failed, retrying with networkidle: {str(e)}"
                )
                # Fall back to networkidle only if needed
                response = await page.goto(
                    url,
                    wait_until="networkidle",
                    timeout=30000,
                )

            if not response:
                raise PageLoadError(f"Failed to load page {url}: No response")

            if response.status >= 400:
                raise PageLoadError(
                    f"Failed to load page {url}: Status {response.status}"
                )

            # Quick delay for any remaining dynamic content
            delay_min, delay_max = self.config["delays"]["after_dynamic"]
            await asyncio.sleep(random.uniform(delay_min, delay_max))

            content = await page.content()
            await page.close()
            return content

        except Exception as e:
            if "page" in locals():
                await page.close()
            raise PageLoadError(f"Failed to load page {url}: {str(e)}")

    async def _crawl_recursive(
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
            content = await self.get_page_content(url)

            if current_depth < max_depth:
                links = self._extract_links(content, url)

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

                if current_depth < max_depth and links:
                    logger.debug(f"Following {len(links)} links from {url}")
                    for link in links:
                        sub_docs = await self._crawl_recursive(
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

    async def crawl(self, url: str, max_depth: int = 2) -> List[Document]:
        """Crawl a URL and its linked pages up to max_depth."""
        logger.info(f"Starting crawl of {url}")
        self.visited_urls.clear()

        try:
            documents = await self._crawl_recursive(url, 0, max_depth)
            logger.info(f"Completed crawl: processed {len(documents)} documents")

            if self._browser:
                await self._browser.close()
                self._browser = None
                self._context = None

            return documents
        except Exception as e:
            if self._browser:
                await self._browser.close()
                self._browser = None
                self._context = None
            raise e

    def run_crawl(self, url: str, max_depth: int = 2) -> List[Document]:
        """Synchronous wrapper for the async crawl method."""
        # Suppress asyncio warnings on Windows
        suppress_asyncio_warnings()

        @windows_event_loop
        def _run():
            return asyncio.run(self.crawl(url, max_depth))

        return _run()
