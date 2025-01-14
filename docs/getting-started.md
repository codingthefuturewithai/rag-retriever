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

   Alternatively, you can set it as an environment variable:

   ```bash
   export OPENAI_API_KEY="sk-your-api-key-here"
   ```

   Note: When using with Cursor, adding the key to `config.yaml` is the most reliable method.

## Loading Your First Documentation

Let's load some documentation about Angular 18.1's new features to test the setup. Open a new terminal and run:

```bash
rag-retriever --fetch https://blog.ninja-squad.com/2024/07/10/what-is-new-angular-18.1 --max-depth 0
```

You should see output similar to this:

```
INFO:rag_retriever.main:
Starting content fetch and indexing process...
INFO:rag_retriever.main:Starting crawl operation...
INFO:rag_retriever.crawling.playwright_crawler:Starting crawl of https://blog.ninja-squad.com/2024/07/10/what-is-new-angular-18.1
INFO:rag_retriever.crawling.playwright_crawler:Processed document: https://blog.ninja-squad.com/2024/07/10/what-is-new-angular-18.1
INFO:rag_retriever.crawling.playwright_crawler:Completed crawl: processed 1 documents
INFO:rag_retriever.main:
Indexing documents...
INFO:rag_retriever.vectorstore.store:Processing 1 documents (total size: 11268 chars) into 10 chunks (total size: 11847 chars)
INFO:rag_retriever.vectorstore.store:Successfully added 10 chunks to vector store
INFO:rag_retriever.main:Indexing complete.
```

This indicates that the content was successfully fetched, processed into chunks, and indexed in the vector store.

### Verifying the Content

Let's verify that the content was properly indexed by running a search query:

```bash
rag-retriever --query "Angular 18.1 @let syntax template usage" --score-threshold 0.5
```

You should see output similar to this:

```
INFO:rag_retriever.main:
Starting content search...
1.
Source: https://blog.ninja-squad.com/2024/07/10/what-is-new-angular-18.1
Relevance Score: 0.7260
Content: ## @let syntax

The main feature of this release is undoubtedly the new
@let
 syntax in Angular templates.
This new syntax (in developer preview) allows you to define a template variable in the template itself,
without having to declare it in the component class.
```

The high relevance score (0.7260) indicates that the content was successfully indexed and is highly relevant to our query.

> **💡 TIP**: While these examples focus on new technology features, RAG Retriever is valuable for any knowledge that isn't part of the LLM's training data. This includes:
>
> - Your organization's architecture decisions and patterns
> - Team-specific coding conventions and best practices
> - Internal tech stack preferences and standards
> - Project-specific implementation details
> - Private APIs or internal tools documentation
> - Company-specific business logic and requirements

## Configuring AI Assistants

Now let's set up your AI coding assistants to use RAG Retriever. You can use either aider or Cursor (or both).

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
   Create an Angular 18.1 component using the new @let syntax
   ```

### Option 2: Setting up Cursor

1. Download and install [Cursor](https://cursor.sh/)

2. Follow the [Configuring Cursor](./coding-assistants/configuring-ai-assistants.md#configuring-cursor) instructions to set up the RAG Retriever integration.

3. Open a new project in Cursor and test the integration with the same prompt:
   ```
   Create an Angular 18.1 component using the new @let syntax
   ```

## What to Expect

When you run the test prompt, your AI assistant should:

1. Recognize that it needs to verify its knowledge about Angular 18.1's @let syntax
2. Use RAG Retriever to search the documentation you loaded
3. Find relevant information about the feature
4. Provide an accurate response based on the retrieved documentation

> **Note about LLM Training Data**: If you're using an LLM trained on data after April 2024, it may already have knowledge of Angular 18.1 and Java 23 features. In this case, you'll need to find documentation about even newer technologies or features to properly test the RAG Retriever integration. Look for announcements, beta features, or release candidates that were published after your LLM's training cutoff date.

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
   ```

2. Review the [full configuration guide](./coding-assistants/configuring-ai-assistants.md) for detailed setup options

3. Check out the [main README](../README.md) for advanced features and configuration options

## Troubleshooting

- If queries return no results, make sure you've successfully loaded documentation using `--fetch` or `--ingest` commands
- If the AI assistant isn't using RAG Retriever, verify you've copied the complete instructions and restarted the assistant
- For more help, see the [Expected Behavior](./coding-assistants/configuring-ai-assistants.md#expected-behavior) section of the configuration guide
