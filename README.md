# RAG Retriever

A semantic search system that crawls websites, indexes content, and provides AI-powered search capabilities through an MCP server. Built with modular architecture using OpenAI embeddings and ChromaDB vector store.

## 🚀 Quick Start with AI Assistant

Let your AI coding assistant help you set up and use RAG Retriever:

**Setup**: Direct your AI assistant to [`SETUP_ASSISTANT_PROMPT.md`](SETUP_ASSISTANT_PROMPT.md)  
**Usage**: Direct your AI assistant to [`USAGE_ASSISTANT_PROMPT.md`](USAGE_ASSISTANT_PROMPT.md)  
**CLI Operations**: Direct your AI assistant to [`CLI_ASSISTANT_PROMPT.md`](CLI_ASSISTANT_PROMPT.md)  
**Administration**: Direct your AI assistant to [`ADMIN_ASSISTANT_PROMPT.md`](ADMIN_ASSISTANT_PROMPT.md)  
**Advanced Content**: Direct your AI assistant to [`ADVANCED_CONTENT_INGESTION_PROMPT.md`](ADVANCED_CONTENT_INGESTION_PROMPT.md)  
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

## MCP vs CLI Capabilities

### MCP Server (Claude Code Integration)
The MCP server provides **secure, AI-friendly access** to core functionality:

- **Web Crawling**: Index websites and documentation
- **Semantic Search**: Search across collections with relevance scoring
- **Collection Discovery**: List and explore available collections
- **Quality Assessment**: Audit content quality and system health
- **Intentionally Limited**: No administrative operations for security

### CLI (Full Administrative Control)
The command-line interface provides **complete system control**:

- **All MCP Capabilities**: Everything available through MCP server
- **Collection Management**: Delete collections, clean entire vector store
- **Advanced Content Ingestion**: Images, PDFs, GitHub repos, Confluence
- **Local File Processing**: Directory scanning, bulk operations
- **System Administration**: Configuration, maintenance, troubleshooting
- **Rich Output Options**: JSON, verbose logging, custom formatting

### Web UI (Visual Management)
The Streamlit-based web interface provides **intuitive visual control**:

- **Interactive Search**: Visual search interface with adjustable parameters
- **Collection Management**: View, delete, edit descriptions, compare collections
- **Content Discovery**: Web search and direct content indexing workflow
- **Visual Analytics**: Statistics, charts, and collection comparisons
- **User-Friendly**: No command-line knowledge required
- **Real-time Feedback**: Immediate visual confirmation of operations

### When to Use Each Interface

| Task | MCP Server | CLI | Web UI | Recommendation |
|------|------------|-----|---------|----------------|
| Search content | ✅ | ✅ | ✅ | **MCP** for AI workflows, **UI** for interactive exploration |
| Index websites | ✅ | ✅ | ✅ | **UI** for discovery workflow, **MCP** for AI integration |
| Delete collections | ❌ | ✅ | ✅ | **UI** for visual confirmation, **CLI** for scripting |
| Edit collection metadata | ❌ | ❌ | ✅ | **UI** only option |
| Visual analytics | ❌ | ❌ | ✅ | **UI** only option |
| Content discovery | ❌ | ❌ | ✅ | **UI** provides search → select → index workflow |
| Process local files | ❌ | ✅ | ❌ | **CLI** only option |
| Analyze images | ❌ | ✅ | ❌ | **CLI** only option |
| GitHub integration | ❌ | ✅ | ❌ | **CLI** only option |
| System maintenance | ❌ | ✅ | ❌ | **CLI** only option |
| AI assistant integration | ✅ | ❌ | ❌ | **MCP** designed for AI workflows |
| Visual collection comparison | ❌ | ❌ | ✅ | **UI** provides interactive charts |

## Available Claude Code Commands

Once configured as an MCP server, you can use:

### `/rag-list-collections`
Discover all available vector store collections with document counts and metadata.

### `/rag-search-knowledge "query [collection] [limit] [threshold]"`
Search indexed content using semantic similarity:
- `"python documentation"` - searches default collection
- `"python documentation python_docs"` - searches specific collection  
- `"python documentation all"` - searches ALL collections
- `"error handling all 10 0.4"` - custom parameters

