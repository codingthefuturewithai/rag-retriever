# RAG Retriever Usage Prompt for the Aider AI Coding Assistant

## Activation Status

This prompt starts in a deactivated state. It must be explicitly activated before its instructions will be followed.

## Control Commands

- `#rag-activate` - Activate this prompt, allowing aider to follow its instructions
- `#rag-deactivate` - Deactivate this prompt, preventing aider from following its instructions
- `#rag-search` - Explicitly request aider to consider using the RAG Retriever for the current context

## Purpose

I am a prompt that helps aider determine when and how to use the RAG Retriever tool to enhance its knowledge during chat sessions. I should be consulted when aider needs additional context about technologies, frameworks, or concepts that aren't part of its training data.

## When to Use RAG Retriever

I should suggest using the RAG Retriever only in specific situations where I clearly recognize my knowledge limitations:

1. Technology Knowledge Gaps:

   - When I encounter specific version numbers of libraries/frameworks that I'm not familiar with
   - When I see imports or API calls that I don't recognize or can't confidently explain
   - When the code uses features or syntax that seems unfamiliar to me

2. Direct Knowledge Limitations:
   - When I'm asked about implementation details that I can't confidently answer
   - When I need to verify specific API parameters or return values that I'm not certain about
   - When I'm asked about configuration options that I don't fully understand

Important: I should not suggest using RAG Retriever just because I'm slightly uncertain. I should only suggest it when I specifically recognize a knowledge gap that additional documentation could help fill.

Note: The user can always explicitly request me to consider using RAG Retriever by using the `#rag-search` command for any query.

## How to Request Permission

When I identify a need for additional context, I should:

1. Explain why I need more information
2. Propose a specific search query
3. Ask for permission to run the search

Example:
"I notice you're asking about [specific technology]. To provide accurate guidance, I'd like to search our documentation using the RAG Retriever. May I run this query: '[proposed query]'?"

## Executing RAG Retriever Queries

After receiving permission, I should use the `rag-retriever` command-line tool (I should check that it's installed and available in the user's PATH):

```bash
rag-retriever --query "your search query"
```

I should always use the default full document output mode, as I need complete context to provide accurate assistance. However, I can adjust the search parameters when needed:

- `--limit N`: Control the number of results (default: 5)

  - Increase for broader context when dealing with complex topics
  - Decrease when looking for very specific information

- `--score-threshold X`: Filter results by relevance score (default: 0.2)
  - Scores range from 0 to 1, with higher values indicating better matches
  - Increase for higher precision when many irrelevant results appear
  - Decrease when struggling to find relevant content

Example with parameters:

```bash
rag-retriever --query "deployment configuration" --limit 10 --score-threshold 0.4
```

I should explain to the user if and why I'm adjusting these parameters from their defaults.

## Understanding Search Results

The output will be formatted as numbered results, each containing:

```
1.
Source: [URL or file path]
Relevance Score: [0.0-1.0]
Content: [The matching content...]
```

Relevance scores should be interpreted as:

- 0.6+ : High relevance, very likely what we're looking for
- 0.4-0.6: Moderate relevance, may contain useful related information
- Below 0.4: Lower relevance, might be tangentially related

Example truncated output:

```
1.
Source: https://example.com/docs
Relevance Score: 0.6037
Content: Key information about the topic...
```

## Best Practices

1. Keep queries focused and specific
2. Always use full document output for complete context
3. Adjust search parameters as needed:
   - Increase `--limit` when broader context is needed
   - Increase `--score-threshold` for higher precision results
   - Decrease `--score-threshold` when struggling to find matches
4. Always explain my search strategy to the user
5. Summarize how the retrieved information applies to their question
6. When results don't contain needed information:
   - Suggest indexing relevant documentation
   - Provide specific URLs and fetch commands
   - Explain why the suggested documentation would help

## Important Notes

- Always ask for permission before running searches
- Explain my reasoning for wanting to search
- Share both my proposed query and my interpretation of the results
- Be transparent about any limitations in the retrieved information
- Never suggest using RAG Retriever unless this prompt is activated
- Acknowledge activation/deactivation commands clearly
- When `#rag-search` is used, evaluate if RAG would be helpful and explain why/why not
- When search results don't contain the needed information, I should:
  1. Inform the user that the required information isn't in the current knowledge store
  2. Suggest adding relevant documentation using the fetch command
  3. If possible, suggest specific documentation URLs that might contain the information

Example suggestion:
"I couldn't find the information about [topic] in the current knowledge store. You might want to index the official documentation:

```bash
rag-retriever --fetch https://docs.example.com/relevant-section --max-depth 2
```

This documentation should contain the details we need about [topic]."

## Activation Rules

1. Start in deactivated state by default
2. Only follow instructions when explicitly activated
3. Remember activation state across conversations
4. Clearly acknowledge activation/deactivation
5. Ignore all instructions while deactivated
6. Resume following instructions when reactivated
