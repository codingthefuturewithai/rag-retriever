# RAG Retriever Getting Started Guide

Interactive guidance for new users to navigate the RAG Retriever ecosystem and get productive quickly.

## Prerequisites
This command provides comprehensive guidance for new users. No specific technical prerequisites required.

## Arguments
Use $ARGUMENTS to specify your experience level or specific needs:
- "new" - Complete beginner walkthrough
- "experienced" - Advanced user quickstart
- "mcp" - Focus on MCP server setup and usage
- "cli" - Focus on CLI operations and administration
- "admin" - Administrative operations guidance
- "help" - Show all available guidance options

Examples:
- "new" - Complete beginner guide
- "experienced" - Skip basics, show advanced features
- "mcp" - MCP server setup and usage
- "cli" - CLI operations and administration
- "admin" - Administrative tasks and maintenance

## Implementation Approach
This command uses **direct implementation** to provide personalized guidance based on user experience and needs.

## Your Task

### 1. **Assess User Experience and Needs**
   - Determine user's experience level from $ARGUMENTS
   - Identify specific focus areas (MCP, CLI, admin, etc.)
   - Provide appropriate guidance level

### 2. **Provide Tailored Guidance**

#### **For New Users ("new")**
**You are**: New to RAG Retriever, need complete walkthrough
**I'll provide**: Step-by-step guidance from zero to productive

1. **System Overview**
   - Explain the three interfaces: MCP Server, CLI, Web UI
   - Show capability differences and when to use each
   - Provide decision matrix for interface selection

2. **Quick Start Path Selection**
   - **Path 1**: "I want AI assistant integration" → MCP setup
   - **Path 2**: "I want full control from start" → CLI setup
   - **Path 3**: "I want to understand everything first" → Complete overview

3. **Next Steps**
   - Direct to appropriate setup prompt
   - Provide specific commands to get started
   - Set expectations for learning timeline

#### **For Experienced Users ("experienced")**
**You are**: Familiar with RAG concepts, want to get productive quickly
**I'll provide**: Advanced quickstart with focus on powerful features

1. **Advanced Capabilities Overview**
   - CLI-only features: image analysis, GitHub integration, administrative control
   - MCP server advantages: AI assistant workflows, secure operations
   - Enterprise features: Confluence integration, advanced content processing

2. **Power User Recommendations**
   - Start with CLI for full control
   - Add MCP integration for AI workflows
   - Focus on collection organization and quality management

3. **Advanced Workflows**
   - Multi-source content ingestion
   - Administrative maintenance schedules
   - Quality assessment strategies

#### **For MCP Focus ("mcp")**
**You want**: MCP server setup and AI assistant integration
**I'll provide**: MCP-specific guidance and best practices

1. **MCP Server Setup**
   - Direct to [`SETUP_ASSISTANT_PROMPT.md`](SETUP_ASSISTANT_PROMPT.md)
   - Explain MCP configuration process
   - Show Claude Code integration steps

2. **Available MCP Commands**
   - `/rag-list-collections` - Collection discovery
   - `/rag-search-knowledge` - Semantic search
   - `/rag-index-website` - Website crawling
   - `/rag-audit-collections` - Quality assessment
   - `/rag-assess-quality` - Content evaluation
   - `/rag-manage-collections` - Administrative guidance
   - `/rag-ingest-content` - Advanced content help
   - `/rag-cli-help` - CLI command assistance

3. **MCP Workflows**
   - Daily usage patterns with AI assistants
   - Best practices for MCP operations
   - When to switch to CLI for advanced operations

#### **For CLI Focus ("cli")**
**You want**: Command-line operations and full system control
**I'll provide**: CLI-specific guidance and administrative capabilities

1. **CLI Setup and Configuration**
   - Direct to [`CLI_ASSISTANT_PROMPT.md`](CLI_ASSISTANT_PROMPT.md)
   - Show complete command reference
   - Explain CLI-only capabilities

2. **CLI-Only Features**
   - Collection deletion: `rag-retriever --clean --collection NAME`
   - Local file processing: `rag-retriever --ingest-directory PATH`
   - Image analysis: `rag-retriever --ingest-image PATH`
   - GitHub integration: `rag-retriever --github-repo URL`
   - System maintenance: `rag-retriever --init`, `rag-retriever --ui`

