# RAG Retriever

A Python application that loads and processes web pages, local documents, images, GitHub repositories, and Confluence spaces, indexing their content using embeddings, and enabling semantic search queries. Built with a modular architecture using OpenAI embeddings and Chroma vector store.

## What It Does

RAG Retriever enhances your AI coding assistant (like aider, Cursor, or Windsurf) by giving it access to:

- Documentation about new technologies and features
- Your organization's architecture decisions and coding standards
- Internal APIs and tools documentation
- GitHub repositories and their documentation
- Confluence spaces and documentation
- Visual content like architecture diagrams, UI mockups, and technical illustrations
- Any other knowledge that isn't part of the LLM's training data

This can help provide new knowledge to your AI tools, prevent hallucinations and ensure your AI assistant follows your team's practices.

> **💡 Note**: For detailed instructions on setting up and configuring your AI coding assistant with RAG Retriever, see our [AI Assistant Setup Guide](https://github.com/codingthefuturewithai/ai-assistant-instructions/blob/main/instructions/setup/ai-assistant-setup-guide.md).

## How It Works

RAG Retriever processes various types of content:

- Text documents and PDFs are chunked and embedded for semantic search
- Images are analyzed using AI vision models to generate detailed textual descriptions
- Web pages are crawled and their content is extracted
- GitHub repositories are indexed with their code and documentation
- Confluence spaces are indexed with their full content hierarchy

When you search, the system finds semantically relevant content across all sources. For images, instead of returning the images themselves, it returns their AI-generated descriptions, making visual content searchable alongside your documentation.

## Watch a Short Demo Video (not all RAG Retriever features are shown)

[![Watch the video](https://img.youtube.com/vi/oQ6fSWUZYh0/0.jpg)](https://youtu.be/oQ6fSWUZYh0)

_RAG Retriever seamlessly integrating with aider, Cursor, and Windsurf to provide accurate, up-to-date information during development._

> **💡 Note**: While our examples focus on AI coding assistants, RAG Retriever can enhance any AI-powered development environment or tool that can execute command-line applications. Use it to augment IDEs, CLI tools, or any development workflow that needs reliable, up-to-date information.

## Why Do We Need Such Tools?

Modern AI coding assistants each implement their own way of loading external context from files and web sources. However, this creates several challenges:

- Knowledge remains siloed within each tool's ecosystem
- Support for different document types and sources varies widely
- Integration with enterprise knowledge bases (Confluence, Notion, etc.) is limited
- Each tool requires learning its unique context-loading mechanisms

RAG Retriever solves these challenges by:

1. Providing a unified knowledge repository that can ingest content from diverse sources
2. Offering a simple command-line interface that works with any AI tool supporting shell commands

> **💡 For a detailed discussion** of why centralized knowledge retrieval tools are crucial for AI-driven development, see our [Why RAG Retriever](docs/why-rag-retriever.md) guide.

## Prerequisites

### Core Requirements

- Python 3.10-3.12 (Download from [python.org](https://python.org))
- pipx (Install with one of these commands):

  ```bash
  # On MacOS
  brew install pipx

  # On Windows/Linux
  python -m pip install --user pipx
  ```

---

> ### 🚀 Ready to Try It? Let's Go!
>
> **Get up and running in 10 minutes!**
>
> 1. Install RAG Retriever: `pipx install rag-retriever`
> 2. Configure your AI coding assistant by following our [AI Assistant Setup Guide](https://github.com/codingthefuturewithai/ai-assistant-instructions/blob/main/instructions/setup/ai-assistant-setup-guide.md)
> 3. Start using RAG Retriever with your configured AI assistant!
>
> For detailed installation and configuration steps, see our [Getting Started Guide](docs/getting-started.md).

---

### Optional Dependencies

The following dependencies are only required for specific advanced PDF processing features:

**MacOS**: `brew install tesseract`
**Windows**: Install [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

### System Requirements

The application uses Playwright with Chromium for web crawling:

- Chromium browser is automatically installed during package installation
- Sufficient disk space for Chromium (~200MB)
- Internet connection for initial setup and crawling

Note: The application will automatically download and manage Chromium installation.

## Installation

Install RAG Retriever as a standalone application:

```bash
pipx install rag-retriever
```

This will:

- Create an isolated environment for the application
- Install all required dependencies
- Install Chromium browser automatically
- Make the `rag-retriever` command available in your PATH

## How to Upgrade

To upgrade RAG Retriever to the latest version:

```bash
pipx upgrade rag-retriever
```

This will:

- Upgrade the package to the latest available version
- Preserve your existing configuration and data
- Update any new dependencies automatically

After installation, initialize the configuration:

```bash
# Initialize configuration files
rag-retriever --init
```

This creates a configuration file at `~/.config/rag-retriever/config.yaml` (Unix/Mac) or `%APPDATA%\rag-retriever\config.yaml` (Windows)

### Setting up your API Key

Add your OpenAI API key to your configuration file:

```yaml
api:
  openai_api_key: "sk-your-api-key-here"
```

> **Security Note**: During installation, RAG Retriever automatically sets strict file permissions (600) on `config.yaml` to ensure it's only readable by you. This helps protect your API key.

### Customizing Configuration

All settings are in `config.yaml`. For detailed information about all configuration options, best practices, and example configurations, see our [Configuration Guide](docs/configuration-guide.md).

### Data Storage

The vector store database is stored at:

- Unix/Mac: `~/.local/share/rag-retriever/chromadb/`
- Windows: `%LOCALAPPDATA%\rag-retriever\chromadb/`

This location is automatically managed by the application and should not be modified directly.

### Uninstallation

To completely remove RAG Retriever:

```bash
# Remove the application and its isolated environment
pipx uninstall rag-retriever

# Remove Playwright browsers
python -m playwright uninstall chromium

# Optional: Remove configuration and data files
# Unix/Mac:
rm -rf ~/.config/rag-retriever ~/.local/share/rag-retriever
# Windows (run in PowerShell):
Remove-Item -Recurse -Force "$env:APPDATA\rag-retriever"
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\rag-retriever"
```

### Development Setup

If you want to contribute to RAG Retriever or modify the code:

```bash
# Clone the repository
git clone https://github.com/codingthefuturewithai/rag-retriever.git
cd rag-retriever

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Unix/Mac
venv\Scripts\activate     # Windows

# Install in editable mode
pip install -e .

# Initialize user configuration
./scripts/run-rag.sh --init  # Unix/Mac
scripts\run-rag.bat --init   # Windows
```

## Project Structure

The project is organized into the following key directories:

```
rag_retriever/              # Main package directory
├── main.py                # Core application logic
├── cli.py                 # Command-line interface implementation
├── config/               # Configuration management
├── document_processor/   # Document processing modules
├── vectorstore/         # Vector storage and embedding
├── crawling/            # Web crawling functionality
├── search/              # Search implementation
└── utils/              # Utility functions and helpers

tests/                    # Test suite
├── unit/               # Unit tests
├── integration/        # Integration tests
├── data/              # Test data files
├── docs/              # Test documentation
└── results/           # Test execution results

docs/                    # Project documentation
├── getting-started.md         # Quick start guide
├── configuration-guide.md     # Configuration details
├── why-rag-retriever.md      # Project motivation and benefits
├── future-features.md        # Planned enhancements
├── rag-retriever-usage-guide.md  # Usage instructions
└── images/                   # Documentation images

scripts/                 # Utility scripts
├── install.py          # Installation helper script
├── test_github_loader.py    # GitHub integration tests
├── test_pdf_processing.py   # PDF processing tests
├── organize_pdfs.py         # PDF organization utility
├── run-rag.sh              # Unix/Mac runner script
└── run-rag.bat             # Windows runner script

tools/                   # Development tools
└── test_utils/         # Test utilities
    ├── verify_categorization.py   # Category verification
    ├── categorize_pdfs.py        # PDF categorization
    ├── run_regression_tests.py   # Regression testing
    └── ingest_samples.sh         # Sample data ingestion
```

### Key Components

- **document_processor/**: Handles processing of various document types (PDF, text, etc.)
- **vectorstore/**: Manages document embeddings and vector storage using ChromaDB
- **crawling/**: Implements web crawling and content extraction
- **search/**: Provides semantic search functionality
- **config/**: Manages application configuration and settings
- **utils/**: Contains shared utility functions and helpers
- **tests/**: Comprehensive test suite with unit and integration tests
- **docs/**: User and developer documentation
- **scripts/**: Installation and testing utility scripts
- **tools/**: Development and testing utilities

### Supporting Directories

- **tests/**: Comprehensive test suite with unit and integration tests
- **docs/**: User and developer documentation
- **scripts/**: Installation and testing utility scripts
- **tools/**: Development and testing tools

The test suite is organized into unit tests and integration tests, with separate directories for test data, documentation, and results. The `docs/` directory contains comprehensive guides for users and contributors, including specific instructions for AI assistant integration.

## Usage Examples

### Local Document Processing

```bash
# Process a single file
rag-retriever --ingest-file path/to/document.pdf

# Process all supported files in a directory
rag-retriever --ingest-directory path/to/docs/

# Enable OCR for scanned documents (update config.yaml first)
# Set in config.yaml:
# document_processing.pdf_settings.ocr_enabled: true
rag-retriever --ingest-file scanned-document.pdf

# Enable image extraction from PDFs (update config.yaml first)
# Set in config.yaml:
# document_processing.pdf_settings.extract_images: true
rag-retriever --ingest-file document-with-images.pdf
```

### Web Content Fetching

```bash
# Basic fetch
rag-retriever --fetch https://example.com

# With depth control (default: 2)
rag-retriever --fetch https://example.com --max-depth 2

# Enable verbose output
rag-retriever --fetch https://example.com --verbose
```

### Image Analysis

```bash
# Analyze and index a single image
rag-retriever --ingest-image diagrams/RAG-Retriever-architecture.png

# Process all images in a directory
rag-retriever --ingest-image-directory diagrams/system-design/

# Search for specific architectural details
rag-retriever --query "How does RAG Retriever handle different types of document processing in its architecture?"
rag-retriever --query "What components are responsible for vector storage in the RAG Retriever system?"

# Combine with other content in searches
rag-retriever --query "Compare the error handling approach shown in the RAG Retriever architecture with the approach used by the latest LangChain framework"
```

The image analysis feature uses AI vision models to create detailed descriptions of your visual content, making it searchable alongside your documentation. When you search, you'll receive relevant text descriptions of the images rather than the images themselves.

### Web Search

```bash
# Search the web using DuckDuckGo
rag-retriever --web-search "your search query"

# Control number of results
rag-retriever --web-search "your search query" --results 10
```

### Confluence Integration

RAG Retriever can load and index content directly from your Confluence spaces. To use this feature:

1. Configure your Confluence credentials in `~/.config/rag-retriever/config.yaml`:

```yaml
api:
  confluence:
    url: "https://your-domain.atlassian.net" # Your Confluence instance URL
    username: "your-email@example.com" # Your Confluence username/email
    api_token: "your-api-token" # API token from https://id.atlassian.com/manage-profile/security/api-tokens
    space_key: null # Optional: Default space to load from
    parent_id: null # Optional: Default parent page ID
    include_attachments: false # Whether to include attachments
    limit: 50 # Max pages per request
    max_pages: 1000 # Maximum total pages to load
```

2. Load content from Confluence:

```bash
# Load from configured default space
rag-retriever --confluence

# Load from specific space
rag-retriever --confluence --space-key TEAM

# Load from specific parent page
rag-retriever --confluence --parent-id 123456

# Load from specific space and parent
rag-retriever --confluence --space-key TEAM --parent-id 123456
```

The loaded content will be:

- Converted to markdown format
- Split into appropriate chunks
- Embedded and stored in your vector store
- Available for semantic search just like any other content

### Searching Content

```bash
# Basic search
rag-retriever --query "How do I configure logging?"

# Limit results
rag-retriever --query "deployment steps" --limit 5

# Set minimum relevance score
rag-retriever --query "error handling" --score-threshold 0.7

# Get full content (default) or truncated
rag-retriever --query "database setup" --truncate

# Output in JSON format
rag-retriever --query "API endpoints" --json
```

### GitHub Repository Integration

```bash
# Load a GitHub repository
rag-retriever --github-repo https://github.com/username/repo.git

# Load a specific branch
rag-retriever --github-repo https://github.com/username/repo.git --branch main

# Load only specific file types
rag-retriever --github-repo https://github.com/username/repo.git --file-extensions .py .md .js
```

The GitHub loader:

- Clones repositories to a temporary directory
- Automatically cleans up after processing
- Supports branch selection
- Filters files by extension
- Excludes common non-documentation paths (node_modules, **pycache**, etc.)
- Enforces file size limits for better processing

## Understanding Search Results

Search results include relevance scores based on cosine similarity:

- Scores range from 0 to 1, where 1 indicates perfect similarity
- Default threshold is 0.3 (configurable via `search.default_score_threshold`)
- Typical interpretation:
  - 0.7+: Very high relevance (nearly exact matches)
  - 0.6 - 0.7: High relevance
  - 0.5 - 0.6: Good relevance
  - 0.3 - 0.5: Moderate relevance
  - Below 0.3: Lower relevance

## Notes

- Uses OpenAI's text-embedding-3-large model for generating embeddings by default
- Content is automatically cleaned and structured during indexing
- Implements URL depth-based crawling control
- Vector store persists between runs unless explicitly deleted
- Uses cosine similarity for more intuitive relevance scoring
- Minimal output by default with `--verbose` flag for troubleshooting
- Full content display by default with `--truncate` option for brevity
- ⚠️ Changing chunk size/overlap settings after ingesting content may lead to inconsistent search results. Consider reprocessing existing content if these settings must be changed.

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Command Line Options

Core options:

- `--init`: Initialize user configuration files
- `--clean`: Clean (delete) the vector store
- `--verbose`: Enable verbose output for troubleshooting
- `--json`: Output results in JSON format

Content Search:

- `--query STRING`: Search query to find relevant content
- `--limit N`: Maximum number of results to return
- `--score-threshold N`: Minimum relevance score threshold
- `--truncate`: Truncate content in search results (default: show full content)

Web Content:

- `--fetch URL`: Fetch and index web content
- `--max-depth N`: Maximum depth for recursive URL loading (default: 2)
- `--web-search STRING`: Perform DuckDuckGo web search
- `--results N`: Number of web search results (default: 5)

File Processing:

- `--ingest-file PATH`: Ingest a local file (supports .pdf, .md, .txt)
- `--ingest-directory PATH`: Ingest a directory of files

Image Processing:

- `--ingest-image PATH`: Path to an image file or URL to analyze and ingest
- `--ingest-image-directory PATH`: Path to a directory containing images to analyze and ingest

GitHub Integration:

- `--github-repo URL`: URL of the GitHub repository to load
- `--branch STRING`: Specific branch to load from the repository (default: main)
- `--file-extensions EXT [EXT ...]`: Specific file extensions to load (e.g., .py .md .js)

Confluence Integration:

- `--confluence`: Load from Confluence
- `--space-key STRING`: Confluence space key
- `--parent-id STRING`: Confluence parent page ID
