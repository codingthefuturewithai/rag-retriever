# Manage RAG Retriever Collections

Administrative collection operations including deletion, cleanup, and maintenance tasks.

## Prerequisites
This command requires both CLI access and MCP server configuration. Administrative operations use the CLI while status checking uses MCP tools.

## Arguments
Use $ARGUMENTS to specify management operation:
- "list" - Show all collections with detailed analysis
- "delete COLLECTION_NAME" - Delete specific collection
- "clean" - Delete entire vector store (nuclear option)
- "health" - Assess collection health and quality

Examples:
- "list" - Show all collections
- "delete old_docs" - Delete specific collection
- "clean" - Delete entire vector store
- "health python_docs" - Check specific collection health

## Implementation Approach
This command uses **direct implementation** combining MCP tools for analysis and CLI guidance for administrative actions.

## Your Task

### 1. **Parse Arguments**
   - Extract operation type from $ARGUMENTS
   - Identify target collection name if specified
   - Provide guidance on available operations if unclear

### 2. **Collection Management Operations**

#### **List Collections (Enhanced)**
- Use `list_collections()` to get current state
- Analyze collection sizes, dates, and metadata
- Identify potential issues or maintenance needs
- Recommend collection organization improvements

#### **Delete Specific Collection**
- **IMPORTANT**: This requires CLI access, not MCP
- Use `list_collections()` to verify collection exists
- Provide exact CLI command: `rag-retriever --clean --collection COLLECTION_NAME`
- Explain that this is irreversible
- Suggest verification steps after deletion

#### **Clean Entire Vector Store**
- **CRITICAL**: This deletes ALL data permanently
- Use `list_collections()` to show what will be deleted
- Provide exact CLI command: `rag-retriever --clean`
- Require explicit confirmation from user
- Explain recovery options (re-indexing from sources)

#### **Health Assessment**
- Use `vector_search()` to test collection functionality
- Check for common issues (empty results, low scores)
- Identify collections needing maintenance
- Recommend improvement actions

### 3. **Administrative Workflows**

#### **Collection Cleanup Workflow**
1. List all collections with analysis
2. Identify obsolete or problematic collections
3. Provide deletion commands for cleanup
4. Suggest consolidation opportunities

#### **Re-indexing Workflow**
1. Show current collection state
2. Provide deletion command for old collection
3. Suggest appropriate re-indexing command
4. Include verification steps

#### **System Maintenance**
1. Comprehensive collection health check
2. Identify storage optimization opportunities
3. Recommend maintenance schedule
4. Provide troubleshooting guidance

### 4. **Safety and Verification**
- Always confirm destructive operations
- Provide verification commands after changes
- Explain recovery procedures
- Warn about irreversible actions

## CLI Commands You Will Provide

### Collection Management
```bash
# List collections (enhanced analysis)
rag-retriever --list-collections --verbose

# Delete specific collection
rag-retriever --clean --collection COLLECTION_NAME

# Nuclear option: delete all data
rag-retriever --clean

# Verify changes
rag-retriever --list-collections
```

### Health and Maintenance
```bash
# Test collection functionality
rag-retriever --query "test" --collection COLLECTION_NAME --verbose

# System health check
rag-retriever --query "health" --search-all-collections --limit 1

# Re-index collection
rag-retriever --clean --collection OLD_COLLECTION
rag-retriever --fetch-url "https://source.com" --collection NEW_COLLECTION
```

## Success Criteria
- Clear understanding of collection management operations
- Proper CLI commands provided for administrative tasks
- Safety warnings and confirmations for destructive operations
- Verification steps included for all changes
- Comprehensive health assessment when requested

## Available MCP Tools
- `list_collections()` - Show current collections with metadata
- `vector_search(query_text, collection_name, search_all_collections)` - Test collection functionality

## Important Notes
- **Administrative operations require CLI access** - MCP cannot delete or modify collections
- **All deletion operations are irreversible** - Always confirm before proceeding
- **No incremental updates** - Must delete and re-index to update content
- **Safety first** - Provide verification steps and explain consequences

## Your Administrative Actions

**You CAN:**
- Analyze collection health and provide recommendations
- Construct CLI commands for administrative operations
- Provide step-by-step workflows for complex tasks
- Offer troubleshooting guidance for collection issues

**You CANNOT:**
- Execute administrative commands directly
- Delete collections without CLI access
- Modify system configuration
- Access actual collection data beyond metadata