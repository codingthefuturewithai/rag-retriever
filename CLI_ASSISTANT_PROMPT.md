# CLI Assistant Prompt for RAG Retriever

Read this entire prompt, then help me use RAG Retriever's command-line interface effectively. The CLI provides comprehensive functionality beyond what's available through the MCP server.

## Context

I need to use RAG Retriever's command-line interface to perform operations that aren't available through the MCP server, including administrative tasks, advanced content ingestion, and system management.

## CLI vs MCP Capabilities

### MCP Server Tools (Limited, Secure Subset)
- `list_collections()` - List collections
- `vector_search()` - Search content
- `crawl_and_index_url()` - Index websites
- `web_search()` - Search the web

### CLI-Only Capabilities (Full Administrative Control)
- **Collection Management**: Delete collections, clean entire vector store
- **Advanced Content Ingestion**: Local files, images, PDFs, GitHub repos, Confluence
- **System Administration**: Configuration, initialization, maintenance
- **Rich Output Options**: JSON, verbose logging, custom formatting
- **Web Interface**: Launch visual management interface

## Complete CLI Reference

### Core System Commands

#### **`rag-retriever --version`**
- Show version information
- Use for troubleshooting and support

#### **`rag-retriever --init`**
- Initialize user configuration files
- Creates config.yaml in OS-appropriate location
- Required for first-time setup

#### **`rag-retriever --ui [--port PORT]`**
- Launch Streamlit web interface
- Default port: 8501
- Visual collection management and search

### Collection Management

#### **`rag-retriever --list-collections`**
- Show all collections with detailed metadata
- Document counts, creation dates, descriptions
- Essential for understanding your knowledge base

#### **`rag-retriever --clean [--collection NAME]`**
- **WITHOUT --collection**: Deletes entire vector store (nuclear option)
- **WITH --collection**: Deletes specific collection only
- **CRITICAL**: No incremental updates exist - must delete before re-indexing

### Content Indexing

#### **`rag-retriever --fetch-url URL [--max-depth N] [--collection NAME]`**
- Crawl and index websites
- max-depth: How deep to follow links (default: 2)
- collection: Target collection name (creates if not exists)

#### **`rag-retriever --ingest-file PATH [--collection NAME]`**
- Ingest single local file (markdown, text, PDF)
- Supports rich document processing

#### **`rag-retriever --ingest-directory PATH [--collection NAME]`**
- Bulk ingest entire directory of documents
- Processes all supported file types

#### **`rag-retriever --ingest-image PATH [--collection NAME]`**
- Analyze and ingest single image using OpenAI Vision
- Generates detailed descriptions and insights

#### **`rag-retriever --ingest-image-directory PATH [--collection NAME]`**
- Bulk process directory of images
- Each image analyzed individually

#### **`rag-retriever --github-repo URL [--branch BRANCH] [--file-extensions EXT...] [--collection NAME]`**
- Clone and index GitHub repository
- Filter by file extensions (.py, .md, .js, etc.)
- Specify branch or use default

#### **`rag-retriever --confluence [--space-key KEY] [--parent-id ID] [--collection NAME]`**
- Load Confluence space content
- Requires Confluence configuration in config.yaml

### Search Operations

#### **`rag-retriever --query "SEARCH_TERMS" [OPTIONS]`**
- Search indexed content
- **Options:**
  - `--limit N`: Max results (default: 8)
  - `--score-threshold N`: Min relevance score (default: 0.3)
  - `--collection NAME`: Search specific collection
  - `--search-all-collections`: Search across ALL collections
  - `--truncate`: Show truncated content (default: full)
  - `--json`: Output in JSON format

### Web Search

#### **`rag-retriever --web-search "QUERY" [OPTIONS]`**
- Search the web (Google or DuckDuckGo)
- **Options:**
  - `--results N`: Number of results (default: 5)
  - `--search-provider [google|duckduckgo]`: Choose provider
  - `--google-api-key KEY`: Override Google API key
  - `--google-cse-id ID`: Override Google CSE ID
  - `--json`: Output in JSON format

### Global Options

#### **`--verbose`**
- Enable detailed logging
- Essential for troubleshooting
- Shows internal processing steps

#### **`--collection NAME`**
- Specify target collection for most operations
- Creates collection if it doesn't exist
- Defaults to "default" collection

## Common CLI Workflows

