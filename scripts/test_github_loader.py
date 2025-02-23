"""Script to test the GitHub repository loader."""

import logging
from pathlib import Path
import yaml

from rag_retriever.document_processor import GitHubLoader

# Set up logging
logging.basicConfig(level=logging.INFO)


def load_config():
    """Load configuration from the default config file."""
    config_path = (
        Path(__file__).parent.parent / "rag_retriever" / "config" / "config.yaml"
    )
    with open(config_path) as f:
        return yaml.safe_load(f)


def main():
    """Test loading a GitHub repository."""
    # Load config
    config = load_config()

    # Initialize the loader
    loader = GitHubLoader(config)

    # Test with a small, public repository
    repo_url = "https://github.com/openai/openai-cookbook.git"

    try:
        # Load only Python and Markdown files
        documents = loader.load_repository(
            repo_url=repo_url, file_filter=lambda x: x.endswith((".py", ".md"))
        )

        print(f"\nSuccessfully loaded {len(documents)} documents")
        print("\nFirst few documents:")
        for i, doc in enumerate(documents[:3]):
            print(f"\nDocument {i+1}:")
            print(f"Source: {doc.metadata.get('source', 'Unknown')}")
            print(f"Content preview: {doc.page_content[:200]}...")

    except Exception as e:
        print(f"Error loading repository: {str(e)}")


if __name__ == "__main__":
    main()
