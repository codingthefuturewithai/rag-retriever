# Admin Assistant Prompt for RAG Retriever

Read this entire prompt, then help me perform administrative tasks for RAG Retriever system management, collection maintenance, and troubleshooting.

## Context

I need to perform administrative operations on my RAG Retriever system including collection management, system maintenance, quality control, and troubleshooting. These tasks require CLI access since administrative functions are intentionally not exposed through the MCP server for security reasons.

## Administrative Scope

### MCP Server Limitations (By Design)
- **No deletion capabilities** - Cannot delete collections or vector store
- **No administrative functions** - Cannot perform system maintenance
- **No configuration access** - Cannot modify system settings
- **Security-focused** - Only provides safe search and indexing operations

### CLI Administrative Powers
- **Full collection management** - Create, delete, clean entire vector store
- **System configuration** - Initialize, configure, maintain system
- **Content maintenance** - Re-index, update, bulk operations
- **Quality control** - Assessment, cleanup, optimization
- **Troubleshooting** - Verbose logging, debugging, system validation

## Core Administrative Tasks

### 1. Collection Management

#### **List and Analyze Collections**
```bash
# Get comprehensive collection overview
rag-retriever --list-collections --verbose

# Output as JSON for programmatic analysis
rag-retriever --list-collections --json
```

#### **Delete Specific Collection**
```bash
# Delete individual collection (safe operation)
rag-retriever --clean --collection collection_name

# Verify deletion
rag-retriever --list-collections
```

#### **Nuclear Option: Delete Entire Vector Store**
```bash
# WARNING: This deletes ALL collections and data
rag-retriever --clean

# Confirm all data is gone
rag-retriever --list-collections
```

### 2. Content Re-indexing Workflows

#### **Critical Concept: No Incremental Updates**
RAG Retriever does NOT support incremental updates. To refresh content:
1. **Delete existing collection completely**
2. **Re-index all content from scratch**
3. **Verify new content is accessible**

#### **Standard Re-indexing Workflow**
```bash
# 1. Check current state
rag-retriever --list-collections

# 2. Delete outdated collection
rag-retriever --clean --collection old_docs

# 3. Re-index from fresh source
rag-retriever --fetch-url "https://updated-site.com" --collection updated_docs

# 4. Verify new content
rag-retriever --query "test search" --collection updated_docs
rag-retriever --list-collections
```

#### **Bulk Re-indexing Multiple Collections**
```bash
# Delete multiple collections
rag-retriever --clean --collection docs_v1
rag-retriever --clean --collection docs_v2
rag-retriever --clean --collection docs_v3

# Re-index with new structure
rag-retriever --fetch-url "https://new-docs.com" --collection unified_docs
```

### 3. System Maintenance

#### **Configuration Management**
```bash
# Initialize or reset configuration
rag-retriever --init --verbose

# Verify configuration is working
rag-retriever --query "test" --verbose
```

#### **System Health Check**
```bash
# Test all collections
rag-retriever --query "system test" --search-all-collections --limit 1

# Verbose system validation
rag-retriever --list-collections --verbose

# Launch UI for visual inspection
rag-retriever --ui
```

#### **Storage Management**
```bash
# Check collection sizes and counts
rag-retriever --list-collections

# Clean up empty or problematic collections
rag-retriever --clean --collection empty_collection

# Optimize storage by consolidating similar collections
rag-retriever --clean --collection scattered_docs_1
rag-retriever --clean --collection scattered_docs_2
rag-retriever --ingest-directory ~/consolidated_docs --collection unified_docs
```

### 4. Quality Control and Assessment

#### **Content Quality Audit**
```bash
# Test search quality across all collections
rag-retriever --query "known_topic" --search-all-collections --score-threshold 0.4

# Identify low-quality collections
rag-retriever --query "test_query" --search-all-collections --json | analyze_scores

# Verbose output for quality assessment
rag-retriever --query "quality_test" --verbose --score-threshold 0.3
```

#### **Collection Health Assessment**
```bash
# Check each collection individually
rag-retriever --query "health_check" --collection collection1
rag-retriever --query "health_check" --collection collection2

# Cross-collection consistency check
rag-retriever --query "same_topic" --search-all-collections --limit 10
```

### 5. Troubleshooting and Debugging

#### **Common Issues and Solutions**

