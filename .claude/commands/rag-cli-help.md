# RAG Retriever CLI Help

Interactive CLI command builder and context-sensitive help for RAG Retriever operations.

## Prerequisites
This command provides CLI guidance and command construction. No MCP server required, but CLI access needed for execution.

## Arguments
Use $ARGUMENTS to specify help topic or operation:
- "commands" - Show all available CLI commands
- "search" - Help with search operations
- "ingest" - Help with content ingestion
- "admin" - Help with administrative operations
- "config" - Help with configuration and setup
- "examples" - Show common usage examples
- "COMMAND_NAME" - Help with specific command

Examples:
- "commands" - List all CLI commands
- "search" - Search help and examples
- "ingest" - Content ingestion guidance
- "admin" - Administrative operations
- "--fetch-url" - Help with specific command

## Implementation Approach
This command uses **direct implementation** to provide interactive CLI guidance and command construction.

## Your Task

### 1. **Parse Arguments and Identify Help Topic**
   - Extract help topic from $ARGUMENTS
   - Determine user's specific needs
   - Provide comprehensive guidance for requested topic

### 2. **Command Reference and Help**

#### **Complete Command List**
When user requests "commands", provide:
```bash
# Core System Commands
rag-retriever --version                    # Show version
rag-retriever --init                       # Initialize configuration
rag-retriever --ui [--port PORT]           # Launch web interface

# Collection Management
rag-retriever --list-collections           # List all collections
rag-retriever --clean [--collection NAME]  # Delete collections/store

# Content Ingestion
rag-retriever --fetch-url URL [OPTIONS]    # Crawl websites
rag-retriever --ingest-file PATH           # Process single file
rag-retriever --ingest-directory PATH      # Process directory
rag-retriever --ingest-image PATH          # Analyze single image
rag-retriever --ingest-image-directory PATH # Process image directory
rag-retriever --github-repo URL [OPTIONS]  # Index GitHub repository
rag-retriever --confluence [OPTIONS]       # Load Confluence content

# Search Operations
rag-retriever --query "TEXT" [OPTIONS]     # Search content
rag-retriever --web-search "TEXT" [OPTIONS] # Search web

# Global Options
--verbose                                  # Enable verbose output
--collection NAME                          # Specify collection
--json                                     # JSON output format
```

#### **Search Operations Help**
```bash
# Basic search
rag-retriever --query "search terms"

# Collection-specific search
rag-retriever --query "search terms" --collection collection_name

# Cross-collection search
rag-retriever --query "search terms" --search-all-collections

# Advanced search options
rag-retriever --query "search terms" --limit 10 --score-threshold 0.4 --json

# Web search
rag-retriever --web-search "search terms" --results 10 --search-provider google
```

#### **Content Ingestion Help**
```bash
# Website crawling
rag-retriever --fetch-url "https://docs.example.com" --max-depth 3 --collection docs

# Local file processing
rag-retriever --ingest-file ~/document.pdf --collection documents
rag-retriever --ingest-directory ~/docs --collection all_docs

# Image analysis
rag-retriever --ingest-image ~/diagram.png --collection visuals
rag-retriever --ingest-image-directory ~/screenshots --collection ui_docs

# GitHub repository
rag-retriever --github-repo https://github.com/user/repo --file-extensions .py .md --collection source

# Confluence integration
rag-retriever --confluence --space-key "TECH" --collection confluence_docs
```

#### **Administrative Operations Help**
```bash
# List collections with details
rag-retriever --list-collections --verbose

# Delete specific collection
rag-retriever --clean --collection collection_name

# Nuclear option: delete all data
rag-retriever --clean

# System initialization
rag-retriever --init --verbose

# Launch web interface
rag-retriever --ui --port 8080
```

### 3. **Interactive Command Builder**

#### **Command Construction Workflow**
1. **Identify user goal** - What are they trying to accomplish?
2. **Recommend appropriate command** - Based on goal and content type
3. **Provide complete syntax** - Include all necessary parameters
4. **Explain options** - Describe optional parameters and their effects
5. **Include verification** - Show how to confirm the operation worked

