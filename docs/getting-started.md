# Getting Started with RAG Retriever

This guide will walk you through installing RAG Retriever, loading your first documentation, and testing it with AI coding assistants.

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
   > - Web content crawling
   > - Basic PDF text extraction
   > - Markdown processing
   > - Vector storage and search
   > - Confluence space integration
   > - DuckDuckGo web search

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

Let's load some documentation about Java 23's new features to test the setup. Open a new terminal and run:

```bash
rag-retriever --fetch https://www.happycoders.eu/java/java-23-features --max-depth 0
```

You should see output similar to this:

```
INFO:rag_retriever.main:
Starting content fetch and indexing process...
INFO:rag_retriever.main:Starting crawl operation...
INFO:rag_retriever.crawling.playwright_crawler:Starting crawl of https://www.happycoders.eu/java/java-23-features
INFO:rag_retriever.crawling.playwright_crawler:Processed document: https://www.happycoders.eu/java/java-23-features
INFO:rag_retriever.crawling.playwright_crawler:Completed crawl: processed 1 documents
INFO:rag_retriever.main:
Indexing documents...
INFO:rag_retriever.vectorstore.store:Processing 1 documents (total size: 11268 chars) into 10 chunks (total size: 11847 chars)
INFO:rag_retriever.vectorstore.store:Successfully added 39 chunks to vector store
INFO:rag_retriever.main:Indexing complete.
```

This indicates that the content was successfully fetched, processed into chunks, and indexed in the vector store.

### Verifying the Content

Let's verify that the content was properly indexed by running a search query:

```bash
rag-retriever --query "Java 23 Markdown Documentation Comments JavaDoc syntax" --score-threshold 0.5
```

You should see output similar to this:

```
INFO:rag_retriever.main:
Starting content search...
1.
Source: https://www.happycoders.eu/java/java-23-features
Relevance Score: 0.6636
Content: ## Markdown Documentation Comments – JEP 467

To format JavaDoc comments, we have always had to use HTML. This was undoubtedly a good choice in 1995, but nowadays, Markdown is much more popular than HTML for writing documentation.

JDK Enhancement Proposal 467 allows us to write JavaDoc comments in Markdown from Java 23 onwards.
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

## Configuring AI Assistants

Now let's set up your AI coding assistants to use RAG Retriever. You can use aider, Cursor, Windsurf, or any combination of these tools.

### Option 1: Setting up Aider

1. Install aider if you haven't already:

   ```bash
   pipx install aider-chat
   ```

2. Follow the [Configuring Aider](./coding-assistants/configuring-ai-assistants.md#configuring-aider) instructions to set up the RAG Retriever integration.

3. Start a new aider session (the --no-stream flag is optional, but recommended for testing):

   ```bash
   aider --sonnet --no-stream
   ```

4. Test the integration with this prompt:
   ```
   Show me how to write a class documentation comment using Java 23's new Markdown syntax
   ```

### Option 2: Setting up Cursor

1. Download and install [Cursor](https://cursor.sh/)

2. Follow the [Configuring Cursor](./coding-assistants/configuring-ai-assistants.md#configuring-cursor) instructions to set up the RAG Retriever integration.

3. Open a new project in Cursor and test the integration with the same prompt:
   ```
   Show me how to write a class documentation comment using Java 23's new Markdown syntax
   ```

### Option 3: Setting up Windsurf

1. Download and install [Windsurf](https://codeium.com/windsurf)

2. Follow the [Configuring Windsurf](./coding-assistants/configuring-ai-assistants.md#configuring-windsurf) instructions to set up the RAG Retriever integration.

3. Open a new project in Windsurf and test the integration with the same prompt:
   ```
   Show me how to write a class documentation comment using Java 23's new Markdown syntax
   ```

## What to Expect

When you run the test prompt, your AI assistant should:

1. Recognize that it needs to verify its knowledge about Java 23's Markdown documentation syntax
2. Use RAG Retriever to search the documentation you loaded
3. Find relevant information about the feature
4. Provide an accurate response based on the retrieved documentation

> **Note about LLM Training Data**: If you're using an LLM trained on data after September 2023, it may already have knowledge of Java 23 features. In this case, you'll need to find documentation about even newer technologies or features to properly test the RAG Retriever integration. Look for announcements, beta features, or release candidates that were published after your LLM's training cutoff date.

If the assistant doesn't automatically use RAG Retriever, you can:

1. Remind it: "Please verify your knowledge about [feature/version] using RAG Retriever before proceeding."
2. Try a different example using more recent technology features
3. Ask about a very specific implementation detail that's only documented in your loaded content

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
   --init                 Initialize user configuration files
   --fetch URL           Fetch and index web content
   --max-depth N         Maximum depth for recursive URL loading (default: 2)
   --query STRING        Search query to find relevant content
   --limit N             Maximum number of results to return
   --score-threshold N   Minimum relevance score threshold
   --truncate            Truncate content in search results
   --json               Output results in JSON format
   --clean              Clean (delete) the vector store
   --verbose            Enable verbose output for troubleshooting
   --ingest-file PATH   Ingest a local file
   --ingest-directory PATH  Ingest a directory of files
   --web-search STRING  Perform DuckDuckGo web search
   --results N          Number of web search results (default: 5)
   --confluence         Load from Confluence
   --space-key STRING   Confluence space key
   --parent-id STRING   Confluence parent page ID
   ```

3. Review the [full configuration guide](./configuration-guide.md) for detailed setup options

## Troubleshooting

- If queries return no results, make sure you've successfully loaded documentation using `--fetch` or `--ingest` commands
- If the AI assistant isn't using RAG Retriever, verify you've copied the complete instructions and restarted the assistant
- For more help, see the [Expected Behavior](./coding-assistants/configuring-ai-assistants.md#expected-behavior) section of the configuration guide
