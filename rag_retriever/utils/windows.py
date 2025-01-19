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

        # Suppress all ResourceWarnings about unclosed resources
        warnings.filterwarnings(
            "ignore",
            category=ResourceWarning,
        )
        # Suppress RuntimeWarnings about sockets
        warnings.filterwarnings(
            "ignore",
            category=RuntimeWarning,
        )

        # Patch the warning display for asyncio
        def custom_showwarning(
            message, category, filename, lineno, file=None, line=None
        ):
            # Skip warnings about pipes, transports, and unclosed resources
            if isinstance(message, Warning) and any(
                x in str(message).lower() for x in ["pipe", "transport", "unclosed"]
            ):
                return
            original_showwarning(message, category, filename, lineno, file, line)

        original_showwarning = warnings.showwarning
        warnings.showwarning = custom_showwarning
