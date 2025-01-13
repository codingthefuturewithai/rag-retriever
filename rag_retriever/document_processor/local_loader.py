"""Module for loading local documents into the vector store."""

from pathlib import Path
from typing import List, Optional, Iterator, Dict, Any, Tuple
import logging
import os
import tempfile
from PIL import Image
import pytesseract
import io
import numpy as np

from langchain_core.documents import Document
from langchain_community.document_loaders import (
    DirectoryLoader,
    TextLoader,
    PyPDFLoader,
    UnstructuredPDFLoader,
    PyMuPDFLoader,
)

logger = logging.getLogger(__name__)


class LocalDocumentLoader:
    """Handles loading of local documents (markdown, text, pdf) into Document objects."""

    def __init__(
        self,
        config: Dict[str, Any],
        show_progress: bool = True,
        use_multithreading: bool = True,
    ):
        """Initialize the document loader.

        Args:
            config: Configuration dictionary containing document processing settings
            show_progress: Whether to show a progress bar during loading
            use_multithreading: Whether to use multiple threads for directory loading
        """
        self.config = config
        self.show_progress = show_progress
        self.use_multithreading = use_multithreading
        self.supported_extensions = set(
            config.get("document_processing", {}).get("supported_extensions", [])
        )
        self.pdf_settings = config.get("document_processing", {}).get(
            "pdf_settings", {}
        )

        # Initialize OCR settings
        self.ocr_config = {
            "enabled": self.pdf_settings.get("ocr_enabled", False),
            "languages": self.pdf_settings.get("languages", ["eng"]),
            "min_confidence": self.pdf_settings.get("min_ocr_confidence", 60),
            "max_image_size": self.pdf_settings.get("max_image_size", 4096),
            "min_image_size": self.pdf_settings.get("min_image_size", 50),
        }

    def _check_pdf_size(self, file_path: Path) -> None:
        """Check if PDF file size is within configured limits.

        Args:
            file_path: Path to the PDF file

        Raises:
            ValueError: If the file size exceeds the configured limit
        """
        max_size_mb = self.pdf_settings.get("max_file_size_mb", 50)
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)  # Convert to MB
        if file_size_mb > max_size_mb:
            raise ValueError(
                f"PDF file size ({file_size_mb:.1f}MB) exceeds the maximum allowed size of {max_size_mb}MB"
            )

    def _preprocess_image(self, image: Image.Image) -> Tuple[Image.Image, bool]:
        """Preprocess image for better OCR results.

        Args:
            image: PIL Image to preprocess

        Returns:
            Tuple of (preprocessed image, whether preprocessing succeeded)
        """
        try:
            # Convert to RGB if needed
            if image.mode not in ("RGB", "L"):
                image = image.convert("RGB")

            # Get image dimensions
            width, height = image.size

            # Check if image is too small
            if (
                width < self.ocr_config["min_image_size"]
                or height < self.ocr_config["min_image_size"]
            ):
                logger.debug(f"Image too small ({width}x{height}), skipping")
                return image, False

            # Resize if image is too large
            max_size = self.ocr_config["max_image_size"]
            if width > max_size or height > max_size:
                ratio = min(max_size / width, max_size / height)
                new_size = (int(width * ratio), int(height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
                logger.debug(
                    f"Resized image from {width}x{height} to {new_size[0]}x{new_size[1]}"
                )

            # Convert to grayscale for better OCR
            image = image.convert("L")

            # Enhance contrast
            import PIL.ImageOps

            image = PIL.ImageOps.autocontrast(image)

            # Denoise (if image is noisy)
            if self.pdf_settings.get("denoise_images", True):
                import PIL.ImageFilter

                image = image.filter(PIL.ImageFilter.MedianFilter(size=3))

            return image, True

        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            return image, False

    def _process_image_with_ocr(self, image_path: str, languages: List[str]) -> str:
        """Process an image with OCR to extract text.

        Args:
            image_path: Path to the image file
            languages: List of language codes for OCR

        Returns:
            Extracted text from the image
        """
        try:
            # Open image
            with Image.open(image_path) as image:
                # Preprocess image
                processed_image, success = self._preprocess_image(image)
                if not success:
                    return ""

                # Configure tesseract
                lang_str = "+".join(languages)
                custom_config = (
                    f"-l {lang_str} "  # Language
                    "--oem 1 "  # LSTM only
                    "--psm 6 "  # Assume uniform block of text
                    "-c tessedit_create_pdf=0 "  # Don't create PDF
                    "-c tessedit_pageseg_mode=6 "  # Assume uniform text block
                    "-c textord_heavy_nr=0 "  # Don't assume heavy noise
                    "-c tessedit_do_invert=0 "  # Don't try to invert colors
                    "-c tessedit_min_word_length=3"  # Minimum word length
                )

                # Perform OCR with confidence check
                result = pytesseract.image_to_data(
                    processed_image,
                    config=custom_config,
                    output_type=pytesseract.Output.DICT,
                )

                # Filter by confidence and build text
                lines = []
                current_line = []
                last_block_num = -1

                for i in range(len(result["text"])):
                    conf = int(result["conf"][i])
                    text = result["text"][i].strip()
                    block_num = result["block_num"][i]

                    # Skip low confidence or empty text
                    if conf < self.ocr_config["min_confidence"] or not text:
                        continue

                    # Handle line breaks
                    if block_num != last_block_num and current_line:
                        lines.append(" ".join(current_line))
                        current_line = []

                    current_line.append(text)
                    last_block_num = block_num

                # Add final line
                if current_line:
                    lines.append(" ".join(current_line))

                return "\n".join(lines)

        except Exception as e:
            logger.error(f"OCR failed for image {image_path}: {str(e)}")
            return ""

    def _process_pdf_images(self, file_path: str, temp_dir: str) -> List[Document]:
        """Extract and process images from PDF if enabled in settings.

        Args:
            file_path: Path to the PDF file
            temp_dir: Directory to store temporary image files

        Returns:
            List of Document objects containing image metadata and OCR text
        """
        if not self.pdf_settings.get("extract_images", False):
            return []

        try:
            import fitz  # PyMuPDF

            image_docs = []
            pdf_document = fitz.open(file_path)

            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                image_list = page.get_images()

                for img_idx, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        base_image = pdf_document.extract_image(xref)
                        image_bytes = base_image["image"]

                        # Skip if image is too small
                        if len(image_bytes) < 1024:  # Skip images smaller than 1KB
                            continue

                        # Save image temporarily for processing
                        image_path = os.path.join(
                            temp_dir, f"page_{page_num}_img_{img_idx}.png"
                        )
                        with open(image_path, "wb") as img_file:
                            img_file.write(image_bytes)

                        # Extract text with OCR if enabled
                        image_text = ""
                        if self.ocr_config["enabled"]:
                            logger.debug(
                                f"Running OCR on image from page {page_num + 1}"
                            )
                            image_text = self._process_image_with_ocr(
                                image_path, self.ocr_config["languages"]
                            )

                        if image_text or not self.ocr_config["enabled"]:
                            # Create document with image metadata and OCR text
                            content = f"Image on page {page_num + 1}"
                            if image_text:
                                content = f"{content}\nOCR Text:\n{image_text}"

                            image_doc = Document(
                                page_content=content,
                                metadata={
                                    "source": file_path,
                                    "page": page_num + 1,
                                    "image_path": image_path,
                                    "image_index": img_idx,
                                    "type": "image",
                                    "size": len(image_bytes),
                                    "has_ocr": bool(image_text),
                                },
                            )
                            image_docs.append(image_doc)

                    except Exception as e:
                        logger.error(
                            f"Error processing image {img_idx} on page {page_num}: {str(e)}"
                        )
                        continue

            return image_docs

        except ImportError:
            logger.warning("PyMuPDF not installed. Image extraction disabled.")
            return []
        except Exception as e:
            logger.error(f"Error extracting images from PDF: {str(e)}")
            return []

    def load_file(self, file_path: str) -> List[Document]:
        """Load a single file with appropriate loader based on extension.

        Args:
            file_path: Path to the file to load

        Returns:
            List of Document objects

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file type is not supported or file size exceeds limits
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        suffix = path.suffix.lower()
        if suffix not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {suffix}")

        if suffix in [".md", ".txt"]:
            logger.debug(f"Loading text file: {file_path}")
            loader = TextLoader(file_path, autodetect_encoding=True)
            try:
                return list(loader.lazy_load())
            except Exception as e:
                logger.error(f"Error loading file {file_path}: {str(e)}")
                raise

        if suffix == ".pdf":
            logger.debug(f"Loading PDF file: {file_path}")
            self._check_pdf_size(path)

            documents = []
            with tempfile.TemporaryDirectory() as temp_dir:
                # Try different loaders in order of preference
                loaders = [
                    (PyMuPDFLoader, "PyMuPDF"),
                    (UnstructuredPDFLoader, "Unstructured"),
                    (PyPDFLoader, "PyPDF"),
                ]

                text_extracted = False
                for loader_class, name in loaders:
                    try:
                        if name == "Unstructured":
                            loader = loader_class(
                                file_path,
                                mode=self.pdf_settings.get("mode", "elements"),
                                strategy=self.pdf_settings.get("strategy", "fast"),
                                languages=(
                                    self.pdf_settings.get("ocr_languages", ["eng"])
                                    if self.ocr_config["enabled"]
                                    else None
                                ),
                            )
                        else:
                            loader = loader_class(file_path)

                        page_docs = loader.load()
                        if page_docs:
                            documents.extend(page_docs)
                            text_extracted = True
                            logger.info(f"Successfully extracted text with {name}")
                            break
                        else:
                            logger.warning(f"No text extracted with {name}")

                    except Exception as e:
                        logger.error(f"Error loading PDF with {name}: {str(e)}")
                        continue

                if not text_extracted:
                    logger.warning("Failed to extract text with all loaders")

                # Process images regardless of text extraction success
                if self.pdf_settings.get("extract_images", False):
                    image_docs = self._process_pdf_images(file_path, temp_dir)
                    if image_docs:
                        documents.extend(image_docs)
                        logger.info(f"Extracted {len(image_docs)} images from PDF")

                if not documents:
                    raise ValueError("No content could be extracted from PDF")

                return documents

        raise ValueError(f"Unhandled file type: {suffix}")

    def load_directory(
        self, directory_path: str, glob_pattern: str = "**/*.[mp][dt][fd]"
    ) -> List[Document]:
        """Load all supported documents from a directory.

        Args:
            directory_path: Path to the directory to load files from
            glob_pattern: Pattern to match files against. Default matches .md, .txt, and .pdf files.
                        Use "**/*.txt" for text files, "**/*.pdf" for PDFs, or "**/*.md" for markdown.

        Returns:
            List of Document objects

        Raises:
            FileNotFoundError: If the directory doesn't exist
        """
        path = Path(directory_path)
        if not path.exists() or not path.is_dir():
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        logger.info(f"Loading documents from directory: {directory_path}")

        # First check if there are any matching files
        matching_files = list(path.glob(glob_pattern))
        if not matching_files:
            logger.warning(
                f"No matching files found in {directory_path} using pattern {glob_pattern}"
            )
            return []

        logger.debug(
            f"Found {len(matching_files)} matching files: {[f.name for f in matching_files]}"
        )

        # Process each file individually to handle different loaders
        documents = []
        for file_path in matching_files:
            try:
                file_docs = self.load_file(str(file_path))
                documents.extend(file_docs)
            except Exception as e:
                logger.error(f"Error loading file {file_path}: {str(e)}")
                continue

        return documents
