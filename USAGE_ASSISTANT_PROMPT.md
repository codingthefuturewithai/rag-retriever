# Usage Assistant Prompt for RAG Retriever

Read this entire prompt, then help me use RAG Retriever effectively for semantic search and knowledge management.

## Context

I have RAG Retriever installed and configured. Now I need help using it effectively to build searchable knowledge bases and perform semantic search across indexed content.

## How RAG Retriever Works

RAG Retriever is a semantic search system that:
- **Crawls websites** using Playwright or Crawl4AI (20x faster option)
- **Indexes content** into ChromaDB vector collections using OpenAI embeddings
- **Provides semantic search** with relevance scoring and source attribution
- **Organizes knowledge** into named collections (like databases)
- **Integrates with Claude Code** via MCP server for AI-powered workflows

## Available Interfaces

### 1. Command Line Interface
```bash
rag-retriever --help                    # Show all options
rag-retriever --fetch URL              # Index a website
rag-retriever --search "query"         # Search content
rag-retriever --ui                     # Launch web interface
```

### 2. Claude Code Commands (if MCP configured)
- `/list-collections` - Discover available collections
- `/search-knowledge` - Search across collections  
- `/index-website` - Crawl and index websites
- `/audit-collections` - Review collection health

### 3. MCP Tools (for other AI assistants)
- `list_collections()` - Show available collections
- `vector_search(query, collection_name, search_all_collections)` - Search content
- `crawl_and_index_url(url, max_depth, collection_name)` - Index websites

## Common Workflows

### First-Time Setup Workflow
1. **Discover what exists**: Check current collections
2. **Plan your collections**: Decide on organization strategy
3. **Start indexing**: Begin with your most important content
4. **Test search**: Verify content is searchable
5. **Expand gradually**: Add more content over time

### Content Indexing Workflow
1. **Choose collection name**: Use descriptive names like `python_docs`, `company_wiki`
2. **Select crawler**: Playwright (reliable) or Crawl4AI (20x faster)
3. **Set max depth**: How deep to crawl linked pages (default: 2)
4. **Monitor progress**: Watch for errors or failed pages
5. **Verify indexing**: Test search to ensure content is accessible

### Search Workflow
1. **Identify target collections**: Know where your content lives
2. **Choose search scope**: Single collection vs all collections
3. **Craft effective queries**: Use natural language, be specific
4. **Evaluate results**: Check relevance scores and sources
5. **Refine searches**: Adjust queries based on results

## Collection Organization Strategies

### Topic-Based Organization
```
- python_docs (Python documentation)
- javascript_docs (JS/Node.js documentation)
- company_wiki (Internal company knowledge)
- claude_code_docs (Claude Code documentation)
- research_papers (Academic papers)
```

### Project-Based Organization
```
- project_alpha (All docs for Project Alpha)
- project_beta (All docs for Project Beta)
- shared_knowledge (Cross-project documentation)
```

### Source-Based Organization
```
- anthropic_docs (All Anthropic documentation)
- github_repos (Code repositories)
- blog_posts (Technical blog posts)
- tutorials (Learning materials)
```

## Best Practices

### 🏗️ **Collection Organization (CRITICAL)**
- **Group related topics in single collections** - Keep Python docs, Django docs, FastAPI docs separate, not mixed
- **Use descriptive, consistent names** - `python_docs`, `company_wiki`, `claude_code_docs` not `docs1`, `stuff`
- **Avoid spreading related knowledge** - Don't put React concepts across multiple collections
- **Plan hierarchically** - `frontend_docs` > `react_docs` > `react_hooks_docs` for specific needs

### 📊 **Content Quality Management (ESSENTIAL)**
- **ALWAYS assess content quality before indexing** - Poor documentation corrupts your knowledge base
- **Use AI to evaluate content** - Have your AI assistant review sample content for accuracy
- **Watch for contradictory information** - Multiple sources saying different things = quality problem
- **Identify and remove outdated content** - Old documentation leads to wrong answers
- **Monitor search relevance scores** - Consistently low scores (< 0.3) indicate quality issues

