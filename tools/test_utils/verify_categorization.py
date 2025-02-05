#!/usr/bin/env python3

import sys
from pathlib import Path
from categorize_pdfs import PDFAnalyzer

# Get the directory where the script is located
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
TEST_DATA_DIR = PROJECT_ROOT / "tests" / "data" / "pdfs"


def verify_sample(pdf_path: str, expected_category: str) -> bool:
    analyzer = PDFAnalyzer()
    actual_category = analyzer.analyze_pdf(pdf_path)
    print(f"\nVerifying {pdf_path}")
    print(f"Expected category: {expected_category}")
    print(f"Actual category: {actual_category}")

    # Additional checks based on category
    if expected_category == "images":
        has_images = analyzer.has_images(pdf_path)
        print(f"Has images: {has_images}")
    elif expected_category == "tables":
        has_tables = analyzer.has_tables(pdf_path)
        print(f"Has tables: {has_tables}")
    elif expected_category == "technical":
        is_technical = analyzer.is_technical(pdf_path)
        print(f"Is technical: {is_technical}")
    elif expected_category == "scanned":
        is_scanned = analyzer.is_scanned(pdf_path)
        print(f"Is scanned: {is_scanned}")

    return actual_category == expected_category


def main():
    samples = {
        "images": TEST_DATA_DIR / "images" / "images_001.pdf",
        "tables": TEST_DATA_DIR / "tables" / "tables_093.pdf",
        "technical": TEST_DATA_DIR / "technical" / "technical_040.pdf",
        "scanned": TEST_DATA_DIR / "scanned" / "scanned_015.pdf",
    }

    results = []
    for category, path in samples.items():
        if path.exists():
            result = verify_sample(str(path), category)
            results.append((category, result))
        else:
            print(f"\nError: Sample file not found: {path}")

    print("\nVerification Summary:")
    for category, result in results:
        status = "✓" if result else "✗"
        print(f"{category}: {status}")


if __name__ == "__main__":
    main()
