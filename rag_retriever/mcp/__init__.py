"""MCP server package"""

import logging
import sys
import asyncio
from .server import app, server

__all__ = ["server", "main"]

logger = logging.getLogger(__name__)


def main() -> int:
    """Entry point for the MCP stdio server."""
    try:
        # Run the stdio server
        asyncio.run(server.run_stdio_async())
        return 0
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}", exc_info=True)
        return 1
