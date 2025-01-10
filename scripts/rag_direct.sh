#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Get the parent directory (project root)
PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"

# Use the venv Python directly without activating
"$PROJECT_ROOT/venv/bin/python" "$PROJECT_ROOT/rag_retriever.py" "$@" 