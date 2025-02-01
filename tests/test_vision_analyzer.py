"""Tests for the vision analyzer module."""

import pytest
from unittest.mock import patch, MagicMock
import base64
import os
from pathlib import Path

from rag_retriever.document_processor.vision_analyzer import VisionAnalyzer

# Test configuration
TEST_CONFIG = {
    "image_processing": {
        "vision_enabled": True,
        "vision_model": "gpt-4o-mini",
        "vision_max_tokens": 1000,
        "system_prompt": "Analyze this image and describe what you see.",
    }
}


@pytest.fixture
def vision_analyzer():
    """Create a VisionAnalyzer instance for testing."""
    return VisionAnalyzer(TEST_CONFIG)


@pytest.fixture
def test_image_path(tmp_path):
    """Create a temporary test image."""
    from PIL import Image

    # Create a simple test image
    img_path = tmp_path / "test.png"
    img = Image.new("RGB", (100, 30), color="white")
    img.save(img_path)

    return str(img_path)


def test_encode_local_image(vision_analyzer, test_image_path):
    """Test encoding a local image file."""
    encoded = vision_analyzer._encode_image(test_image_path)
    assert encoded is not None
    assert isinstance(encoded, str)
    # Verify it's valid base64
    try:
        base64.b64decode(encoded)
    except Exception:
        pytest.fail("Invalid base64 encoding")


@patch("httpx.get")
def test_encode_url_image(mock_get, vision_analyzer):
    """Test encoding an image from URL."""
    mock_response = MagicMock()
    mock_response.content = b"fake_image_data"
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    encoded = vision_analyzer._encode_image("https://example.com/image.jpg")
    assert encoded is not None
    assert isinstance(encoded, str)
    mock_get.assert_called_once()


def test_encode_invalid_image(vision_analyzer):
    """Test encoding an invalid image path."""
    encoded = vision_analyzer._encode_image("nonexistent.jpg")
    assert encoded is None


@patch("langchain_core.prompts.ChatPromptTemplate")
@patch("langchain_openai.ChatOpenAI")
def test_analyze_image(mock_chat, mock_prompt, vision_analyzer, test_image_path):
    """Test image analysis with mocked OpenAI response."""
    # Create mock response
    mock_response = MagicMock()
    mock_response.content = "Test response content"

    # Mock the chain's invoke method
    vision_analyzer.chain = MagicMock()
    vision_analyzer.chain.invoke.return_value = mock_response

    # Test analysis
    result = vision_analyzer.analyze_image(test_image_path)

    # Verify results
    assert result is not None
    assert result["source"] == test_image_path
    assert result["type"] == "vision_analysis"
    assert result["content"] == "Test response content"

    # Verify the chain was invoked
    vision_analyzer.chain.invoke.assert_called_once()


@patch("langchain_openai.ChatOpenAI")
def test_analyze_invalid_image(mock_chat, vision_analyzer):
    """Test analysis with an invalid image."""
    result = vision_analyzer.analyze_image("nonexistent.jpg")
    assert result is None
    mock_chat.return_value.invoke.assert_not_called()


def test_default_system_prompt():
    """Test that the default system prompt is comprehensive."""
    analyzer = VisionAnalyzer({})
    assert "Visual elements" in analyzer.DEFAULT_SYSTEM_PROMPT
    assert "Text content" in analyzer.DEFAULT_SYSTEM_PROMPT
    assert "Spatial relationships" in analyzer.DEFAULT_SYSTEM_PROMPT
    assert "Notable features" in analyzer.DEFAULT_SYSTEM_PROMPT
    assert "Overall context" in analyzer.DEFAULT_SYSTEM_PROMPT
