#!/usr/bin/env python3

import json
import subprocess
import sys
import time
from pathlib import Path
import logging
import re
from datetime import datetime
import shutil
import os

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Get the directory where the script is located
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
TESTS_DIR = PROJECT_ROOT / "tests"


def run_command(command):
    """Run a shell command and return the output"""
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with exit code {e.returncode}")
        logger.error(f"Error output: {e.stderr}")
        raise


def setup_test_vector_store():
    """Create and get path to test vector store"""
    test_vector_store = (TESTS_DIR / "results/test_vector_store").absolute()
    if test_vector_store.exists():
        shutil.rmtree(test_vector_store)
    test_vector_store.mkdir(parents=True, exist_ok=True)
    return test_vector_store


def clear_vector_store(vector_store_path):
    """Clear the vector store at the specified path"""
    logger.info(f"Clearing vector store at {vector_store_path}...")
    if vector_store_path.exists():
        shutil.rmtree(vector_store_path)
        vector_store_path.mkdir(parents=True)


def validate_response(response, expected_keywords):
    """
    Validate the response contains expected keywords and meets quality criteria
    Returns (is_valid, details) tuple
    """
    if "No results found" in response or "Error" in response:
        return False, "No results found or error in response"

    # Convert response to lowercase for case-insensitive matching
    response_lower = response.lower()

    # Check for expected keywords (case-insensitive)
    missing_keywords = []
    found_keywords = []
    for keyword in expected_keywords:
        if keyword.lower() in response_lower:
            found_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)

    # Calculate keyword coverage
    coverage = len(found_keywords) / len(expected_keywords) if expected_keywords else 0

    # Require at least 50% of keywords to be present
    if coverage < 0.5:
        return (
            False,
            f"Response missing too many expected keywords. Found: {found_keywords}, Missing: {missing_keywords}",
        )

    # Check response length (should be at least 20 words)
    word_count = len(response.split())
    if word_count < 20:
        return False, f"Response too short ({word_count} words)"

    return True, f"Response valid. Found keywords: {found_keywords}"


def run_regression_tests():
    """Run regression tests for PDF processing."""
    # Set up results directory and test vector store
    results_dir = TESTS_DIR / "results"
    results_dir.mkdir(exist_ok=True)

    test_vector_store = setup_test_vector_store()

    # Create timestamped report file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = results_dir / f"regression_test_report_{timestamp}.txt"

    # Set up file handler for logging
    file_handler = logging.FileHandler(report_file)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(file_handler)

    try:
        # Set environment variable for test vector store
        os.environ["VECTOR_STORE_PATH"] = str(test_vector_store)
        logger.info(f"Using test vector store at: {test_vector_store}")

        # Load test cases
        test_data_dir = TESTS_DIR / "data"
        with open(test_data_dir / "regression_tests.json") as f:
            test_config = json.load(f)

        test_cases = test_config["test_cases"]
        total_tests = len(test_cases)
        passed_tests = 0
        failed_tests = []

        for test_case in test_cases:
            # Construct full PDF path using category
            pdf_name = test_case["file"]
            category = test_case["category"]
            pdf_path = test_data_dir / "pdfs" / category / pdf_name

            logger.info(f"Testing {category} PDF: {pdf_name}")
            logger.info(f"Full path: {pdf_path}")

            if not pdf_path.exists():
                logger.error(f"PDF file not found: {pdf_path}")
                failed_tests.append(
                    {
                        "file": pdf_name,
                        "error": "File not found",
                        "category": category,
                        "response": "File not found",
                    }
                )
                continue

            query = test_case["query"]
            expected_keywords = test_case["expected_keywords"]

            try:
                # Clear vector store before each test
                clear_vector_store(test_vector_store)

                # Ingest the PDF
                logger.info(f"\nTesting {category} PDF: {pdf_name}")
                logger.info("Ingesting PDF...")
                ingest_cmd = f'VECTOR_STORE_PATH="{test_vector_store}" {PROJECT_ROOT}/scripts/run-rag.sh --ingest-file "{pdf_path}"'
                ingest_output = run_command(ingest_cmd)
                logger.debug(f"Ingest output: {ingest_output}")

                # Run the query
                logger.info(f"Running query: {query}")
                query_cmd = f'VECTOR_STORE_PATH="{test_vector_store}" {PROJECT_ROOT}/scripts/run-rag.sh --query "{query}"'
                result = run_command(query_cmd)
                logger.debug(f"Query response: {result}")

                # Validate the response
                is_valid, details = validate_response(result, expected_keywords)

                if is_valid:
                    logger.info(f"Test passed! {details}")
                    passed_tests += 1
                else:
                    logger.error(f"Test failed: {details}")
                    failed_tests.append(
                        {
                            "file": test_case["file"],
                            "error": details,
                            "category": category,
                            "response": result,
                        }
                    )

            except Exception as e:
                logger.error(f"Test failed for {test_case['file']}: {str(e)}")
                failed_tests.append(
                    {
                        "file": test_case["file"],
                        "error": str(e),
                        "category": category,
                        "response": "Exception occurred",
                    }
                )

        # Print summary
        logger.info("\nTest Summary:")
        logger.info(f"Total tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {len(failed_tests)}")

        if failed_tests:
            logger.error("\nFailed Tests:")
            for test in failed_tests:
                logger.error(f"- {test['category']}/{test['file']}: {test['error']}")
                logger.debug(f"  Response: {test['response']}")
            sys.exit(1)
        else:
            logger.info("\nAll tests passed!")
            logger.info(f"Test report saved to: {report_file}")
            sys.exit(0)

    finally:
        # Clean up
        if test_vector_store.exists():
            shutil.rmtree(test_vector_store)
        # Remove file handler
        logger.removeHandler(file_handler)
        file_handler.close()
        # Clear environment variable
        os.environ.pop("VECTOR_STORE_PATH", None)


if __name__ == "__main__":
    run_regression_tests()
