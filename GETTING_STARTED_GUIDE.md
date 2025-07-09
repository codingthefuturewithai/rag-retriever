# Getting Started with RAG Retriever - Complete Guide

**New to RAG Retriever?** This guide will help you navigate the complete ecosystem and get productive quickly.

## 🎯 For New Developers

**You are**: Familiar with RAG concepts, experienced programmer, but new to this specific RAG solution  
**You want**: To build searchable knowledge bases, understand administrative capabilities, and know how to get help when needed  
**You need**: A clear path from zero to productive, with full understanding of available tools and interfaces

## 📋 Complete System Overview

RAG Retriever provides **three different interfaces** for different use cases:

### 🤖 **MCP Server** (AI Assistant Integration)
- **Best for**: Daily usage with Claude Code and other AI assistants
- **Provides**: Secure, AI-friendly access to core functionality
- **Capabilities**: Search, index websites, list collections, quality assessment
- **Limitations**: No administrative operations (by design for security)

### 💻 **Command Line Interface** (Full Control)
- **Best for**: Administrative tasks, advanced content ingestion, system maintenance
- **Provides**: Complete system control with all capabilities
- **Capabilities**: Everything MCP does PLUS collection deletion, local file processing, image analysis, GitHub integration
- **Power user**: Full administrative control

### 🌐 **Web Interface** (Visual Management)
- **Best for**: Visual exploration, collection browsing, interactive search
- **Provides**: Streamlit-based GUI for visual management
- **Access**: Launch via `rag-retriever --ui`

## 🚀 Quick Start Decision Tree

**Choose your path based on your immediate needs:**

### Path 1: "I want to get started quickly with AI assistants"
→ **Start with MCP Setup**
1. Follow [`SETUP_ASSISTANT_PROMPT.md`](SETUP_ASSISTANT_PROMPT.md) for MCP configuration
2. Use [`USAGE_ASSISTANT_PROMPT.md`](USAGE_ASSISTANT_PROMPT.md) for daily operations
3. Graduate to CLI when you need administrative control

### Path 2: "I want full control from the beginning"
→ **Start with CLI**
1. Follow [`SETUP_ASSISTANT_PROMPT.md`](SETUP_ASSISTANT_PROMPT.md) for basic setup
2. Use [`CLI_ASSISTANT_PROMPT.md`](CLI_ASSISTANT_PROMPT.md) for comprehensive CLI operations
3. Add MCP integration later for AI assistant workflows

### Path 3: "I need to understand everything first"
→ **Read this guide completely, then choose Path 1 or 2**

## 📚 Available Documentation and Prompts

### 🎬 **Setup and Configuration**
- [`SETUP_ASSISTANT_PROMPT.md`](SETUP_ASSISTANT_PROMPT.md) - Initial setup for both MCP and CLI
- [`QUICKSTART.md`](QUICKSTART.md) - Copy-paste commands for immediate use

### 📖 **Daily Usage and Operations**
- [`USAGE_ASSISTANT_PROMPT.md`](USAGE_ASSISTANT_PROMPT.md) - MCP workflows and best practices
- [`CLI_ASSISTANT_PROMPT.md`](CLI_ASSISTANT_PROMPT.md) - Complete CLI reference and workflows

### 🔧 **Advanced and Administrative**
- [`ADMIN_ASSISTANT_PROMPT.md`](ADMIN_ASSISTANT_PROMPT.md) - Collection management, deletion, system maintenance
- [`ADVANCED_CONTENT_INGESTION_PROMPT.md`](ADVANCED_CONTENT_INGESTION_PROMPT.md) - Images, PDFs, GitHub, Confluence

### 🆘 **Help and Troubleshooting**
- [`TROUBLESHOOTING_ASSISTANT_PROMPT.md`](TROUBLESHOOTING_ASSISTANT_PROMPT.md) - Common issues and solutions
- This guide - Master navigator for the ecosystem

## 🎯 Available Claude Code Commands

Once you have MCP configured, these commands are available:

### Core Operations
- `/rag-list-collections` - Show all collections
- `/rag-search-knowledge` - Search across collections
- `/rag-index-website` - Crawl and index websites
- `/rag-audit-collections` - Review collection health
- `/rag-assess-quality` - Evaluate content quality

### Administrative Guidance
- `/rag-manage-collections` - Administrative operations (provides CLI commands)
- `/rag-ingest-content` - Advanced content ingestion guidance
- `/rag-cli-help` - Interactive CLI help system
- `/rag-getting-started` - This guide as an interactive command

## 🛠️ Key Concepts You Need to Know

### 1. **MCP vs CLI Capability Differences**
- **MCP**: Secure, AI-friendly, limited to safe operations
- **CLI**: Full system control, administrative operations, advanced content types
- **When to use each**: See the comparison table in [`README.md`](README.md)

### 2. **No Incremental Updates**
- RAG Retriever doesn't support incremental updates
- To refresh content: Delete collection → Re-index from scratch
- Plan your collection organization accordingly

### 3. **Collection Organization Strategy**
- Use descriptive names: `python_docs`, `company_wiki`, not `docs1`
- One topic per collection: Keep related content together
- Plan for growth: Start with core content, expand gradually

### 4. **Content Quality is Critical**
- Poor quality content corrupts your knowledge base
- Use quality assessment tools regularly
- Remove outdated content promptly

## 🗺️ Learning Path for New Users

### Stage 1: **Basic Setup and First Success** (30 minutes)
1. **Setup**: Use [`SETUP_ASSISTANT_PROMPT.md`](SETUP_ASSISTANT_PROMPT.md) to get configured
2. **First index**: Index a simple documentation site
3. **First search**: Verify content is searchable
4. **Success metric**: You can search and get relevant results

