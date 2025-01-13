#!/usr/bin/env python3

import os
import sys
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Tuple
import pypdf
import pytesseract
from PIL import Image
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFAnalyzer:
    def __init__(self):
        self.categories = {
            "simple": [],
            "images": [],
            "tables": [],
            "technical": [],
            "scanned": [],
            "multilingual": [],
        }

    def has_images(self, pdf_path: str) -> bool:
        try:
            with open(pdf_path, "rb") as file:
                reader = pypdf.PdfReader(file)
                for page in reader.pages:
                    if "/XObject" in page["/Resources"]:
                        for obj in page["/Resources"]["/XObject"].values():
                            if obj["/Subtype"] == "/Image":
                                return True
            return False
        except Exception as e:
            logger.error(f"Error checking for images in {pdf_path}: {str(e)}")
            return False

    def is_scanned(self, pdf_path: str) -> bool:
        try:
            with open(pdf_path, "rb") as file:
                reader = pypdf.PdfReader(file)
                # Check first page for text
                text = reader.pages[0].extract_text().strip()
                # If no text but has images, likely scanned
                return not text and self.has_images(pdf_path)
        except Exception as e:
            logger.error(f"Error checking if scanned for {pdf_path}: {str(e)}")
            return False

    def has_tables(self, pdf_path: str) -> bool:
        try:
            with open(pdf_path, "rb") as file:
                reader = pypdf.PdfReader(file)
                text = reader.pages[0].extract_text()
                # Basic heuristic: Look for patterns that might indicate tables
                return bool(
                    text.count("|") > 5
                    or text.count("\t") > 5
                    or (
                        text.count("  ") > 10
                        and any(line.count("  ") > 3 for line in text.split("\n"))
                    )
                )
        except Exception as e:
            logger.error(f"Error checking for tables in {pdf_path}: {str(e)}")
            return False

    def is_technical(self, pdf_path: str) -> bool:
        try:
            with open(pdf_path, "rb") as file:
                reader = pypdf.PdfReader(file)
                text = reader.pages[0].extract_text()
                # Check for mathematical symbols and patterns
                technical_indicators = [
                    "∑",
                    "∫",
                    "≠",
                    "±",
                    "∞",
                    "≤",
                    "≥",  # Math symbols
                    "theorem",
                    "proof",
                    "equation",  # Math terms
                    "def ",
                    "class ",
                    "function",  # Code indicators
                    "algorithm",
                    "complexity",  # CS terms
                ]
                return any(
                    indicator in text.lower() for indicator in technical_indicators
                )
        except Exception as e:
            logger.error(f"Error checking if technical for {pdf_path}: {str(e)}")
            return False

    def analyze_pdf(self, pdf_path: str) -> str:
        try:
            if self.is_scanned(pdf_path):
                return "scanned"
            elif self.is_technical(pdf_path):
                return "technical"
            elif self.has_tables(pdf_path):
                return "tables"
            elif self.has_images(pdf_path):
                return "images"
            else:
                return "simple"
        except Exception as e:
            logger.error(f"Error analyzing {pdf_path}: {str(e)}")
            return "simple"  # Default to simple if analysis fails

    def categorize_pdfs(self, source_dir: str) -> Dict[str, List[str]]:
        source_path = Path(source_dir)
        for pdf_file in source_path.glob("*.pdf"):
            try:
                category = self.analyze_pdf(str(pdf_file))
                self.categories[category].append(str(pdf_file))
                logger.info(f"Categorized {pdf_file.name} as {category}")
            except Exception as e:
                logger.error(f"Error processing {pdf_file}: {str(e)}")

        return self.categories


def main():
    if len(sys.argv) != 2:
        print("Usage: python categorize_pdfs.py <pdf_directory>")
        sys.exit(1)

    pdf_dir = sys.argv[1]
    analyzer = PDFAnalyzer()

    logger.info(f"Analyzing PDFs in {pdf_dir}")
    categories = analyzer.categorize_pdfs(pdf_dir)

    # Save results
    output_file = "pdf_categories.json"
    with open(output_file, "w") as f:
        json.dump(categories, f, indent=2)

    logger.info(f"Results saved to {output_file}")

    # Print summary
    print("\nPDF Categorization Summary:")
    for category, files in categories.items():
        print(f"{category}: {len(files)} files")


if __name__ == "__main__":
    main()
