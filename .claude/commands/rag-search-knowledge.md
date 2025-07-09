# Search RAG Retriever Knowledge Base

Search across vector store collections for specific information and insights.

## Prerequisites
This command requires the RAG Retriever MCP server to be configured in your Claude Code setup. The server provides semantic search capabilities across your indexed content collections.

## Arguments
Use $ARGUMENTS to specify search parameters:
- Query string (required)
- Collection name (optional - if not specified, searches ONLY the "default" collection)
- "all" - special keyword to search across ALL collections
- Number of results (optional - defaults to 8)
- Score threshold (optional - defaults to 0.3)

Examples:
- "Claude Code documentation" - searches default collection only
- "Claude Code documentation claude_code_docs" - searches specific collection
- "Claude Code documentation all" - searches ALL collections
- "error handling python 10 0.4" - searches default with custom limit/threshold
- "error handling all 10 0.4" - searches all collections with custom parameters

## Implementation Approach
This command uses **direct implementation** for focused knowledge retrieval.

## Your Task
1. **Parse Arguments**
   - Extract query from $ARGUMENTS
   - Identify optional collection name (or "all" for cross-collection search)
   - Parse optional limit and score threshold parameters
   - Use sensible defaults if not specified

2. **Collection Selection**
   - If no collection specified: search ONLY the "default" collection
   - If "all" specified: set `search_all_collections=True` to search across all collections
   - If specific collection specified: search that collection only
   - Use `list_collections` to show available collections if user needs guidance

3. **Perform Search**
   - Use `vector_search` with appropriate parameters:
     - `search_all_collections=True` if user specified "all"
     - `collection_name=name` if user specified a specific collection
     - Default to "default" collection if no collection specified
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
- `vector_search(query_text, limit, score_threshold, full_content, collection_name, search_all_collections)` - Search for information