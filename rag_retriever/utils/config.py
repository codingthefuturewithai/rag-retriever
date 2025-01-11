"""Configuration management for the RAG retriever application."""

import os
from pathlib import Path
from typing import Dict, Any
from importlib import resources
import logging
import shutil

import yaml
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def get_config_dir() -> Path:
    """Get user-specific config directory path."""
    if os.name == "nt":  # Windows
        config_dir = Path(os.environ.get("APPDATA", "~/.config"))
    else:  # Unix-like
        config_dir = Path("~/.config")
    return config_dir.expanduser() / "rag-retriever"


def get_data_dir() -> Path:
    """Get user-specific data directory path."""
    if os.name == "nt":  # Windows
        data_dir = Path(os.environ.get("LOCALAPPDATA", "~/.local/share"))
    else:  # Unix-like
        data_dir = Path("~/.local/share")
    return data_dir.expanduser() / "rag-retriever"


def get_user_config_path() -> Path:
    """Get user-specific config file path."""
    return get_config_dir() / "config.yaml"


def get_user_env_path() -> Path:
    """Get user-specific .env file path."""
    return get_config_dir() / ".env"


def ensure_user_directories() -> None:
    """Create user config and data directories if they don't exist."""
    config_dir = get_config_dir()
    data_dir = get_data_dir()

    config_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    logger.debug("Created user directories: %s, %s", config_dir, data_dir)


def create_user_env() -> None:
    """Create a new .env file in user config directory using the example template."""
    env_path = get_user_env_path()

    # Don't overwrite existing .env
    if env_path.exists():
        logger.info("User .env already exists at: %s", env_path)
        return

    # Copy the example template from package resources
    with resources.files("rag_retriever.config").joinpath(".env.example").open(
        "r"
    ) as src:
        with open(env_path, "w") as dst:
            dst.write(src.read())

    logger.info("Created .env file at: %s", env_path)
    logger.info("Please edit this file to add your OpenAI API key")


def create_user_config() -> None:
    """Create a new user config file by copying the default."""
    config_path = get_user_config_path()

    # Don't overwrite existing config
    if config_path.exists():
        logger.info("User config already exists at: %s", config_path)
        return

    # Copy the default config file
    with resources.files("rag_retriever.config").joinpath("default_config.yaml").open(
        "r"
    ) as src:
        with open(config_path, "w") as dst:
            dst.write(src.read())

    logger.info("Created user config file at: %s", config_path)


def initialize_user_files() -> None:
    """Initialize all user-specific files in standard locations."""
    ensure_user_directories()
    create_user_config()
    create_user_env()


def get_env_value(key: str, default: Any = None) -> Any:
    """Get config value from environment variable."""
    env_key = f"RAG_RETRIEVER_{key.upper()}"
    return os.environ.get(env_key, default)


def mask_api_key(key: str) -> str:
    """Mask an API key showing only first 4 and last 4 characters."""
    if not key or len(key) < 8:
        return "not set"
    return f"{key[:4]}...{key[-4:]}"


def log_env_source() -> None:
    """Log information about where environment variables are loaded from."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY is not set in any environment file")
        return

    # Check each possible source
    env_sources = [
        (Path("~/.env").expanduser(), "home directory (~/.env)"),
        (get_user_env_path(), "user config directory"),
        (Path(".env"), "current directory"),
    ]

    for env_path, description in env_sources:
        if env_path.exists():
            with open(env_path) as f:
                if "OPENAI_API_KEY" in f.read():
                    logger.info(
                        "Using OPENAI_API_KEY from %s (key: %s)",
                        description,
                        mask_api_key(api_key),
                    )
                    return

    logger.info(
        "Using OPENAI_API_KEY from environment variables (key: %s)",
        mask_api_key(api_key),
    )


# Initialize environment
env_path = get_user_env_path()
local_env = Path(".env")  # Local development .env file

# Try local .env first (for development), then fall back to user config .env
if local_env.exists():
    load_dotenv(local_env)
    logger.debug("Loaded .env from current directory: %s", local_env.absolute())
elif env_path.exists():
    load_dotenv(env_path)
    logger.debug("Loaded .env from user config: %s", env_path)
else:
    logger.info(
        "No .env file found. Run 'rag-retriever --init' to create one at: %s", env_path
    )

# Log where we got our environment variables from
log_env_source()


class Config:
    """Configuration manager for the application."""

    def __init__(self, config_path: str | None = None):
        """Initialize configuration manager.

        Args:
            config_path: Path to the YAML configuration file.
                        If None, uses default config from package.
        """
        self._config_path = None
        self._env_path = None

        # Load default config first
        with resources.files("rag_retriever.config").joinpath(
            "default_config.yaml"
        ).open("r") as f:
            self._config = yaml.safe_load(f)

        # Try to load user config if it exists
        user_config_path = get_user_config_path()
        if user_config_path.exists():
            try:
                with open(user_config_path, "r") as f:
                    user_config = yaml.safe_load(f)
                # Merge user config with default config
                self._merge_configs(user_config)
                self._config_path = str(user_config_path)
                logger.debug("Loaded user config from %s", user_config_path)
            except Exception as e:
                logger.warning("Failed to load user config: %s", str(e))
        else:
            logger.info(
                "No user config found. Run 'rag-retriever --init' to create one at: %s",
                user_config_path,
            )

        # If explicit config path provided, load and merge it
        if config_path:
            try:
                with open(config_path, "r") as f:
                    explicit_config = yaml.safe_load(f)
                self._merge_configs(explicit_config)
                self._config_path = config_path
                logger.debug("Loaded explicit config from %s", config_path)
            except Exception as e:
                logger.warning("Failed to load explicit config: %s", str(e))

        # Check for environment file
        local_env = Path(".env")
        if local_env.exists():
            self._env_path = str(local_env.absolute())
        else:
            env_path = get_user_env_path()
            if env_path.exists():
                self._env_path = str(env_path)

        # Apply environment variable overrides
        self._apply_env_overrides()

    def _merge_configs(self, override_config: Dict[str, Any]) -> None:
        """Recursively merge override config into base config."""
        for key, value in override_config.items():
            if (
                key in self._config
                and isinstance(self._config[key], dict)
                and isinstance(value, dict)
            ):
                self._merge_configs(value)
            else:
                self._config[key] = value

    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides to config."""
        # Vector store overrides
        if embed_model := get_env_value("EMBEDDING_MODEL"):
            self._config["vector_store"]["embedding_model"] = embed_model
        if embed_dim := get_env_value("EMBEDDING_DIMENSIONS"):
            self._config["vector_store"]["embedding_dimensions"] = int(embed_dim)
        if persist_dir := get_env_value("PERSIST_DIRECTORY"):
            self._config["vector_store"]["persist_directory"] = persist_dir

        # Content processing overrides
        if chunk_size := get_env_value("CHUNK_SIZE"):
            self._config["content"]["chunk_size"] = int(chunk_size)
        if chunk_overlap := get_env_value("CHUNK_OVERLAP"):
            self._config["content"]["chunk_overlap"] = int(chunk_overlap)

        # Search overrides
        if default_limit := get_env_value("DEFAULT_LIMIT"):
            self._config["search"]["default_limit"] = int(default_limit)
        if score_threshold := get_env_value("SCORE_THRESHOLD"):
            self._config["search"]["default_score_threshold"] = float(score_threshold)

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

    @property
    def config_path(self) -> str:
        """Get the path to the active configuration file."""
        return self._config_path or "using default configuration"

    @property
    def env_path(self) -> str:
        """Get the path to the active environment file."""
        return self._env_path or "environment variables not loaded from file"


# Global config instance
config = Config()
