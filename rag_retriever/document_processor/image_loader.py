"""Module for loading and processing images for the vector store."""

import os
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
import requests
from PIL import Image
import io
from urllib.parse import urlparse

from langchain_core.documents import Document
from .local_loader import LocalDocumentLoader
from .vision_analyzer import VisionAnalyzer

logger = logging.getLogger(__name__)


class ImageLoader:
    """Handles loading and processing of images from various sources."""

    SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".svg", ".webp", ".gif"}

    def __init__(
        self,
        config: Dict[str, Any],
        show_progress: bool = True,
    ):
        """Initialize the image loader.

        Args:
            config: Configuration dictionary containing image processing settings
            show_progress: Whether to show a progress bar during loading
        """
        self.config = config
        self.show_progress = show_progress

        # Initialize vision analyzer if enabled
        vision_enabled = config.get("image_processing", {}).get("vision_enabled", True)
        self.vision_analyzer = VisionAnalyzer(config) if vision_enabled else None

        # Reuse existing image processing from LocalDocumentLoader for OCR fallback
        self.local_loader = LocalDocumentLoader(config, show_progress)

    def _is_valid_url(self, url: str) -> bool:
        """Check if a URL is valid.

        Args:
            url: URL to validate

        Returns:
            bool: True if URL is valid, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    def _download_image(self, url: str) -> Optional[bytes]:
        """Download image from URL.

        Args:
            url: URL to download image from

        Returns:
            Optional[bytes]: Image bytes if successful, None otherwise
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Failed to download image from {url}: {str(e)}")
            return None

    def _validate_image(self, file_path: str) -> bool:
        """Validate image file format and size.

        Args:
            file_path: Path to image file

        Returns:
            bool: True if image is valid, False otherwise
        """
        try:
            # Check file extension
            ext = Path(file_path).suffix.lower()
            if ext not in self.SUPPORTED_FORMATS:
                logger.warning(f"Unsupported image format: {ext}")
                return False

            # Check file size
            max_size_mb = self.config.get("image_processing", {}).get(
                "max_file_size_mb", 10
            )
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb > max_size_mb:
                logger.warning(
                    f"Image file too large: {file_size_mb:.1f}MB > {max_size_mb}MB"
                )
                return False

            # Validate image can be opened
            with Image.open(file_path) as img:
                img.verify()
            return True

        except Exception as e:
            logger.error(f"Image validation failed for {file_path}: {str(e)}")
            return False

    def _convert_analysis_to_markdown(
        self, analysis: Dict[str, Any], source: str
    ) -> str:
        """Convert vision analysis to markdown format.

        Args:
            analysis: Vision analysis result dictionary
            source: Source of the image (path or URL)

        Returns:
            str: Markdown formatted analysis
        """
        # Extract the filename or URL for the title
        title = os.path.basename(source) if not self._is_valid_url(source) else source

        # Build markdown content
        md_parts = []

        # Title and source
        md_parts.append(f"# Image Analysis: {title}\n")

        # Core Message section
        core = analysis["core_message"]
        md_parts.extend(
            [
                "## Core Message\n",
                f"**Main Purpose**: {core['main_purpose']}\n",
                f"**Key Message**: {core['key_message']}\n",
                f"**Domain**: {core['domain']}\n",
            ]
        )

        # Content Analysis section
        content = analysis["content"]
        md_parts.append("\n## Content Analysis\n")

        if content["key_elements"]:
            md_parts.append("\n### Key Elements\n")
            for element in content["key_elements"]:
                md_parts.append(f"- {element}\n")

        if content["relationships"]:
            md_parts.append("\n### Relationships\n")
            for rel in content["relationships"]:
                md_parts.append(f"- {rel}\n")

        if content["patterns"]:
            md_parts.append("\n### Patterns\n")
            for pattern in content["patterns"]:
                md_parts.append(f"- {pattern}\n")

        if content["presentation_method"]:
            md_parts.append(
                f"\n**Presentation Method**: {content['presentation_method']}\n"
            )

        # Context section
        context = analysis["context"]
        md_parts.append("\n## Context\n")
        md_parts.append(f"**Intended Audience**: {context['intended_audience']}\n")

        if context["addressed_needs"]:
            md_parts.append("\n### Addressed Needs\n")
            for need in context["addressed_needs"]:
                md_parts.append(f"- {need}\n")

        if context["key_insights"]:
            md_parts.append("\n### Key Insights\n")
            for insight in context["key_insights"]:
                md_parts.append(f"- {insight}\n")

        if context["implications"]:
            md_parts.append("\n### Implications\n")
            for impl in context["implications"]:
                md_parts.append(f"- {impl}\n")

        # Technical Details section (if present and relevant)
        tech = analysis.get("technical_details")
        if tech and any(tech.values()):
            md_parts.append("\n## Technical Details\n")

            if tech.get("specifications"):
                md_parts.append("\n### Specifications\n")
                for spec in tech["specifications"]:
                    md_parts.append(f"- {spec}\n")

            if tech.get("structure"):
                md_parts.append(f"\n**Structure**: {tech['structure']}\n")

            if tech.get("methodology"):
                md_parts.append(f"\n**Methodology**: {tech['methodology']}\n")

            if tech.get("requirements"):
                md_parts.append("\n### Requirements\n")
                for req in tech["requirements"]:
                    md_parts.append(f"- {req}\n")

        # Summary section
        if analysis.get("summary"):
            md_parts.extend(["\n## Summary\n", f"{analysis['summary']}\n"])

        return "".join(md_parts)

    def load_image(self, source: str) -> Optional[Document]:
        """Load image from file path or URL.

        Args:
            source: File path or URL of image

        Returns:
            Optional[Document]: Document containing image analysis in markdown format
        """
        try:
            # Handle URL source
            if self._is_valid_url(source):
                image_bytes = self._download_image(source)
                if not image_bytes:
                    return None

                # Save to temporary file for processing
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=Path(source).suffix
                ) as tmp:
                    tmp.write(image_bytes)
                    tmp_path = tmp.name

                if not self._validate_image(tmp_path):
                    os.unlink(tmp_path)
                    return None

                # Process image with vision model
                if not self.vision_analyzer:
                    logger.error("Vision analysis is required but not enabled")
                    return None

                analysis = self.vision_analyzer.analyze_image(tmp_path)
                if not analysis:
                    logger.error(f"Vision analysis failed for image: {source}")
                    return None

                os.unlink(tmp_path)

            # Handle local file source
            else:
                if not self._validate_image(source):
                    return None

                # Process image with vision model
                if not self.vision_analyzer:
                    logger.error("Vision analysis is required but not enabled")
                    return None

                analysis = self.vision_analyzer.analyze_image(source)
                if not analysis:
                    logger.error(f"Vision analysis failed for image: {source}")
                    return None

            # Convert analysis to markdown
            markdown_content = self._convert_analysis_to_markdown(
                analysis["analysis"], source
            )

            # Create document with metadata
            metadata = {
                "source": source,
                "type": "image",
                "extension": Path(source).suffix.lower(),
                "analysis_type": "vision",
            }

            return Document(page_content=markdown_content, metadata=metadata)

        except Exception as e:
            logger.error(f"Failed to load image from {source}: {str(e)}")
            return None

    def load_directory(self, directory_path: str) -> List[Document]:
        """Load all supported images from a directory.

        Args:
            directory_path: Path to directory containing images

        Returns:
            List[Document]: List of documents containing image data
        """
        documents = []
        directory = Path(directory_path)

        if not directory.is_dir():
            logger.error(f"Not a directory: {directory_path}")
            return documents

        for ext in self.SUPPORTED_FORMATS:
            for file_path in directory.glob(f"**/*{ext}"):
                if doc := self.load_image(str(file_path)):
                    documents.append(doc)

        return documents
