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

This helps prevent hallucinations and ensures your AI assistant follows your team's practices.

## How It Works

RAG Retriever processes various types of content:

- Text documents are chunked and embedded for semantic search
- Images are analyzed using AI vision models to generate detailed textual descriptions
- Web pages are crawled and their content is extracted
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
> **Get up and running in 10 minutes!** Head over to our [Getting Started Guide](docs/getting-started.md) for a quick setup that will have your AI assistant using RAG Retriever right away.
>
> ⚡ Quick install: `pipx install rag-retriever`

---

### Optional Dependencies

The following dependencies are only required for specific advanced features:

#### OCR Support (Optional)

Required only for:

- Processing scanned documents
- Extracting text from images in PDFs
- Converting images to searchable text

**MacOS**: `brew install tesseract`
**Windows**: Install [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

#### Advanced PDF Processing (Optional)

Required only for:

- Complex PDF layouts
- Better table extraction
- Technical document processing

**MacOS**: `brew install poppler`
**Windows**: Install [Poppler](https://github.com/oschwartz10612/poppler-windows/releases/)

The core functionality works without these dependencies, including:

- Basic PDF text extraction
- Markdown and text file processing
- Web content crawling
- Vector storage and search

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

Key configuration sections include:

```yaml
# Vector store settings
vector_store:
  embedding_model: "text-embedding-3-large"
  embedding_dimensions: 3072
  chunk_size: 1000
  chunk_overlap: 200

# Local document processing
document_processing:
  supported_extensions:
    - ".md"
    - ".txt"
    - ".pdf"
  pdf_settings:
    max_file_size_mb: 50
    extract_images: false
    ocr_enabled: false
    languages: ["eng"]
    strategy: "fast"
    mode: "elements"

# Search settings
search:
  default_limit: 8
  default_score_threshold: 0.3

# Image processing
image_processing:
  vision_model: "gpt-4-vision-preview"
  vision_max_tokens: 1000
  supported_formats:
    - ".png"
    - ".jpg"
    - ".jpeg"
    - ".gif"
    - ".webp"
  max_file_size_mb: 20
```

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
├── cli.py                  # Command-line interface implementation
├── main.py                 # Core application logic
├── config/                 # Configuration management
├── document_processor/     # Document processing modules
├── vectorstore/           # Vector storage and embedding
├── crawling/              # Web crawling functionality
├── search/                # Search implementation
└── utils/                 # Utility functions and helpers

tests/                     # Test suite
├── unit/                  # Unit tests
├── integration/           # Integration tests
├── data/                 # Test data files
├── docs/                 # Test documentation
└── results/              # Test results output

docs/                     # Project documentation
├── getting-started.md    # Quick start guide
├── configuration-guide.md # Configuration details
├── why-rag-retriever.md  # Project motivation and benefits
└── coding-assistants/    # AI assistant integration guides

scripts/                  # Utility scripts
├── install.py           # Installation helper script
├── test_pdf_processing.py # PDF processing test script
└── test_github_loader.py # GitHub loader test script

tools/                    # Development tools
└── test_utils/          # Test utilities and helpers
    ├── verify_categorization.py
    ├── run_regression_tests.py
    ├── ingest_samples.sh
    └── categorize_pdfs.py
```

### Key Components

- **document_processor/**: Handles different types of documents (PDF, Markdown, text), GitHub repositories, and Confluence content
- **vectorstore/**: Manages document embeddings and vector storage using ChromaDB
- **crawling/**: Implements web page crawling and content extraction
- **search/**: Provides semantic search functionality
- **config/**: Manages application configuration and settings
- **utils/**: Contains shared utilities and helper functions

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

Configuration options in `config.yaml`:

```yaml
github_settings:
  supported_extensions:
    - ".py"
    - ".js"
    - ".md"
    # ... more extensions
  excluded_patterns:
    - "node_modules/**"
    - "__pycache__/**"
    - "*.pyc"
    - ".git/**"
    # ... more patterns
  max_file_size_mb: 10
  default_branch: "main"
```

## Configuration Options

The configuration file (`config.yaml`) is organized into several sections:

### Vector Store Settings

```yaml
vector_store:
  persist_directory: null # Set automatically to OS-specific path
  embedding_model: "text-embedding-3-large"
  embedding_dimensions: 3072
  chunk_size: 1000 # Size of text chunks for indexing
  chunk_overlap: 200 # Overlap between chunks
```

### Document Processing Settings

```yaml
document_processing:
  # Supported file extensions
  supported_extensions:
    - ".md"
    - ".txt"
    - ".pdf"

  # Patterns to exclude from processing
  excluded_patterns:
    - ".*"
    - "node_modules/**"
    - "__pycache__/**"
    - "*.pyc"
    - ".git/**"

  # Fallback encodings for text files
  encoding_fallbacks:
    - "utf-8"
    - "latin-1"
    - "cp1252"

  # PDF processing settings
  pdf_settings:
    max_file_size_mb: 50
    extract_images: false
    ocr_enabled: false
    languages: ["eng"]
    password: null
    strategy: "fast" # Options: fast, accurate
    mode: "elements" # Options: single_page, paged, elements
```

### Image Processing Settings

```yaml
image_processing:
  vision_model: "gpt-4o-mini" # OpenAI vision model to use
  vision_max_tokens: 1000 # Maximum tokens for image analysis
  supported_formats: # Supported image formats
    - ".png"
    - ".jpg"
    - ".jpeg"
    - ".gif"
    - ".webp"
  max_file_size_mb: 20 # Maximum image file size in MB
```

### Content Processing Settings

```yaml
content:
  chunk_size: 2000
  chunk_overlap: 400
  # Text splitting separators (in order of preference)
  separators:
    - "\n## " # h2 headers (strongest break)
    - "\n### " # h3 headers
    - "\n#### " # h4 headers
    - "\n- " # bullet points
    - "\n• " # alternative bullet points
    - "\n\n" # paragraphs
    - ". " # sentences (weakest break)
```

### Search Settings

```yaml
search:
  default_limit: 8 # Default number of results
  default_score_threshold: 0.3 # Minimum relevance score
```

### Browser Settings (Web Crawling)

```yaml
browser:
  wait_time: 2 # Base wait time in seconds
  viewport:
    width: 1920
    height: 1080
  delays:
    before_request: [1, 3] # Min and max seconds
    after_load: [2, 4]
    after_dynamic: [1, 2]
  launch_options:
    headless: true
    channel: "chrome"
  context_options:
    bypass_csp: true
    java_script_enabled: true
```

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

## Features

### Core Features (No Additional Dependencies)

- Web crawling and content extraction
- Basic PDF text extraction
- Markdown and text file processing
- Vector storage and semantic search
- Configuration management
- Basic document chunking and processing

### Advanced Features (Optional Dependencies Required)

- **OCR Processing** (Requires Tesseract):

  - Scanned document processing
  - Image text extraction
  - PDF image text extraction

- **Enhanced PDF Processing** (Requires Poppler):
  - Complex layout handling
  - Table extraction
  - Technical document processing
  - Better handling of multi-column layouts

All core features work without installing optional dependencies. Install optional dependencies only if you need their specific features.

For more detailed usage instructions and examples, please refer to the [local-document-loading.md](docs/local-document-loading.md) documentation.

## Project Structure

```
rag-retriever/
├── rag_retriever/         # Main package directory
│   ├── config/           # Configuration settings
│   ├── crawling/         # Web crawling functionality
│   ├── vectorstore/      # Vector storage operations
│   ├── search/          # Search functionality
│   └── utils/           # Utility functions
```

## Dependencies

Key dependencies include:

- openai: For embeddings generation (text-embedding-3-large model)
- chromadb: Vector store implementation with cosine similarity
- selenium: JavaScript content rendering
- beautifulsoup4: HTML parsing
- python-dotenv: Environment management

## Notes

- Uses OpenAI's text-embedding-3-large model for generating embeddings by default
- Content is automatically cleaned and structured during indexing
- Implements URL depth-based crawling control
- Vector store persists between runs unless explicitly deleted
- Uses cosine similarity for more intuitive relevance scoring
- Minimal output by default with `--verbose` flag for troubleshooting
- Full content display by default with `--truncate` option for brevity
- ⚠️ Changing chunk size/overlap settings after ingesting content may lead to inconsistent search results. Consider reprocessing existing content if these settings must be changed.

## Future Development

RAG Retriever is under active development with many planned improvements. We maintain a detailed roadmap of future enhancements in our [Future Features](docs/future-features.md) document, which outlines:

- Document lifecycle management improvements
- Integration with popular documentation platforms
- Vector store analysis and visualization
- Search quality enhancements
- Performance optimizations

While the current version is fully functional for core use cases, there are currently some limitations that will be addressed in future releases. Check the future features document for details on potential upcoming improvements.

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Command Line Options

Core options:

- `--init`: Initialize user configuration files
- `--fetch URL`: Fetch and index web content
- `--max-depth N`: Maximum depth for recursive URL loading (default: 2)
- `--query STRING`: Search query to find relevant content
- `--limit N`: Maximum number of results to return
- `--score-threshold N`: Minimum relevance score threshold
- `--truncate`: Truncate content in search results
- `--json`: Output results in JSON format
- `--clean`: Clean (delete) the vector store
- `--verbose`: Enable verbose output for troubleshooting
- `--ingest-file PATH`: Ingest a local file
- `--ingest-directory PATH`: Ingest a directory of files
- `--web-search STRING`: Perform DuckDuckGo web search
- `--results N`: Number of web search results (default: 5)
- `--confluence`: Load from Confluence
- `--space-key STRING`: Confluence space key
- `--parent-id STRING`: Confluence parent page ID

# Web search (using DuckDuckGo)

rag-retriever --web-search "your search query" --results 5

# You can then fetch content from the web search results using --fetch

rag-retriever --fetch https://found-url-from-search.com --max-depth 0

# For example, to learn about new Java features:

rag-retriever --web-search "Java 23 new features guide" --results 3
rag-retriever --fetch https://www.happycoders.eu/java/java-23-features --max-depth 0

# Load from Confluence (requires configuration in ~/.config/rag-retriever/config.yaml)

rag-retriever --confluence --space-key TEAM

# Clean up vector store if needed

rag-retriever --clean
