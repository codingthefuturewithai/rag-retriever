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
First get the full path (don't use tilde):

```bash
echo "Full MCP path: $HOME/.local/bin/mcp-rag-retriever"
```

Add the MCP server using the FULL path from above:

```bash
claude mcp add-json -s user rag-retriever '{"type":"stdio","command":"/Users/username/.local/bin/mcp-rag-retriever"}'
```

**Important**: Replace `/Users/username/` with your actual home directory path from the echo command.

**Windows users**: Check `pipx list` for the exact path and use that full path.

### 5. Verify Setup
Run a Claude Code command to test:
```
/list-collections
```

### 6. Test with Real Content
Index Claude Code documentation to verify full functionality:
```
/index-website "https://docs.anthropic.com/en/docs/claude-code/overview 3 claude_code_docs"
```

Wait 1-2 minutes for crawling, then test search:
```
/search-knowledge "MCP server setup claude_code_docs"
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