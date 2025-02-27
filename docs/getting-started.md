# Getting Started with RAG Retriever

This guide will walk you through installing RAG Retriever and loading your first documentation.

## Prerequisites

Before installing RAG Retriever, ensure you have the following requirements installed:

1. **Python 3.10-3.12**: Download from [python.org](https://python.org)

2. **Git**: Required for core functionality and GitHub integration

   - **Windows**: Download from [Git for Windows](https://git-scm.com/download/windows)
     - During installation, select "Git from the command line and also from 3rd-party software"
     - Choose "Use Windows' default console window"
   - **macOS**: Install via `brew install git`
   - **Linux**: Use your distribution's package manager (e.g., `apt install git` or `dnf install git`)

3. **Windows Users Only**: Visual Studio C++ Build Tools
   - Download from [Visual Studio Downloads](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
   - Install with "Desktop development with C++" workload
   - Required for ChromaDB and other dependencies

## Installation

1. Install RAG Retriever using pipx:

   ```bash
   # On MacOS
   brew install pipx
   pipx install rag-retriever

   # On Windows/Linux
   python -m pip install --user pipx
   pipx install rag-retriever
   ```

   > **Core Features**: The basic installation includes everything needed for:
   >
   > - Web content crawling and indexing
   > - Basic PDF text extraction
   > - Markdown and text file processing
   > - Vector storage and semantic search
   > - Confluence space integration
   > - DuckDuckGo web search
   > - GitHub repository integration
   > - Basic image analysis and indexing
   > - JSON output formatting
   > - Configurable relevance scoring
   > - Local file and directory processing

   > **Optional Features**: If you need advanced features, install additional dependencies:
   >
   > **For OCR Support** (scanned documents & image text extraction):
   >
   > - MacOS: `brew install tesseract`
   > - Windows: [Install Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
   >
   > **For Advanced PDF Processing** (complex layouts & tables):
   >
   > - MacOS: `brew install poppler`
   > - Windows: [Install Poppler](https://github.com/oschwartz10612/poppler-windows/releases/)
   >
   > Note: Install these only if you need their specific features. The core functionality works without them.

2. Initialize the configuration:

   ```bash
   rag-retriever --init
   ```

3. Add your OpenAI API key to the config file at `~/.config/rag-retriever/config.yaml`:

   ```yaml
   api:
     openai_api_key: "sk-your-api-key-here"
   ```

   > **Security Note**: During installation, RAG Retriever automatically sets strict file permissions (600) on `config.yaml` to ensure it's only readable by you. This helps protect your API key.

## Loading Your First Documentation

Let's load some documentation to test the setup. We'll try both web documentation and a GitHub repository:

### Loading Web Documentation

```bash
rag-retriever --fetch https://www.happycoders.eu/java/java-23-features --max-depth 0
```

### Loading a GitHub Repository

```bash
# Load a popular open-source repository
rag-retriever --github-repo https://github.com/openai/openai-quickstart-python.git

# You can also specify a branch and file types
rag-retriever --github-repo https://github.com/openai/openai-python.git --branch main --file-extensions .py .md

# Example with a larger repository
rag-retriever --github-repo https://github.com/langchain-ai/langchain.git --branch master --file-extensions .py .md
```

### Processing Images

```bash
# Process a single image (e.g., architecture diagram)
rag-retriever --ingest-image diagrams/system-architecture.png

# Process all images in a directory
rag-retriever --ingest-image-directory docs/diagrams/

# Process an image from a URL
rag-retriever --ingest-image https://example.com/images/diagram.png
```

When processing images, RAG Retriever:

- Analyzes the image content using AI vision models
- Generates detailed textual descriptions
- Makes visual content searchable alongside your documentation
- Supports common image formats (PNG, JPG, JPEG, GIF, WEBP)
- Can process both local files and image URLs

> **Note**: Image processing settings like the vision model and token limits are configured in your `config.yaml` file. See the [configuration guide](./configuration-guide.md) for details.

You should see output similar to this:

```
INFO:rag_retriever.document_processor.github_loader:Loading GitHub repository: https://github.com/openai/openai-quickstart-python.git
INFO:rag_retriever.vectorstore.store:Processing 5 documents (total size: 17054 chars) into 12 chunks
INFO:rag_retriever.vectorstore.store:Successfully added chunks to vector store
```

### Verifying the Content

Let's verify that the content was properly indexed by running search queries:

```bash
# Search web documentation
rag-retriever --query "Java 23 Markdown Documentation Comments JavaDoc syntax" --score-threshold 0.5

# Search GitHub repository content
rag-retriever --query "How to use the OpenAI API client" --score-threshold 0.5
```

The high relevance score (0.6636) indicates that the content was successfully indexed and is highly relevant to our query.

> **💡 TIP**: While these examples focus on new technology features, RAG Retriever is valuable for any knowledge that isn't part of the LLM's training data. This includes:
>
> - Your organization's architecture decisions and patterns
> - Team-specific coding conventions and best practices
> - Internal tech stack preferences and standards
> - Project-specific implementation details
> - Private APIs or internal tools documentation
> - Company-specific business logic and requirements

## Using with AI Coding Assistants

RAG Retriever is designed to work with various AI coding assistants. For detailed instructions on setting up and configuring your preferred AI coding assistant with RAG Retriever, please refer to our [AI Assistant Setup Guide](https://github.com/codingthefuturewithai/ai-assistant-instructions/blob/main/instructions/setup/ai-assistant-setup-guide.md).

## Next Steps

1. Load more documentation relevant to your projects:

   ```bash
   # Web documentation
   rag-retriever --fetch URL --max-depth DEPTH

   # Local files
   rag-retriever --ingest-file PATH
   rag-retriever --ingest-directory PATH

   # Web search (using DuckDuckGo)
   rag-retriever --web-search "your search query" --results 5

   # You can then fetch content from the web search results using --fetch
   rag-retriever --fetch https://found-url-from-search.com --max-depth 0

   # Load from Confluence (requires configuration in ~/.config/rag-retriever/config.yaml)
   rag-retriever --confluence --space-key TEAM

   # Clean up vector store if needed
   rag-retriever --clean
   ```

2. Explore all available options:

   ```bash
   # Core options
   --init                Initialize user configuration files in standard locations
   --fetch URL          URL to fetch and index
   --max-depth N        Maximum depth for recursive URL loading (default: 2)
   --query STRING       Search query to find relevant content
   --limit N            Maximum number of results to return
   --score-threshold N  Minimum relevance score threshold
   --truncate           Truncate content in search results (default: show full content)
   --json              Output results in JSON format
   --clean             Clean (delete) the vector store
   --verbose           Enable verbose output for troubleshooting

   # File ingestion options
   --ingest-file PATH          Path to a local markdown or text file to ingest
   --ingest-directory PATH     Path to a directory containing markdown and text files to ingest

   # Image processing options
   --ingest-image PATH         Path to an image file or URL to analyze and ingest
   --ingest-image-directory PATH  Path to a directory containing images to analyze and ingest

   # Web search options
   --web-search STRING     Perform a web search query
   --search-provider STRING  Search provider to use (choices: duckduckgo, google; default: duckduckgo)
   --results N            Number of results to return for web search (default: 5)

   # GitHub options
   --github-repo URL     URL of the GitHub repository to load
   --branch STRING       Specific branch to load from the repository
   --file-extensions EXT [EXT ...]  Specific file extensions to load (e.g., .py .md .js)

   # Confluence options
   --confluence          Load content from Confluence using configured settings
   --space-key STRING    Confluence space key to load content from
   --parent-id STRING    Confluence parent page ID to start loading from
   ```

3. Review the [full configuration guide](./configuration-guide.md) for detailed setup options

## Troubleshooting

If you're experiencing issues:

- Verify that content was successfully loaded using `--fetch` or `--ingest` commands
- Check the [configuration guide](./configuration-guide.md) for proper setup
- Use the `--verbose` flag for detailed logging output
- Make sure your OpenAI API key is correctly configured
- For AI assistant integration issues, refer to the [AI Assistant Setup Guide](https://github.com/codingthefuturewithai/ai-assistant-instructions/blob/main/instructions/setup/ai-assistant-setup-guide.md)

## Optional Features

### Google Search Integration

RAG Retriever supports Google's Programmable Search Engine as an alternative to the default DuckDuckGo search. To use Google Search, you'll need to:

1. Set up Google Search credentials (one of the following methods):

   a. Environment variables (recommended for development):

   ```bash
   export GOOGLE_API_KEY=your_api_key
   export GOOGLE_CSE_ID=your_cse_id
   ```

   b. Configuration file (recommended for permanent setup):

   ```yaml
   # In ~/.config/rag-retriever/config.yaml
   search:
     google_search:
       api_key: "your_api_key"
       cse_id: "your_cse_id"
   ```

   c. Command-line arguments (for one-time use):

   ```bash
   rag-retriever --web-search "your query" \
                 --search-provider google \
                 --google-api-key "your_api_key" \
                 --google-cse-id "your_cse_id"
   ```

2. Use Google Search:

   ```bash
   # Using credentials from config or environment
   rag-retriever --web-search "your query" --search-provider google

   # Or specify credentials directly (overrides config and environment)
   rag-retriever --web-search "your query" \
                 --search-provider google \
                 --google-api-key "your_api_key" \
                 --google-cse-id "your_cse_id"
   ```

3. For programmatic use:

   ```python
   from rag_retriever.search import web_search

   # Using credentials from config or environment
   results = web_search("your query", provider="google")

   # Process results
   for result in results:
       print(f"Title: {result.title}")
       print(f"URL: {result.url}")
       print(f"Snippet: {result.snippet}")
   ```

Credential Priority:

1. Command-line arguments (highest priority)
2. Environment variables
3. Configuration file
4. Falls back to DuckDuckGo if no valid credentials found

# Example web search commands:

# Using default DuckDuckGo search

rag-retriever --web-search "your search query" --results 5

# Using Google search (requires GOOGLE_API_KEY and GOOGLE_CSE_ID environment variables)

rag-retriever --web-search "your search query" --search-provider google --results 5

# You can then fetch content from the web search results using --fetch

rag-retriever --fetch https://found-url-from-search.com --max-depth 0
