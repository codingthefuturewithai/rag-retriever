# Index Website into RAG Retriever

Crawl and index a website into the RAG Retriever vector store for future semantic search.

## Prerequisites
This command requires the RAG Retriever MCP server to be configured in your Claude Code setup. The server handles web crawling and content indexing into vector store collections.

## Arguments
Use $ARGUMENTS to specify crawling parameters:
- URL (required)
- Max depth (optional - defaults to 2)
- Collection name (optional - creates new collection if not exists)

Examples:
- "https://docs.anthropic.com/claude-code"
- "https://python.org/docs 3"
- "https://fastapi.tiangolo.com fastapi_docs 2"

## Implementation Approach
This command uses **direct implementation** to coordinate website crawling and indexing.

## Your Task
1. **Parse Arguments**
   - Extract URL from $ARGUMENTS (required)
   - Parse optional max_depth (default: 2)
   - Parse optional collection_name (default: generates from URL)

2. **Pre-Crawl Analysis**
   - Validate the URL is accessible
   - Estimate the scope of crawling based on max_depth
   - Suggest appropriate collection name if not provided
   - Use `list_collections` to check for existing collections

3. **Initiate Crawling**
   - Use `crawl_and_index_url` to start the crawling process
   - Monitor progress and provide updates
   - Handle any errors or issues that arise

4. **Post-Crawl Verification**
   - Use `list_collections` to verify the collection was created/updated
   - Perform a test search to validate indexed content
   - Provide summary of pages crawled and content indexed

## Success Criteria
- Website successfully crawled and indexed
- Content stored in appropriate collection
- Verification that search functionality works with new content
- Clear summary of indexing results

## Available MCP Tools
- `list_collections()` - Check existing collections
- `crawl_and_index_url(url, max_depth, collection_name)` - Index website content
- `vector_search(query, collection_name)` - Verify indexed content