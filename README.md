# RAG Retriever

A Python application that loads and processes web pages, local documents, images, GitHub repositories, and Confluence spaces, indexing their content using embeddings, and enabling semantic search queries. Built with a modular architecture using OpenAI embeddings and Chroma vector store. Now featuring support for Anthropic's Model Context Protocol (MCP), enabling direct integration with AI assistants like Cursor and Claude Desktop.

## What It Does

RAG Retriever enhances your AI coding assistant (like aider, Cursor, or Windsurf) by giving it access to:

- Documentation about new technologies and features
- Your organization's architecture decisions and coding standards
- Internal APIs and tools documentation
- GitHub repositories and their documentation
- Confluence spaces and documentation
- Visual content like architecture diagrams, UI mockups, and technical illustrations
- Any other knowledge that isn't part of the LLM's training data

This can help provide new knowledge to your AI tools, prevent hallucinations and ensure your AI assistant follows your team's practices.

> **💡 Note**: For detailed instructions on setting up and configuring your AI coding assistant with RAG Retriever, see our [AI Assistant Setup Guide](https://github.com/codingthefuturewithai/ai-assistant-instructions/blob/main/instructions/setup/ai-assistant-setup-guide.md).

## How It Works

RAG Retriever processes various types of content:

- Text documents and PDFs are chunked and embedded for semantic search
- Images are analyzed using AI vision models to generate detailed textual descriptions
- Web pages are crawled and their content is extracted
- GitHub repositories are indexed with their code and documentation
- Confluence spaces are indexed with their full content hierarchy

All content can be organized into collections for better organization and targeted searching. By default, searches are performed within the current collection, but you can also explicitly search across all collections using the `--search-all-collections` flag. For images, instead of returning the images themselves, it returns their AI-generated descriptions, making visual content searchable alongside your documentation.

[![Watch the video](https://img.youtube.com/vi/oQ6fSWUZYh0/0.jpg)](https://youtu.be/oQ6fSWUZYh0)

_RAG Retriever seamlessly integrating with aider, Cursor, and Windsurf to provide accurate, up-to-date information during development._

> **💡 Note**: While our examples focus on AI coding assistants, RAG Retriever can enhance any AI-powered development environment or tool that can execute command-line applications. Use it to augment IDEs, CLI tools, or any development workflow that needs reliable, up-to-date information.

## Why Do We Need Such Tools?

Modern AI coding assistants each implement their own way of loading external context from files and web sources. However, this creates several challenges:

- Knowledge remains siloed within each tool's ecosystem
- Support for different document types and sources varies widely
- Integration with enterprise knowledge bases (Confluence, Notion, etc.) is limited
- Each tool requires learning its unique context-loading mechanisms

RAG Retriever solves these challenges by:

1. Providing a unified knowledge repository that can ingest content from diverse sources
2. Offering both a command-line interface and a Model Context Protocol (MCP) server that work with any AI tool supporting shell commands or MCP integration
3. Supporting collections to organize and manage content effectively

> **💡 For a detailed discussion** of why centralized knowledge retrieval tools are crucial for AI-driven development, see our [Why RAG Retriever](docs/why-rag-retriever.md) guide.

## Prerequisites

### Core Requirements

- Python 3.10-3.12 (Download from [python.org](https://python.org))
- **Windows Users Only**: Visual Studio C++ Build Tools
  - Download from [Visual Studio Downloads](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
  - Install with "Desktop development with C++" workload
  - Required for ChromaDB and other dependencies
- Git (Required for core functionality)
  - **Windows**: Download from [Git for Windows](https://git-scm.com/download/windows)
    - During installation, select "Git from the command line and also from 3rd-party software"
    - Choose "Use Windows' default console window"
  - **macOS**: `brew install git`
  - **Linux**: Use your distribution's package manager (e.g., `apt install git` or `dnf install git`)
- One of these package managers:

  - pipx (Recommended, install with one of these commands):

    ```bash
    # On MacOS
    brew install pipx

    # On Windows/Linux
    python -m pip install --user pipx
    ```

  - uv (Alternative, faster installation):

    ```bash
    # On MacOS
    brew install uv

    # On Windows/Linux
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

---

> ### 🚀 Ready to Try It? Let's Go!
>
> **Get up and running in 10 minutes!**
>
> 1. Install RAG Retriever using one of these methods:
>
>    ```bash
>    # Using pipx (recommended for isolation)
>    pipx install rag-retriever
>
>    # Using uv (faster installation)
>    uv pip install --system rag-retriever
>    ```
>
> 2. Configure your AI coding assistant by following our [AI Assistant Setup Guide](https://github.com/codingthefuturewithai/ai-assistant-instructions/blob/main/instructions/setup/ai-assistant-setup-guide.md)
> 3. Start using RAG Retriever with your configured AI assistant!
>
> For detailed installation and configuration steps, see our [Getting Started Guide](docs/getting-started.md).

---

### Optional Dependencies

The following dependencies are only required for specific advanced PDF processing features:

**MacOS**: `brew install tesseract`
**Windows**: Install [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

### System Requirements

The application supports multiple web crawling backends:

**Playwright Crawler** (Default):
- Chromium browser is automatically installed during package installation
- Sufficient disk space for Chromium (~200MB)
- Internet connection for initial setup and crawling

**Crawl4AI Crawler** (Alternative, 20x faster):
- Chromium browser (automatically installed via Playwright)
- Additional system dependencies for optimal performance
- Configured via `crawler.type: "crawl4ai"` in config.yaml

**System-Level Dependencies**:
- Git (Required for core functionality, GitHub integration)
- At least one working crawler (Playwright OR Crawl4AI) must be available
- All dependencies are validated at startup with clear error messages

Note: The application will automatically download and manage Chromium installation. System validation occurs before any configuration is used to ensure all required tools are available.

## Installation

Install RAG Retriever as a standalone application:

```bash
pipx install rag-retriever
```

This will:

- Create an isolated environment for the application
- Install all required dependencies
- Install Chromium browser automatically
- Make the `rag-retriever` command available in your PATH

## How to Upgrade

To upgrade RAG Retriever to the latest version, use the same package manager you used for installation:

```bash
# If installed with pipx
pipx upgrade rag-retriever

# If installed with uv
uv pip install --system --upgrade rag-retriever
```

Both methods will:

- Upgrade the package to the latest available version
- Preserve your existing configuration and data
- Update any new dependencies automatically

After upgrading, it's recommended to reinitialize the configuration to ensure you have any new settings:

```bash
# Initialize configuration files
rag-retriever --init
```

This creates a configuration file at `~/.config/rag-retriever/config.yaml` (Unix/Mac) or `%APPDATA%\rag-retriever\config.yaml` (Windows)

### Setting up your API Key

Add your OpenAI API key to your configuration file:

```yaml
api:
  openai_api_key: "sk-your-api-key-here"
```

> **Security Note**: During installation, RAG Retriever automatically sets strict file permissions (600) on `config.yaml` to ensure it's only readable by you. This helps protect your API key.

### Customizing Configuration

All settings are in `config.yaml`. For detailed information about all configuration options, best practices, and example configurations, see our [Configuration Guide](docs/configuration-guide.md).

### Data Storage

The vector store database and collections are stored at:

- Unix/Mac: `~/.local/share/rag-retriever/chromadb/`
- Windows: `%LOCALAPPDATA%\rag-retriever\chromadb/`

Each collection is stored in its own subdirectory, with collection metadata maintained in a central metadata file. This location is automatically managed by the application and should not be modified directly.

## Knowledge Management Web Interface

![RAG Retriever UI](docs/images/rag-retriever-UI-collections.png)

RAG Retriever includes a modern web interface intended to help you manage your knowledge store. The UI provides:

- Collection management with statistics and comparisons
- Semantic search with relevance scoring
- Interactive visualizations of collection metrics

To launch the UI:

```bash
# If installed via pipx or uv
rag-retriever --ui

# If running from local repository
python scripts/run_ui.py
```

For detailed instructions on using the interface, see our [RAG Retriever UI User Guide](docs/rag-retriever-ui-guide.md).

### Uninstallation

To completely remove RAG Retriever:

```bash
# Remove the application and its isolated environment
pipx uninstall rag-retriever

# Remove Playwright browsers
python -m playwright uninstall chromium

# Optional: Remove configuration and data files
# Unix/Mac:
rm -rf ~/.config/rag-retriever ~/.local/share/rag-retriever
# Windows (run in PowerShell):
Remove-Item -Recurse -Force "$env:APPDATA\rag-retriever"
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\rag-retriever"
```

### Development Setup

If you want to contribute to RAG Retriever or modify the code:

```bash
# Clone the repository
git clone https://github.com/codingthefuturewithai/rag-retriever.git
cd rag-retriever

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Unix/Mac
venv\Scripts\activate     # Windows

# Install in editable mode
pip install -e .

# Initialize user configuration
./scripts/run-rag.sh --init  # Unix/Mac
scripts\run-rag.bat --init   # Windows
```

## Collections

RAG Retriever organizes content into collections, allowing you to:

- Group related content together (e.g., by project, team, or topic)
- Search within specific collections or across all collections
- Manage and clean up collections independently
- Track metadata like creation date, last modified, and document counts

### Collection Features

- **Default Collection**: All content goes to the 'default' collection unless specified otherwise
- **Collection Management**:
  - Create collections automatically by specifying a name
  - List all collections and their metadata
  - Delete specific collections while preserving others
  - Search within a specific collection or across all collections
- **Collection Metadata**:
  - Creation timestamp
  - Last modified timestamp
  - Document count
  - Total chunks processed
  - Optional description

### Using Collections

All commands support specifying a collection:

```bash
# List all collections
rag-retriever --list-collections

# Add content to a specific collection
rag-retriever --fetch-url https://example.com --collection docs
rag-retriever --ingest-file document.md --collection project-x
rag-retriever --github-repo https://github.com/org/repo.git --collection code-docs

# Search within a specific collection
rag-retriever --query "search term" --collection docs

# Search across all collections
rag-retriever --query "search term" --search-all-collections

# Delete a specific collection
rag-retriever --clean --collection old-docs
```

## Usage Examples

### Local Document Processing

```bash
# Process a single file
rag-retriever --ingest-file path/to/document.pdf

# Process all supported files in a directory
rag-retriever --ingest-directory path/to/docs/

# Enable OCR for scanned documents (update config.yaml first)
# Set in config.yaml:
# document_processing.pdf_settings.ocr_enabled: true
rag-retriever --ingest-file scanned-document.pdf

# Enable image extraction from PDFs (update config.yaml first)
# Set in config.yaml:
# document_processing.pdf_settings.extract_images: true
rag-retriever --ingest-file document-with-images.pdf
```

### Web Content Fetching

```bash
# Basic fetch
rag-retriever --fetch https://example.com

# With depth control (default: 2)
rag-retriever --fetch https://example.com --max-depth 2

# Enable verbose output
rag-retriever --fetch https://example.com --verbose
```

### Image Analysis

```bash
# Analyze and index a single image
rag-retriever --ingest-image diagrams/RAG-Retriever-architecture.png

# Process all images in a directory
rag-retriever --ingest-image-directory diagrams/system-design/

# Search for specific architectural details
rag-retriever --query "How does RAG Retriever handle different types of document processing in its architecture?"
rag-retriever --query "What components are responsible for vector storage in the RAG Retriever system?"

# Combine with other content in searches
rag-retriever --query "Compare the error handling approach shown in the RAG Retriever architecture with the approach used by the latest LangChain framework"
```

The image analysis feature uses AI vision models to create detailed descriptions of your visual content, making it searchable alongside your documentation. When you search, you'll receive relevant text descriptions of the images rather than the images themselves.

### Web Search

```bash
# Search the web using DuckDuckGo
rag-retriever --web-search "your search query"

# Control number of results
rag-retriever --web-search "your search query" --results 10
```

### Confluence Integration

RAG Retriever can load and index content directly from your Confluence spaces. To use this feature:

1. Configure your Confluence credentials in `~/.config/rag-retriever/config.yaml`:

```yaml
api:
  confluence:
    url: "https://your-domain.atlassian.net" # Your Confluence instance URL
    username: "your-email@example.com" # Your Confluence username/email
    api_token: "your-api-token" # API token from https://id.atlassian.com/manage-profile/security/api-tokens
    space_key: null # Optional: Default space to load from
    parent_id: null # Optional: Default parent page ID
    include_attachments: false # Whether to include attachments
    limit: 50 # Max pages per request
    max_pages: 1000 # Maximum total pages to load
```

2. Load content from Confluence:

```bash
# Load from configured default space
rag-retriever --confluence

# Load from specific space
rag-retriever --confluence --space-key TEAM

# Load from specific parent page
rag-retriever --confluence --parent-id 123456

# Load from specific space and parent
rag-retriever --confluence --space-key TEAM --parent-id 123456
```

The loaded content will be:

- Converted to markdown format
- Split into appropriate chunks
- Embedded and stored in your vector store
- Available for semantic search just like any other content

### Searching Content

```bash
# Basic search
rag-retriever --query "How do I configure logging?"

# Limit results
rag-retriever --query "deployment steps" --limit 5

# Set minimum relevance score
rag-retriever --query "error handling" --score-threshold 0.7

# Get full content (default) or truncated
rag-retriever --query "database setup" --truncate

# Output in JSON format
rag-retriever --query "API endpoints" --json
```

### GitHub Repository Integration

```bash
# Load a GitHub repository
rag-retriever --github-repo https://github.com/username/repo.git

# Load a specific branch
rag-retriever --github-repo https://github.com/username/repo.git --branch main

# Load only specific file types
rag-retriever --github-repo https://github.com/username/repo.git --file-extensions .py .md .js
```

The GitHub loader:

- Clones repositories to a temporary directory
- Automatically cleans up after processing
- Supports branch selection
- Filters files by extension
- Excludes common non-documentation paths (node_modules, **pycache**, etc.)
- Enforces file size limits for better processing

## Understanding Search Results

Search results include relevance scores based on cosine similarity:

- Scores range from 0 to 1, where 1 indicates perfect similarity
- Default threshold is 0.3 (configurable via `search.default_score_threshold`)
- Typical interpretation:
  - 0.7+: Very high relevance (nearly exact matches)
  - 0.6 - 0.7: High relevance
  - 0.5 - 0.6: Good relevance
  - 0.3 - 0.5: Moderate relevance
  - Below 0.3: Lower relevance

## Notes

- Uses OpenAI's text-embedding-3-large model for generating embeddings by default
- Content is automatically cleaned and structured during indexing
- Implements URL depth-based crawling control
- Vector store persists between runs unless explicitly deleted
- Uses cosine similarity for more intuitive relevance scoring
- Minimal output by default with `--verbose` flag for troubleshooting
- Full content display by default with `--truncate` option for brevity
- ⚠️ Changing chunk size/overlap settings after ingesting content may lead to inconsistent search results. Consider reprocessing existing content if these settings must be changed.

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Command Line Options

Core options:

- `--version`: Show version information
- `--init`: Initialize user configuration files
- `--clean`: Clean (delete) the vector store
- `--verbose`: Enable verbose output for troubleshooting
- `--json`: Output results in JSON format

Content Search:

- `--query STRING`: Search query to find relevant content
- `--limit N`: Maximum number of results to return
- `--score-threshold N`: Minimum relevance score threshold
- `--truncate`: Truncate content in search results (default: show full content)

Web Content:

- `--fetch URL`: Fetch and index web content
- `--max-depth N`: Maximum depth for recursive URL loading (default: 2)
- `--web-search STRING`: Perform DuckDuckGo web search
- `--results N`: Number of web search results (default: 5)

File Processing:

- `--ingest-file PATH`: Ingest a local file (supports .pdf, .md, .txt)
- `--ingest-directory PATH`: Ingest a directory of files

Image Processing:

- `--ingest-image PATH`: Path to an image file or URL to analyze and ingest
- `--ingest-image-directory PATH`: Path to a directory containing images to analyze and ingest

GitHub Integration:

- `--github-repo URL`: URL of the GitHub repository to load
- `--branch STRING`: Specific branch to load from the repository (default: main)
- `--file-extensions EXT [EXT ...]`: Specific file extensions to load (e.g., .py .md .js)

Confluence Integration:

- `--confluence`: Load from Confluence
- `--space-key STRING`: Confluence space key
- `--parent-id STRING`: Confluence parent page ID

## Web Search Integration

RAG Retriever supports multiple search providers for retrieving web content:

### Default Search Provider

By default, RAG Retriever will try to use Google Search if configured, falling back to DuckDuckGo if Google credentials are not available. You can change the default provider in your `config.yaml`:

```yaml
search:
  default_provider: "google" # or "duckduckgo"
```

### Using Google Search

To use Google's Programmable Search Engine:

1. Set up Google Search credentials (one of these methods):

   ```bash
   # Environment variables (recommended for development)
   export GOOGLE_API_KEY=your_api_key
   export GOOGLE_CSE_ID=your_cse_id

   # Or in config.yaml (recommended for permanent setup)
   search:
     google_search:
       api_key: "your_api_key"
       cse_id: "your_cse_id"
   ```

2. Use Google Search:

   ```bash
   # Use default provider (will use Google if configured)
   rag-retriever --web-search "your query"

   # Explicitly request Google
   rag-retriever --web-search "your query" --search-provider google
   ```

### Using DuckDuckGo Search

DuckDuckGo search is always available and requires no configuration:

```bash
# Use DuckDuckGo explicitly
rag-retriever --web-search "your query" --search-provider duckduckgo
```

### Provider Selection Behavior

- When no provider is specified:
  - Uses the default_provider from config
  - If Google is default but not configured, silently falls back to DuckDuckGo
- When Google is explicitly requested but not configured:
  - Shows error message suggesting to use DuckDuckGo
- When DuckDuckGo is requested:
  - Uses DuckDuckGo directly

For detailed configuration options and setup instructions, see our [Configuration Guide](docs/configuration-guide.md#search-provider-configuration).

## MCP Integration (Experimental)

RAG Retriever provides support for Anthropic's Model Context Protocol (MCP), enabling AI assistants to directly leverage its retrieval capabilities. The MCP integration currently offers a focused set of core features, with ongoing development to expand the available functionality.

### Currently Supported MCP Features

**Search Operations**

- Web search using DuckDuckGo

  - Customizable number of results
  - Results include titles, URLs, and snippets
  - Markdown-formatted output

- Vector store search
  - Semantic search across indexed content
  - Search within specific collections
  - Search across all collections simultaneously
  - Configurable result limits
  - Score threshold filtering
  - Full or partial content retrieval
  - Source attribution with collection information
  - Markdown-formatted output with relevance scores

**Content Processing**

- URL content processing
  - Fetch and ingest web content
  - Store content in specific collections
  - Automatically extract and clean text content
  - Store processed content in vector store for semantic search
  - Support for recursive crawling with depth control

### Server Modes

RAG Retriever's MCP server supports multiple operation modes:

1. **stdio Mode** (Default)

   - Used by Cursor and Claude Desktop integrations
   - Communicates via standard input/output
   - Configure as shown in the integration guides below

2. **SSE Mode**

   - Runs as a web server with Server-Sent Events
   - Useful for web-based integrations or development
   - Start with:

   ```bash
   python rag_retriever/mcp/server.py --port 3001
   ```

3. **Debug Mode**
   - Uses the MCP Inspector for testing and development
   - Helpful for debugging tool implementations
   - Start with:
   ```bash
   mcp dev rag_retriever/mcp/server.py
   ```

### Cursor Integration

1. First install RAG Retriever following the installation instructions above.

2. Get the full path to the MCP server:

```bash
which mcp-rag-retriever
```

This will output something like `/Users/<username>/.local/bin/mcp-rag-retriever`

3. Configure Cursor:
   - Open Cursor Settings > Features > MCP Servers
   - Click "+ Add New MCP Server"
   - Configure the server:
     - Name: rag-retriever
     - Type: stdio
     - Command: [paste the full path from step 2]

For more details about MCP configuration in Cursor, see the [Cursor MCP documentation](https://docs.cursor.com/context/model-context-protocol).

### Claude Desktop Integration

1. First install RAG Retriever following the installation instructions above.

2. Get the full path to the MCP server:

```bash
which mcp-rag-retriever
```

This will output something like `/Users/<username>/.local/bin/mcp-rag-retriever`

3. Configure Claude Desktop:
   - Open Claude menu > Settings > Developer > Edit Config
   - Add RAG Retriever to the MCP servers configuration:

```json
{
  "mcpServers": {
    "rag-retriever": {
      "command": "/Users/<username>/.local/bin/mcp-rag-retriever"
    }
  }
}
```

For more details, see the [Claude Desktop MCP documentation](https://modelcontextprotocol.io/quickstart/user#for-claude-desktop-users).
