# Local Document Loading Feature

## Current Implementation Status

1. Added local document processing capability with `LocalDocumentLoader` class
2. Supports markdown (.md) and text (.txt) files
3. Can load both individual files and entire directories
4. Uses LangChain's `DirectoryLoader` and `TextLoader` with automatic encoding detection
5. Supports multithreading for directory loading
6. Includes progress bar for directory loading

## Key Features

- Single file loading with `load_file(file_path)`
- Directory loading with `load_directory(directory_path, glob_pattern)`
- Configurable glob patterns for file matching (e.g., "**/\*.md", "**/_.txt", "\*\*/_.[mt][dx][td]")
- Error handling for unsupported file types and missing files
- Automatic encoding detection for text files

## Current Limitations

1. Only supports .md and .txt files currently
2. No recursive directory depth control
3. No file size limits or chunking controls
4. No metadata extraction from files
5. No support for binary formats (PDF, DOC, etc.)

## Next Steps

1. Add support for more file types (PDF, DOCX, etc.)
2. Implement file size checks and warnings
3. Add metadata extraction (file path, modified date, etc.)
4. Add configuration options for:
   - Maximum file size
   - Directory recursion depth
   - Chunk size/overlap for different file types
   - File type exclusions
5. Add tests for the document processing functionality

## Testing Needed

1. Test with large directories
2. Test with different file encodings
3. Test error handling scenarios
4. Test memory usage with large files
5. Test concurrent loading performance