### Fresh Setup Workflow
```bash
# 1. Initialize configuration
rag-retriever --init

# 2. Edit config.yaml to add OpenAI API key
# 3. Start with documentation indexing
rag-retriever --fetch-url "https://docs.python.org" --collection python_docs

# 4. Verify indexing worked
rag-retriever --list-collections
rag-retriever --query "list comprehension" --collection python_docs
```

### Re-indexing Workflow (No Incremental Updates)
```bash
# 1. Delete existing collection
rag-retriever --clean --collection outdated_docs

# 2. Re-index from scratch
rag-retriever --fetch-url "https://updated-docs.com" --collection updated_docs

# 3. Verify new content
rag-retriever --query "new features" --collection updated_docs
```

### Advanced Content Ingestion
```bash
# Index local documentation
rag-retriever --ingest-directory ~/docs --collection local_docs

# Index GitHub repository
rag-retriever --github-repo https://github.com/user/repo --file-extensions .py .md --collection code_docs

# Process images for visual documentation
rag-retriever --ingest-image-directory ~/screenshots --collection visual_docs

# Load Confluence space
rag-retriever --confluence --space-key "TECH" --collection confluence_tech
```

### Administrative Maintenance
```bash
# Check system status
rag-retriever --list-collections --verbose

# Clean up old collections
rag-retriever --clean --collection old_collection

# Search across everything
rag-retriever --query "error handling" --search-all-collections --json

# Launch UI for visual management
rag-retriever --ui --port 8080
```

## Key Concepts

### Collection Strategy
- **One topic per collection**: Keep related content together
- **Descriptive names**: Use `python_docs`, `company_wiki`, not `docs1`
- **No incremental updates**: Delete entire collection before re-indexing
- **Regular maintenance**: Use `--clean` to remove outdated collections

### Content Processing
- **PDF support**: Automatic text extraction and OCR
- **Image analysis**: OpenAI Vision generates detailed descriptions
- **GitHub integration**: Selective file processing with filters
- **Confluence sync**: Space-level content import

### Search Optimization
- **Cross-collection search**: Use `--search-all-collections` for broad queries
- **Score thresholds**: Adjust `--score-threshold` for quality control
- **Collection targeting**: Use `--collection` for focused searches
- **JSON output**: Enable `--json` for programmatic processing

## Administrative Tasks

### Collection Cleanup
```bash
# List all collections to identify candidates for deletion
rag-retriever --list-collections

# Delete specific outdated collection
rag-retriever --clean --collection old_docs

# Nuclear option: delete entire vector store
rag-retriever --clean
```

### System Maintenance
```bash
# Check configuration
rag-retriever --init --verbose

# Validate all collections
rag-retriever --query "test" --search-all-collections --limit 1

# Launch UI for visual inspection
rag-retriever --ui
```

### Content Quality Management
```bash
# Test search quality across collections
rag-retriever --query "known_topic" --search-all-collections --score-threshold 0.4

# Verbose output for debugging
rag-retriever --query "problem_search" --verbose --json
```

## Error Handling and Troubleshooting

### Common Issues
- **Configuration errors**: Run `--init` and verify config.yaml
- **API key issues**: Check OpenAI API key in config.yaml
- **Collection not found**: Use `--list-collections` to verify names
- **Poor search results**: Adjust `--score-threshold` or re-index

### Debugging Commands
```bash
# Verbose logging for all operations
rag-retriever --verbose --query "test"

# JSON output for programmatic analysis
rag-retriever --list-collections --json

# UI for visual debugging
rag-retriever --ui
```

## Your Helpful Actions

**You CAN safely:**
- Help construct CLI commands with proper syntax
- Suggest collection organization strategies
- Recommend workflows for content ingestion
- Provide troubleshooting guidance
- Explain command options and parameters
- Help with administrative tasks

**You CANNOT:**
- Access or modify configuration files
- Execute CLI commands directly
- Access actual collection contents
- Modify or delete collections without explicit confirmation

## Success Criteria

Effective CLI usage should result in:
- **Organized collections** with clear naming and purpose
- **Comprehensive content coverage** through diverse ingestion methods
- **Regular maintenance** through cleanup and re-indexing
- **Optimal search performance** through proper configuration
- **Efficient workflows** using appropriate CLI commands

Remember: The CLI provides full administrative control that's intentionally not available through the MCP server. Use it for system management, advanced content ingestion, and maintenance tasks.