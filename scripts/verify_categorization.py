#!/usr/bin/env python3

import sys
from pathlib import Path
from categorize_pdfs import PDFAnalyzer


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
        "images": "test_pdfs/images/images_001.pdf",
        "tables": "test_pdfs/tables/tables_001.pdf",
        "technical": "test_pdfs/technical/technical_001.pdf",
        "scanned": "test_pdfs/scanned/scanned_001.pdf",
    }

    results = []
    for category, path in samples.items():
        if Path(path).exists():
            result = verify_sample(path, category)
            results.append((category, result))
        else:
            print(f"\nError: Sample file not found: {path}")

    print("\nVerification Summary:")
    for category, result in results:
        status = "✓" if result else "✗"
        print(f"{category}: {status}")


if __name__ == "__main__":
    main()
