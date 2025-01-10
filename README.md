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
│   ├── vectorstore/       # Vector storage operations
│   ├── search/           # Search functionality
│   └── utils/            # Utility functions
├── tests/                 # Test files
├── rag_retriever.py      # Command-line interface
├── run.sh                # Unix convenience script
└── run.bat               # Windows convenience script
```

## Usage

The application comes with convenience scripts for both Windows and Mac/Linux users.

### Windows Users

```batch
# Run the application
run.bat [arguments]

# Clean the vector store
run.bat clean
```

### Mac/Linux Users

First, make the script executable:

```bash
chmod +x run.sh
```

Then:

```bash
# Run the application
./run.sh [arguments]

# Clean the vector store
./run.sh clean
```

### Understanding Relevance Scores

The search results include relevance scores that indicate how well each document matches your query:

- Scores above 0.4 indicate very high relevance
- Scores between 0.3-0.4 indicate good relevance
- Scores below 0.3 indicate lower relevance

## Configuration

The application uses a modular configuration system:

- Vector store location: `./vectorstore/`
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

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the [LICENSE NAME] - see the LICENSE file for details.
