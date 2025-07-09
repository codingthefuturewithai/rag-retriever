# Troubleshooting Guide for RAG Retriever

Use this guide when encountering issues with RAG Retriever installation, configuration, or operation.

## Problem Categories

### Installation Issues
### Configuration Problems  
### Crawler and Indexing Failures
### Search and Performance Issues
### MCP Server Integration Problems

---

## Installation Issues

### Problem: pipx Installation Fails
**Symptoms:**
- `pipx install rag-retriever` fails with dependency errors
- Package not found errors
- Python version compatibility issues

**Solutions:**
1. **Check Python version**: Requires Python 3.10+
   ```bash
   python --version
   ```

2. **Upgrade pipx**:
   ```bash
   python -m pip install --upgrade pipx
   ```

3. **Try pip installation**:
   ```bash
   pip install rag-retriever
   ```

4. **Development installation**:
   ```bash
   git clone https://github.com/user/rag-retriever.git
   cd rag-retriever
   pip install -e .
   ```

### Problem: Browser Installation Fails
**Symptoms:**
- `playwright install chromium` fails
- Browser download timeouts
- Permission errors during installation

**Solutions:**
1. **Manual browser installation**:
   ```bash
   python -m playwright install chromium --force
   ```

2. **Check disk space**: Browser requires ~200MB
   ```bash
   df -h
   ```

3. **Alternative installation**:
   ```bash
   pip install playwright==1.49.0
   python -m playwright install chromium
   ```

4. **System-specific issues**:
   - **macOS**: May need Xcode command line tools
   - **Linux**: May need additional dependencies
   - **Windows**: May need Visual C++ redistributables

---

## Configuration Problems

### Problem: Config File Not Found
**Symptoms:**
- `rag-retriever --init` doesn't create config
- Config file missing after initialization
- Permission denied errors

**Solutions:**
1. **Check config location** (OS-specific):
   - **macOS/Linux**: `~/.config/rag-retriever/config.yaml`
   - **Windows**: `%APPDATA%\rag-retriever\config.yaml`

2. **Create directory manually**:
   ```bash
   mkdir -p ~/.config/rag-retriever
   ```

3. **Run with proper permissions**:
   ```bash
   sudo rag-retriever --init  # Only if necessary
   ```

### Problem: API Key Configuration Issues
**Symptoms:**
- "OpenAI API key not found" errors
- Authentication failures
- "Invalid API key" messages

**Solutions:**
1. **Verify API key format** - Must start with `sk-`

2. **Check config.yaml structure**:
   ```yaml
   api:
     openai_api_key: sk-your-actual-key-here
   ```

3. **Environment variable fallback**:
   ```bash
   export OPENAI_API_KEY=sk-your-key-here
   ```

4. **Test API key separately**:
   ```bash
   curl -H "Authorization: Bearer sk-your-key" https://api.openai.com/v1/models
   ```

5. **Check API key credits** in OpenAI dashboard

---

## Crawler and Indexing Failures

### Problem: Crawl4AI Dependencies Missing
**Symptoms:**
- "Crawl4AI not available" warnings
- ImportError for crawl4ai modules
- Crawler fallback to Playwright

**Solutions:**
1. **Install Crawl4AI**:
   ```bash
   pip install crawl4ai>=0.4.0
   ```

2. **Check system validation**:
   ```bash
   rag-retriever --help  # Shows system validation results
   ```

3. **Use Playwright fallback**:
   ```yaml
   crawler:
     type: "playwright"
   ```

### Problem: Website Crawling Fails
**Symptoms:**
- "Failed to load page" errors
- Timeouts during crawling
- Empty content extraction

**Solutions:**
1. **Check URL accessibility**:
   ```bash
   curl -I https://example.com
   ```

2. **Try different crawler**:
   ```yaml
   crawler:
     type: "playwright"  # or "crawl4ai"
   ```

3. **Adjust crawler settings**:
   ```yaml
   browser:
     wait_time: 5
     launch_options:
       headless: true
       timeout: 60000
   ```

4. **Reduce crawl depth**:
   ```bash
   rag-retriever --fetch "https://example.com" --max-depth 1
   ```

### Problem: ChromaDB Metadata Errors
**Symptoms:**
- "Expected metadata value to be a str, int, float or bool, got None"
- Database insertion failures
- Metadata validation errors

**Solutions:**
1. **This is fixed in recent versions** - update RAG Retriever:
   ```bash
   pipx upgrade rag-retriever
   ```

2. **Check collection status**:
   ```bash
   rag-retriever --search "test" --collection default
   ```

3. **Clear problematic collection**:
   ```bash
   rag-retriever --clean-db --collection collection_name
   ```

---

## Search and Performance Issues

### Problem: Poor Search Results
**Symptoms:**
- No results for obvious queries
- Irrelevant results returned
- Low relevance scores

**Solutions:**
1. **Check collection contents**:
   ```bash
   rag-retriever --audit-collections
   ```

2. **Lower score threshold**:
   ```bash
   rag-retriever --search "query" --score-threshold 0.2
   ```

3. **Try different query phrasings**:
   - "How to handle errors" vs "error handling"
   - "Python documentation" vs "Python docs"

4. **Search all collections**:
   ```bash
   rag-retriever --search "query" --search-all-collections
   ```

### Problem: Slow Performance
**Symptoms:**
- Long indexing times
- Slow search responses
- High memory usage

**Solutions:**
1. **Use Crawl4AI** for faster crawling:
   ```yaml
   crawler:
     type: "crawl4ai"
   ```

