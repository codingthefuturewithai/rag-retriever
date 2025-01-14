# PDF Processing Tests

This guide covers testing the RAG Retriever's PDF processing capabilities, including text extraction, image processing, OCR, and information retrieval from various types of PDFs.

## Quick Start: Running PDF Tests

To verify PDF processing functionality using our test suite:

1. Run the PDF regression tests:

   ```bash
   ./tests/scripts/run_regression_tests.py
   ```

   This script:

   - Creates a temporary test vector store
   - For each test case:
     - Ingests a test PDF
     - Runs queries to verify text extraction and retrieval
     - Validates the results
   - Generates a detailed test report

2. View the results in `tests/results/regression_test_report_[timestamp].txt`

Note: You can also manually ingest and test individual PDFs using:

```bash
./tests/scripts/ingest_samples.sh    # Ingests our curated set of test PDFs
./scripts/run-rag.sh --query "your query"  # Run queries against ingested PDFs
```

## Test PDF Organization

The project includes a minimal set of test PDFs (~1.8MB) in the `tests/data/pdfs/` directory, organized by processing requirements:

- `images/`: PDFs with images requiring extraction and OCR
- `tables/`: PDFs with tables requiring structured data extraction
- `technical/`: PDFs with technical content (math, code, diagrams) requiring special processing
- `scanned/`: Scanned documents requiring full-page OCR

These files verify different aspects of our PDF processing pipeline.

## Extended PDF Test Corpus

A larger corpus of pre-categorized PDFs (~1.3GB) is available for comprehensive testing of PDF processing capabilities. This archive contains PDFs organized by processing requirements (images, tables, technical, scanned):

**Download**: [DOWNLOAD_LOCATION_PLACEHOLDER]

### Setting up the Extended Test Corpus

1. Download `pdf_corpus.tar.gz`
2. Extract to a location outside the project:
   ```bash
   tar -xzf pdf_corpus.tar.gz -C /path/to/extract
   ```
   This will create a `test_pdfs` directory containing categorized PDFs with symbolic links to the original files.

### PDF Categorization Tools

If you have new PDFs to analyze for testing:

1. **Analyze PDF Features**:

   ```bash
   ./tests/scripts/categorize_pdfs.py /path/to/pdfs
   ```

   This analyzes PDFs for features like images, tables, and technical content, generating `pdf_categories.json`.

2. **Organize by Processing Type**:
   ```bash
   ./tests/scripts/organize_pdfs.py
   ```
   This creates symbolic links organizing PDFs by their processing requirements.

### Adding New PDF Test Cases

When selecting new PDFs for processing tests:

1. Choose PDFs that:

   - Are relatively small (< 1MB if possible)
   - Exercise specific PDF processing features
   - Produce consistent extraction results
   - Cover different processing challenges (OCR, tables, etc.)

2. Update test configuration:

   ```bash
   tests/data/regression_tests.json
   ```

   Add test cases with queries that verify proper text extraction and processing.

3. Run regression tests to verify:
   ```bash
   ./tests/scripts/run_regression_tests.py
   ```

## Test Results

PDF processing test results are stored in:

```
tests/results/
├── regression_test_report_[timestamp].txt  # Detailed processing results
└── test_vector_store/                      # Temporary store for processed PDFs
```
