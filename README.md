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

All settings are in `config.yaml`. Common adjustments include:

```yaml
content:
  chunk_size: 2000 # Size of text chunks for indexing
  chunk_overlap: 400 # Overlap between chunks

search:
  default_limit: 8 # Number of results returned
  default_score_threshold: 0.3 # Minimum relevance score
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
rag-retriever --query "deployment options" --limit 8

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
  chunk_size: 2000
  chunk_overlap: 400
  # Separators for text splitting, in order of preference
  separators:
    - "\n## " # h2 headers (strongest break)
    - "\n### " # h3 headers
    - "\n#### " # h4 headers
    - "\n- " # bullet points
    - "\n• " # alternative bullet points
    - "\n\n" # paragraphs
    - ". " # sentences (weakest break)
  ui_patterns:
    - "Theme\\s+Auto\\s+Light\\s+Dark"
    - "Previous\\s+topic|Next\\s+topic"
    - "Navigation"
    - "Jump\\s+to"
    - "Search"
    - "Skip\\s+to\\s+content"

search:
  default_limit: 8
  default_score_threshold: 0.3

selenium:
  wait_time: 2
  options:
    - "--headless"
    - "--no-sandbox"
    - "--disable-dev-shm-usage"
```

### Environment Variables

The application requires an OpenAI API key to be set in your `.env` file:

```bash
# Required: Set in ~/.config/rag-retriever/.env (Unix/Mac)
# or %APPDATA%\rag-retriever\.env (Windows)
OPENAI_API_KEY=your-api-key-here
```

All other configuration should be done by editing the config.yaml file as shown above.

## Using with AI Assistants

RAG Retriever can be integrated with most AI coding assistants (like aider, Cursor, GitHub Copilot, Codeium Windsurf, etc.) that are capable of running command line tools to enhance their knowledge with up-to-date documentation. We provide a prompt template that instructs AI assistants on how to properly use the RAG Retriever tool:

[ai-assistant-prompt.md](docs/ai-assistant-prompt.md)

**Important:** To use RAG Retriever with AI assistants, install it using the `pipx install rag-retriever` method described in the Installation section above. This ensures the `rag-retriever` command is available globally in your system PATH, which is required for AI assistants to access it.

To use this prompt:

1. Copy the prompt content into your AI assistant's instructions or system prompt
2. Activate the RAG functionality with `#rag-activate`
3. The assistant will now suggest using RAG Retriever when it needs additional context
4. Use `#rag-search` to explicitly request the assistant to consider using RAG for a specific query
5. Use `#rag-deactivate` to disable RAG functionality

The prompt ensures the assistant:

- Only suggests RAG when there are clear knowledge gaps
- Properly analyzes search results before suggesting fetches
- Uses appropriate search parameters and depth settings
- Provides clear explanations of its search strategy

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