2. **Optimize chunk settings**:
   ```yaml
   content:
     chunk_size: 1000
     chunk_overlap: 200
   ```

3. **Monitor system resources**:
   ```bash
   top -p $(pgrep -f rag-retriever)
   ```

4. **Index selectively** - avoid indexing everything at once

---

## MCP Server Integration Problems

### Problem: MCP Server Not Found
**Symptoms:**
- "MCP server not found" in Claude Code
- Connection refused errors
- Server not listed in `claude mcp list`

**Solutions:**
1. **Re-add MCP server**:
   ```bash
   claude mcp remove rag-retriever
   # Get your home directory first
   echo $HOME
   # Then use the full path (replace with your actual home directory)
   claude mcp add-json -s user rag-retriever '{"type":"stdio","command":"/Users/timkitchens/.local/bin/mcp-rag-retriever"}'
   ```

2. **Check server status**:
   ```bash
   claude mcp list
   ```

3. **Test server directly**:
   ```bash
   python -m rag_retriever.mcp --help
   ```

4. **Restart Claude Code** after configuration changes

### Problem: Permission Errors
**Symptoms:**
- Tool permission denied
- "mcp__rag-retriever__*" not allowed
- Interactive permission prompts

**Solutions:**
1. **Edit settings.json**:
   ```json
   {
     "allow": ["mcp__rag-retriever__*"]
   }
   ```

2. **Grant permissions interactively**: Choose "Yes, and don't ask again"

3. **Check settings location**:
   - **macOS**: `~/.claude/settings.json`
   - **Linux**: `~/.config/claude/settings.json`
   - **Windows**: `%APPDATA%\claude\settings.json`

---

## System Validation Issues

### Problem: System Dependencies Missing
**Symptoms:**
- "System validation failed" errors
- Missing Git, Playwright, or other dependencies
- Application refuses to start

**Solutions:**
1. **Install missing dependencies**:
   ```bash
   # Git
   # macOS: xcode-select --install
   # Linux: sudo apt-get install git
   # Windows: Download from git-scm.com
   
   # Playwright
   python -m playwright install chromium
   ```

2. **Check system validation**:
   ```bash
   rag-retriever --help  # Shows validation results
   ```

3. **Force bypass validation** (not recommended):
   ```bash
   export RAG_RETRIEVER_SKIP_VALIDATION=1
   ```

---

## Data and Storage Issues

### Problem: Collections Not Persisting
**Symptoms:**
- Collections disappear after restart
- Data not saved to disk
- ChromaDB connection issues

**Solutions:**
1. **Check data directory**:
   ```bash
   ls -la ~/.local/share/rag-retriever/
   ```

2. **Verify ChromaDB path**:
   ```yaml
   vector_store:
     persist_directory: null  # Uses default OS path
   ```

3. **Manual cleanup and rebuild**:
   ```bash
   rag-retriever --clean-db
   rag-retriever --fetch "https://example.com"
   ```

### Problem: Database Corruption
**Symptoms:**
- SQLite database errors
- Inconsistent search results
- ChromaDB startup failures

**Solutions:**
1. **Complete database reset**:
   ```bash
   rag-retriever --clean-db
   ```

2. **Backup and restore**:
   ```bash
   cp -r ~/.local/share/rag-retriever ~/.local/share/rag-retriever.backup
   ```

3. **Rebuild from scratch**:
   ```bash
   rag-retriever --clean-db
   # Re-index your content
   ```

---

## Diagnostic Commands

### System Information
```bash
rag-retriever --help        # Shows system validation
python --version            # Python version
pip list | grep rag         # Package versions
```

### Collection Health
```bash
rag-retriever --audit-collections  # Collection overview
rag-retriever --search "test"      # Test search
```

### Crawler Testing
```bash
rag-retriever --fetch "https://example.com" --verbose
```

### MCP Server Testing
```bash
python -m rag_retriever.mcp --help
claude mcp list
```

---

## Log Locations

### Application Logs
- **macOS/Linux**: `~/.local/share/rag-retriever/logs/`
- **Windows**: `%LOCALAPPDATA%\rag-retriever\logs\`

### Browser Logs
- Playwright logs in system temp directory
- Crawl4AI logs in application logs

### ChromaDB Logs
- Database files in `~/.local/share/rag-retriever/chromadb/`

---

## Emergency Recovery

### Complete Reset
```bash
# Stop all processes
pkill -f rag-retriever

# Remove all data
rm -rf ~/.local/share/rag-retriever
rm -rf ~/.config/rag-retriever

# Reinstall
pipx uninstall rag-retriever
pipx install rag-retriever

# Reconfigure
rag-retriever --init
# Add API key to config.yaml
```

### Minimal Recovery
```bash
# Just reset database
rag-retriever --clean-db

# Test basic functionality
rag-retriever --fetch "https://example.com"
rag-retriever --search "test"
```

---

## Getting Help

### Community Support
- GitHub Issues: [Repository Issues](https://github.com/user/rag-retriever/issues)
- Documentation: [RAG Retriever Docs](https://docs.example.com)

### Debug Information to Include
- RAG Retriever version: `rag-retriever --version`
- Python version: `python --version`
- Operating system and version
- Error messages and stack traces
- Configuration files (without API keys)
- Steps to reproduce the issue

### Before Asking for Help
1. Check this troubleshooting guide
2. Search existing GitHub issues
3. Try the diagnostic commands above
4. Attempt basic recovery steps
5. Gather debug information

Remember: Never share your API keys or sensitive configuration when asking for help!