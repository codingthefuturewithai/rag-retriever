"""Tests for the vision analyzer module."""

import pytest
from unittest.mock import patch, MagicMock
import base64
import os
from pathlib import Path
import json

from rag_retriever.document_processor.vision_analyzer import VisionAnalyzer
from rag_retriever.utils.config import config

# Test configuration
TEST_CONFIG = {
    "image_processing": {
        "vision_enabled": True,
        "vision_model": "gpt-4o-mini",
        "vision_max_tokens": 1000,
    }
}

# Test configuration with custom prompt
TEST_CONFIG_WITH_CUSTOM_PROMPT = {
    "image_processing": {
        "vision_enabled": True,
        "vision_model": "gpt-4o-mini",
        "vision_max_tokens": 1000,
        "system_prompt": "Custom prompt for testing",
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
    """Test that the default system prompt is used when no custom prompt is provided."""
    analyzer = VisionAnalyzer(TEST_CONFIG)
    # The first message in the prompt template should be our system message
    system_message = analyzer.prompt.messages[0]
    assert system_message.prompt.template == analyzer.DEFAULT_SYSTEM_PROMPT


def test_custom_system_prompt():
    """Test that custom system prompt from config overrides the default."""
    analyzer = VisionAnalyzer(TEST_CONFIG_WITH_CUSTOM_PROMPT)
    system_message = analyzer.prompt.messages[0]
    assert system_message.prompt.template == "Custom prompt for testing"
    assert system_message.prompt.template != analyzer.DEFAULT_SYSTEM_PROMPT


def test_analyze_real_image():
    """Test analyzing a real image from the test data directory."""
    # Initialize the analyzer with the actual config
    analyzer = VisionAnalyzer(config._config)

    # Use a real test image
    test_image = "./tests/data/images/post-scaffolding-sprint-workflow.png"

    # Analyze the image
    result = analyzer.analyze_image(test_image)

    # Verify the result structure
    assert result is not None
    assert "source" in result
    assert "content" in result
    assert "type" in result
    assert result["source"] == test_image
    assert result["type"] == "vision_analysis"
    assert isinstance(result["content"], str)
    assert len(result["content"]) > 0
