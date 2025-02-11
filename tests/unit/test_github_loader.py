"""Unit tests for the GitHub loader module."""

import pytest
from pathlib import Path
from unittest.mock import patch

from rag_retriever.document_processor.github_loader import GitHubLoader


@pytest.fixture
def config():
    """Test configuration fixture."""
    return {
        "github_settings": {
            "supported_extensions": [".py", ".md"],
            "excluded_patterns": ["node_modules/**", "__pycache__/**"],
            "max_file_size_mb": 10,
            "default_branch": "main",
        }
    }


@pytest.fixture
def default_config():
    """Empty config to test defaults."""
    return {}


@pytest.fixture
def github_loader(config):
    """GitHub loader fixture with test config."""
    return GitHubLoader(config)


@pytest.fixture
def default_loader(default_config):
    """GitHub loader fixture with default config."""
    return GitHubLoader(default_config)


def test_init_with_config(github_loader):
    """Test GitHubLoader initialization with provided config."""
    assert set(github_loader.supported_extensions) == {".py", ".md"}
    assert github_loader.max_file_size == 10 * 1024 * 1024  # 10MB in bytes
    assert github_loader.default_branch == "main"
    assert "node_modules/**" in github_loader.excluded_patterns
    assert "__pycache__/**" in github_loader.excluded_patterns


def test_init_with_defaults(default_loader):
    """Test GitHubLoader initialization with default values."""
    # Check that default extensions include common programming languages
    assert ".py" in default_loader.supported_extensions
    assert ".js" in default_loader.supported_extensions
    assert ".md" in default_loader.supported_extensions

    # Check default excluded patterns
    assert "node_modules/**" in default_loader.excluded_patterns
    assert "__pycache__/**" in default_loader.excluded_patterns
    assert ".git/**" in default_loader.excluded_patterns

    # Check default file size and branch
    assert default_loader.max_file_size == 10 * 1024 * 1024  # Default 10MB
    assert default_loader.default_branch == "main"


@patch("pathlib.Path.stat")
@patch("pathlib.Path.match")
def test_file_filter_valid_file(mock_match, mock_stat, github_loader):
    """Test that valid files pass the filter."""
    # Setup mocks
    mock_match.return_value = False  # File doesn't match any excluded pattern
    mock_stat.return_value.st_size = 1024  # 1KB file

    # Test a valid Python file
    path = Path("test.py")
    assert path.suffix in github_loader.supported_extensions
    assert mock_stat.return_value.st_size <= github_loader.max_file_size
    assert not any(path.match(pattern) for pattern in github_loader.excluded_patterns)


@patch("pathlib.Path.stat")
@patch("pathlib.Path.match")
def test_file_filter_excluded_pattern(mock_match, mock_stat, github_loader):
    """Test that files matching excluded patterns are filtered out."""
    # Setup mocks
    mock_match.side_effect = lambda pattern: pattern == "node_modules/**"
    mock_stat.return_value.st_size = 1024  # 1KB file

    # Test a file in node_modules
    path = Path("node_modules/package.json")
    assert any(path.match(pattern) for pattern in github_loader.excluded_patterns)


@patch("pathlib.Path.stat")
@patch("pathlib.Path.match")
def test_file_filter_size_limit(mock_match, mock_stat, github_loader):
    """Test that files exceeding size limit are filtered out."""
    # Setup mocks
    mock_match.return_value = False
    mock_stat.return_value.st_size = 20 * 1024 * 1024  # 20MB file

    # Test a large file
    path = Path("large_file.py")
    assert mock_stat.return_value.st_size > github_loader.max_file_size


@patch("pathlib.Path.stat")
@patch("pathlib.Path.match")
def test_file_filter_unsupported_extension(mock_match, mock_stat, github_loader):
    """Test that files with unsupported extensions are filtered out."""
    # Setup mocks
    mock_match.return_value = False
    mock_stat.return_value.st_size = 1024  # 1KB file

    # Test file with unsupported extension
    path = Path("test.xyz")
    assert path.suffix not in github_loader.supported_extensions
