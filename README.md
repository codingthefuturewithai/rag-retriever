# RAG Retriever

A Python application that recursively loads web pages, indexes their content using embeddings, and enables semantic search queries. Built with a modular architecture using OpenAI embeddings and Chroma vector store.

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd rag-retriever
```

2. Create and activate a virtual environment:

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

## Usage Examples

### Direct Execution (No venv activation)

For scenarios where you need to run the tool from another Python environment or application, use the direct execution scripts:

**Windows:**

```batch
C:\path\to\rag-retriever\rag_direct.bat --fetch https://example.com
```

**Mac/Linux:**

```bash
/path/to/rag-retriever/rag_direct.sh --fetch https://example.com
```

These scripts use the tool's Python environment directly without activation, making them safe to use:

- From another Python virtual environment
- From scripts or applications
- Without interfering with the current Python environment

### Fetching and Indexing Content

Using Python directly:

Index a single page:

```bash
python rag_retriever.py --fetch https://example.com
```

Or using convenience scripts:

```bash
# Windows
run.bat --fetch https://example.com

# Mac/Linux
./run.sh --fetch https://example.com
```

Index with depth control (crawls linked pages):

```bash
# Python
python rag_retriever.py --fetch https://example.com --max-depth 2

# Windows
run.bat --fetch https://example.com --max-depth 2

# Mac/Linux
./run.sh --fetch https://example.com --max-depth 2
```

The `--max-depth` parameter controls how deep the crawler will follow links:

- depth 0: Only the initial URL
- depth 1: Initial URL + linked pages
- depth 2 (default): Initial URL + linked pages + pages linked from those
- depth 3+: Continue following links to specified depth

Index multiple pages:

```bash
# Python
python rag_retriever.py --fetch https://docs.example.com/page1
python rag_retriever.py --fetch https://docs.example.com/page2

# Windows
run.bat --fetch https://docs.example.com/page1
run.bat --fetch https://docs.example.com/page2

# Mac/Linux
./run.sh --fetch https://docs.example.com/page1
./run.sh --fetch https://docs.example.com/page2
```

### Searching Content

Using Python directly:

Basic search:

```bash
python rag_retriever.py --query "How do I get started?"
```

Or using convenience scripts:

```bash
# Windows
run.bat --query "How do I get started?"

# Mac/Linux
./run.sh --query "How do I get started?"
```

Search with custom result limit:

```bash
# Python
python rag_retriever.py --query "deployment options" --limit 3

# Windows
run.bat --query "deployment options" --limit 3

# Mac/Linux
./run.sh --query "deployment options" --limit 3
```

Search with custom relevance threshold:

```bash
# Python
python rag_retriever.py --query "advanced configuration" --score-threshold 0.3

# Windows
run.bat --query "advanced configuration" --score-threshold 0.3

# Mac/Linux
./run.sh --query "advanced configuration" --score-threshold 0.3
```

Show full content in results:

```bash
# Python
python rag_retriever.py --query "installation steps" --full

# Windows
run.bat --query "installation steps" --full

# Mac/Linux
./run.sh --query "installation steps" --full
```

Get JSON output:

```bash
# Python
python rag_retriever.py --query "API reference" --json

# Windows
run.bat --query "API reference" --json

# Mac/Linux
./run.sh --query "API reference" --json
```

### Managing the Vector Store

Clean (delete) the vector store:

```bash
python rag_retriever.py --clean
```

Or using convenience scripts:

```bash
# Windows
run.bat clean

# Mac/Linux
./run.sh clean
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
├── config/                 # Configuration settings
├── src/
│   ├── crawling/          # Web crawling functionality
│   ├── vectorstore/       # Vector storage operations
│   ├── search/           # Search functionality
│   └── utils/            # Utility functions
├── tests/                 # Test files
├── rag_retriever.py      # Command-line interface
├── run.sh                # Unix convenience script
└── run.bat               # Windows convenience script
```

## Configuration

The application uses a YAML-based configuration system (`config/default_config.yaml`):

```yaml
vector_store:
  persist_directory: "./chromadb"
  embedding_model: "text-embedding-3-large"
  embedding_dimensions: 3072

content:
  chunk_size: 500
  chunk_overlap: 100

search:
  default_limit: 5
  default_score_threshold: 0.2
```

## Dependencies

Key dependencies include:

- openai: For embeddings generation (text-embedding-3-large model)
- chromadb: Vector store implementation with cosine similarity
- selenium: JavaScript content rendering
- beautifulsoup4: HTML parsing
- python-dotenv: Environment management

## Development

The application follows a modular architecture:

- Separate modules for crawling, storage, and search functionality
- Configuration management through dedicated config module
- Prepared for future test implementation

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