3. **CLI Workflows**
   - Administrative task procedures
   - Advanced content ingestion strategies
   - System maintenance and troubleshooting

#### **For Administrative Focus ("admin")**
**You want**: Administrative operations and system maintenance
**I'll provide**: Administrative guidance and maintenance procedures

1. **Administrative Capabilities**
   - Direct to [`ADMIN_ASSISTANT_PROMPT.md`](ADMIN_ASSISTANT_PROMPT.md)
   - Explain administrative limitations of MCP (by design)
   - Show CLI administrative commands

2. **Key Administrative Tasks**
   - Collection management and cleanup
   - Content quality assessment and maintenance
   - System health monitoring and optimization
   - Re-indexing procedures (no incremental updates)

3. **Administrative Workflows**
   - Regular maintenance schedules
   - Quality assessment procedures
   - Troubleshooting and recovery processes

### 3. **Provide Navigation Guidance**

#### **Available Documentation**
- [`SETUP_ASSISTANT_PROMPT.md`](SETUP_ASSISTANT_PROMPT.md) - Initial setup
- [`USAGE_ASSISTANT_PROMPT.md`](USAGE_ASSISTANT_PROMPT.md) - Daily operations
- [`CLI_ASSISTANT_PROMPT.md`](CLI_ASSISTANT_PROMPT.md) - Complete CLI reference
- [`ADMIN_ASSISTANT_PROMPT.md`](ADMIN_ASSISTANT_PROMPT.md) - Administrative operations
- [`ADVANCED_CONTENT_INGESTION_PROMPT.md`](ADVANCED_CONTENT_INGESTION_PROMPT.md) - Rich content processing
- [`TROUBLESHOOTING_ASSISTANT_PROMPT.md`](TROUBLESHOOTING_ASSISTANT_PROMPT.md) - Problem solving
- [`GETTING_STARTED_GUIDE.md`](GETTING_STARTED_GUIDE.md) - Complete ecosystem guide

#### **Interactive Commands**
- `/rag-getting-started` - This guide
- `/rag-cli-help` - CLI command builder
- `/rag-manage-collections` - Collection management
- `/rag-ingest-content` - Content ingestion guidance

### 4. **Provide Specific Next Steps**

#### **Immediate Actions**
1. **Setup**: Specific prompt to follow for initial configuration
2. **First Success**: Concrete first task to accomplish
3. **Verification**: How to confirm everything is working
4. **Next Learning**: Where to go for continued learning

#### **Success Metrics**
- **30 minutes**: Basic setup and first search working
- **1 hour**: Understanding interface differences and capabilities
- **1 day**: Productive use of primary interface
- **1 week**: Advanced operations and administrative tasks

### 5. **Common User Scenarios**

#### **Scenario 1: Documentation Search System**
- Focus on MCP setup for AI assistant integration
- Website indexing and search workflows
- Quality assessment and maintenance

#### **Scenario 2: Personal Knowledge Base**
- Focus on CLI for full control and local content
- Advanced content ingestion (files, images, GitHub)
- Administrative maintenance procedures

#### **Scenario 3: Enterprise Integration**
- Focus on both MCP and CLI capabilities
- Advanced content sources (Confluence, GitHub)
- Team workflows and quality management

## Success Criteria
- User understands their options and capabilities
- Clear next steps provided based on user needs
- Appropriate documentation resources identified
- Realistic expectations set for learning timeline

## Your Getting Started Actions

**You CAN:**
- Assess user experience and provide appropriate guidance level
- Recommend specific learning paths based on user needs
- Direct users to appropriate documentation and prompts
- Provide realistic timelines and expectations
- Explain interface differences and capabilities

**You CANNOT:**
- Perform setup operations directly
- Access system configuration
- Execute commands or operations
- Modify system settings

## Remember

**Goal**: Get users productive quickly while building solid understanding of the ecosystem.

**Key Concepts to Emphasize**:
- Three interfaces serve different purposes
- MCP for AI workflows, CLI for administration
- No incremental updates - plan collection organization
- Quality management is critical for good results

**Success Indicators**:
- User can successfully search indexed content
- User understands when to use which interface
- User knows where to get help for specific tasks
- User has realistic expectations for system capabilities