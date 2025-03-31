# RAG Retriever User Guide

RAG Retriever is a command-line tool for searching and retrieving information from a knowledge base built from web documentation, local documents, GitHub repositories, and images.

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

# Search in a specific collection
rag-retriever --query "API endpoints" --collection api-docs

# Search across all collections
rag-retriever --query "API endpoints" --search-all-collections
```

## Managing Collections

RAG Retriever organizes your knowledge base into collections, allowing you to separate different types of content.

### Listing Collections

View all available collections and their metadata:

```bash
rag-retriever --list-collections
```

This will display:

- Collection names
- Creation dates
- Last modified dates
- Document counts
- Total chunks
- Descriptions (if available)

### Using Collections

Specify a collection when adding content:

```bash
# Add content to a specific collection
rag-retriever --fetch-url https://docs.example.com/api --collection api-docs
rag-retriever --github-repo https://github.com/username/repo.git --collection code-docs
rag-retriever --ingest-file document.pdf --collection pdf-docs
```

Specify a collection when searching:

```bash
# Search within a specific collection
rag-retriever --query "configuration options" --collection api-docs

# Search across all collections
rag-retriever --query "configuration options" --search-all-collections
```

### Cleaning Collections

Delete a specific collection or the entire vector store:

```bash
# Delete a specific collection
rag-retriever --clean --collection old-docs

# Delete the entire vector store (all collections)
rag-retriever --clean
```

## Adding Documentation

### GitHub Repositories

Add GitHub repositories to your knowledge base:

```bash
# Add a repository with default settings
rag-retriever --github-repo https://github.com/username/repo.git

# Specify a branch
rag-retriever --github-repo https://github.com/username/repo.git --branch main

# Filter specific file types
rag-retriever --github-repo https://github.com/username/repo.git --file-extensions .py .md .js

# Add to a specific collection
rag-retriever --github-repo https://github.com/username/repo.git --collection code-docs

# Examples with real repositories
rag-retriever --github-repo https://github.com/openai/openai-python.git --branch main
rag-retriever --github-repo https://github.com/langchain-ai/langchain.git --branch master --file-extensions .py .md
```

The GitHub loader supports:

- Automatic temporary directory management
- Branch selection
- File type filtering
- Size limits and pattern exclusions
- Metadata preservation (source, branch, file path)

Configure GitHub settings in your `config.yaml`:

```yaml
github_settings:
  supported_extensions:
    - ".py"
    - ".js"
    - ".md"
  excluded_patterns:
    - "node_modules/**"
    - "__pycache__/**"
  max_file_size_mb: 10
  default_branch: "main"
```

### Local Documents

Add local documents to the knowledge base:

```bash
# Add a single file (supports .pdf, .md, .txt)
rag-retriever --ingest-file path/to/document.pdf

# Add all supported files from a directory
rag-retriever --ingest-directory path/to/docs/

# Add to a specific collection
rag-retriever --ingest-file path/to/document.pdf --collection pdf-docs

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
rag-retriever --fetch-url https://docs.example.com/guide --max-depth 0

# Add a section with limited depth
rag-retriever --fetch-url https://docs.example.com/api --max-depth 1

# Add documentation with default depth (2)
rag-retriever --fetch-url https://docs.example.com/tutorial

# Add to a specific collection
rag-retriever --fetch-url https://docs.example.com/api --collection api-docs
```

### Images

Add images to the knowledge base for analysis and retrieval:

```bash
# Add a single image
rag-retriever --ingest-image path/to/image.jpg

# Add all images from a directory
rag-retriever --ingest-image-directory path/to/images/

# Add to a specific collection
rag-retriever --ingest-image path/to/image.jpg --collection image-docs
```

### Confluence Content

Add content from Confluence to your knowledge base:

```bash
# Add content from a specific Confluence space
rag-retriever --confluence --space-key DOCS

# Add content from a specific parent page
rag-retriever --confluence --space-key DOCS --parent-id 123456

# Add to a specific collection
rag-retriever --confluence --space-key DOCS --collection confluence-docs
```

## Web Search

Perform web searches directly from the command line:

```bash
# Basic web search
rag-retriever --web-search "your search query"

# Specify number of results
rag-retriever --web-search "your search query" --results 10

# Choose search provider
rag-retriever --web-search "your search query" --search-provider google

# Output in JSON format
rag-retriever --web-search "your search query" --json
```

## User Interface

Launch the web-based user interface:

```bash
# Launch UI with default port (8501)
rag-retriever --ui

# Launch UI with custom port
rag-retriever --ui --port 8080
```

## Configuration

Initialize user configuration files:

```bash
rag-retriever --init
```

This creates default configuration files in the standard locations.

Enable verbose logging for troubleshooting:

```bash
rag-retriever --verbose --fetch-url https://docs.example.com/api
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
