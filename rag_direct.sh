#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Use the venv Python directly without activating
"$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/rag_retriever.py" "$@" 