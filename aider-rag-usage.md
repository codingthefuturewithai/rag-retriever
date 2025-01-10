# Using RAG Retriever in Aider Sessions

This guide explains how to use the RAG retriever direct execution scripts during an aider chat session to enhance your coding conversations with relevant documentation context.

## Usage Within Aider

When in an aider chat session, use the `/run` command with the appropriate direct execution script for your platform:

### Windows
```
/run rag_direct.bat --query "your search query"
```

### Mac/Linux
```
/run ./rag_direct.sh --query "your search query"
```

## Common Operations

Search for relevant documentation:
```
/run ./rag_direct.sh --query "error handling" --full
```

Index new documentation:
```
/run ./rag_direct.sh --fetch https://example.com/docs
```

Clean the vector store:
```
/run ./rag_direct.sh --clean
```

## Tips

1. Run relevant searches before asking questions to give aider proper context
2. Use `--full` when you need complete documentation sections
3. Clean the index occasionally to remove outdated content
