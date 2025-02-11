"""Configuration file for pytest."""

import pytest


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "integration: mark tests that require external services or network access",
    )
