#!/usr/bin/env python3
"""Script to run the RAG Retriever UI."""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Run the Streamlit app
if __name__ == "__main__":
    import streamlit.web.cli as stcli

    # Get the path to the app.py file
    app_path = project_root / "rag_retriever" / "ui" / "app.py"

    sys.argv = [
        "streamlit",
        "run",
        str(app_path),
        "--server.address=localhost",
        "--server.port=8501",
    ]

    sys.exit(stcli.main())
