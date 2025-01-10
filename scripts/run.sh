#!/bin/bash

# Make script executable from anywhere
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Ensure we're in the virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Pass all arguments to the Python script
python3 rag_retriever.py "$@" 