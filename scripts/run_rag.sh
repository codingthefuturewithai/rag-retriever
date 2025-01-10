#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate the virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Run the command with all arguments passed to this script
python "$SCRIPT_DIR/rag_retriever.py" "$@"

# Deactivate the virtual environment
deactivate 