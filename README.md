# RAG Retriever

A Python application that recursively loads web pages, indexes their content using embeddings, and enables semantic search queries. Built with a modular architecture using OpenAI embeddings and Chroma vector store.

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- pip (Python package installer)

### Installation

1. Install the package:

```bash
pip install rag-retriever
```

2. Initialize user files:

```bash
rag-retriever --init
```

This will create:

- Configuration file at `~/.config/rag-retriever/config.yaml`
- Environment file at `~/.config/rag-retriever/.env`
- Data directory at `~/.local/share/rag-retriever/`

3. Edit the `.env` file to add your OpenAI API key:

```bash
# Unix/Mac
nano ~/.config/rag-retriever/.env

# Windows
notepad %APPDATA%\rag-retriever\.env
```

## Usage Examples

### Fetching and Indexing Content

Index a single page:

```bash
rag-retriever --fetch https://example.com
```

Index with depth control (crawls linked pages):

```bash
rag-retriever --fetch https://example.com --max-depth 2
```

The `--max-depth` parameter controls how deep the crawler will follow links:

- depth 0: Only the initial URL
- depth 1: Initial URL + linked pages
- depth 2 (default): Initial URL + linked pages + pages linked from those
- depth 3+: Continue following links to specified depth

Index multiple pages:

```bash
rag-retriever --fetch https://docs.example.com/page1
rag-retriever --fetch https://docs.example.com/page2
```

### Searching Content

Basic search:

```bash
rag-retriever --query "How do I get started?"
```

Search with custom result limit:

```bash
rag-retriever --query "deployment options" --limit 3
```

Search with custom relevance threshold:

```bash
rag-retriever --query "advanced configuration" --score-threshold 0.3
```

Show full content in results:

```bash
rag-retriever --query "installation steps" --full
```

Get JSON output:

```bash
rag-retriever --query "API reference" --json
```

### Managing the Vector Store

Clean (delete) the vector store:

```bash
rag-retriever --clean
```

## Understanding Search Results

The search results include relevance scores based on cosine similarity:

- Scores closer to 1.0 indicate higher relevance
- Typical ranges:
  - 0.8 - 1.0: Very high relevance (nearly exact matches)
  - 0.6 - 0.8: High relevance
  - 0.4 - 0.6: Moderate relevance
  - Below 0.4: Lower relevance

The default threshold is 0.2, but you can adjust this using the `--score-threshold` parameter.

## Configuration

The application uses a standard directory structure for user files:

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

### Configuration Options

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

You can override any setting using environment variables in your `.env` file:

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
- Support for full content display and relevance threshold filtering

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

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the [LICENSE NAME] - see the LICENSE file for details.
