# RAG Retriever - QUICKSTART

This guide provides the EXACT commands to get RAG Retriever installed and running for semantic search.

## Prerequisites
- Python 3.10+ installed
- OpenAI API key (keep it secret!)
- Git installed  
- Sufficient disk space (~500MB for dependencies)

## Step-by-Step Commands

### 1. Install RAG Retriever
```bash
# Recommended: Install via pipx (automatically installs browsers)
pipx install rag-retriever

# Alternative: Install via pip
pip install rag-retriever
```

### 2. Initialize Configuration
```bash
# Create config file with all settings pre-configured
rag-retriever --init
```

**Config file locations:**
- **macOS/Linux**: `~/.config/rag-retriever/config.yaml`
- **Windows**: `%APPDATA%\rag-retriever\config.yaml`

### 3. Configure API Key (ONLY Required Change)
**IMPORTANT**: Replace `null` with your OpenAI API key in the config file.

**macOS/Linux:**
```bash
# Edit the config file
nano ~/.config/rag-retriever/config.yaml

# Find this line and replace null:
api:
  openai_api_key: sk-your-actual-api-key-here  # Change from: null
```

**Windows:**
```cmd
# Edit the config file
notepad %APPDATA%\rag-retriever\config.yaml

# Find this line and replace null:
api:
  openai_api_key: sk-your-actual-api-key-here  # Change from: null
```

### 4. Verify Installation (browsers auto-installed)
```bash
# Check that everything is working (browsers should be pre-installed)
rag-retriever --help

# If you see browser errors, run:
python -m playwright install chromium
```

### 5. Verify Installation
```bash
# Check that everything is working
rag-retriever --help

# Should show no system validation errors
```

### 6. Test with Sample Content
```bash
# Index a simple website
rag-retriever --fetch "https://example.com" --collection test

# Search the indexed content
rag-retriever --search "example" --collection test
```

## Optional: Claude Code Integration

If you want to use RAG Retriever with Claude Code:

### 7. Add MCP Server
```bash
# Get your home directory
echo $HOME

# Add RAG Retriever as MCP server using the FULL path
# Replace /Users/timkitchens with your actual home directory from above
claude mcp add-json -s user rag-retriever '{"type":"stdio","command":"/Users/timkitchens/.local/bin/mcp-rag-retriever"}'

# Verify it's added
claude mcp list
```

**For Other AI Assistants (Windsurf, Cursor, etc.):**
Add this JSON configuration (with your actual home directory):
```json
"rag-retriever": {
  "command": "/Users/timkitchens/.local/bin/mcp-rag-retriever"
}
```

### 8. Grant Permissions
Edit `~/.claude/settings.json` and add to the "allow" array:
```json
"mcp__rag-retriever__*"
```

### 9. Test Claude Code Integration
```bash
# Restart Claude Code
claude

# Test basic integration:
/list-collections
```

### 10. Test with Real Content
Index Claude Code documentation to verify full functionality:
```
/index-website "https://docs.anthropic.com/en/docs/claude-code/overview 3 claude_code_docs"
```

Wait 1-2 minutes for crawling, then test search:
```
/search-knowledge "MCP server setup claude_code_docs"
```

## Common Commands

### Basic Usage
```bash
# Index a website
rag-retriever --fetch "https://docs.python.org" --collection python_docs

# Search content
rag-retriever --search "list comprehension" --collection python_docs

# Search all collections
rag-retriever --search "python" --search-all-collections

# Launch web interface
rag-retriever --ui
```

### Collection Management
```bash
# List all collections
rag-retriever --list-collections

# Clean specific collection
rag-retriever --clean-db --collection old_collection

# Clean all collections
rag-retriever --clean-db
```

### Advanced Crawling
```bash
# Deep crawl with custom depth
rag-retriever --fetch "https://docs.site.com" --max-depth 3 --collection site_docs

# Use faster Crawl4AI crawler (edit config.yaml first)
crawler:
  type: "crawl4ai"
```

## Configuration Options

### Crawler Selection
Edit `~/.config/rag-retriever/config.yaml`:
```yaml
# Use Crawl4AI (20x faster)
crawler:
  type: "crawl4ai"

# Or use Playwright (more reliable)
crawler:
  type: "playwright"
```

### Search Settings
```yaml
search:
  default_limit: 10
  default_score_threshold: 0.3
```

### Content Processing
```yaml
content:
  chunk_size: 2000
  chunk_overlap: 400
```

## Troubleshooting Quick Fixes

### Installation Issues
```bash
# If pipx fails
pip install rag-retriever

# If browser install fails
python -m playwright install chromium --force

# If dependencies are missing
pip install --upgrade pip
pip install rag-retriever[all]
```

### API Key Issues
```bash
# Test API key directly
curl -H "Authorization: Bearer sk-your-key" https://api.openai.com/v1/models

# Set environment variable as fallback
export OPENAI_API_KEY=sk-your-key-here
```

### Search Issues
```bash
# Check what's indexed
rag-retriever --list-collections

# Lower search threshold
rag-retriever --search "query" --score-threshold 0.2

# Search all collections
rag-retriever --search "query" --search-all-collections
```

## That's It!

You now have RAG Retriever installed and ready to use for semantic search.

## Next Steps

1. **Index your important content**:
   ```bash
   rag-retriever --fetch "https://your-important-site.com" --collection important_docs
   ```

2. **Organize with collections**:
   - Use descriptive names: `python_docs`, `company_wiki`, `research_papers`
   - Keep related content together
   - Use the `default` collection for general content

3. **Use Claude Code commands** (if MCP configured):
   - `/list-collections` - See what's available
   - `/search-knowledge "query"` - Search your content
   - `/index-website "https://site.com"` - Add new content
   - `/audit-collections` - Review collection health

4. **Explore the web interface**:
   ```bash
   rag-retriever --ui
   ```

## Data Storage

Your data is stored in:
- **macOS/Linux**: `~/.local/share/rag-retriever/`
- **Windows**: `%LOCALAPPDATA%\rag-retriever\`

Collections persist between sessions and are automatically backed up.

## Getting Help

- Run with `--verbose` for detailed logging
- Check `TROUBLESHOOTING_ASSISTANT_PROMPT.md` for common issues
- Use `USAGE_ASSISTANT_PROMPT.md` for advanced usage patterns