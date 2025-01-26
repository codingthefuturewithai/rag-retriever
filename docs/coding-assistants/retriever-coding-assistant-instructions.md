I have a local tool you can use to try to retrieve new content, such as API or framework docs when you need but lack critical knowledge. Advise the user to attempt to use this tool when you need to. Here's instructions for how to use it:

IMPORTANT: BE SURE TO PLACE QUOTES AROUND THE QUERY

# Basic search

rag-retriever --query "How do I get started?"

# With custom result limit

rag-retriever --query "deployment options" --limit 5

# With minimum relevance score

rag-retriever --query "advanced configuration" --score-threshold 0.5

# JSON output format

rag-retriever --query "API reference" --json

Here's an example of a query command:

$ rag-retriever --query "What is the purpose of the RAG Retriever?" --score-threshold 0.1

1.  Source: ./docs/rag-retriever-usage-guide.md
    Relevance Score: 0.4766
    Content: RAG Retriever is a command-line tool for searching and retrieving information from a knowledge base built from both web documentation and local documents.

2.  Source: ./docs/rag-retriever-usage-guide.md
    Relevance Score: 0.4249
    Content: Search results include:

- Source URL/file path
- Relevance score (0.0-1.0)
- Matching content snippet

Scores range from 0 to 1, where 1 indicates perfect similarity
Default threshold is 0.3
Typical interpretation:
0.7+: Very high relevance (nearly exact matches)
0.6 - 0.7: High relevance
0.5 - 0.6: Good relevance
0.3 - 0.5: Moderate relevance
Below 0.3: Lower relevance
