# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## CRITICAL SESSION CONTEXT (JULY 2025)

**COMPLETED MAJOR DOCUMENTATION OVERHAUL - ALL CHANGES APPLIED AND TESTED**

### What Was Just Completed:
1. **AI-First Documentation Strategy Implemented** - Following claude-mcp-knowledge-base pattern
2. **Complete CLI Documentation Created** - Comprehensive coverage of CLI-only capabilities
3. **Command Namespace Updated** - All commands now use `rag-` prefix for clarity
4. **UI Capabilities Properly Documented** - 5 screenshots integrated with accurate descriptions
5. **Master Navigator Created** - GETTING_STARTED_GUIDE.md for new users
6. **Architecture Diagrams Updated** - Mermaid diagrams ready for README integration

### New Documentation Files Created:
- `CLI_ASSISTANT_PROMPT.md` - Complete CLI reference and workflows
- `ADMIN_ASSISTANT_PROMPT.md` - Administrative operations and maintenance  
- `ADVANCED_CONTENT_INGESTION_PROMPT.md` - Images, PDFs, GitHub, Confluence
- `GETTING_STARTED_GUIDE.md` - Master navigator for entire ecosystem

### New Claude Code Commands (with rag- prefix):
- `/rag-list-collections` - Show collections with metadata
- `/rag-search-knowledge` - Semantic search across collections
- `/rag-index-website` - Crawl and index websites
- `/rag-audit-collections` - Review collection health
- `/rag-assess-quality` - Evaluate content quality 
- `/rag-manage-collections` - Administrative operations (provides CLI commands)
- `/rag-ingest-content` - Advanced content ingestion guidance
- `/rag-cli-help` - Interactive CLI help system
- `/rag-getting-started` - Interactive getting started guide

### UI Screenshots Integrated (5 total):
1. `rag-retriever-UI-collections.png` - Collections management overview
2. `rag-retreiver-UI-delete-collection.png` - Collection actions and deletion
3. `rag-retriever-UI-search.png` - Interactive knowledge search interface
4. `rag-retriever-UI-compare-collections.png` - Collection analytics and comparison
5. `rag-retreiver-UI-discover-and-index-new-web-content.png` - Content discovery workflow

### Key Architectural Understanding:
- **3 Interfaces**: MCP Server (AI-friendly), CLI (full admin), Web UI (visual management)
- **MCP Limitations by Design**: No deletion, no local files, no advanced ingestion (security)
- **CLI Full Control**: All capabilities including admin, local files, images, GitHub, Confluence
- **Web UI Strengths**: Discovery workflow (search → select → index), visual confirmation, analytics
- **No Incremental Updates**: Must delete collections before re-indexing
- **Quality Assessment**: Only accessible via Claude Code commands

### Ready for Implementation:
Two Mermaid architecture diagrams are prepared for README:
1. **Layered Content Ingestion Architecture** - Shows full content source capabilities
2. **Technical Component Architecture** - Shows system components and relationships

**NEXT STEP**: Replace text diagrams in README with Mermaid versions if approved.

**STATUS**: All documentation complete and integrated. System ready for production use.

## Development Commands

### Testing
- `python -m pytest` - Run all tests with coverage reporting
- `python -m pytest tests/unit/` - Run unit tests only
- `python -m pytest tests/integration/` - Run integration tests only
- `python -m pytest -k "test_name"` - Run specific test by name
- `python -m pytest --verbose` - Run tests with verbose output
- `python -m pytest --collect-only` - Show all available tests without running them

### Development Setup
- `python -m venv venv` - Create virtual environment
- `source venv/bin/activate` (Unix/Mac) or `venv\Scripts\activate` (Windows) - Activate virtual environment
- `pip install -e .` - Install package in editable mode for development
- `python -m playwright install chromium` - Install required browser for web crawling

### Running the Application
- `python -m rag_retriever.cli --help` - Show all command line options
- `python -m rag_retriever.cli --init` - Initialize configuration files
- `python -m rag_retriever.cli --ui` - Launch the web interface
- `python scripts/run_ui.py` - Alternative way to run the UI from development setup

### MCP Server
- `python -m rag_retriever.mcp` - Run MCP server in stdio mode
- `python -m rag_retriever.mcp --port 3001` - Run MCP server in SSE mode
- `mcp dev rag_retriever/mcp/server.py` - Run MCP server in debug mode

## Architecture Overview

### Core Components

**CLI Layer (`rag_retriever/cli.py`)**
- Command-line interface parsing and argument handling
- Entry point for all user interactions
- Coordinates between different modules

**Main Application Logic (`rag_retriever/main.py`)**
- Core orchestration functions: `process_url()`, `search_content()`
- System information gathering and OpenAI client initialization
- Error handling and retry logic with exponential backoff

**Vector Store (`rag_retriever/vectorstore/store.py`)**
- ChromaDB-based vector storage with OpenAI embeddings
- Collection management with metadata tracking
- Document chunking and batch processing with configurable retry logic
- Uses `text-embedding-3-large` model (3072 dimensions) by default

**Search System (`rag_retriever/search/`)**
- `searcher.py`: Vector similarity search with configurable thresholds
- `web_search.py`: Web search integration (Google/DuckDuckGo)
- Results include relevance scores and source attribution

**Document Processing (`rag_retriever/document_processor/`)**
- `local_loader.py`: Local file processing (PDF, markdown, text)
- `github_loader.py`: GitHub repository cloning and processing
- `confluence_loader.py`: Confluence space content extraction
- `image_loader.py`: Image analysis using OpenAI vision models
- `vision_analyzer.py`: AI-powered image description generation

