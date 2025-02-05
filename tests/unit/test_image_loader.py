"""Tests for the image loader module."""

import os
import pytest
from pathlib import Path
import tempfile
import shutil
from PIL import Image
import requests
from unittest.mock import patch, MagicMock

from rag_retriever.document_processor import ImageLoader

# Test configuration
TEST_CONFIG = {
    "image_processing": {
        "max_file_size_mb": 10,
        "languages": ["eng"],
        "min_confidence": 60,
        "max_image_size": 4096,
        "min_image_size": 50,
        "denoise_images": True,
        "extract_text": True,
    }
}


@pytest.fixture
def image_loader():
    """Create an ImageLoader instance for testing."""
    return ImageLoader(TEST_CONFIG)


@pytest.fixture
def test_image_path():
    """Create a temporary test image."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        # Create a simple test image
        img = Image.new("RGB", (100, 30), color="white")
        img.save(tmp.name)
        yield tmp.name
        # Cleanup
        os.unlink(tmp.name)


def test_supported_formats(image_loader):
    """Test supported image formats."""
    assert ".png" in image_loader.SUPPORTED_FORMATS
    assert ".jpg" in image_loader.SUPPORTED_FORMATS
    assert ".jpeg" in image_loader.SUPPORTED_FORMATS
    assert ".svg" in image_loader.SUPPORTED_FORMATS
    assert ".webp" in image_loader.SUPPORTED_FORMATS
    assert ".gif" in image_loader.SUPPORTED_FORMATS


def test_validate_image_valid_file(image_loader, test_image_path):
    """Test image validation with a valid file."""
    assert image_loader._validate_image(test_image_path)


def test_validate_image_invalid_format(image_loader):
    """Test image validation with an invalid format."""
    with tempfile.NamedTemporaryFile(suffix=".invalid") as tmp:
        assert not image_loader._validate_image(tmp.name)


def test_validate_image_file_too_large(image_loader, test_image_path):
    """Test image validation with a file that's too large."""
    with patch("os.path.getsize") as mock_size:
        # Mock file size to be 11MB (over the 10MB limit)
        mock_size.return_value = 11 * 1024 * 1024
        assert not image_loader._validate_image(test_image_path)


def test_is_valid_url(image_loader):
    """Test URL validation."""
    assert image_loader._is_valid_url("https://example.com/image.jpg")
    assert image_loader._is_valid_url("http://example.com/image.png")
    assert not image_loader._is_valid_url("not_a_url")
    assert not image_loader._is_valid_url("file:///local/path")


@patch("requests.get")
def test_download_image_success(mock_get, image_loader):
    """Test successful image download."""
    mock_response = MagicMock()
    mock_response.content = b"fake_image_data"
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = image_loader._download_image("https://example.com/image.jpg")
    assert result == b"fake_image_data"
    mock_get.assert_called_once()


@patch("requests.get")
def test_download_image_failure(mock_get, image_loader):
    """Test failed image download."""
    mock_get.side_effect = requests.exceptions.RequestException()
    result = image_loader._download_image("https://example.com/image.jpg")
    assert result is None


def test_load_image_local_file(image_loader, test_image_path):
    """Test loading a local image file."""
    document = image_loader.load_image(test_image_path)
    assert document is not None
    assert document.metadata["source"] == test_image_path
    assert document.metadata["type"] == "image"
    assert document.metadata["extension"] == ".png"


@patch("requests.get")
def test_load_image_from_url(mock_get, image_loader, test_image_path):
    """Test loading an image from a URL."""
    # Mock successful image download
    with open(test_image_path, "rb") as f:
        image_data = f.read()

    mock_response = MagicMock()
    mock_response.content = image_data
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    document = image_loader.load_image("https://example.com/test.png")
    assert document is not None
    assert document.metadata["source"] == "https://example.com/test.png"
    assert document.metadata["type"] == "image"
    assert document.metadata["extension"] == ".png"


def test_load_directory(image_loader):
    """Test loading images from a directory."""
    # Create a temporary directory with test images
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create a few test images
        for i in range(3):
            img = Image.new("RGB", (100, 30), color="white")
            img.save(os.path.join(tmp_dir, f"test{i}.png"))

        # Create a file with unsupported extension
        Path(os.path.join(tmp_dir, "test.txt")).touch()

        documents = image_loader.load_directory(tmp_dir)
        assert len(documents) == 3

        for doc in documents:
            assert doc.metadata["type"] == "image"
            assert doc.metadata["extension"] == ".png"
