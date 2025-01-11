"""Content cleaning and processing module."""

import re
import warnings
from typing import List
from bs4 import BeautifulSoup, NavigableString, GuessedAtParserWarning

from rag_retriever.utils.config import config


class ContentCleaner:
    """Clean and process HTML content."""

    def __init__(self):
        """Initialize the content cleaner with configuration."""
        self.ui_patterns = config.content["ui_patterns"]

    def clean_element(self, element: BeautifulSoup | NavigableString) -> str:
        """Recursively clean and extract text from HTML elements while preserving structure.

        Args:
            element: BeautifulSoup element or NavigableString to clean.

        Returns:
            Cleaned text content.
        """
        if isinstance(element, NavigableString):
            return element.strip()

        # Skip navigation and UI elements
        if (
            element.name in ["nav", "header", "footer"]
            or element.get("role") == "navigation"
        ):
            return ""

        # Skip elements with certain classes or IDs that typically contain navigation/UI
        classes = element.get("class", [])
        if any(c for c in classes if "nav" in c.lower() or "menu" in c.lower()):
            return ""

        # Preserve code blocks
        if element.name in ["pre", "code"]:
            return "\n" + element.get_text() + "\n"

        # Handle main content areas with special attention
        if element.name == "main" or element.get("role") == "main":
            text = " ".join(
                self.clean_element(child)
                for child in element.children
                if self.clean_element(child)
            )
            return "\n" + text + "\n"

        # Handle paragraphs and block elements
        if element.name in ["p", "div", "section", "article"]:
            text = " ".join(
                self.clean_element(child)
                for child in element.children
                if self.clean_element(child)
            )
            return "\n" + text + "\n" if text else ""

        # Handle headers with hierarchy
        if element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            level = int(element.name[1])
            prefix = "#" * level + " "
            text = element.get_text().strip()
            return f"\n{prefix}{text}\n" if text else ""

        # Handle lists
        if element.name in ["ul", "ol"]:
            items = [
                self.clean_element(li) for li in element.find_all("li", recursive=False)
            ]
            return (
                "\n"
                + "\n".join(f"• {item.strip()}" for item in items if item.strip())
                + "\n"
            )

        # Recursively process other elements
        return " ".join(
            self.clean_element(child)
            for child in element.children
            if self.clean_element(child)
        )

    def clean(self, html_content: str) -> str:
        """Clean and structure HTML content."""
        # Suppress parser warnings
        warnings.filterwarnings("ignore", category=GuessedAtParserWarning)

        # Remove template code comments
        html_content = re.sub(
            r"<!--\[\[\[.*?\]\]\]-->", "", html_content, flags=re.DOTALL
        )
        html_content = re.sub(r"<!--.*?-->", "", html_content, flags=re.DOTALL)

        soup = BeautifulSoup(html_content, "lxml")

        # Remove script and style elements
        for element in soup(["script", "style"]):
            element.decompose()

        # Extract main content
        main_content = soup.find("main") or soup.find("article") or soup.find("body")
        if not main_content:
            main_content = soup

        # Get cleaned text
        text = self.clean_element(main_content)

        # Post-process the text
        text = self._post_process(text)

        return text.strip()

    def _post_process(self, text: str) -> str:
        """Post-process cleaned text.

        Args:
            text: Text to post-process.

        Returns:
            Post-processed text.
        """
        # Replace multiple newlines with double newline
        text = re.sub(r"\n\s*\n+", "\n\n", text)

        # Replace multiple spaces with single space
        text = re.sub(r" +", " ", text)

        # Remove UI patterns
        for pattern in self.ui_patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)

        return text