**Web Crawling (`rag_retriever/crawling/`)**
- `playwright_crawler.py`: Playwright-based web page crawling (default)
- `crawl4ai_crawler.py`: Crawl4AI-based crawling with aggressive navigation filtering
- `content_cleaner.py`: HTML content cleaning and text extraction
- `exceptions.py`: Custom exceptions for crawler error handling
- Crawler selection via config: `crawler.type: "playwright"` or `"crawl4ai"`

**MCP Integration (`rag_retriever/mcp/server.py`)**
- Model Context Protocol server for AI assistant integration
- Supports stdio, SSE, and debug modes
- Provides search and content processing capabilities

### Configuration System

**Config Management (`rag_retriever/utils/config.py`)**
- YAML-based configuration with OS-specific paths
- User config: `~/.config/rag-retriever/config.yaml` (Unix/Mac) or `%APPDATA%\rag-retriever\config.yaml` (Windows)
- Default config: `rag_retriever/config/config.yaml`

**Key Configuration Areas:**
- Crawler selection (`crawler.type: "playwright"` or `"crawl4ai"`) with automatic fallback
- Vector store settings (embedding model, chunk size, dimensions)
- Document processing (supported formats, PDF settings, GitHub integration)
- Browser settings (Playwright configuration, stealth options)
- API keys (OpenAI, Google Search, Confluence)
- Search providers and thresholds
- System validation occurs before any configuration is used

### Data Flow

1. **Content Ingestion**: Documents/URLs → Document Processors → Text Chunks
2. **Embedding**: Text Chunks → OpenAI Embeddings → Vector Store (ChromaDB)
3. **Search**: Query → Embedding → Similarity Search → Ranked Results
4. **Collection Management**: Content organized into named collections with metadata

### Recent Development Notes

**AI-First Documentation Implementation (July 2025)**
- Implemented comprehensive AI-first documentation strategy following claude-mcp-knowledge-base pattern
- Created specialized assistant prompts for different user types and use cases
- Updated all Claude Code commands to use `rag-` prefix for namespace clarity
- Integrated Web UI capabilities with accurate screenshot documentation
- Created master navigator (GETTING_STARTED_GUIDE.md) to prevent user overwhelm
- Enhanced README with complete MCP vs CLI vs UI capability comparison
- Documented CLI-only administrative capabilities (collection deletion, local file processing)
- Quality assessment tools accessible via Claude Code commands for systematic content evaluation

**Crawl4AI Integration (January 2025)**
- Successfully integrated Crawl4AI as alternative to Playwright crawling
- Key implementation: BFSDeepCrawlStrategy + PruningContentFilter (threshold=0.7) + fit_markdown
- Working solution in `/crawl4ai_poc/aggressive_filtering.py` demonstrates proper content filtering
- Integration complete: drop-in replacement via `get_crawler()` factory in `main.py`
- Dependencies updated: playwright>=1.49.0, crawl4ai>=0.4.0 added to pyproject.toml
- Configuration: Toggle via `crawler.type` setting in config.yaml
- Performance: 20x faster parsing with aggressive navigation filtering
- Resolved dotenv warnings: Added `SUPPRESS_DOTENV_WARNING` environment variable to prevent crawl4ai dotenv parsing warnings
- **Future Enhancement Consideration**: Crawl4AI LLM Integration
  - Crawl4AI supports LLM-based extraction strategies for structured content extraction
  - Potential capabilities: automatic schema extraction, content summarization, entity extraction
  - Could enhance RAG Retriever with intelligent content preprocessing and structured data extraction
  - Would require LLM provider configuration (OpenAI, Anthropic, Gemini, etc.) for extraction strategies
  - API keys already configured via config.yaml, making future LLM integration straightforward

**System-Level Dependency Validation (January 2025)**
- Implemented comprehensive system validation in `utils/system_validation.py`
- Validates ALL system-level tools on startup: Playwright browsers, Git, Tesseract OCR
- Critical requirement: At least one working crawler (Playwright OR Crawl4AI) must be available
- Early failure principle: Application refuses to start if system dependencies missing
- Validation runs for both CLI (`rag-retriever` command) and MCP clients (`mcp-rag-retriever`)
- Import chain: MCP server → `mcp/server.py` → imports `main.py` → validation triggers
- Clear error messages with installation instructions prevent runtime surprises
- Design principle: Better to fail fast at startup than fail late during tool execution

### Key Design Patterns

**Async/Await Architecture**
- Playwright crawler uses async operations for web crawling
- Crawl4AI crawler uses BFSDeepCrawlStrategy for content extraction
- Windows-specific event loop handling in `utils/windows.py`

**Error Handling**
- Custom exceptions for different error types
- Retry logic with exponential backoff for API calls
- Graceful degradation for optional features

**Extensible Plugin System**
- Document loaders are modular and can be extended
- Search providers can be swapped (Google/DuckDuckGo)
- Image processing with pluggable vision models

**Configuration-Driven**
- All behavior configurable via YAML files
- OS-specific path handling
- Environment variable overrides supported

## Development Guidelines

### Testing Strategy
- Unit tests focus on individual components
- Integration tests cover end-to-end workflows
- Use pytest fixtures for test data management
- Mock external APIs in unit tests

### Code Organization
- Each major feature has its own module
- Shared utilities in `utils/` directory
- Configuration centralized in `config/`
- Clear separation between CLI, core logic, and data layers

### Dependencies
- Core: OpenAI, ChromaDB, Langchain, Playwright
- UI: Streamlit, Plotly, Pandas
- Testing: pytest, pytest-cov
- Python 3.10-3.12 supported

### API Key Management
- Store API keys in config.yaml with restricted file permissions (600)
- Never commit API keys to version control
- Support environment variable overrides
- Graceful fallback when optional API keys are missing