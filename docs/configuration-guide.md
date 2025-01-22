# Configuration Guide

This guide explains all configuration options available in `config.yaml`. The configuration file is automatically created at:

- Unix/Mac: `~/.config/rag-retriever/config.yaml`
- Windows: `%APPDATA%\rag-retriever\config.yaml`

## Vector Store Settings

```yaml
vector_store:
  persist_directory: null # Set automatically to OS-specific path
  embedding_model: "text-embedding-3-large"
  embedding_dimensions: 3072
  chunk_size: 1000 # Size of text chunks for indexing
  chunk_overlap: 200 # Overlap between chunks
```

⚠️ **Critical**: Neither `embedding_model` nor `embedding_dimensions` can be changed after documents have been indexed. The selected `embedding_dimensions` value must match values allowed by the chosen embedding model. For example, while text-embedding-3-large supports 1024 or 256 dimensions, 3072 is recommended for optimal results. Changing EITHER value requires deleting the existing vector store and reindexing all documents.

⚠️ **Important**: Changing `chunk_size` or `chunk_overlap` after ingesting content may lead to inconsistent search results. Consider reprocessing existing content if these settings must be changed.

## Document Processing

```yaml
document_processing:
  # Supported file extensions
  supported_extensions:
    - ".md"
    - ".txt"
    - ".pdf"

  # Patterns to exclude from processing
  excluded_patterns:
    - ".*"
    - "node_modules/**"
    - "__pycache__/**"
    - "*.pyc"
    - ".git/**"

  # Fallback encodings for text files
  encoding_fallbacks:
    - "utf-8"
    - "latin-1"
    - "cp1252"

  # PDF processing settings
  pdf_settings:
    max_file_size_mb: 50 # Maximum PDF file size in megabytes
    extract_images: false # Whether to extract images from PDFs
    ocr_enabled: false # NOT YET SUPPORTED
    languages: ["eng"] # Languages for text extraction (future OCR support)
    password: null # For password-protected PDFs
    strategy: "fast" # Options: fast, accurate
    mode: "elements" # Options: single_page, paged, elements
```

## Content Processing

```yaml
content:
  chunk_size: 2000
  chunk_overlap: 400
  # Text splitting separators (in order of preference)
  separators:
    - "\n## " # h2 headers (strongest break)
    - "\n### " # h3 headers
    - "\n#### " # h4 headers
    - "\n- " # bullet points
    - "\n• " # alternative bullet points
    - "\n\n" # paragraphs
    - ". " # sentences (weakest break)
  # UI cleanup patterns
  ui_patterns:
    - "Theme\\s+Auto\\s+Light\\s+Dark"
    - "Previous\\s+topic|Next\\s+topic"
    - "Navigation"
    - "Jump\\s+to"
    - "Search"
    - "Skip\\s+to\\s+content"
```

## Search Settings

```yaml
search:
  default_limit: 8 # Default number of results
  default_score_threshold: 0.3 # Minimum relevance score
```

## Browser Settings (Web Crawling)

```yaml
browser:
  wait_time: 2 # Base wait time in seconds
  viewport:
    width: 1920
    height: 1080
  # Random delays to appear more human-like
  delays:
    before_request: [1, 3] # Min and max seconds
    after_load: [2, 4]
    after_dynamic: [1, 2]
  # Browser launch options
  launch_options:
    headless: true
    channel: "chromium" # Uses Chromium by default (installed automatically)
  # Context options for stealth
  context_options:
    bypass_csp: true # Bypass Content Security Policy
    java_script_enabled: true
    user_agent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
  # Additional stealth settings
  stealth:
    languages: ["en-US", "en"]
    platform: "MacIntel" # Automatically set based on OS
    vendor: "Google Inc."
    webgl_vendor: "Intel Inc." # Automatically set based on OS
```

## API Settings

```yaml
api:
  openai_api_key: "sk-your-api-key-here" # Required: Set your OpenAI API key here
  confluence:
    url: null # Your Confluence instance URL (e.g., https://your-domain.atlassian.net)
    username: null # Your Confluence username/email
    api_token: null # Your Confluence API token
    space_key: null # Optional: Specific space to search in
    parent_id: null # Optional: Specific parent page ID to start from
    include_attachments: false # Whether to include attachments
    limit: 50 # Max pages per request
    max_pages: 1000 # Maximum total pages to retrieve
    batch_size: 50 # Number of pages to process in parallel
```

## Dependencies

RAG Retriever requires Python 3.10-3.12 and uses the following key dependencies:

- OpenAI 1.59.4 for embeddings and API integration
- ChromaDB 0.5.23 for vector storage
- Langchain 0.3.14 for document processing
- Playwright 1.42.0 for web crawling
- PyMuPDF and Unstructured for PDF processing
- Atlassian Python API for Confluence integration

## Example Configurations

### Minimal Configuration

```yaml
vector_store:
  embedding_model: "text-embedding-3-large"
  chunk_size: 1000
  chunk_overlap: 200

search:
  default_limit: 5
  default_score_threshold: 0.3
```

### PDF-Focused Configuration

```yaml
document_processing:
  pdf_settings:
    extract_images: true
    strategy: "accurate"
    mode: "elements"
```

### Web Crawling Configuration

```yaml
browser:
  delays:
    before_request: [2, 4]
    after_load: [3, 5]
  launch_options:
    headless: false
  stealth:
    languages: ["en-US", "en"]
    platform: "MacIntel"
```