### `/rag-index-website "url [max_depth] [collection]"`
Crawl and index website content:
- `"https://docs.python.org"` - index with defaults
- `"https://docs.python.org 3"` - custom crawl depth
- `"https://docs.python.org python_docs 2"` - custom collection

### `/rag-audit-collections`
Review collection health, identify issues, and get maintenance recommendations.

### `/rag-assess-quality`
Systematically evaluate content quality, accuracy, and reliability to ensure high-quality search results.

### `/rag-manage-collections`
Administrative collection operations including deletion and cleanup (provides CLI commands).

### `/rag-ingest-content`
Guide through advanced content ingestion for local files, images, and enterprise systems.

### `/rag-cli-help`
Interactive CLI command builder and comprehensive help system.

## Web UI Interface

Launch the visual interface with: `rag-retriever --ui`

### Collection Management
![Collection Management](docs/images/rag-retriever-UI-collections.png)
*Comprehensive collection overview with statistics, metadata, and management actions*

### Collection Actions and Deletion
![Collection Actions](docs/images/rag-retreiver-UI-delete-collection.png)
*Collection management interface showing edit description and delete collection options with visual confirmation*

### Interactive Knowledge Search
![Search Interface](docs/images/rag-retriever-UI-search.png)
*Search indexed content with adjustable parameters (max results, score threshold) and explore results with metadata and expandable content*

### Collection Analytics and Comparison
![Collection Comparison](docs/images/rag-retriever-UI-compare-collections.png)
*Side-by-side collection comparison with interactive charts showing document counts, chunks, and performance metrics*

### Content Discovery and Indexing Workflow
![Content Discovery](docs/images/rag-retreiver-UI-discover-and-index-new-web-content.png)
*Search the web, select relevant content, adjust crawl depth, and index directly into collections - complete discovery-to-indexing workflow*

The Web UI excels at:
- **Content Discovery Workflow**: Search → Select → Adjust → Index new content in one seamless interface
- **Visual Collection Management**: View statistics, edit descriptions, delete collections with confirmation
- **Interactive Search**: Real-time parameter adjustment and visual exploration of indexed content
- **Collection Analytics**: Compare collections with interactive charts and performance metrics
- **Administrative Tasks**: User-friendly collection deletion and management operations

## How It Works

1. **Content Ingestion**: Web pages are crawled and processed into clean text
2. **Embedding Generation**: Text is converted to vectors using OpenAI's embedding models
3. **Vector Storage**: Embeddings are stored in ChromaDB with metadata
4. **Semantic Search**: Queries are embedded and matched against stored vectors
5. **Result Ranking**: Results are ranked by similarity and returned with sources

## Architecture

### Layered Content Ingestion Architecture