### 🔍 **Quality Assessment Workflow**
1. **Pre-indexing**: Have AI review sample pages for accuracy and completeness
2. **Post-indexing**: Use `/audit-collections` to systematically assess quality
3. **Regular testing**: Search for known topics and verify answers are correct
4. **Score monitoring**: Track relevance scores - declining scores indicate quality degradation
5. **Source validation**: Check that sources are current and authoritative

### Effective Indexing
- **Use descriptive collection names** - `claude_code_docs` not `docs1`
- **Set appropriate max_depth** - 2-3 levels usually sufficient
- **Choose right crawler** - Crawl4AI for speed, Playwright for reliability
- **Monitor for errors** - Check logs for failed pages
- **Test after indexing** - Verify content is searchable

### Effective Searching
- **Use natural language** - "How to handle errors in Python" vs "error handling"
- **Be specific** - "Claude Code MCP setup" vs "setup"
- **Try different phrasings** - Search results vary with query wording
- **Use collection names** - Search specific collections when possible
- **Check relevance scores** - Scores below 0.3 may not be relevant

### Collection Management
- **Regular audits** - Use `/audit-collections` to check collection health
- **Consistent naming** - Use underscore_style for collection names
- **Avoid duplication** - Don't index same content in multiple collections
- **Plan for growth** - Start with core content, expand gradually

## Advanced Usage

### Cross-Collection Search
Search across ALL collections:
```bash
rag-retriever --search "query" --search-all-collections
```

Or with Claude Code:
```
/search-knowledge "query all"
```

### Custom Search Parameters
```bash
rag-retriever --search "query" --limit 15 --score-threshold 0.4
```

### Crawler Configuration
Edit config.yaml to customize:
```yaml
crawler:
  type: "crawl4ai"  # or "playwright"

browser:
  headless: true
  wait_time: 2

content:
  chunk_size: 2000
  chunk_overlap: 400
```

### Web Interface
Launch for visual collection management:
```bash
rag-retriever --ui
```

## Troubleshooting Common Issues

### Poor Search Results
- **Check collection contents** - Use `/audit-collections` to verify content
- **Try different queries** - Rephrase your search terms
- **Lower score threshold** - Try 0.2 instead of 0.3
- **Check embedding model** - Ensure using text-embedding-3-large

### Indexing Failures
- **Check crawler logs** - Look for specific error messages
- **Verify URL accessibility** - Can you access the site manually?
- **Try different crawler** - Switch between Playwright and Crawl4AI
- **Reduce max_depth** - Start with depth 1, increase gradually

### Performance Issues
- **Use Crawl4AI** - 20x faster than Playwright
- **Reduce chunk_size** - Smaller chunks = faster processing
- **Index selectively** - Don't index everything at once
- **Monitor system resources** - ChromaDB can use significant memory

## Your Helpful Actions

**You CAN safely:**
- Run search commands to help me find information
- Check collection status and health
- Suggest collection organization strategies
- Help craft effective search queries
- Run system diagnostics and help interpret results
- Launch the web interface for visual management

**You CANNOT:**
- Access or modify my API key
- Delete collections without explicit confirmation
- Index content from URLs I haven't approved
- Access the actual content of my collections (only metadata)

## Claude Code Integration

If I have MCP configured, you can:
- Use `/list-collections` to show available collections
- Use `/search-knowledge` to search for information
- Use `/index-website` to help me add new content
- Use `/audit-collections` to review collection health

## Success Metrics

Good RAG Retriever usage should result in:
- **Organized collections** with clear naming and purpose
- **Comprehensive coverage** of important knowledge domains
- **Fast, relevant search results** with high confidence scores
- **Regular maintenance** through audits and updates
- **Effective integration** with AI coding workflows

## Common Use Cases

### Documentation Search
- Index official documentation sites
- Search for specific APIs, functions, or concepts
- Find examples and usage patterns

### Knowledge Management
- Index company wikis and internal documentation
- Search for policies, procedures, and best practices
- Maintain up-to-date organizational knowledge

### Research and Learning
- Index technical blogs and tutorials
- Search for specific topics or technologies
- Build personal knowledge bases

### Code Documentation
- Index GitHub repositories and code documentation
- Search for implementation patterns and examples
- Maintain project-specific knowledge bases

Please let me know what you'd like to accomplish with RAG Retriever, and I'll guide you through the most effective approach!