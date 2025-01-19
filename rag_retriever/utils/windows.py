"""Windows-specific utilities."""

import sys
import warnings
import asyncio
import platform
import functools


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


def windows_event_loop(func):
    """Decorator to handle Windows event loop properly."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if platform.system().lower() == "windows":
            try:
                loop = asyncio.get_event_loop()
                if not isinstance(loop, asyncio.ProactorEventLoop):
                    loop = asyncio.ProactorEventLoop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.ProactorEventLoop()
                asyncio.set_event_loop(loop)

            try:
                return func(*args, **kwargs)
            finally:
                try:
                    # Cancel all pending tasks
                    pending = asyncio.all_tasks(loop)
                    for task in pending:
                        task.cancel()
                    if not loop.is_closed():
                        # Run the loop to complete all cancellations
                        loop.run_until_complete(
                            asyncio.gather(*pending, return_exceptions=True)
                        )
                        # Clean up async generators
                        loop.run_until_complete(loop.shutdown_asyncgens())
                        loop.close()
                except Exception:
                    pass  # Ignore cleanup errors
        else:
            return func(*args, **kwargs)

    return wrapper