```mermaid
flowchart TD
    subgraph CS ["CONTENT SOURCES"]
        subgraph WC ["Web Content"]
            WC1["Playwright"]
            WC2["Crawl4AI"] 
            WC3["Web Search"]
            WC4["Discovery UI"]
        end
        subgraph LF ["Local Files"]
            LF1["PDF Files"]
            LF2["Markdown"]
            LF3["Text Files"]
            LF4["Directories"]
        end
        subgraph RM ["Rich Media"]
            RM1["Images"]
            RM2["Screenshots"]
            RM3["Diagrams"]
            RM4["OpenAI Vision"]
        end
        subgraph ES ["Enterprise Systems"]
            ES1["GitHub Repos"]
            ES2["Confluence Spaces"]
            ES3["Private Repos"]
            ES4["Branch Selection"]
        end
    end
    
    subgraph PP ["PROCESSING PIPELINE"]
        subgraph CC ["Content Cleaning"]
            CC1["HTML Parsing"]
            CC2["Text Extract"]
            CC3["Format Normal"]
        end
        subgraph TC ["Text Chunking"]
            TC1["Smart Splits"]
            TC2["Overlap Mgmt"]
            TC3["Size Control"]
        end
        subgraph EB ["Embedding"]
            EB1["OpenAI API"]
            EB2["Vector Gen"]
            EB3["Batch Process"]
        end
        subgraph QA ["Quality Assessment"]
            QA1["Relevance Scoring"]
            QA2["Search Quality"]
            QA3["Collection Auditing"]
        end
    end
    
    subgraph SSE ["STORAGE & SEARCH ENGINE"]
        subgraph CD ["ChromaDB"]
            CD1["Vector Store"]
            CD2["Persistence"]
            CD3["Performance"]
        end
        subgraph COL ["Collections"]
            COL1["Topic-based"]
            COL2["Named Groups"]
            COL3["Metadata"]
        end
        subgraph SS ["Semantic Search"]
            SS1["Similarity"]
            SS2["Thresholds"]
            SS3["Cross-search"]
        end
        subgraph MS ["Metadata Store"]
            MS1["Source Attribution"]
            MS2["Timestamps"]
            MS3["Descriptions"]
        end
    end
    
    subgraph UI ["USER INTERFACES"]
        subgraph WUI ["Web UI"]
            WUI1["Discovery"]
            WUI2["Visual Mgmt"]
            WUI3["Interactive"]
        end
        subgraph CLI ["CLI"]
            CLI1["Full Admin"]
            CLI2["All Features"]
            CLI3["Maintenance"]
        end
        subgraph MCP ["MCP Server"]
            MCP1["Tool Provider"]
            MCP2["Secure Ops"]
            MCP3["FastMCP"]
        end
        subgraph AI ["AI Assistant Integ"]
            AI1["Claude Code Cmds"]
            AI2["AI Workflows"]
            AI3["Assistant Commands"]
        end
    end
    
    CS --> PP
    PP --> SSE
    SSE --> UI
```

### Technical Component Architecture

```mermaid
graph TB
    subgraph RAG ["RAG RETRIEVER SYSTEM"]
        subgraph INTERFACES ["USER INTERFACES"]
            WEB["Streamlit Web UI<br/>(ui/app.py)<br/>• Discovery<br/>• Collections<br/>• Search"]
            CLI_MOD["CLI Module<br/>(cli.py)<br/>• Full Control<br/>• Admin Ops<br/>• All Features<br/>• Maintenance"]
            MCP_SRV["MCP Server<br/>(mcp/server.py)<br/>• FastMCP Framework<br/>• Tool Definitions<br/>• AI Integration<br/>• Claude Code Support"]
        end
        
        subgraph CORE ["CORE ENGINE"]
            PROC["Content Processing<br/>(main.py)<br/>• URL Processing<br/>• Search Coordination<br/>• Orchestration"]
            LOADERS["Document Loaders<br/>• LocalLoader<br/>• ImageLoader<br/>• GitHubLoader<br/>• ConfluenceLoader"]
            SEARCH["Search Engine<br/>(searcher.py)<br/>• Semantic Search<br/>• Cross-collection<br/>• Score Ranking"]
        end
        
        subgraph DATA ["DATA LAYER"]
            VECTOR["Vector Store<br/>(store.py)<br/>• ChromaDB<br/>• Collections<br/>• Metadata<br/>• Persistence"]
            CRAWLERS["Web Crawlers<br/>(crawling/)<br/>• Playwright<br/>• Crawl4AI<br/>• ContentClean<br/>• URL Handling"]
            CONFIG["Config System<br/>(config.py)<br/>• YAML Config<br/>• User Settings<br/>• API Keys<br/>• Validation"]
        end
        
        subgraph EXTERNAL ["EXTERNAL APIS"]
            OPENAI["OpenAI API<br/>• Embeddings<br/>• Vision Model<br/>• Batch Process"]
            SEARCH_API["Search APIs<br/>• Google Search<br/>• DuckDuckGo<br/>• Web Discovery"]
            EXT_SYS["External Systems<br/>• GitHub API<br/>• Confluence<br/>• Git Repos"]
        end
    end
    
    WEB --> PROC
    CLI_MOD --> PROC
    MCP_SRV --> PROC
    
    PROC <--> LOADERS
    PROC <--> SEARCH
    LOADERS <--> SEARCH
    
    CORE --> VECTOR
    CORE --> CRAWLERS
    CORE --> CONFIG
    
    DATA --> OPENAI
    DATA --> SEARCH_API
    DATA --> EXT_SYS
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