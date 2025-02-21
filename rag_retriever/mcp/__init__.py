"""MCP server package"""

import logging
import sys
from .server import app, server

__all__ = ["server"]

logger = logging.getLogger(__name__)
