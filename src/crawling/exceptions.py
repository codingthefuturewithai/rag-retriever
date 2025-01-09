"""Exceptions for the crawling module."""


class CrawlerError(Exception):
    """Base exception for crawler-related errors."""

    pass


class PageLoadError(CrawlerError):
    """Raised when a page cannot be loaded."""

    pass


class ContentExtractionError(CrawlerError):
    """Raised when content cannot be extracted from a page."""

    pass
