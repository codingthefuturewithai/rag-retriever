"""Windows-specific utilities."""

import sys
import warnings
import asyncio
import platform


def suppress_asyncio_warnings():
    """Suppress asyncio-related warnings on Windows."""
    if platform.system().lower() == "windows":
        # Handle Python 3.12+ asyncio changes
        if sys.version_info >= (3, 12):
            # Use ProactorEventLoop as the default event loop
            loop = asyncio.ProactorEventLoop()
            asyncio.set_event_loop(loop)
        elif sys.version_info >= (3, 8):
            # For Python 3.8-3.11, use WindowsSelectorEventLoopPolicy
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        warnings.filterwarnings(
            "ignore", message=".*unclosed.*", category=ResourceWarning
        )
        warnings.filterwarnings(
            "ignore", message=".*socket.*closed.*", category=RuntimeWarning
        )
