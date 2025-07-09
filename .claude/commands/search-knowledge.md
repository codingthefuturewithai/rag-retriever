# Search RAG Retriever Knowledge Base

Search across vector store collections for specific information and insights.

## Prerequisites
This command requires the RAG Retriever MCP server to be configured in your Claude Code setup. The server provides semantic search capabilities across your indexed content collections.

## Arguments
Use $ARGUMENTS to specify search parameters:
- Query string (required)
- Collection name (optional - **IMPORTANT**: if not specified, searches ONLY the "default" collection, not all collections)
- Number of results (optional - defaults to 8)
- Score threshold (optional - defaults to 0.3)

Examples:
- "Claude Code documentation" 
- "Claude Code documentation claude_code_docs"
- "error handling python 10 0.4"

## Implementation Approach
This command uses **direct implementation** for focused knowledge retrieval.

## Your Task
1. **Parse Arguments**
   - Extract query from $ARGUMENTS
   - Identify optional collection name, limit, and score threshold
   - Use sensible defaults if not specified

2. **Collection Selection**
   - **CRITICAL**: If no collection specified, search will ONLY check the "default" collection
   - Use `list_collections` to show all available collections if user needs different content
   - Guide user to select appropriate collection based on their query
   - Many users will need to specify a collection name to find their content

3. **Perform Search**
   - Use `vector_search` with specified parameters
   - Search the most relevant collection for the query
   - Display results with relevance scores and source information

4. **Result Analysis**
   - Analyze search results for relevance and quality
   - Highlight the most useful information found
   - Suggest related searches or different collections if results are insufficient

## Success Criteria
- Relevant information retrieved from vector store
- Results displayed with context and source attribution
- Clear guidance on result quality and relevance

## Available MCP Tools
- `list_collections()` - Discover available collections
- `vector_search(query, limit, score_threshold, collection_name, search_all_collections)` - Search for information