# Ingest Content into RAG Retriever

Guide users through advanced content ingestion using CLI-only capabilities for rich media, local files, and enterprise integrations.

## Prerequisites
This command requires CLI access for advanced content ingestion. MCP server only supports basic web crawling.

## Arguments
Use $ARGUMENTS to specify content type and source:
- "website URL" - Web crawling (available in MCP)
- "local PATH" - Local files and directories (CLI only)
- "images PATH" - Image analysis and ingestion (CLI only)
- "github REPO_URL" - GitHub repository ingestion (CLI only)
- "confluence SPACE_KEY" - Confluence space ingestion (CLI only)
- "help" - Show all available ingestion options

Examples:
- "website https://docs.python.org" - Crawl website
- "local ~/documents" - Process local directory
- "images ~/screenshots" - Analyze image directory
- "github https://github.com/user/repo" - Index GitHub repository
- "confluence TECH" - Load Confluence space

## Implementation Approach
This command uses **direct implementation** to guide users through appropriate ingestion workflows based on content type.

## Your Task

### 1. **Parse Arguments and Identify Content Type**
   - Extract content type and source from $ARGUMENTS
   - Determine appropriate ingestion method
   - Provide guidance if content type is unclear

### 2. **Content-Specific Ingestion Guidance**

#### **Website Crawling**
- Can use MCP: `crawl_and_index_url(url, max_depth, collection_name)`
- Also available via CLI: `rag-retriever --fetch-url URL --max-depth N --collection NAME`
- Recommend appropriate crawl depth and collection naming
- Provide post-crawl verification steps

#### **Local File Processing**
- **CLI ONLY** - Not available through MCP
- Single file: `rag-retriever --ingest-file PATH --collection NAME`
- Directory: `rag-retriever --ingest-directory PATH --collection NAME`
- Supports: PDF, markdown, text, structured documents
- Explain file type support and processing capabilities

#### **Image Analysis and Ingestion**
- **CLI ONLY** - Requires OpenAI Vision API
- Single image: `rag-retriever --ingest-image PATH --collection NAME`
- Directory: `rag-retriever --ingest-image-directory PATH --collection NAME`
- Explain image analysis capabilities (diagrams, screenshots, charts)
- Provide tips for optimal image quality

#### **GitHub Repository Ingestion**
- **CLI ONLY** - Requires git and repository access
- Basic: `rag-retriever --github-repo REPO_URL --collection NAME`
- With filters: `rag-retriever --github-repo REPO_URL --file-extensions .py .md --collection NAME`
- Branch selection: `rag-retriever --github-repo REPO_URL --branch BRANCH --collection NAME`
- Explain file filtering and branch selection options

#### **Confluence Integration**
- **CLI ONLY** - Requires Confluence API configuration
- Space: `rag-retriever --confluence --space-key SPACE --collection NAME`
- With parent: `rag-retriever --confluence --space-key SPACE --parent-id ID --collection NAME`
- Explain configuration requirements and authentication

### 3. **Multi-Source Ingestion Workflows**

#### **Comprehensive Documentation Project**
1. Web documentation via MCP or CLI
2. Local documentation via CLI
3. Image documentation via CLI
4. Source code via GitHub CLI
5. Enterprise wiki via Confluence CLI

#### **Knowledge Base Migration**
1. Assess current content sources
2. Plan collection organization strategy
3. Provide step-by-step ingestion commands
4. Include verification and testing steps

#### **Developer Documentation**
1. Code repository ingestion
2. API documentation processing
3. Architecture diagram analysis
4. Configuration file processing

### 4. **Configuration and Setup Guidance**

#### **Required Configuration**
- OpenAI API key (for image analysis)
- GitHub token (for private repositories)
- Confluence credentials (for enterprise integration)
- Proper file permissions and access

#### **Collection Organization**
- Suggest appropriate collection names
- Recommend content type separation
- Explain collection management best practices

### 5. **Troubleshooting and Optimization**

#### **Common Issues**
- File permission problems
- API key configuration issues
- Network connectivity problems
- Large dataset processing considerations

#### **Performance Optimization**
- Batch processing strategies
- File filtering recommendations
- Collection size management
- Processing time expectations

## CLI Commands You Will Provide

### Basic Ingestion
```bash
# Website crawling
rag-retriever --fetch-url "https://docs.example.com" --collection example_docs

# Local file processing
rag-retriever --ingest-file ~/document.pdf --collection documents
rag-retriever --ingest-directory ~/docs --collection all_docs

# Image analysis
rag-retriever --ingest-image ~/diagram.png --collection visuals
rag-retriever --ingest-image-directory ~/screenshots --collection ui_docs
```

### Advanced Ingestion
```bash
# GitHub repository
rag-retriever --github-repo https://github.com/user/repo --file-extensions .py .md --collection source_code

# Confluence space
rag-retriever --confluence --space-key "TECH" --collection confluence_docs

# Multi-source workflow
rag-retriever --fetch-url "https://docs.com" --collection web_docs
rag-retriever --ingest-directory ~/local_docs --collection local_docs
rag-retriever --ingest-image-directory ~/diagrams --collection visual_docs
```

### Verification and Testing
```bash
# Verify ingestion
rag-retriever --list-collections
rag-retriever --query "test content" --collection new_collection

# Quality check
rag-retriever --query "known_topic" --collection ingested_content --verbose
```

## Success Criteria
- Appropriate ingestion method selected based on content type
- Complete CLI commands provided with proper parameters
- Collection organization strategy recommended
- Configuration requirements explained
- Verification steps included for all ingestion operations

## Available MCP Tools
- `crawl_and_index_url(url, max_depth, collection_name)` - Web crawling only
- `list_collections()` - Verify ingestion results
- `vector_search(query_text, collection_name)` - Test ingested content

## Important Notes
- **Advanced ingestion requires CLI access** - Most capabilities not available through MCP
- **Configuration dependencies** - Image analysis requires OpenAI API, GitHub requires git, etc.
- **Processing time** - Large datasets may take significant time to process
- **Collection planning** - Organize content types into appropriate collections

## Your Ingestion Actions

**You CAN:**
- Recommend appropriate ingestion methods for different content types
- Provide complete CLI command syntax with parameters
- Suggest collection organization strategies
- Explain configuration requirements and setup
- Offer troubleshooting guidance for common issues

**You CANNOT:**
- Execute ingestion commands directly
- Access local files or directories
- Connect to external services (GitHub, Confluence)
- Modify system configuration
- Process actual content files