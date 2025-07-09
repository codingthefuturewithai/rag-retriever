# Advanced Content Ingestion Prompt for RAG Retriever

Read this entire prompt, then help me use RAG Retriever's advanced content ingestion capabilities to process rich media, local files, code repositories, and enterprise content.

## Context

I need to use RAG Retriever's advanced content ingestion features that are only available through the CLI. These capabilities go far beyond simple web crawling and include image analysis, PDF processing, local file systems, GitHub repositories, and enterprise integrations.

## Advanced Ingestion Capabilities

### MCP Server Limitations (By Design)
- **Web crawling only** - Limited to `crawl_and_index_url()` function
- **No local file access** - Cannot process local directories or files
- **No rich media** - Cannot analyze images, PDFs, or multimedia content
- **No enterprise integrations** - Cannot access GitHub, Confluence, or other systems

### CLI Advanced Capabilities
- **Image Analysis** - OpenAI Vision-powered image understanding
- **PDF Processing** - Text extraction with OCR fallback
- **Local File Systems** - Bulk processing of local directories
- **GitHub Integration** - Repository cloning and selective ingestion
- **Confluence Integration** - Enterprise wiki content extraction
- **Rich Document Support** - Markdown, text, and structured content

## Content Type Capabilities

### 1. Image Analysis and Ingestion

#### **Single Image Processing**
```bash
# Analyze and ingest single image
rag-retriever --ingest-image ~/screenshots/architecture.png --collection visual_docs

# Process image from URL
rag-retriever --ingest-image "https://example.com/diagram.jpg" --collection diagrams

# With verbose output to see analysis
rag-retriever --ingest-image ~/docs/flowchart.png --collection processes --verbose
```

#### **Bulk Image Processing**
```bash
# Process entire directory of images
rag-retriever --ingest-image-directory ~/screenshots --collection visual_knowledge

# Process documentation images
rag-retriever --ingest-image-directory ~/project/docs/images --collection project_visuals
```

#### **Image Analysis Capabilities**
- **Technical Diagrams**: Architecture, flowcharts, UML diagrams
- **Screenshots**: UI documentation, error messages, system states
- **Charts and Graphs**: Data visualizations, metrics, dashboards
- **Code Screenshots**: Code snippets, terminal outputs, configurations
- **Documentation Images**: Infographics, process flows, system maps

### 2. PDF and Document Processing

#### **Single File Processing**
```bash
# Process PDF document
rag-retriever --ingest-file ~/documents/manual.pdf --collection manuals

# Process markdown file
rag-retriever --ingest-file ~/docs/README.md --collection documentation

# Process text file
rag-retriever --ingest-file ~/notes/meeting_notes.txt --collection meeting_records
```

#### **Bulk Document Processing**
```bash
# Process entire document directory
rag-retriever --ingest-directory ~/documents --collection all_docs

# Process specific project documentation
rag-retriever --ingest-directory ~/project/docs --collection project_docs
```

#### **Document Processing Capabilities**
- **PDF Text Extraction**: Automatic text extraction from PDFs
- **OCR Processing**: Optical character recognition for scanned documents
- **Markdown Support**: Rich formatting preservation
- **Text Files**: Plain text, structured data, logs
- **Metadata Extraction**: File information, creation dates, sources

### 3. GitHub Repository Integration

#### **Repository Ingestion**
```bash
# Clone and index entire repository
rag-retriever --github-repo https://github.com/user/repo --collection repo_docs

# Specific branch
rag-retriever --github-repo https://github.com/user/repo --branch develop --collection dev_docs

# Filter by file extensions
rag-retriever --github-repo https://github.com/user/repo --file-extensions .py .md --collection python_docs

# Comprehensive example
rag-retriever --github-repo https://github.com/fastapi/fastapi --file-extensions .py .md .rst --collection fastapi_source --verbose
```

