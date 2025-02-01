"""Module for analyzing images using OpenAI's vision models."""

import base64
import logging
import os
from typing import Dict, Any, Optional
import httpx
from pathlib import Path
import json

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class VisionAnalyzer:
    """Handles image analysis using OpenAI's vision models."""

    DEFAULT_SYSTEM_PROMPT = """Analyze this image and describe what you observe. Focus on:
        1.      The main subject or focus
        2.      Key elements and their significance
        3.      Important details and their context
        4.      Overall meaning or purpose

Provide a clear, detailed description that captures both what is shown and its significance."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the vision analyzer.

        Args:
            config: Configuration dictionary containing vision model settings
        """
        vision_config = config.get("image_processing", {})
        api_config = config.get("api", {})

        # Prioritize API key from config
        api_key = api_config.get("openai_api_key")
        if not api_key:
            # Fall back to environment variable
            api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OpenAI API key not found. Please set it in config.yaml or OPENAI_API_KEY environment variable."
            )

        self.model = ChatOpenAI(
            api_key=api_key,
            model=vision_config.get("vision_model", "gpt-4o-mini"),
            max_tokens=vision_config.get("vision_max_tokens", 1000),
        )

        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    vision_config.get("system_prompt", self.DEFAULT_SYSTEM_PROMPT),
                ),
                (
                    "user",
                    [
                        {
                            "type": "image_url",
                            "image_url": {"url": "data:image/jpeg;base64,{image_data}"},
                        }
                    ],
                ),
            ]
        )

        # Create the analysis chain
        self.chain = self.prompt | self.model

    def _encode_image(self, image_path: str) -> Optional[str]:
        """Encode image file or URL to base64.

        Args:
            image_path: Local file path or URL of the image

        Returns:
            Base64 encoded image data or None if failed
        """
        try:
            # Handle URLs
            if image_path.startswith(("http://", "https://")):
                response = httpx.get(image_path)
                response.raise_for_status()
                image_data = response.content
            # Handle local files
            else:
                with open(image_path, "rb") as f:
                    image_data = f.read()

            return base64.b64encode(image_data).decode("utf-8")

        except Exception as e:
            logger.error(f"Failed to encode image {image_path}: {str(e)}")
            return None

    def analyze_image(self, image_path: str) -> Optional[Dict[str, Any]]:
        """Analyze an image using the vision model.

        Args:
            image_path: Path to image file or URL

        Returns:
            Dictionary containing analysis results or None if failed
        """
        try:
            # Encode the image
            image_data = self._encode_image(image_path)
            if not image_data:
                return None

            # Get analysis from the model
            logger.debug(f"Sending image to vision model: {image_path}")
            logger.debug(f"Image data: {image_data[:50]}... [truncated]")

            response = self.chain.invoke({"image_data": image_data})

            # Structure the response
            analysis = {
                "source": image_path,
                "content": response.content,
                "type": "vision_analysis",
            }

            return analysis

        except Exception as e:
            logger.error(f"Failed to analyze image {image_path}: {str(e)}")
            return None
