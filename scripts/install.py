"""Installation utilities for RAG Retriever."""

import subprocess
import sys
import logging
import platform
import os
import site
import pkg_resources

logger = logging.getLogger(__name__)


def get_pipx_python():
    """Get the Python executable path for the current environment."""
    if "VIRTUAL_ENV" in os.environ:
        # If we're in a virtual environment (including pipx)
        if platform.system().lower() == "windows":
            return os.path.join(os.environ["VIRTUAL_ENV"], "Scripts", "python.exe")
        return os.path.join(os.environ["VIRTUAL_ENV"], "bin", "python")
    return sys.executable


def install_package(package_name: str):
    """Install a Python package using pip."""
    python_exe = get_pipx_python()
    try:
        logger.info(f"Installing {package_name} using {python_exe}")
        subprocess.run(
            [python_exe, "-m", "pip", "install", package_name],
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info(f"Successfully installed {package_name}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install {package_name}: {e.stderr}")
        raise


def is_package_installed(package_name: str) -> bool:
    """Check if a Python package is installed."""
    try:
        pkg_resources.get_distribution(package_name)
        return True
    except pkg_resources.DistributionNotFound:
        return False


def install_browsers():
    """Install required browsers for Playwright."""
    python_exe = get_pipx_python()
    try:
        # First ensure playwright is installed
        if not is_package_installed("playwright"):
            logger.info("Installing playwright package...")
            install_package("playwright")

        logger.info(f"Installing Playwright browsers using {python_exe}...")
        # First try installing chromium
        result = subprocess.run(
            [python_exe, "-m", "playwright", "install", "chromium"],
            check=True,
            capture_output=True,
            text=True,
        )
        logger.debug(f"Chromium installation output: {result.stdout}")

        # On Windows, also try installing Chrome if chromium fails
        if platform.system().lower() == "windows":
            try:
                chrome_result = subprocess.run(
                    [python_exe, "-m", "playwright", "install", "chrome"],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                logger.debug(f"Chrome installation output: {chrome_result.stdout}")
            except subprocess.CalledProcessError:
                logger.warning(
                    "Could not install Chrome, but Chromium is available as fallback"
                )

        logger.info("Successfully installed Playwright browsers")

    except subprocess.CalledProcessError as e:
        if platform.system().lower() == "windows":
            logger.error(
                "Failed to install Playwright browsers. On Windows, please run:\n"
                f"1. {python_exe} -m playwright install chromium\n"
                "If that doesn't work, try:\n"
                "2. playwright install chromium"
            )
        else:
            logger.error(
                f"Failed to install Playwright browsers: {str(e)}\n"
                f"Please run: {python_exe} -m playwright install chromium"
            )
        # Don't fail the installation, just warn the user

    except Exception as e:
        logger.error(f"Unexpected error installing browsers: {str(e)}")
        if platform.system().lower() == "windows":
            logger.info(
                "Please try running these commands manually:\n"
                f"1. {python_exe} -m playwright install chromium\n"
                "If that doesn't work:\n"
                "2. playwright install chromium"
            )
        else:
            logger.info(
                f"Please run '{python_exe} -m playwright install chromium' manually"
            )
        # Don't fail the installation, just warn the user
