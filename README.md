# RAG Retriever

A Python application that loads and processes web pages, local documents, and Confluence spaces, indexing their content using embeddings, and enabling semantic search queries. Built with a modular architecture using OpenAI embeddings and Chroma vector store.

## What It Does

RAG Retriever enhances your AI coding assistant (like aider or Cursor) by giving it access to:

- Documentation about new technologies and features
- Your organization's architecture decisions and coding standards
- Internal APIs and tools documentation
- Confluence spaces and documentation
- Any other knowledge that isn't part of the LLM's training data

This helps prevent hallucinations and ensures your AI assistant follows your team's practices.

> **💡 Note**: While our examples focus on AI coding assistants, RAG Retriever can enhance any AI-powered development environment or tool that can execute command-line applications. Use it to augment IDEs, CLI tools, or any development workflow that needs reliable, up-to-date information.

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

---

### 🚀 Ready to Try It?

Head over to our [Getting Started Guide](docs/getting-started.md) for a quick setup that will get your AI assistant using the RAG Retriever in 5 minutes!

---

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

This creates:

- A configuration file at `~/.config/rag-retriever/config.yaml` (Unix/Mac) or `%APPDATA%\rag-retriever\config.yaml` (Windows)
- A `.env` file in the same directory for your OpenAI API key

### Setting up your API Key

Add your OpenAI API key to the `.env` file:

```bash
OPENAI_API_KEY=your-api-key-here
```

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

# With depth control
rag-retriever --fetch https://example.com --max-depth 2

# Minimal output mode
rag-retriever --fetch https://example.com --verbose false
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
