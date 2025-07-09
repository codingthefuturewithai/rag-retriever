"""Configuration management for the RAG retriever application."""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from importlib.resources import files
import logging
import shutil
import stat

import yaml

logger = logging.getLogger(__name__)


def secure_file_permissions(file_path: Path) -> None:
    """Set secure file permissions (600) on the given file."""
    if os.name != "nt":  # Skip on Windows
        os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)


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


def ensure_user_directories() -> None:
    """Create user config and data directories if they don't exist."""
    config_dir = get_config_dir()
    data_dir = get_data_dir()

    config_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    logger.debug("Created user directories: %s, %s", config_dir, data_dir)


def create_user_config() -> None:
    """Create a new user config file by copying the default."""
    config_path = get_user_config_path()

    try:
        # Ensure parent directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy the default config file
        with files("rag_retriever.config").joinpath("config.yaml").open("r") as src:
            with open(config_path, "w", encoding="utf-8") as dst:
                dst.write(src.read())

        logger.info("Created user config file at: %s", config_path)
    except Exception as e:
        raise RuntimeError(
            f"Failed to create configuration file at {config_path}. "
            f"Please ensure you have write permissions to this location. Error: {e}"
        )


def initialize_user_files() -> None:
    """Initialize all user-specific files in standard locations."""
    ensure_user_directories()
    create_user_config()


def get_env_value(key: str, default: Any = None) -> Any:
    """Get config value from environment variable."""
    env_key = f"RAG_RETRIEVER_{key.upper()}"
    return os.environ.get(env_key, default)


def mask_api_key(key: str) -> str:
    """Mask an API key showing only first 4 and last 4 characters."""
    if not key or len(key) < 8:
        return "not set"
    return f"{key[:4]}...{key[-4:]}"




