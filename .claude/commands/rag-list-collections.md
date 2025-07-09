# List RAG Retriever Collections

Discover all available vector store collections and their contents.

## Prerequisites
This command requires the RAG Retriever MCP server to be configured in your Claude Code setup. The server manages vector store collections for semantic search.

## Implementation Approach
This command uses **direct implementation** as it involves straightforward MCP operations and data analysis.

## Your Task
1. **Collection Discovery**
   - Use `list_collections` to retrieve all available collections
   - Display collection names with document counts
   - Show metadata like creation dates and descriptions

2. **Collection Analysis**
   - Analyze the size and scope of each collection
   - Identify the most useful collections for different use cases
   - Note any empty or underutilized collections

3. **Usage Recommendations**
   - Suggest which collections to use for different types of queries
   - Recommend collection names for specific search scenarios
   - Identify collections that might need updating or expansion

## Success Criteria
- Complete list of all collections displayed
- Document counts and metadata shown for each collection
- Clear recommendations for collection usage

## Available MCP Tools
- `list_collections()` - List all available collections with metadata
- `vector_search(query, collection_name)` - Search specific collections if needed for analysis