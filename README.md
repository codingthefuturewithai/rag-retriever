# RAG Retriever

A Python application that recursively loads web pages, indexes their content using embeddings, and enables semantic search queries. Built with a modular architecture using OpenAI embeddings and Chroma vector store.

## Features

- Recursively crawl and index web pages up to a specified depth
- Respect URL path depth for more controlled crawling
- Handle JavaScript-rendered content using Selenium WebDriver
- Clean and structure content while preserving meaningful hierarchy
- Store embeddings in a local Chroma vector database
- Perform semantic search with customizable relevance scoring
- Support for full content display and relevance threshold filtering

## Project Structure

```
rag-retriever/
├── config/                 # Configuration settings
├── src/
│   ├── crawling/          # Web crawling functionality
│   ├── storage/           # Vector storage operations
│   ├── search/            # Search functionality
│   └── main.py           # Core application logic
├── tests/                 # Test files
├── rag_retriever.py      # Command-line interface
├── rag.sh                # Unix convenience script
└── rag.bat               # Windows convenience script
```

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd rag-retriever
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

## Usage

The application can be run either directly with Python or using the convenience scripts (`rag.sh` for Unix/Mac or `rag.bat` for Windows).

### Using Convenience Scripts

Unix/Mac:

```bash
# Fetch and index content
./rag.sh fetch https://example.com 2

# Search with default settings
./rag.sh query "What is the main topic?"

# Search with options
./rag.sh query "What is discussed?" --full --score 0.3

# Clean the vector store
./rag.sh clean

# Show help
./rag.sh help
```

Windows:

```batch
# Fetch and index content
rag.bat fetch https://example.com 2

# Search with default settings
rag.bat query "What is the main topic?"

# Search with options
rag.bat query "What is discussed?" --full --score 0.3

# Clean the vector store
rag.bat clean

# Show help
rag.bat help
```

### Direct Python Usage

```bash
# Recursively index pages up to depth 2
python rag_retriever.py --fetch https://example.com --max-depth 2

# Basic search
python rag_retriever.py --query "What is the main topic?"

# Search with custom relevance threshold and full content display
python rag_retriever.py --query "What is discussed?" --score-threshold 0.3 --full
```

### Understanding Relevance Scores

The search results include relevance scores that indicate how well each document matches your query:

- Scores above 0.4 indicate very high relevance
- Scores between 0.3-0.4 indicate good relevance
- Scores below 0.3 indicate lower relevance

### Example Output

```bash
$ python rag_retriever.py --query "What are the features?" --score-threshold 0.3 --full

Vector store location: ./chromadb
Searching for: 'What are the features?'
Score threshold: 0.3

Source: https://example.com/features
Relevance Score: 0.4123
Content: [Full content of the matched document...]
```

## Configuration

The application uses a modular configuration system:

- Vector store location: `./chromadb/`
- Default relevance threshold: 0.3
- Configurable crawling depth and URL patterns
- Environment-based API key management

## Dependencies

Key dependencies include:

- openai: For embeddings generation
- chromadb: Vector store implementation
- selenium: JavaScript content rendering
- beautifulsoup4: HTML parsing
- python-dotenv: Environment management

## Development

The application follows a modular architecture for better maintainability:

- Separate modules for crawling, storage, and search functionality
- Configuration management through dedicated config module
- Prepared for future test implementation

## Notes

- Uses OpenAI's text-embedding-3-large model for generating embeddings
- Content is automatically cleaned and structured during indexing
- Implements URL depth-based crawling control
- Vector store persists between runs unless explicitly deleted
