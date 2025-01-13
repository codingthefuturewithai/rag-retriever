#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( dirname "$( dirname "$SCRIPT_DIR" )" )"

# Set up vector store path
export VECTOR_STORE_PATH="$PROJECT_ROOT/tests/results/test_vector_store"
mkdir -p "$VECTOR_STORE_PATH"

# Clean existing vector store
"$PROJECT_ROOT/scripts/run-rag.sh" --clean

# Ingest sample PDFs
echo "Ingesting tables PDF..."
"$PROJECT_ROOT/scripts/run-rag.sh" --ingest-file "$PROJECT_ROOT/tests/data/pdfs/tables/tables_093.pdf"

echo "Ingesting images PDF..."
"$PROJECT_ROOT/scripts/run-rag.sh" --ingest-file "$PROJECT_ROOT/tests/data/pdfs/images/images_344.pdf"

echo "Ingesting scanned PDF..."
"$PROJECT_ROOT/scripts/run-rag.sh" --ingest-file "$PROJECT_ROOT/tests/data/pdfs/scanned/scanned_015.pdf"

echo "Ingesting simple PDF..."
"$PROJECT_ROOT/scripts/run-rag.sh" --ingest-file "$PROJECT_ROOT/tests/data/pdfs/simple/simple_079.pdf"

echo "Ingesting technical PDF..."
"$PROJECT_ROOT/scripts/run-rag.sh" --ingest-file "$PROJECT_ROOT/tests/data/pdfs/technical/technical_040.pdf"

echo "Done ingesting samples." 