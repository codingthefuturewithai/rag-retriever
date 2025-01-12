"""Installation utilities for RAG Retriever."""

import subprocess
import sys
import logging

logger = logging.getLogger(__name__)


def install_browsers():
    """Install required browsers for Playwright."""
    try:
        logger.info("Installing Playwright browsers...")
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"], check=True
        )
        logger.info("Successfully installed Playwright browsers")
    except subprocess.CalledProcessError as e:
        logger.error("Failed to install Playwright browsers: %s", str(e))
        logger.info("Please run 'playwright install chromium' manually")
    except Exception as e:
        logger.error("Unexpected error installing browsers: %s", str(e))
        logger.info("Please run 'playwright install chromium' manually")
