# Using RAG Retriever in Aider Sessions

> **Note:** This guide covers only the direct execution scripts for use within aider sessions.
> For complete documentation of the RAG Retriever tool's features, configuration, and general usage,
> please refer to the project's **README.md** file.

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

For detailed explanations of all available options and features, please consult the project's README.md file.