#### **GitHub Integration Features**
- **Selective File Processing**: Filter by extensions (.py, .md, .js, etc.)
- **Branch Selection**: Target specific branches or use default
- **Automatic Cloning**: Temporary repository cloning and cleanup
- **Code and Documentation**: Process both source code and documentation
- **Metadata Preservation**: File paths, commit information, repository context

### 4. Confluence Enterprise Integration

#### **Confluence Space Loading**
```bash
# Load entire Confluence space
rag-retriever --confluence --space-key "TECH" --collection confluence_tech

# Load from specific parent page
rag-retriever --confluence --space-key "DOCS" --parent-id "123456" --collection confluence_docs

# With verbose output
rag-retriever --confluence --space-key "PROJ" --collection project_wiki --verbose
```

#### **Confluence Integration Features**
- **Space-level Import**: Import entire Confluence spaces
- **Hierarchical Processing**: Respect page hierarchies and relationships
- **Rich Content**: Preserve formatting, links, and structure
- **Metadata Extraction**: Author information, creation dates, page relationships
- **Authentication**: Uses configured Confluence credentials

### 5. Local File System Processing

#### **Directory Structures**
```bash
# Process complex directory structure
rag-retriever --ingest-directory ~/knowledge_base --collection personal_kb

# Process project documentation
rag-retriever --ingest-directory ~/projects/my_app/docs --collection app_docs

# Process multiple directories (run separately)
rag-retriever --ingest-directory ~/docs/api --collection api_docs
rag-retriever --ingest-directory ~/docs/user_guide --collection user_docs
```

#### **File System Features**
- **Recursive Processing**: Automatically processes subdirectories
- **File Type Detection**: Automatic format recognition
- **Batch Processing**: Efficient handling of large file sets
- **Error Handling**: Graceful handling of unreadable files
- **Progress Tracking**: Shows processing status for large operations

## Advanced Ingestion Workflows

### 1. Comprehensive Documentation Project

#### **Multi-Source Documentation**
```bash
# 1. Web documentation
rag-retriever --fetch-url "https://docs.myproject.com" --collection web_docs

# 2. GitHub source code
rag-retriever --github-repo https://github.com/myorg/myproject --file-extensions .py .md --collection source_docs

# 3. Local documentation
rag-retriever --ingest-directory ~/project/internal_docs --collection internal_docs

# 4. Visual documentation
rag-retriever --ingest-image-directory ~/project/diagrams --collection visual_docs

# 5. Confluence knowledge base
rag-retriever --confluence --space-key "PROJ" --collection confluence_docs
```

#### **Verification and Testing**
```bash
# Test each collection
rag-retriever --query "installation" --collection web_docs
rag-retriever --query "code structure" --collection source_docs
rag-retriever --query "architecture" --collection visual_docs

# Cross-collection search
rag-retriever --query "deployment process" --search-all-collections
```

### 2. Knowledge Base Migration

#### **From Local Files to Searchable Knowledge Base**
```bash
# 1. Process all document types
rag-retriever --ingest-directory ~/old_docs/pdfs --collection pdf_knowledge
rag-retriever --ingest-directory ~/old_docs/markdown --collection markdown_knowledge
rag-retriever --ingest-image-directory ~/old_docs/images --collection image_knowledge

# 2. Consolidate into unified collection
rag-retriever --ingest-directory ~/reorganized_docs --collection unified_knowledge

# 3. Quality verification
rag-retriever --query "important_topic" --collection unified_knowledge --verbose
```

### 3. Developer Knowledge Base

#### **Code Repository Documentation**
```bash
# 1. Core framework documentation
rag-retriever --github-repo https://github.com/django/django --file-extensions .py .md .rst --collection django_source

# 2. Project-specific code
rag-retriever --github-repo https://github.com/myteam/myproject --file-extensions .py .md --collection project_code

# 3. Configuration files and deployment
rag-retriever --ingest-directory ~/deployment_configs --collection deployment_docs

# 4. Architecture diagrams
rag-retriever --ingest-image-directory ~/architecture_diagrams --collection system_design
```

