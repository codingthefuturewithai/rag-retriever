#!/bin/bash

# Function to display help message
show_help() {
    echo "RAG Retriever - Command Line Helper"
    echo
    echo "Usage:"
    echo "  ./rag.sh fetch <url> [depth]     - Fetch and index content from URL"
    echo "  ./rag.sh query <text> [options]  - Search indexed content"
    echo "  ./rag.sh clean                   - Remove the vector store"
    echo "  ./rag.sh help                    - Show this help message"
    echo
    echo "Options for query:"
    echo "  --full                - Show full content in results"
    echo "  --score <threshold>   - Set relevance score threshold (default: 0.3)"
    echo
    echo "Examples:"
    echo "  ./rag.sh fetch https://example.com 2"
    echo "  ./rag.sh query \"What are the main features?\" --full"
    echo "  ./rag.sh query \"Tell me about installation\" --score 0.4"
}

# Function to confirm action
confirm() {
    read -p "$1 [y/N] " response
    case "$response" in
        [yY][eE][sS]|[yY]) 
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# Check if we're already in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    # Only activate if we're not already in a virtual environment
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
fi

# Main command handling
case "$1" in
    "fetch")
        if [ -z "$2" ]; then
            echo "Error: URL is required"
            echo "Usage: ./rag.sh fetch <url> [depth]"
            exit 1
        fi
        depth=${3:-2}  # Default depth is 2 if not specified
        python rag_retriever.py --fetch "$2" --max-depth "$depth"
        ;;
        
    "query")
        if [ -z "$2" ]; then
            echo "Error: Query text is required"
            echo "Usage: ./rag.sh query <text> [options]"
            exit 1
        fi
        
        # Build the command with optional parameters
        cmd="python rag_retriever.py --query \"$2\""
        
        # Process additional arguments
        shift 2
        while [ "$#" -gt 0 ]; do
            case "$1" in
                "--full")
                    cmd="$cmd --full"
                    ;;
                "--score")
                    if [ -z "$2" ]; then
                        echo "Error: Score threshold value is required"
                        exit 1
                    fi
                    cmd="$cmd --score-threshold $2"
                    shift
                    ;;
            esac
            shift
        done
        
        # Execute the command
        eval $cmd
        ;;
        
    "clean")
        if [ -d "./chromadb" ]; then
            echo "Warning: This will delete all indexed content from the vector store."
            if confirm "Are you sure you want to continue?"; then
                echo "Removing vector store..."
                rm -rf ./chromadb
                echo "Vector store removed."
            else
                echo "Operation cancelled."
            fi
        else
            echo "Vector store not found."
        fi
        ;;
        
    "help"|*)
        show_help
        ;;
esac 