### Stage 2: **Understanding the Ecosystem** (1 hour)
1. **Explore interfaces**: Try MCP commands, CLI commands, and web UI
2. **Learn collection management**: List, create, and organize collections
3. **Quality assessment**: Use audit and quality tools
4. **Success metric**: You understand how to organize and maintain content

### Stage 3: **Advanced Operations** (As needed)
1. **Administrative tasks**: Learn collection deletion and cleanup
2. **Advanced content**: Process images, local files, GitHub repositories
3. **Enterprise integration**: Connect to Confluence or other systems
4. **Success metric**: You can handle complex content ingestion and system maintenance

## 🎛️ Interface Decision Matrix

| What you want to do | MCP Server | CLI | Web UI | Recommendation |
|---------------------|------------|-----|---------|----------------|
| Search content | ✅ | ✅ | ✅ | **MCP** (AI-friendly) |
| Index websites | ✅ | ✅ | ❌ | **MCP** (convenient) |
| Delete collections | ❌ | ✅ | ❌ | **CLI** (only option) |
| Process local files | ❌ | ✅ | ❌ | **CLI** (only option) |
| Analyze images | ❌ | ✅ | ❌ | **CLI** (only option) |
| GitHub integration | ❌ | ✅ | ❌ | **CLI** (only option) |
| System maintenance | ❌ | ✅ | ❌ | **CLI** (only option) |
| Visual exploration | ❌ | ❌ | ✅ | **Web UI** (only option) |
| AI assistant workflows | ✅ | ❌ | ❌ | **MCP** (designed for this) |

## 🆘 Where to Get Help

### 1. **For Specific Operations**
- **MCP workflows**: [`USAGE_ASSISTANT_PROMPT.md`](USAGE_ASSISTANT_PROMPT.md)
- **CLI operations**: [`CLI_ASSISTANT_PROMPT.md`](CLI_ASSISTANT_PROMPT.md)
- **Administrative tasks**: [`ADMIN_ASSISTANT_PROMPT.md`](ADMIN_ASSISTANT_PROMPT.md)
- **Advanced content**: [`ADVANCED_CONTENT_INGESTION_PROMPT.md`](ADVANCED_CONTENT_INGESTION_PROMPT.md)

### 2. **For Problems and Errors**
- **Troubleshooting guide**: [`TROUBLESHOOTING_ASSISTANT_PROMPT.md`](TROUBLESHOOTING_ASSISTANT_PROMPT.md)
- **CLI help command**: `/rag-cli-help` or `rag-retriever --help`
- **Verbose output**: Add `--verbose` to any CLI command

### 3. **For Interactive Help**
- **Getting started**: `/rag-getting-started` command
- **CLI help**: `/rag-cli-help` command
- **Collection management**: `/rag-manage-collections` command

## 🏁 Common Success Scenarios

### Scenario 1: **Documentation Search System**
1. Use [`SETUP_ASSISTANT_PROMPT.md`](SETUP_ASSISTANT_PROMPT.md) to configure MCP
2. Use `/rag-index-website` to index documentation sites
3. Use `/rag-search-knowledge` for daily searches
4. Use `/rag-audit-collections` for quality maintenance

### Scenario 2: **Personal Knowledge Base**
1. Use [`CLI_ASSISTANT_PROMPT.md`](CLI_ASSISTANT_PROMPT.md) for full CLI setup
2. Use CLI to process local files, images, and GitHub repositories
3. Use [`ADMIN_ASSISTANT_PROMPT.md`](ADMIN_ASSISTANT_PROMPT.md) for maintenance
4. Add MCP integration for AI assistant workflows

### Scenario 3: **Enterprise Integration**
1. Use [`SETUP_ASSISTANT_PROMPT.md`](SETUP_ASSISTANT_PROMPT.md) for basic setup
2. Use [`ADVANCED_CONTENT_INGESTION_PROMPT.md`](ADVANCED_CONTENT_INGESTION_PROMPT.md) for Confluence
3. Use [`ADMIN_ASSISTANT_PROMPT.md`](ADMIN_ASSISTANT_PROMPT.md) for ongoing maintenance
4. Use [`USAGE_ASSISTANT_PROMPT.md`](USAGE_ASSISTANT_PROMPT.md) for team workflows

## 🔄 Typical User Journey

### Week 1: **Getting Started**
- Setup and configuration
- First successful indexing and search
- Understanding basic concepts

### Week 2: **Building Your Knowledge Base**
- Indexing important documentation
- Learning collection organization
- Developing search skills

### Month 1: **Advanced Operations**
- Administrative tasks and maintenance
- Advanced content ingestion
- Quality assessment and optimization

### Ongoing: **Maintenance and Expansion**
- Regular quality audits
- Content updates and re-indexing
- New content source integration

## 💡 Pro Tips for Success

1. **Start small**: Index one small documentation site first
2. **Name collections well**: Use descriptive, consistent names
3. **Quality over quantity**: Better to have accurate content than lots of poor content
4. **Learn both interfaces**: MCP for daily use, CLI for administration
5. **Regular maintenance**: Schedule periodic quality assessments
6. **Document your setup**: Keep track of what's indexed where

## 🎯 Next Steps

**Ready to start?** Choose your path:

1. **Quick MCP setup**: Go to [`SETUP_ASSISTANT_PROMPT.md`](SETUP_ASSISTANT_PROMPT.md)
2. **Full CLI control**: Go to [`CLI_ASSISTANT_PROMPT.md`](CLI_ASSISTANT_PROMPT.md)
3. **Need help deciding**: Use the `/rag-getting-started` command for interactive guidance

Remember: The goal is to build a reliable, searchable knowledge base that enhances your development workflow. Start with the basics, then gradually expand your capabilities as you become more comfortable with the system.