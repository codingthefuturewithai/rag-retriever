# RAG Retriever Usage Guide

RAG Retriever is a command-line tool for searching and retrieving information from a knowledge base of documentation.

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
```

## Adding Documentation

Add new documentation to the knowledge base:

```bash
# Add a single page
rag-retriever --fetch https://docs.example.com/guide --max-depth 0

# Add a section with limited depth
rag-retriever --fetch https://docs.example.com/api --max-depth 1
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
