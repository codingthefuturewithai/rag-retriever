"""Configuration management for the RAG retriever application."""

import os
from pathlib import Path
from typing import Dict, Any

import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration manager for the application."""

    def __init__(self, config_path: str | None = None):
        """Initialize configuration manager.

        Args:
            config_path: Path to the YAML configuration file.
                        If None, uses default config from package.
        """
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "config",
                "default_config.yaml",
            )

        self.config_path = config_path
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        with open(self.config_path, "r") as f:
            return yaml.safe_load(f)

    @property
    def vector_store(self) -> Dict[str, Any]:
        """Get vector store configuration."""
        return self._config["vector_store"]

    @property
    def content(self) -> Dict[str, Any]:
        """Get content processing configuration."""
        return self._config["content"]

    @property
    def search(self) -> Dict[str, Any]:
        """Get search configuration."""
        return self._config["search"]

    @property
    def selenium(self) -> Dict[str, Any]:
        """Get Selenium configuration."""
        return self._config["selenium"]

    def get_persist_directory(self) -> str:
        """Get the vector store persistence directory.

        Returns:
            Absolute path to the persistence directory.
        """
        persist_dir = self.vector_store["persist_directory"]
        if not os.path.isabs(persist_dir):
            # Make relative paths relative to the project root
            persist_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), persist_dir
            )
        return persist_dir


# Global config instance
config = Config()
