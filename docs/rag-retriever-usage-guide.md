# RAG Retriever User Guide

RAG Retriever is a command-line tool for searching and retrieving information from a knowledge base built from both web documentation and local documents.

## Basic Search

Search through the knowledge base using natural language queries:

```bash
rag-retriever --query "your search terms here"
```

Example searches:

```bash
# Search for specific framework features
rag-retriever --query "How does the zoneless mode impact the Angular 18 framework's dependency on zone.js?"

# Search for detailed configuration
rag-retriever --query "What are the optimal chunk_size and chunk_overlap settings for ChromaDB when indexing API documentation over 100KB?"

# Search for API implementation details
rag-retriever --query "When using the app router in Next.js 15, how do you specify that a React component should be rendered on the client side instead of as a server component?"
```

## Search Parameters

Fine-tune your searches with optional parameters:

```bash
# Get more results
rag-retriever --query "deployment options" --limit 12

# Increase relevance threshold
rag-retriever --query "security best practices" --score-threshold 0.5

# Get truncated results
rag-retriever --query "configuration options" --truncate

# Output in JSON format
rag-retriever --query "API endpoints" --json
```

## Adding Documentation

### Local Documents

Add local documents to the knowledge base:

```bash
# Add a single file (supports .pdf, .md, .txt)
rag-retriever --ingest-file path/to/document.pdf

# Add all supported files from a directory
rag-retriever --ingest-directory path/to/docs/

# Process a scanned document
# NOTE: This will only work if OCR capability has been enabled on the Retriever
rag-retriever --ingest-file scanned-document.pdf

# Process a PDF containing images
# NOTE: This will only extract images if image processing has been enabled on the Retriever
rag-retriever --ingest-file document-with-images.pdf
```

### Web Documentation

Add web documentation to the knowledge base:

```bash
# Add a single page
rag-retriever --fetch https://docs.example.com/guide --max-depth 0

# Add a section with limited depth
rag-retriever --fetch https://docs.example.com/api --max-depth 1

# Add documentation with default depth (2)
rag-retriever --fetch https://docs.example.com/tutorial
```

## Understanding Results

Search results include:

- Source URL/file path
- Relevance score (0.0-1.0)
- Matching content snippet

Relevance scores are based on cosine similarity:

- 0.7+ : Very high relevance (nearly exact matches)
- 0.6 - 0.7: High relevance
- 0.5 - 0.6: Good relevance
- 0.3 - 0.5: Moderate relevance
- Below 0.3: Lower relevance

The default threshold is 0.3, which you can adjust using the `--score-threshold` parameter.
