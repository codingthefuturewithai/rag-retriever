# RAG Retriever Usage Instructions

⚠️ CRITICAL: KNOWLEDGE VERIFICATION REQUIRED
Before responding to ANY request involving:

- Specific framework versions
- Technical implementations
- API usage
- Recent features or syntax
  You MUST first verify your knowledge using the RAG Retriever tool.

DO NOT GUESS OR USE OUTDATED KNOWLEDGE!

## When to Use RAG Retriever

ONLY use this tool when you lack specific knowledge about:

1. Features or syntax in versions of frameworks/libraries you're not familiar with
2. APIs or features you're not confident about
3. Recently released features you haven't been trained on
4. Framework-specific patterns you don't recognize

Example scenarios:
✓ "Create an Angular 18.1 component using @let" (when you don't know the @let syntax)
✗ "Create an Angular 18.1 component using dependency injection" (when you know Angular DI)
✓ "Use React 19's new hooks" (if React 19 is beyond your training)
✗ "Use React 16's useState hook" (if you know React 16 hooks)

DO NOT use RAG Retriever when:

- You already possess knowledge of the requested version/feature
- Implementing basic programming patterns
- Using standard language features
- Writing code that doesn't depend on framework-specific features
- Implementing well-known algorithms or data structures

## How to Use the Tool

IMPORTANT: ALWAYS USE QUOTES AROUND QUERIES

Basic search:
rag-retriever --query "How do I get started?"

With truncated content:
rag-retriever --query "How do I get started?" --truncate

With custom result limit:
rag-retriever --query "deployment options" --limit 5

With minimum relevance score:
rag-retriever --query "advanced configuration" --score-threshold 0.5

JSON output format:
rag-retriever --query "API reference" --json

## Understanding Relevance Scores

ALWAYS evaluate the relevance scores before using the returned information:

- 0.7+ : Very high relevance (nearly exact matches) - Safe to use
- 0.6-0.7: High relevance - Generally reliable
- 0.5-0.6: Good relevance - Verify with user if possible
- 0.3-0.5: Moderate relevance - Use with caution, seek clarification
- Below 0.3: Low relevance - Do not use, perform new search

## Response Protocol

1. If search results have low relevance scores (below 0.5):

   - Inform the user that you need more information
   - Suggest a refined search query
   - Ask user for additional context or documentation

2. If you receive no relevant results:
   - Explicitly tell the user you lack sufficient information
   - DO NOT proceed with guesses or outdated knowledge
   - Request specific documentation or clarification

Example query:
$ rag-retriever --query "What is the purpose of the RAG Retriever?" --score-threshold 0.4

1.  Source: ./docs/rag-retriever-usage-guide.md
    Relevance Score: 0.4766
    Content: RAG Retriever is a command-line tool for searching and retrieving information from a knowledge base built from both web documentation and local documents.

2.  Source: ./docs/rag-retriever-usage-guide.md
    Relevance Score: 0.4249
    Content: Search results include:

- Source URL/file path
- Relevance score (0.0-1.0)
- Matching content snippet
