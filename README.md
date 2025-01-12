# RAG Retriever

A Python application that recursively loads web pages, indexes their content using embeddings, and enables semantic search queries. Built with a modular architecture using OpenAI embeddings and Chroma vector store.

## Prerequisites

- Python 3.7 or later (Download from [python.org](https://python.org))
- pipx (Install with one of these commands):

  ```bash
  # On MacOS
  brew install pipx

  # On Windows/Linux
  python -m pip install --user pipx
  ```

## Installation

Install RAG Retriever as a standalone application:

```bash
pipx install rag-retriever
```

This will:

- Create an isolated environment for the application
- Install all required dependencies
- Make the `rag-retriever` command available in your PATH

After installation, initialize the configuration:

```bash
# Initialize configuration
rag-retriever --init

# Edit .env file to add your OpenAI API key
# Unix/Mac:
nano ~/.config/rag-retriever/.env
# Windows:
notepad %APPDATA%\rag-retriever\.env
```

### Uninstallation

To completely remove RAG Retriever:

```bash
# Remove the application and its isolated environment
pipx uninstall rag-retriever

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

## Configuration

The application uses standard locations for all user files, regardless of installation method:

### File Locations

**Unix/Mac:**

- Config: `~/.config/rag-retriever/`
  - `config.yaml`: Configuration settings
  - `.env`: Environment variables and API keys
- Data: `~/.local/share/rag-retriever/`
  - `chromadb/`: Vector store database

**Windows:**

- Config: `%APPDATA%\rag-retriever\`
  - `config.yaml`: Configuration settings
  - `.env`: Environment variables and API keys
- Data: `%LOCALAPPDATA%\rag-retriever\`
  - `chromadb/`: Vector store database

## Usage Examples

### Fetching and Indexing

```bash
# Basic fetch (shows detailed output by default)
rag-retriever --fetch https://example.com

# With depth control
rag-retriever --fetch https://example.com --max-depth 2

# Minimal output mode
rag-retriever --fetch https://example.com --max-depth 0 --verbose false
```

The `--max-depth` parameter controls crawling depth:

- depth 0: Only the initial URL
- depth 1: Initial URL + linked pages
- depth 2 (default): Initial URL + linked pages + pages linked from those

### Searching Content

```bash
# Basic search (shows full content by default)
rag-retriever --query "How do I get started?"

# With truncated content
rag-retriever --query "How do I get started?" --truncate

# With custom limit
rag-retriever --query "deployment options" --limit 3

# With relevance threshold
rag-retriever --query "advanced configuration" --score-threshold 0.3

# JSON output
rag-retriever --query "API reference" --json

# Troubleshooting mode with verbose output
rag-retriever --query "installation steps" --verbose
```

## Understanding Search Results

Search results include relevance scores based on cosine similarity:

- Scores closer to 1.0 indicate higher relevance
- Typical ranges:
  - 0.7+: Very high relevance (nearly exact matches)
  - 0.6 - 0.7: High relevance
  - 0.5 - 0.6: Good relevance
  - 0.3 - 0.5: Moderate relevance
  - Below 0.3: Lower relevance

Default threshold is 0.3, adjustable with `--score-threshold`.

## Configuration Options

The default configuration includes:

```yaml
vector_store:
  persist_directory: null # Set automatically to OS-specific path
  embedding_model: "text-embedding-3-large"
  embedding_dimensions: 3072

content:
  chunk_size: 500
  chunk_overlap: 100
  ui_patterns:
    - "Theme\\s+Auto\\s+Light\\s+Dark"
    - "Previous\\s+topic|Next\\s+topic"
    - "Navigation"
    - "Jump\\s+to"
    - "Search"
    - "Skip\\s+to\\s+content"

search:
  default_limit: 5
  default_score_threshold: 0.2

selenium:
  wait_time: 2
  options:
    - "--headless"
    - "--no-sandbox"
    - "--disable-dev-shm-usage"
```

### Environment Variables

Override settings in your `.env` file:

```bash
# Required
OPENAI_API_KEY=your-api-key-here

# Optional overrides
RAG_RETRIEVER_EMBEDDING_MODEL=text-embedding-3-large
RAG_RETRIEVER_CHUNK_SIZE=1000
RAG_RETRIEVER_DEFAULT_LIMIT=10
```

## Features

- Recursively crawl and index web pages up to a specified depth
- Respect URL path depth for more controlled crawling
- Handle JavaScript-rendered content using Selenium WebDriver
- Clean and structure content while preserving meaningful hierarchy
- Store embeddings in a local Chroma vector database using cosine similarity
- Perform semantic search with customizable relevance scoring
- Support for full content display (default) with optional truncation
- Minimal output by default with verbose mode for troubleshooting
- JSON output format for integration with other tools

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

- Uses OpenAI's text-embedding-3-large model for generating embeddings
- Content is automatically cleaned and structured during indexing
- Implements URL depth-based crawling control
- Vector store persists between runs unless explicitly deleted
- Uses cosine similarity for more intuitive relevance scoring
- Minimal output by default with `--verbose` flag for troubleshooting
- Full content display by default with `--truncate` option for brevity

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