## Content-Specific Best Practices

### Image Processing Best Practices
- **High-quality images**: Use clear, readable images for better analysis
- **Descriptive filenames**: Use meaningful names that provide context
- **Organize by type**: Group screenshots, diagrams, charts separately
- **Regular updates**: Re-process images when content changes

### PDF Processing Best Practices
- **Text-based PDFs**: Work best with automatic text extraction
- **Scanned PDFs**: OCR processing may be slower but still effective
- **File organization**: Use descriptive collection names for different document types
- **Size considerations**: Large PDFs may take longer to process

### GitHub Integration Best Practices
- **File extension filtering**: Use `--file-extensions` to focus on relevant files
- **Branch selection**: Choose active development branches or stable releases
- **Repository size**: Consider processing time for large repositories
- **Update frequency**: Re-index when repository changes significantly

### Confluence Integration Best Practices
- **Space organization**: Process related spaces into separate collections
- **Permission considerations**: Ensure proper Confluence access permissions
- **Content freshness**: Regular re-indexing for updated content
- **Space size**: Large spaces may require significant processing time

## Configuration Requirements

### Image Processing Setup
```yaml
# config.yaml
api:
  openai_api_key: "your-key-here"  # Required for image analysis

content:
  image_analysis_enabled: true
  image_description_detail: "high"  # Options: low, medium, high
```

### GitHub Integration Setup
```yaml
# config.yaml
github:
  access_token: "your-token"  # Optional, for private repositories
  clone_depth: 1  # Shallow clones for faster processing
```

### Confluence Integration Setup
```yaml
# config.yaml
confluence:
  base_url: "https://your-org.atlassian.net"
  username: "your-email@company.com"
  api_token: "your-api-token"
```

## Troubleshooting Advanced Ingestion

### Common Issues and Solutions

#### **Image Processing Failures**
```bash
# Check with verbose output
rag-retriever --ingest-image ~/problem_image.png --verbose

# Verify OpenAI API key configuration
rag-retriever --query "test" --verbose

# Try with different image formats
rag-retriever --ingest-image ~/converted_image.jpg --collection test
```

#### **PDF Processing Issues**
```bash
# Use verbose output to see processing details
rag-retriever --ingest-file ~/problem.pdf --verbose

# Check file permissions and accessibility
ls -la ~/problem.pdf

# Try with different PDF
rag-retriever --ingest-file ~/simple.pdf --collection test
```

#### **GitHub Access Issues**
```bash
# Test with public repository first
rag-retriever --github-repo https://github.com/public/repo --verbose

# Check network connectivity
ping github.com

# Verify git installation
git --version
```

#### **Confluence Connection Issues**
```bash
# Test with verbose output
rag-retriever --confluence --space-key "TEST" --verbose

# Verify configuration
rag-retriever --init --verbose

# Check API token permissions
curl -u email:token https://your-org.atlassian.net/rest/api/content
```

## Your Advanced Ingestion Actions

**You CAN safely:**
- Help plan multi-source content ingestion strategies
- Suggest appropriate collection organization for different content types
- Provide command construction help for complex ingestion workflows
- Recommend best practices for specific content types
- Help troubleshoot ingestion issues with guidance
- Suggest optimization strategies for large-scale processing

**You CANNOT:**
- Execute ingestion commands directly
- Access local files or directories
- Connect to GitHub or Confluence directly
- Modify system configuration
- Process actual files or images

## Success Criteria

Effective advanced content ingestion should result in:
- **Rich, searchable knowledge bases** with diverse content types
- **Efficient processing workflows** for regular content updates
- **Well-organized collections** by content type and source
- **Comprehensive coverage** of all relevant knowledge sources
- **Optimized search performance** across different content types

Remember: Advanced ingestion capabilities are only available through the CLI and require appropriate API keys and system configurations. Always test with small samples before processing large datasets.