**Issue: Search Returns No Results**
```bash
# Check collection exists
rag-retriever --list-collections

# Verify content with lower threshold
rag-retriever --query "broad_search" --score-threshold 0.1 --verbose

# Check specific collection
rag-retriever --query "test" --collection specific_collection --verbose
```

**Issue: Poor Search Quality**
```bash
# Analyze with verbose output
rag-retriever --query "problematic_search" --verbose --json

# Test with different thresholds
rag-retriever --query "same_search" --score-threshold 0.2
rag-retriever --query "same_search" --score-threshold 0.4

# Consider re-indexing if consistently poor
rag-retriever --clean --collection poor_collection
rag-retriever --fetch-url "https://better-source.com" --collection improved_collection
```

**Issue: Collection Corruption or Errors**
```bash
# Try to list collections with verbose output
rag-retriever --list-collections --verbose

# Delete problematic collection
rag-retriever --clean --collection corrupted_collection

# Nuclear option if system is severely corrupted
rag-retriever --clean
rag-retriever --init
```

## Administrative Workflows

### New System Setup
```bash
# 1. Initialize system
rag-retriever --init

# 2. Verify configuration (edit config.yaml if needed)
rag-retriever --version

# 3. Test with small index
rag-retriever --fetch-url "https://simple-site.com" --collection test

# 4. Verify functionality
rag-retriever --query "test" --collection test
rag-retriever --list-collections
```

### Regular Maintenance Schedule
```bash
# Monthly: Review all collections
rag-retriever --list-collections --verbose

# Quarterly: Quality assessment
rag-retriever --query "known_topics" --search-all-collections --verbose

# As needed: Clean up obsolete collections
rag-retriever --clean --collection outdated_collection

# As needed: Re-index updated content
rag-retriever --clean --collection old_docs
rag-retriever --fetch-url "https://updated-docs.com" --collection updated_docs
```

### Content Migration Workflow
```bash
# 1. Backup collection list
rag-retriever --list-collections > collection_backup.txt

# 2. Export important searches (manual verification)
rag-retriever --query "critical_info" --search-all-collections --json > search_backup.json

# 3. Clean migration (if needed)
rag-retriever --clean

# 4. Re-index with new structure
rag-retriever --fetch-url "https://new-source.com" --collection new_structure

# 5. Verify migration
rag-retriever --query "critical_info" --collection new_structure
```

## Administrative Best Practices

### Collection Organization
- **Use descriptive names**: `python_docs`, `company_wiki`, not `docs1`
- **One topic per collection**: Keep related content together
- **Regular cleanup**: Delete obsolete collections promptly
- **Consistent naming**: Use underscore_style for collection names

### Content Maintenance
- **Schedule regular re-indexing**: Plan for content updates
- **Monitor search quality**: Use score thresholds to identify issues
- **Document your collections**: Keep track of what's indexed where
- **Test after changes**: Always verify functionality after maintenance

### System Health
- **Monitor disk space**: Vector stores can be large
- **Check API usage**: Monitor OpenAI API consumption
- **Regular backups**: Keep configuration files backed up
- **Version tracking**: Note RAG Retriever version for troubleshooting

## Emergency Procedures

### System Not Responding
```bash
# 1. Check basic functionality
rag-retriever --version

# 2. Reinitialize if needed
rag-retriever --init --verbose

# 3. Nuclear option: complete reset
rag-retriever --clean
rag-retriever --init
```

### Data Recovery
```bash
# 1. List what's still available
rag-retriever --list-collections

# 2. Export what you can
rag-retriever --query "important_data" --search-all-collections --json > recovery.json

# 3. Re-index from original sources
rag-retriever --fetch-url "https://original-source.com" --collection recovered_data
```

## Your Administrative Actions

**You CAN safely:**
- Help plan collection management strategies
- Suggest re-indexing workflows
- Provide troubleshooting guidance
- Recommend maintenance schedules
- Help with CLI command construction for admin tasks
- Analyze collection health and quality

**You CANNOT:**
- Execute administrative commands directly
- Access or modify configuration files
- Delete collections without explicit confirmation
- Perform system-level operations

## Success Criteria

Effective administrative management should result in:
- **Well-organized collections** with clear purpose and naming
- **Regular maintenance schedule** for content freshness
- **Proactive quality control** through systematic assessment
- **Efficient troubleshooting** when issues arise
- **Documented procedures** for team knowledge sharing

Remember: Administrative functions are powerful and irreversible. Always verify collection names and confirm deletion operations before proceeding. The CLI provides full system control that's intentionally not available through the MCP server.