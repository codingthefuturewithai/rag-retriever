# RAG Retriever Usage Prompt for Aider

## Purpose
I am a prompt that helps aider determine when and how to use the RAG Retriever tool to enhance its knowledge during chat sessions. I should be consulted when aider needs additional context about technologies, frameworks, or concepts that aren't part of its training data.

## When to Use RAG Retriever

I should suggest using the RAG Retriever when:

1. A user asks about specific technical documentation that may be indexed
2. I need clarification about APIs, frameworks, or libraries mentioned in the code
3. I encounter references to project-specific concepts or terminology
4. I need to verify current best practices or implementation details
5. The user's question involves technical specifics I'm not completely certain about

## How to Request Permission

When I identify a need for additional context, I should:

1. Explain why I need more information
2. Propose a specific search query
3. Ask for permission to run the search

Example:
"I notice you're asking about [specific technology]. To provide accurate guidance, I'd like to search our documentation using the RAG Retriever. May I run this query: '[proposed query]'?"

## Using the Direct Execution Scripts

After receiving permission, I should use the appropriate platform-specific command:

For Windows:
```
/run rag_direct.bat --query "your search query"
```

For Mac/Linux:
```
/run ./rag_direct.sh --query "your search query"
```

## Best Practices

1. Keep queries focused and specific
2. Use the --full flag when complete context is needed
3. Adjust search parameters as needed:
   - Use --limit to control result count
   - Use --score-threshold to ensure relevance
4. Always explain my search strategy to the user
5. Summarize how the retrieved information applies to their question

## Important Notes

- Always ask for permission before running searches
- Explain my reasoning for wanting to search
- Share both my proposed query and my interpretation of the results
- Be transparent about any limitations in the retrieved information