#### **Context-Sensitive Help**
- **New user**: Start with `--init` and basic setup
- **Content ingestion**: Guide through appropriate ingestion method
- **Search problems**: Troubleshoot with different parameters
- **Administrative**: Provide safety warnings and verification steps

### 4. **Common Usage Examples**

#### **Getting Started**
```bash
# 1. Initialize system
rag-retriever --init

# 2. Index first content
rag-retriever --fetch-url "https://docs.python.org" --collection python_docs

# 3. Test search
rag-retriever --query "list comprehension" --collection python_docs

# 4. List collections
rag-retriever --list-collections
```

#### **Advanced Workflows**
```bash
# Multi-source documentation project
rag-retriever --fetch-url "https://docs.example.com" --collection web_docs
rag-retriever --github-repo https://github.com/example/repo --file-extensions .md --collection source_docs
rag-retriever --ingest-directory ~/local_docs --collection local_docs
rag-retriever --ingest-image-directory ~/diagrams --collection visual_docs

# Search across all sources
rag-retriever --query "installation process" --search-all-collections
```

#### **Administrative Tasks**
```bash
# Collection maintenance
rag-retriever --list-collections --verbose
rag-retriever --clean --collection outdated_docs
rag-retriever --fetch-url "https://updated-docs.com" --collection updated_docs

# System health check
rag-retriever --query "test" --search-all-collections --limit 1 --verbose
```

### 5. **Command Parameter Explanations**

#### **URL Fetching Parameters**
- `--fetch-url URL`: Target website to crawl
- `--max-depth N`: How deep to follow links (default: 2)
- `--collection NAME`: Target collection (creates if needed)
- `--verbose`: Show detailed processing information

#### **Search Parameters**
- `--query "TEXT"`: Search terms (required)
- `--limit N`: Maximum results (default: 8)
- `--score-threshold N`: Minimum relevance score (default: 0.3)
- `--collection NAME`: Search specific collection
- `--search-all-collections`: Search across all collections
- `--json`: Output results in JSON format

#### **Ingestion Parameters**
- `--ingest-file PATH`: Single file to process
- `--ingest-directory PATH`: Directory to process recursively
- `--ingest-image PATH`: Single image to analyze
- `--github-repo URL`: Repository URL to clone and index
- `--file-extensions EXT...`: Filter files by extension
- `--branch NAME`: Specific branch to process

### 6. **Troubleshooting Guidance**

#### **Common Issues and Solutions**
```bash
# Command not found
# Solution: Check installation and PATH

# API key errors
rag-retriever --init --verbose
# Edit config.yaml to add OpenAI API key

# No search results
rag-retriever --query "terms" --score-threshold 0.1 --verbose
# Lower threshold or re-index content

# Permission errors
ls -la ~/path/to/file
# Check file permissions

# Collection not found
rag-retriever --list-collections
# Verify collection name spelling
```

## Success Criteria
- Appropriate CLI command provided based on user needs
- Complete command syntax with all necessary parameters
- Clear explanations of options and their effects
- Troubleshooting guidance for common issues
- Verification steps included for confirming operations

## Your CLI Help Actions

**You CAN:**
- Provide complete CLI command syntax and examples
- Explain all command parameters and options
- Suggest appropriate workflows for different use cases
- Offer troubleshooting guidance for common issues
- Help construct commands for specific scenarios

**You CANNOT:**
- Execute CLI commands directly
- Access system configuration or files
- Modify or create collections
- Perform actual operations beyond providing guidance

## Command Categories

### Essential Commands (Start Here)
- `--init`: System setup
- `--fetch-url`: Basic content ingestion
- `--query`: Search functionality
- `--list-collections`: System status

### Advanced Commands (Power Users)
- `--ingest-*`: Local and rich content processing
- `--github-repo`: Code repository integration
- `--confluence`: Enterprise integration
- `--clean`: Administrative operations

### Utility Commands (Maintenance)
- `--ui`: Visual interface
- `--web-search`: External search
- `--verbose`: Debugging
- `--json`: Programmatic output

Remember: CLI provides full system control including administrative functions not available through MCP server. Always verify commands before execution, especially deletion operations.