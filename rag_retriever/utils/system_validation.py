"""System-level dependency validation for RAG Retriever."""

import subprocess
import shutil
import logging
from typing import List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class SystemValidationError(Exception):
    """Raised when system dependencies are missing."""
    pass


def check_playwright_browsers() -> bool:
    """Check if Playwright browsers are installed."""
    try:
        # Check if playwright can be imported
        import playwright
        
        # Try to get a browser - this will fail if browsers aren't installed
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            # Just check if we can access a browser type
            browser_type = p.chromium
            return True
            
    except ImportError:
        return False
    except Exception:
        # Browser likely not installed
        return False


def check_git_available() -> bool:
    """Check if git is available for GitHub repository cloning."""
    return shutil.which("git") is not None


def check_tesseract_available() -> bool:
    """Check if Tesseract OCR is available for image processing."""
    return shutil.which("tesseract") is not None


def check_crawler_availability() -> Dict[str, bool]:
    """Check which crawlers are available."""
    availability = {
        "playwright": False,
        "crawl4ai": False
    }
    
    # Check Playwright (system-level browser dependency)
    availability["playwright"] = check_playwright_browsers()
    
    # Check Crawl4AI (Python library dependency)
    try:
        import crawl4ai
        availability["crawl4ai"] = True
    except ImportError:
        availability["crawl4ai"] = False
    
    return availability


def validate_system_dependencies() -> None:
    """
    Validate all system-level dependencies and raise detailed error if any are missing.
    
    Raises:
        SystemValidationError: If critical dependencies are missing
    """
    issues = []
    warnings = []
    
    # Check crawlers - at least one must work
    crawler_status = check_crawler_availability()
    working_crawlers = [name for name, available in crawler_status.items() if available]
    
    if not working_crawlers:
        issues.append(
            "No working web crawlers available:\n"
            "  - Playwright: Requires 'playwright install chromium'\n"
            "  - Crawl4AI: Requires 'pip install crawl4ai>=0.4.0'"
        )
    elif len(working_crawlers) == 1:
        available = working_crawlers[0]
        unavailable = [name for name, available in crawler_status.items() if not available][0]
        warnings.append(f"Only {available} crawler available. {unavailable} is not installed.")
    
    # Check Git (optional but recommended for GitHub integration)
    if not check_git_available():
        warnings.append(
            "Git not found. GitHub repository processing will not work.\n"
            "  Install: https://git-scm.com/downloads"
        )
    
    # Check Tesseract (optional for image OCR)
    if not check_tesseract_available():
        warnings.append(
            "Tesseract OCR not found. Image text extraction will be limited.\n"
            "  Install: https://github.com/tesseract-ocr/tesseract#installation"
        )
    
    # Log warnings
    for warning in warnings:
        logger.warning(warning)
    
    # Raise error for critical issues
    if issues:
        error_msg = "Critical system dependencies missing:\n\n" + "\n\n".join(issues)
        error_msg += "\n\nPlease install the missing dependencies and try again."
        raise SystemValidationError(error_msg)
    
    # Log success
    logger.info(f"System validation passed. Available crawlers: {', '.join(working_crawlers)}")


def get_system_status() -> Dict[str, Any]:
    """Get detailed system dependency status for diagnostics."""
    return {
        "crawlers": check_crawler_availability(),
        "git": check_git_available(),
        "tesseract": check_tesseract_available(),
        "playwright_browsers": check_playwright_browsers()
    }