class Config:
    """Configuration manager for the application."""

    def __init__(self, config_path: str | None = None):
        """Initialize configuration manager."""
        self._config_path = None

        # Debug path resolution
        config_dir = get_config_dir()
        user_config_path = get_user_config_path()
        logger.debug("Config directory resolved to: %s", config_dir)
        logger.debug("User config path resolved to: %s", user_config_path)

        # First ensure user config exists
        if not user_config_path.exists():
            logger.debug("User config not found - creating it")
            create_user_config()
            # Verify creation
            if not user_config_path.exists():
                raise RuntimeError(
                    f"Installation failed: Could not create configuration file at {user_config_path}. "
                    "Please check your permissions and try again."
                )

        # Load user config first
        try:
            with open(user_config_path, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f)
                self._config_path = str(user_config_path)
                logger.debug("Loaded user config from: %s", user_config_path)
        except Exception as e:
            logger.error("Failed to load user config: %s", e)
            raise

        # If explicit config path provided, load and merge it
        if config_path:
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    explicit_config = yaml.safe_load(f)
                self._merge_configs(explicit_config)
                self._config_path = config_path
                logger.debug("Merged explicit config from %s", config_path)
            except Exception as e:
                logger.error("Failed to load explicit config: %s", e)
                raise

        # Apply environment variable overrides
        self._apply_env_overrides()

    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides to config."""
        # Vector store overrides
        if embed_model := get_env_value("EMBEDDING_MODEL"):
            self._config["vector_store"]["embedding_model"] = embed_model
        if embed_dim := get_env_value("EMBEDDING_DIMENSIONS"):
            self._config["vector_store"]["embedding_dimensions"] = int(embed_dim)

        # Search overrides
        if default_limit := get_env_value("DEFAULT_LIMIT"):
            self._config["search"]["default_limit"] = int(default_limit)
        if score_threshold := get_env_value("SCORE_THRESHOLD"):
            self._config["search"]["default_score_threshold"] = float(score_threshold)

    def _merge_configs(self, override_config: Dict[str, Any]) -> None:
        """Recursively merge override config into base config."""
        for key, value in override_config.items():
            if (
                key in self._config
                and isinstance(self._config[key], dict)
                and isinstance(value, dict)
            ):
                self._config[key].update(value)
            else:
                self._config[key] = value

    @property
    def vector_store(self) -> Dict[str, Any]:
        """Get vector store configuration."""
        config = self._config["vector_store"]
        if "batch_processing" not in config:
            # Add default batch processing settings if not present
            config["batch_processing"] = {
                "batch_size": 50,
                "delay_between_batches": 1.0,
                "max_retries": 3,
                "retry_delay": 5.0,
            }
        return config

    @property
    def content(self) -> Dict[str, Any]:
        """Get content processing configuration."""
        return self._config["content"]

    @property
    def search(self) -> Dict[str, Any]:
        """Get search configuration."""
        return self._config["search"]

    @property
    def crawler(self) -> Dict[str, Any]:
        """Get crawler configuration."""
        return self._config.get("crawler", {})

    @property
    def browser(self) -> Dict[str, Any]:
        """Get browser configuration."""
        return self._config.get("browser", {})

    @property
    def config_path(self) -> str:
        """Get the path to the active configuration file."""
        return self._config_path or "using default configuration"


    @property
    def api(self) -> Dict[str, Any]:
        """Get API configuration."""
        return self._config.get("api", {})

    def get_openai_api_key(self) -> Optional[str]:
        """Get OpenAI API key from config or environment."""
        logger.debug("Attempting to get OpenAI API key...")
        logger.debug("Config keys available: %s", list(self._config.keys()))

        if "api" in self._config:
            logger.debug("API section found in config")
            logger.debug("API section keys: %s", list(self._config["api"].keys()))
            if "openai_api_key" in self._config["api"]:
                logger.debug("openai_api_key found in config")
                api_key = self._config["api"]["openai_api_key"]
                logger.debug("API key type: %s", type(api_key))
                logger.debug(
                    "API key starts with sk-: %s",
                    str(api_key).startswith("sk-") if api_key else False,
                )
        else:
            logger.debug("No api section found in config")

        # First try config file (takes precedence)
        if api_key := self.api.get("openai_api_key"):
            logger.debug("Found API key in config file")
            if isinstance(api_key, str) and api_key.startswith("sk-"):
                logger.debug("Using API key from config file")
                # Set environment variable for crawl4ai and other dependencies
                os.environ["OPENAI_API_KEY"] = api_key
                return api_key
            else:
                logger.debug("API key in config is invalid format: %s", type(api_key))

        # Then try environment variable as fallback
        if api_key := os.getenv("OPENAI_API_KEY"):
            logger.debug("Found API key in environment")
            if api_key.startswith("sk-"):
                logger.debug("Using API key from environment variable")
                return api_key
            else:
                logger.debug("API key in environment is invalid format")

        logger.debug("No valid API key found in config or environment")
        return None


def get_google_search_credentials():
    """Get Google Search credentials from config or environment."""
    # Try command line args first (handled in cli.py)

    # Try environment variables
    api_key = os.getenv("GOOGLE_API_KEY")
    cse_id = os.getenv("GOOGLE_CSE_ID")

    logger.debug("Retrieving Google Search credentials:")
    logger.debug(
        "From environment - API Key: %s, CSE ID: %s", bool(api_key), bool(cse_id)
    )

    # If not found, try config file
    if not api_key and not cse_id:
        try:
            search_config = config._config.get("search", {})
            google_config = search_config.get("google_search", {})
            logger.debug(
                "Config sections found - search: %s, google_search: %s",
                bool(search_config),
                bool(google_config),
            )

            api_key = google_config.get("api_key")
            cse_id = google_config.get("cse_id")
            logger.debug(
                "From config - API Key: %s, CSE ID: %s", bool(api_key), bool(cse_id)
            )
        except (KeyError, AttributeError) as e:
            logger.debug("Error reading from config: %s", str(e))
            pass

    return api_key, cse_id


def get_user_friendly_config_path() -> str:
    """Get a user-friendly representation of the config file path for error messages."""
    if os.name == "nt":  # Windows
        return "%APPDATA%\\rag-retriever\\config.yaml"
    else:  # Unix-like
        return "~/.config/rag-retriever/config.yaml"


# Global config instance
config = Config()
