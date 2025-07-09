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
Choose the appropriate installation method:

**Option A: Via pipx (Recommended)**
```bash
pipx install rag-retriever
```

**Option B: Development Installation**
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

This creates OS-specific config files:
- **macOS/Linux**: `~/.config/rag-retriever/config.yaml`
- **Windows**: `%APPDATA%\rag-retriever\config.yaml`

### 3. Configure API Key
**CRITICAL**: I need to add my OpenAI API key to the config file. 

**You should:**
- Tell me the exact location of my config file
- Show me the exact YAML structure to add
- Remind me to keep my API key secret
- **NEVER** ask me to show you the API key

**Example structure to show me:**
```yaml
api:
  openai_api_key: sk-your-actual-api-key-here
```

### 4. Install Browser Dependencies
RAG Retriever needs browser support for web crawling. Help me run:
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

**Add MCP Server:**
```bash
claude mcp add --transport stdio -s user rag-retriever python -m rag_retriever.mcp
```

**Grant Permissions:**
Edit `~/.claude/settings.json` to add:
```json
"mcp__rag-retriever__*"
```

### 7. Test Installation
Create a test collection:
```bash
rag-retriever --fetch "https://example.com" --collection test
```

Then search it:
```bash
rag-retriever --search "test query" --collection test
```

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
- See config file at the correct OS path
- Have chromium browser installed
- Create and search collections
- Use MCP server with Claude Code (if configured)

## Next Steps After Setup

Once installed, I can:
- Use `/list-collections` to see available collections
- Use `/index-website` to crawl and index websites
- Use `/search-knowledge` to search across collections
- Use `/audit-collections` to review collection health

Please guide me through each step, run safe commands on my behalf when possible, and help troubleshoot any issues that arise. Remember - never ask to see my API key!