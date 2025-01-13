#!/usr/bin/env python3
"""Test script for PDF processing capabilities."""

import os
import logging
import argparse
from pathlib import Path
from typing import List, Dict
import json
from datetime import datetime
import random

from rag_retriever.document_processor.local_loader import LocalDocumentLoader
from rag_retriever.utils.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def analyze_pdf(file_path: str, loader: LocalDocumentLoader) -> Dict:
    """Analyze a single PDF file and return metrics.

    Args:
        file_path: Path to the PDF file
        loader: Document loader instance

    Returns:
        Dictionary containing analysis metrics
    """
    path = Path(file_path)
    file_size = path.stat().st_size / (1024 * 1024)  # Size in MB

    try:
        start_time = datetime.now()
        documents = loader.load_file(str(path))
        processing_time = (datetime.now() - start_time).total_seconds()

        # Analyze extracted content
        total_chars = sum(len(doc.page_content) for doc in documents)
        total_pages = len(documents)
        has_images = any(doc.metadata.get("type") == "image" for doc in documents)
        ocr_pages = sum(1 for doc in documents if doc.metadata.get("has_ocr", False))

        return {
            "file_name": path.name,
            "category": path.parent.name,
            "file_size_mb": round(file_size, 2),
            "status": "success",
            "processing_time_seconds": round(processing_time, 2),
            "total_pages": total_pages,
            "total_chars": total_chars,
            "chars_per_page": round(
                total_chars / total_pages if total_pages > 0 else 0, 2
            ),
            "has_images": has_images,
            "ocr_pages": ocr_pages,
        }
    except Exception as e:
        return {
            "file_name": path.name,
            "category": path.parent.name,
            "file_size_mb": round(file_size, 2),
            "status": "error",
            "error": str(e),
        }


def get_sample_pdfs(pdf_dir: str, samples_per_category: int = 2) -> List[str]:
    """Get a sample of PDFs from each category directory.

    Args:
        pdf_dir: Base directory containing category subdirectories
        samples_per_category: Number of PDFs to sample from each category

    Returns:
        List of PDF file paths
    """
    sample_paths = []
    base_dir = Path(pdf_dir)

    # Get all category directories
    categories = [d for d in base_dir.iterdir() if d.is_dir()]

    for category in categories:
        # Get all PDFs in this category
        pdfs = list(category.glob("*.pdf"))
        if pdfs:
            # Take a random sample, but no more than available
            sample_size = min(samples_per_category, len(pdfs))
            category_samples = random.sample(pdfs, sample_size)
            sample_paths.extend(str(p) for p in category_samples)

    return sample_paths


def test_pdf_processing(pdf_dir: str, output_file: str, samples_per_category: int = 2):
    """Test PDF processing on a sample of files from each category.

    Args:
        pdf_dir: Directory containing categorized test PDFs
        output_file: Path to save test results
        samples_per_category: Number of PDFs to test from each category
    """
    # Initialize loader with config
    config = Config()
    loader = LocalDocumentLoader(config._config)

    # Get sample PDFs
    pdf_paths = get_sample_pdfs(pdf_dir, samples_per_category)
    if not pdf_paths:
        logger.error(f"No PDF files found in {pdf_dir}")
        return

    logger.info(
        f"Testing {len(pdf_paths)} PDFs ({samples_per_category} from each category)"
    )

    # Process each PDF
    results = []
    for pdf_path in pdf_paths:
        logger.info(f"Processing {pdf_path}")
        result = analyze_pdf(pdf_path, loader)
        results.append(result)

    # Separate successful and failed results
    successful = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "error"]

    # Group results by category
    by_category = {}
    for result in results:
        category = result["category"]
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(result)

    summary = {
        "total_files": len(results),
        "successful": len(successful),
        "failed": len(failed),
        "total_pages_processed": sum(r["total_pages"] for r in successful),
        "total_processing_time": sum(r["processing_time_seconds"] for r in successful),
        "files_with_ocr": sum(1 for r in successful if r["ocr_pages"] > 0),
        "files_with_images": sum(1 for r in successful if r["has_images"]),
        "by_category": {
            category: {
                "total": len(results),
                "successful": len([r for r in results if r["status"] == "success"]),
                "failed": len([r for r in results if r["status"] == "error"]),
            }
            for category, results in by_category.items()
        },
        "results": results,
    }

    # Save results
    with open(output_file, "w") as f:
        json.dump(summary, f, indent=2)

    logger.info(f"\nTest Summary:")
    logger.info(f"Total Files: {summary['total_files']}")
    logger.info(f"Successful: {summary['successful']}")
    logger.info(f"Failed: {summary['failed']}")
    logger.info(f"Total Pages: {summary['total_pages_processed']}")
    logger.info(f"Files with OCR: {summary['files_with_ocr']}")
    logger.info(f"Files with Images: {summary['files_with_images']}")

    logger.info("\nResults by Category:")
    for category, stats in summary["by_category"].items():
        logger.info(f"{category}: {stats['successful']}/{stats['total']} successful")

    logger.info(f"\nDetailed results saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Test PDF processing capabilities")
    parser.add_argument("pdf_dir", help="Directory containing test PDFs")
    parser.add_argument(
        "--samples",
        type=int,
        default=2,
        help="Number of PDFs to test from each category (default: 2)",
    )
    parser.add_argument(
        "--output",
        default="pdf_test_results.json",
        help="Output file for test results (default: pdf_test_results.json)",
    )
    args = parser.parse_args()

    test_pdf_processing(args.pdf_dir, args.output, args.samples)


if __name__ == "__main__":
    main()
