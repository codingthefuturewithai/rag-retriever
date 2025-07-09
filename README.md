# RAG Retriever

A semantic search system that crawls websites, indexes content, and provides AI-powered search capabilities through an MCP server. Built with modular architecture using OpenAI embeddings and ChromaDB vector store.

## 🚀 Quick Start with AI Assistant

Let your AI coding assistant help you set up and use RAG Retriever:

**Setup**: Direct your AI assistant to [`SETUP_ASSISTANT_PROMPT.md`](SETUP_ASSISTANT_PROMPT.md)  
**Usage**: Direct your AI assistant to [`USAGE_ASSISTANT_PROMPT.md`](USAGE_ASSISTANT_PROMPT.md)  
**Troubleshooting**: Direct your AI assistant to [`TROUBLESHOOTING_ASSISTANT_PROMPT.md`](TROUBLESHOOTING_ASSISTANT_PROMPT.md)

**Quick Commands**: See [`QUICKSTART.md`](QUICKSTART.md) for copy-paste installation commands.

These prompts provide comprehensive instructions for your AI assistant to walk you through setup, usage, and troubleshooting without needing to read through documentation.

## What RAG Retriever Does

RAG Retriever enhances your AI coding workflows by providing:

- **Website Crawling**: Index documentation sites, blogs, and knowledge bases
- **Semantic Search**: Find relevant information using natural language queries
- **Collection Management**: Organize content into themed collections
- **MCP Integration**: Direct access from Claude Code and other AI assistants
- **Fast Processing**: 20x faster crawling with Crawl4AI option
- **Rich Metadata**: Extract titles, descriptions, and source attribution

## Key Features

### 🌐 Advanced Web Crawling
- **Playwright**: Reliable JavaScript-enabled crawling
- **Crawl4AI**: High-performance crawling with content filtering
- **Configurable depth**: Control how deep to crawl linked pages
- **Same-domain focus**: Automatically stays within target sites

### 🔍 Semantic Search
- **OpenAI Embeddings**: Uses text-embedding-3-large for high-quality vectors
- **Relevance Scoring**: Configurable similarity thresholds
- **Cross-Collection Search**: Search across all collections simultaneously
- **Source Attribution**: Track where information comes from

### 📚 Collection Management
- **Named Collections**: Organize content by topic, project, or source
- **Metadata Tracking**: Creation dates, document counts, descriptions
- **Health Monitoring**: Audit collections for quality and freshness
- **Easy Cleanup**: Remove or rebuild collections as needed

### 🎯 Quality Management
- **Content Quality Assessment**: Systematic evaluation of indexed content
- **AI-Powered Quality Review**: Use AI to assess accuracy and completeness
- **Contradiction Detection**: Find conflicting information across collections
- **Relevance Monitoring**: Track search quality metrics over time
- **Best Practice Guidance**: Comprehensive collection organization strategies

### 🤖 AI Integration
- **MCP Server**: Direct integration with Claude Code
- **Custom Commands**: Pre-built workflows for common tasks
- **Tool Descriptions**: Clear interfaces for AI assistants
- **Permission Management**: Secure access controls

## Available Claude Code Commands

Once configured as an MCP server, you can use:

### `/list-collections`
Discover all available vector store collections with document counts and metadata.

### `/search-knowledge "query [collection] [limit] [threshold]"`
Search indexed content using semantic similarity:
- `"python documentation"` - searches default collection
- `"python documentation python_docs"` - searches specific collection  
- `"python documentation all"` - searches ALL collections
- `"error handling all 10 0.4"` - custom parameters

### `/index-website "url [max_depth] [collection]"`
Crawl and index website content:
- `"https://docs.python.org"` - index with defaults
- `"https://docs.python.org 3"` - custom crawl depth
- `"https://docs.python.org python_docs 2"` - custom collection

### `/audit-collections`
Review collection health, identify issues, and get maintenance recommendations.

### `/assess-quality`
Systematically evaluate content quality, accuracy, and reliability to ensure high-quality search results.

## How It Works

1. **Content Ingestion**: Web pages are crawled and processed into clean text
2. **Embedding Generation**: Text is converted to vectors using OpenAI's embedding models
3. **Vector Storage**: Embeddings are stored in ChromaDB with metadata
4. **Semantic Search**: Queries are embedded and matched against stored vectors
5. **Result Ranking**: Results are ranked by similarity and returned with sources

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Crawler   │    │  Text Processor │    │ Vector Storage  │
│                 │    │                 │    │                 │
│ • Playwright    │───▶│ • Content Clean │───▶│ • ChromaDB      │
│ • Crawl4AI      │    │ • Text Chunking │    │ • Collections   │
│ • Content Clean │    │ • Embedding Gen │    │ • Metadata      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌─────────────────┐             │
│   MCP Server    │    │ Search Engine   │             │
│                 │    │                 │             │
│ • Claude Code   │◀───│ • Semantic      │◀────────────┘
│ • Tool Defs     │    │ • Cross-Collect │
│ • Permissions   │    │ • Score Ranking │
└─────────────────┘    └─────────────────┘
```

## Use Cases

### Documentation Management
- Index official documentation sites
- Search for APIs, functions, and usage examples
- Maintain up-to-date development references

### Knowledge Bases
- Index company wikis and internal documentation
- Search for policies, procedures, and best practices
- Centralize organizational knowledge

### Research and Learning
- Index technical blogs and tutorials
- Search for specific topics and technologies
- Build personal knowledge repositories

### Project Documentation
- Index project-specific documentation
- Search for implementation patterns
- Maintain project knowledge bases

## Configuration

RAG Retriever is highly configurable through `config.yaml`:

```yaml
# Crawler selection
crawler:
  type: "crawl4ai"  # or "playwright"

# Search settings
search:
  default_limit: 8
  default_score_threshold: 0.3

# Content processing
content:
  chunk_size: 2000
  chunk_overlap: 400

# API configuration
api:
  openai_api_key: sk-your-key-here
```

## Requirements

- Python 3.10+
- OpenAI API key
- Git (for system functionality)
- ~500MB disk space for dependencies

## Installation

See [`QUICKSTART.md`](QUICKSTART.md) for exact installation commands, or use the AI assistant prompts for guided setup.

## Data Storage

Your content is stored locally in:
- **macOS/Linux**: `~/.local/share/rag-retriever/`
- **Windows**: `%LOCALAPPDATA%\rag-retriever\`

Collections persist between sessions and are automatically managed.

## Performance

- **Crawl4AI**: Up to 20x faster than traditional crawling
- **Embedding Caching**: Efficient vector storage and retrieval
- **Parallel Processing**: Concurrent indexing and search
- **Optimized Chunking**: Configurable content processing

## Security

- **Local Storage**: All data stored locally, no cloud dependencies
- **API Key Protection**: Secure configuration management
- **Permission Controls**: MCP server permission management
- **Source Tracking**: Complete audit trail of indexed content

## Contributing

RAG Retriever is open source and welcomes contributions. See the repository for guidelines.

## License

MIT License - see LICENSE file for details.

## Support

- **Documentation**: Use the AI assistant prompts for guidance
- **Issues**: Report bugs and request features via GitHub issues
- **Community**: Join discussions and share usage patterns

---

**Remember**: Use the AI assistant prompts above rather than reading through documentation. Your AI assistant can guide you through setup, usage, and troubleshooting much more effectively than traditional documentation!