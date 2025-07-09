# Setup Assistant Prompt for RAG Retriever

Read this entire prompt, then help me set up RAG Retriever - a semantic search system that crawls websites, indexes content, and provides AI-powered search capabilities through an MCP server.

## Your Task

I need you to guide me through installing and configuring RAG Retriever so I can:
- Index websites and documents into searchable collections
- Perform semantic search across my indexed content
- Use it as an MCP server with Claude Code for knowledge management

## What RAG Retriever Does

RAG Retriever is a semantic search system that:
- Crawls websites with Playwright or Crawl4AI (20x faster)
- Indexes content into ChromaDB vector collections
- Provides semantic search via OpenAI embeddings
- Offers MCP server integration for AI coding assistants
- Supports multiple collections for organized knowledge management

## Prerequisites You Should Check

Before we start, verify I have:
- Python 3.10+ installed
- OpenAI API key (but DON'T ask me to show it to you)
- Git installed
- Sufficient disk space (ChromaDB and browser dependencies)

## Installation Steps You'll Help Me With

### 1. Install RAG Retriever
**Recommended: Via pipx (includes automatic browser installation)**
```bash
pipx install rag-retriever
```

**Note**: This automatically installs Playwright browsers during installation via the post-install script. No additional browser installation is needed in most cases.

**Alternative: Development Installation**
If I want to modify the code:
```bash
git clone https://github.com/user/rag-retriever.git
cd rag-retriever
pip install -e .
```

### 2. Initialize Configuration
Run the initialization command:
```bash
rag-retriever --init
```

This creates a config file with ALL settings pre-configured:
- **macOS/Linux**: `~/.config/rag-retriever/config.yaml`
- **Windows**: `%APPDATA%\rag-retriever\config.yaml`

### 3. Configure API Key (ONLY Required Change)
**CRITICAL**: The config file has everything pre-configured EXCEPT the OpenAI API key.

**You should:**
- Tell me the exact location of my config file
- Show me that I only need to replace `null` with my API key
- Remind me to keep my API key secret
- **NEVER** ask me to show you the API key

**Find this section in config.yaml and replace `null`:**
```yaml
api:
  openai_api_key: sk-your-actual-api-key-here  # Change from: null
```

**Everything else in the config can stay as-is for basic usage.**

### 4. Verify Browser Installation (Usually Not Needed)
The pipx installation should have automatically installed browsers. Test:
```bash
rag-retriever --help
```

If you see browser-related errors, run:
```bash
python -m playwright install chromium
```

### 5. System Validation
Test that everything is working:
```bash
rag-retriever --help
```

### 6. MCP Server Setup (Optional but Recommended)
If I want to use RAG Retriever with Claude Code:

**First, determine my home directory and build the full path:**
You should run this to get my exact path:
```bash
echo "Full MCP path: $HOME/.local/bin/mcp-rag-retriever"
```

**Then add MCP Server using the full path (NO tilde):**
```bash
claude mcp add-json -s user rag-retriever '{"type":"stdio","command":"/Users/username/.local/bin/mcp-rag-retriever"}'
```

**Replace `/Users/username/` with my actual home directory path from the echo command above.**

**Windows users**: Check `pipx list` to get the exact path, then use that full path.

**Grant Permissions:**
Edit `~/.claude/settings.json` to add:
```json
"mcp__rag-retriever__*"
```

### 7. Test Basic Installation
Create a simple test collection:
```bash
rag-retriever --fetch "https://example.com" --collection test
```

Then search it:
```bash
rag-retriever --search "test query" --collection test
```

### 8. Test MCP Integration with Real Content
If MCP setup was completed, test with Claude Code by indexing the official Claude Code documentation:

**In Claude Code, run this command to index Claude Code docs:**
```
/index-website "https://docs.anthropic.com/en/docs/claude-code/overview 3 claude_code_docs"
```

This will:
- Crawl the Claude Code documentation site
- Index to depth 3 (comprehensive coverage)
- Store in a collection named "claude_code_docs"
- Take 1-2 minutes to complete

**Wait 1-2 minutes for crawling to complete, then test search:**
```
/search-knowledge "setup MCP server claude_code_docs"
```

This should return relevant information about MCP server setup from the Claude Code documentation, proving the system is working end-to-end.

## Important Configuration Options

### Crawler Selection
RAG Retriever supports two crawlers:
- **Playwright**: Reliable, standard web crawling
- **Crawl4AI**: 20x faster with aggressive content filtering

To use Crawl4AI, edit config.yaml:
```yaml
crawler:
  type: "crawl4ai"
```

### Collection Organization
Plan collection naming strategy:
- Use descriptive names: `python_docs`, `company_wiki`, `claude_code_docs`
- Consider topic-based organization
- Default collection is called `default`

## Common Issues to Watch For

### 1. System Dependencies
- If playwright install fails, try: `pip install playwright==1.49.0`
- If Git is missing, install from: https://git-scm.com/
- If Python is too old, upgrade to 3.10+

### 2. API Key Issues
- Key must start with `sk-`
- Set environment variable: `export OPENAI_API_KEY=sk-...` (but don't show me the key)
- Verify key has credits in OpenAI dashboard

### 3. Crawler Dependencies
- Chromium download can be slow/fail - retry if needed
- Crawl4AI requires additional system dependencies
- System validation runs automatically and shows clear error messages

### 4. Permission Issues
- Config directory may need creation
- MCP server needs proper permissions in Claude Code
- Use `--verbose` flag for debugging

## Advanced Options

### UI Interface
Launch web interface:
```bash
rag-retriever --ui
```

### Custom Configuration
Edit config.yaml to customize:
- Embedding models
- Chunk sizes
- Browser settings
- Search thresholds

## Your Helpful Actions

**You CAN safely:**
- Run installation commands on my behalf (pipx, pip, playwright install)
- Check system requirements (python --version, git --version)
- Create directories and copy configuration templates
- Run help commands and system validation
- Test basic functionality

**You CANNOT:**
- See or handle my API key
- Modify API key configuration directly
- Access my existing collections or data
- Run commands that might expose sensitive information

## Success Verification

After setup, I should be able to:
- Run `rag-retriever --help` without errors
- See config file at the correct OS path with only API key needing configuration
- Have chromium browser automatically installed
- Create and search collections via command line
- Use MCP server with Claude Code (if configured)
- Index Claude Code documentation and search it successfully

## Next Steps After Setup

Once installed, I can:
- Use `/list-collections` to see available collections
- Use `/index-website` to crawl and index websites
- Use `/search-knowledge` to search across collections
- Use `/audit-collections` to review collection health

Please guide me through each step, run safe commands on my behalf when possible, and help troubleshoot any issues that arise. Remember - never ask to see my API key!