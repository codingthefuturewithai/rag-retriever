# Setup RAG Retriever MCP Server

Configure the RAG Retriever MCP server for use with Claude Code commands.

## Prerequisites
- RAG Retriever installed via `pipx install rag-retriever` or local development setup
- Claude Code with MCP support
- OpenAI API key configured

## Setup Steps

### 1. Install RAG Retriever
```bash
pipx install rag-retriever
```

### 2. Initialize Configuration
```bash
rag-retriever --init
```

### 3. Configure API Key
Edit your config file (location shown by init command):
```yaml
api:
  openai_api_key: sk-your-api-key-here
```

### 4. Add MCP Server to Claude Code
Add to your Claude Code MCP configuration:

```json
{
  "mcpServers": {
    "rag-retriever": {
      "command": "python",
      "args": ["-m", "rag_retriever.mcp"],
      "env": {
        "OPENAI_API_KEY": "sk-your-api-key-here"
      }
    }
  }
}
```

### 5. Verify Setup
Run a Claude Code command to test:
```
/list-collections
```

## Available MCP Tools
Once configured, you have access to:
- `list_collections()` - Discover available collections
- `vector_search(query, collection_name, limit, score_threshold)` - Search collections
- `crawl_and_index_url(url, max_depth, collection_name)` - Index websites

## Troubleshooting
- Ensure OpenAI API key is valid and has credits
- Check that Python can import `rag_retriever.mcp`
- Verify MCP server is running with `python -m rag_retriever.mcp --help`
- Check Claude Code logs for MCP connection issues

## Next Steps
After setup, use these commands:
- `/list-collections` - See what collections exist
- `/search-knowledge "your query"` - Search for information
- `/index-website "https://docs.example.com"` - Add new content
- `/audit-collections` - Review collection health