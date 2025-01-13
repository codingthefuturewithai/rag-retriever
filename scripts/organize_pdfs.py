#!/usr/bin/env python3

import os
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_symlinks(categories_file: str, test_dir: str):
    # Load the categorization results
    with open(categories_file) as f:
        categories = json.load(f)

    # Create test directories if they don't exist
    test_path = Path(test_dir)
    for category in categories.keys():
        category_dir = test_path / category
        category_dir.mkdir(exist_ok=True)

    # Create symlinks for each file
    for category, files in categories.items():
        category_dir = test_path / category
        for i, file_path in enumerate(files):
            source = Path(file_path)
            if not source.exists():
                logger.warning(f"Source file not found: {file_path}")
                continue

            # Create symlink with a simple numbered name
            target = category_dir / f"{category}_{i+1:03d}.pdf"
            if target.exists():
                target.unlink()
            try:
                target.symlink_to(source)
                logger.info(f"Created symlink: {target} -> {source}")
            except Exception as e:
                logger.error(f"Error creating symlink for {file_path}: {str(e)}")


def main():
    categories_file = "pdf_categories.json"
    test_dir = "test_pdfs"

    if not os.path.exists(categories_file):
        logger.error(f"Categories file not found: {categories_file}")
        return

    create_symlinks(categories_file, test_dir)
    logger.info("PDF organization complete")


if __name__ == "__main__":
    main()
