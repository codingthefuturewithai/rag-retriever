# RAG Retriever

A Python application that recursively loads web pages, indexes their content using embeddings, and enables semantic search queries. Built with LangChain and Chroma vector store.

## Features

- Recursively load and index web pages up to a specified depth
- Handle JavaScript-rendered content using Selenium
- Clean and structure content while preserving meaningful hierarchy
- Store embeddings in a local Chroma vector database
- Perform semantic search with relevance scoring
- Support for JSON output and filtering results by relevance threshold

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
# Create .env file with your OpenAI API key
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

## Usage

### Fetching and Indexing Content

```bash
# Index a single page (depth=0)
python main.py --fetch https://example.com --max-depth 0

# Recursively index pages up to depth 2
python main.py --fetch https://example.com --max-depth 2
```

### Searching Indexed Content

```bash
# Basic search
python main.py --query "What is the main topic?"

# Search with custom relevance threshold
python main.py --query "What is discussed?" --score-threshold 0.25

# Show full content in results
python main.py --query "Tell me about features" --full

# Get results in JSON format
python main.py --query "What are the requirements?" --json
```

### Understanding Relevance Scores

The search results include relevance scores that indicate how well each document matches your query:

- Scores around 0.3+ indicate high relevance
- Scores around 0.2-0.3 indicate moderate relevance
- Scores below 0.2 indicate low relevance

### Example Output

```bash
$ python main.py --query "What is discussed?"

Vector store location: /path/to/chromadb
Searching for: 'What is discussed?'
Score threshold: 0.2

Result 1:
Source: https://example.com
Relevance Score: 0.3245
Content: Main topic discussion about...
```

## Configuration

- Default vector store location: `./chromadb/`
- Default relevance threshold: 0.2
- Default chunk size: 500 characters
- Default chunk overlap: 100 characters

## Dependencies

- langchain-openai: For embeddings
- langchain-chroma: Vector store
- selenium: JavaScript content rendering
- beautifulsoup4: HTML parsing
- python-dotenv: Environment management

## Notes

- The application uses OpenAI's text-embedding-3-large model for generating embeddings
- Content is automatically cleaned and structured during indexing
- The vector store persists between runs unless explicitly deleted
