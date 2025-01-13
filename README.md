# RAG Retriever

A Python application that loads and processes both web pages and local documents, indexing their content using embeddings, and enabling semantic search queries. Built with a modular architecture using OpenAI embeddings and Chroma vector store.

## Prerequisites

- Python 3.10-3.12 (Download from [python.org](https://python.org))
- pipx (Install with one of these commands):

  ```bash
  # On MacOS
  brew install pipx

  # On Windows/Linux
  python -m pip install --user pipx
  ```

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

This creates:

- A configuration file at `~/.config/rag-retriever/config.yaml` (Unix/Mac) or `%APPDATA%\rag-retriever\config.yaml` (Windows)
- A `.env` file in the same directory for your OpenAI API key

### Setting up your API Key

Add your OpenAI API key to the `.env` file:

```bash
OPENAI_API_KEY=your-api-key-here
```

### Customizing Configuration

All settings are in `config.yaml`. Key configuration sections include:

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

### Searching Content

```bash
# Basic search
rag-retriever --query "How do I get started?"

# With truncated content
rag-retriever --query "How do I get started?" --truncate

# With custom result limit
rag-retriever --query "deployment options" --limit 5

# With minimum relevance score
rag-retriever --query "advanced configuration" --score-threshold 0.5

# JSON output format
rag-retriever --query "API reference" --json
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

- **Local Document Loading**: Load markdown, text, and PDF files from local directories.

  - **Single File and Directory Loading**: Easily load individual files or entire directories with support for multithreading and progress indication.
  - **PDF Processing**: Extract text and images from PDFs using multiple loaders, with optional OCR for scanned documents.
  - **Configurable Settings**: Customize supported file types, PDF processing options, and more through configuration files.

- **Error Handling**: Robust error handling for unsupported file types and missing files, with detailed logging for troubleshooting.

- **Configuration**: Flexible configuration options for document processing, including supported extensions and PDF settings.

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

## Known Current Limitations

The following limitations are currently being tracked, with possible future enhancements under consideration:

- Does not check for existing URLs or content in the vector store during fetch operations

  - Possible enhancement: Detect and skip already indexed content by default
  - Possible enhancement: Add `--re-fetch` option to update existing content
  - Possible enhancement: Provide status information about existing content age

- Limited document management capabilities

  - Possible enhancement: Support for deleting specific documents from the vector store
  - Possible enhancement: Support for bulk deletion of documents by base URL
  - Possible enhancement: Document listing and filtering tools

- No direct access to vector store data for analysis

  - Possible enhancement: Tools to examine and analyze stored embeddings and metadata
  - Possible enhancement: Support for export/import of vector store data for backup or transfer

- Command-line interface only
  - Possible enhancement: Web UI for easier interaction with all features
  - Possible enhancement: Real-time progress monitoring and result visualization

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
