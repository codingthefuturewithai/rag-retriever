"""Module for loading Confluence documents into the vector store."""

from typing import List, Dict, Any, Optional
import logging
from langchain_core.documents import Document
from langchain_community.document_loaders import ConfluenceLoader

logger = logging.getLogger(__name__)


class ConfluenceDocumentLoader:
    """Handles loading of Confluence pages into Document objects."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the Confluence document loader.

        Args:
            config: Configuration dictionary containing Confluence settings
        """
        self.config = config.get("api", {}).get("confluence", {})
        if (
            not self.config.get("url")
            or not self.config.get("username")
            or not self.config.get("api_token")
        ):
            raise ValueError(
                "Confluence configuration missing required fields: url, username, and api_token"
            )

        self.loader = ConfluenceLoader(
            url=self.config["url"],
            username=self.config["username"],
            api_key=self.config["api_token"],
            limit=self.config.get("limit", 50),
            max_pages=self.config.get("max_pages", 1000),
            include_attachments=self.config.get("include_attachments", False),
            keep_markdown_format=True,
        )

    def load_pages(
        self, space_key: Optional[str] = None, parent_id: Optional[str] = None
    ) -> List[Document]:
        """Load pages from Confluence.

        Args:
            space_key: Optional space key to filter pages
            parent_id: Optional parent page ID to start from

        Returns:
            List of Document objects containing page content
        """
        try:
            # Use configured values if not provided
            space_key = space_key or self.config.get("space_key")
            parent_id = parent_id or self.config.get("parent_id")

            logger.info(
                f"Loading Confluence pages (space_key={space_key}, parent_id={parent_id})"
            )

            # Load documents using the configured loader
            documents = self.loader.load(
                space_key=space_key,
                parent_id=parent_id,
                include_restricted=False,  # Only load pages the user has access to
                ocr_languages="eng",  # Default to English for any image processing
            )

            logger.info(f"Successfully loaded {len(documents)} Confluence pages")
            return documents

        except Exception as e:
            logger.error(f"Error loading Confluence pages: {str(e)}")
            raise
