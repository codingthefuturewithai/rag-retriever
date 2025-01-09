#!/usr/bin/env python3
"""Entry point script for the RAG retriever application."""

import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

from src.main import main

if __name__ == "__main__":
    sys.exit(main())
