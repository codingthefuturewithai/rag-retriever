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

⚠️ **Critical**: Neither `embedding_model` nor `embedding_dimensions` can be changed after documents have been indexed. Also the selected `embedding_dimensions` value is important and must match values allowed by the chosen embedding model. For example, while text-embedding-3-large can be used with values of 1024 or even 256, you'll likely get better results using 3072 dimensions). In any case, changing EITHER value would make existing embeddings incompatible with new ones. If you need to switch embedding models or change dimensions, you must first delete the existing vector store and reindex all documents.

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
    max_file_size_mb: 50
    extract_images: false # Enable image extraction from PDFs
    ocr_enabled: false # Enable OCR for scanned documents
    languages: ["eng"] # OCR language support
    password: null # For password-protected PDFs
    strategy: "fast" # Options: fast, accurate
    mode: "elements" # Options: single_page, paged, elements
```

## Content Processing

```yaml
content:
  chunk_size: 2000 # Size of text chunks
  chunk_overlap: 400 # Overlap between chunks
  # Text splitting separators (in order of preference)
  separators:
    - "\n## " # h2 headers (strongest break)
    - "\n### " # h3 headers
    - "\n#### " # h4 headers
    - "\n- " # bullet points
    - "\n• " # alternative bullet points
    - "\n\n" # paragraphs
    - ". " # sentences (weakest break)
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
  delays:
    before_request: [1, 3] # Min and max seconds
    after_load: [2, 4]
    after_dynamic: [1, 2]
  launch_options:
    headless: true
    channel: "chrome"
  context_options:
    bypass_csp: true
    java_script_enabled: true
```

## Configuration Tips

1. **Vector Store**

   - Higher `chunk_size` captures more context but may reduce precision
   - Higher `chunk_overlap` improves context continuity but increases storage/processing
   - Consider your use case when adjusting these settings

2. **Document Processing**

   - Add file extensions as needed for your documentation
   - Adjust excluded patterns based on your repository structure
   - Enable OCR only if needed (increases processing time)

3. **Content Processing**

   - Adjust separators based on your document structure
   - Order separators from strongest to weakest breaks
   - Consider document formatting when customizing

4. **Search Settings**

   - Lower score threshold includes more results but may reduce relevance
   - Adjust limit based on your typical usage patterns

5. **Browser Settings**
   - Adjust delays based on target site performance
   - Modify viewport for different screen sizes
   - Enable/disable JavaScript based on site requirements

## Environment Variables

Some settings can be overridden with environment variables:

```bash
OPENAI_API_KEY=your-api-key-here
RAG_RETRIEVER_CONFIG_DIR=/custom/config/path
RAG_RETRIEVER_DATA_DIR=/custom/data/path
```

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
    ocr_enabled: true
    languages: ["eng", "fra"]
    strategy: "accurate"
```

### Web Crawling Configuration

```yaml
browser:
  delays:
    before_request: [2, 4]
    after_load: [3, 5]
  launch_options:
    headless: false
```
