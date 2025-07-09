# Audit RAG Retriever Collections

Review and validate the current state of all vector store collections.

## Prerequisites
This command requires the RAG Retriever MCP server to be configured in your Claude Code setup. The server provides access to vector store collections for analysis and validation.

## Implementation Approach
This command uses **direct implementation** as it involves comprehensive analysis of existing collections.

## Your Task
1. **Collection Inventory**
   - Use `list_collections` to get complete inventory
   - Analyze document counts and metadata for each collection
   - Identify collections that may need attention

2. **Content Quality Assessment**
   - Perform sample searches in each collection
   - Evaluate result quality and relevance
   - Check for potential duplicates or outdated content
   - Assess metadata richness and accuracy

3. **Usage Analysis**
   - Identify most and least used collections
   - Evaluate collection organization and naming
   - Check for overlapping content across collections

4. **Health Check**
   - Verify all collections are accessible
   - Check for any technical issues or corruption
   - Validate search functionality across collections

5. **Recommendations**
   - Suggest collections that need updating or re-indexing
   - Recommend consolidation of similar collections
   - Identify gaps in knowledge coverage
   - Propose new collections for missing topic areas

## Success Criteria
- Comprehensive audit report of all collections
- Quality assessment and technical health status
- Actionable recommendations for improvement
- Clear prioritization of maintenance tasks

## Available MCP Tools
- `list_collections()` - Get complete collection inventory
- `vector_search(query_text, collection_name, search_all_collections)` - Test search quality in specific collections or across all collections
- `crawl_and_index_url(url, max_depth, collection_name)` - Re-index content if needed