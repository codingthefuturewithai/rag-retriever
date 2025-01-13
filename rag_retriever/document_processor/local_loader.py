"""Module for loading local documents into the vector store."""

from pathlib import Path
from typing import List, Optional, Iterator, Dict, Any
import logging
import os
import tempfile
from PIL import Image
import pytesseract

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

    def _process_image_with_ocr(self, image_path: str, languages: List[str]) -> str:
        """Process an image with OCR to extract text.

        Args:
            image_path: Path to the image file
            languages: List of language codes for OCR

        Returns:
            Extracted text from the image
        """
        try:
            # Open and preprocess the image
            image = Image.open(image_path)

            # Convert to RGB if needed (some PDFs produce RGBA images)
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Resize if image is too small (helps with OCR accuracy)
            min_size = 1000
            ratio = max(min_size / image.width, min_size / image.height)
            if ratio > 1:
                new_size = (int(image.width * ratio), int(image.height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)

            # Configure tesseract with better parameters
            lang_str = "+".join(languages)
            custom_config = (
                f"-l {lang_str} "  # Language
                "--oem 3 "  # OCR Engine Mode: Default LSTM
                "--psm 6 "  # Page Segmentation Mode: Assume uniform block of text
                "-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_(),./ "  # Limit characters
                "preserve_interword_spaces=1 "  # Preserve spacing between words
                "textord_heavy_nr=1"  # Handle noisy images better
            )

            # Perform OCR
            text = pytesseract.image_to_string(image, config=custom_config)

            # Post-process the text
            lines = []
            for line in text.splitlines():
                # Remove extra whitespace
                line = " ".join(line.split())
                if line:  # Only keep non-empty lines
                    lines.append(line)

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
                    xref = img[0]
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]

                    # Save image temporarily for processing
                    image_path = os.path.join(
                        temp_dir, f"page_{page_num}_img_{img_idx}.png"
                    )
                    with open(image_path, "wb") as img_file:
                        img_file.write(image_bytes)

                    # Extract text with OCR if enabled
                    image_text = ""
                    if self.pdf_settings.get("ocr_enabled", False):
                        logger.debug(f"Running OCR on image from page {page_num + 1}")
                        image_text = self._process_image_with_ocr(
                            image_path, self.pdf_settings.get("languages", ["eng"])
                        )

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
                # Extract text with high-quality parsing
                try:
                    loader = UnstructuredPDFLoader(
                        file_path,
                        mode=self.pdf_settings.get("mode", "elements"),
                        strategy=self.pdf_settings.get("strategy", "fast"),
                        languages=(
                            self.pdf_settings.get("ocr_languages", ["eng"])
                            if self.pdf_settings.get("ocr_enabled", False)
                            else None
                        ),
                    )
                    documents.extend(loader.load())
                    if not documents:  # If no text was extracted
                        raise ValueError("No text extracted from PDF")
                except Exception as e:
                    logger.error(f"Error loading PDF text with Unstructured: {str(e)}")
                    # Fallback to PyMuPDF for text
                    try:
                        logger.info("Attempting fallback to PyMuPDF loader")
                        loader = PyMuPDFLoader(file_path)
                        documents.extend(loader.load())
                        if not documents:  # If still no text
                            raise ValueError("No text extracted with PyMuPDF")
                    except Exception as e2:
                        logger.error(f"Error loading PDF with PyMuPDF: {str(e2)}")
                        # Last resort fallback
                        logger.info("Attempting final fallback to PyPDFLoader")
                        loader = PyPDFLoader(
                            file_path,
                            password=self.pdf_settings.get("password"),
                        )
                        documents.extend(loader.load())

                # Extract images if enabled
                image_docs = self._process_pdf_images(file_path, temp_dir)
                documents.extend(image_docs)

            return documents

        raise ValueError(f"Unsupported file type: {suffix}")

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
