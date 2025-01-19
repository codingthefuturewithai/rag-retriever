"""Windows-specific utilities."""

import sys
import warnings
import asyncio
import platform
import functools
import logging


def custom_unraisable_hook(unraisable):
    """Custom hook to handle unraisable exceptions during shutdown."""
    # Suppress ResourceWarnings and ValueError from closed pipes
    if (
        isinstance(unraisable.exc_value, (ResourceWarning, ValueError))
        and "closed pipe" in str(unraisable.exc_value).lower()
    ):
        return
    # For other exceptions, call the default handler
    sys.__unraisablehook__(unraisable)


def suppress_asyncio_warnings():
    """Suppress asyncio-related warnings on Windows."""
    if platform.system().lower() == "windows":
        # Set up custom hook for handling shutdown warnings
        sys.unraisablehook = custom_unraisable_hook
        # Suppress all ResourceWarnings from asyncio
        warnings.filterwarnings("ignore", category=ResourceWarning, module="asyncio")
    else:
        # Suppress ResourceWarnings on non-Windows platforms
        warnings.filterwarnings("ignore", category=ResourceWarning)
        warnings.filterwarnings(
            "ignore",
            category=DeprecationWarning,
            message="There is no current event loop",
        )

    # Suppress BeautifulSoup LXML builder deprecation warning
    warnings.filterwarnings(
        "ignore", category=DeprecationWarning, module="bs4.builder._lxml"
    )

    # Set asyncio logger to WARNING by default
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def windows_event_loop(func):
    """Decorator to handle Windows event loop properly."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Always create a new event loop to avoid deprecation warning
        if platform.system().lower() == "windows":
            loop = asyncio.ProactorEventLoop()
        else:
            loop = asyncio.new_event_loop()

        asyncio.set_event_loop(loop)

        # Only enable debug mode if logging is set to DEBUG
        loop.set_debug(logging.getLogger().getEffectiveLevel() <= logging.DEBUG)

        try:
            return func(*args, **kwargs)
        finally:
            try:
                # Get all running tasks
                pending = asyncio.all_tasks(loop)

                # Cancel pending tasks
                for task in pending:
                    task.cancel()

                if not loop.is_closed():
                    # Wait for tasks to cancel
                    loop.run_until_complete(
                        asyncio.gather(*pending, return_exceptions=True)
                    )

                    # Clean up async generators
                    loop.run_until_complete(loop.shutdown_asyncgens())

                    # On Windows, wait for subprocesses to complete
                    if platform.system().lower() == "windows":
                        loop.run_until_complete(
                            asyncio.sleep(0.1)
                        )  # Brief delay for subprocess cleanup

                    # Ensure all transports are closed
                    for task in pending:
                        if hasattr(task, "transport") and task.transport:
                            task.transport.close()

                    # Close the loop
                    loop.close()
            except Exception:
                pass  # Ignore cleanup errors

    return wrapper
