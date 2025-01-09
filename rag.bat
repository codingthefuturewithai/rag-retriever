@echo off
setlocal EnableDelayedExpansion

:: Function to display help message
:show_help
echo RAG Retriever - Command Line Helper
echo.
echo Usage:
echo   rag.bat fetch ^<url^> [depth]     - Fetch and index content from URL
echo   rag.bat query ^<text^> [options]  - Search indexed content
echo   rag.bat clean                   - Remove the vector store
echo   rag.bat help                    - Show this help message
echo.
echo Options for query:
echo   --full                - Show full content in results
echo   --score ^<threshold^>   - Set relevance score threshold (default: 0.3)
echo.
echo Examples:
echo   rag.bat fetch https://example.com 2
echo   rag.bat query "What are the main features?" --full
echo   rag.bat query "Tell me about installation" --score 0.4
goto :eof

:: Function to confirm action
:confirm
set /p response="%~1 [y/N] "
if /i "%response%"=="y" exit /b 0
if /i "%response%"=="yes" exit /b 0
exit /b 1

:: Check if we're already in a virtual environment
if "%VIRTUAL_ENV%"=="" (
    :: Only activate if we're not already in a virtual environment
    if exist venv\Scripts\activate.bat (
        call venv\Scripts\activate.bat
    )
)

:: Main command handling
if "%1"=="" goto show_help
if "%1"=="help" goto show_help

if "%1"=="fetch" (
    if "%2"=="" (
        echo Error: URL is required
        echo Usage: rag.bat fetch ^<url^> [depth]
        exit /b 1
    )
    set depth=2
    if not "%3"=="" set depth=%3
    python rag_retriever.py --fetch "%2" --max-depth !depth!
    goto :eof
)

if "%1"=="query" (
    if "%2"=="" (
        echo Error: Query text is required
        echo Usage: rag.bat query ^<text^> [options]
        exit /b 1
    )
    
    set cmd=python rag_retriever.py --query "%2"
    shift
    shift
    
    :parse_args
    if "%1"=="" goto run_cmd
    if "%1"=="--full" (
        set cmd=!cmd! --full
        shift
        goto parse_args
    )
    if "%1"=="--score" (
        if "%2"=="" (
            echo Error: Score threshold value is required
            exit /b 1
        )
        set cmd=!cmd! --score-threshold %2
        shift
        shift
        goto parse_args
    )
    shift
    goto parse_args
    
    :run_cmd
    !cmd!
    goto :eof
)

if "%1"=="clean" (
    if exist chromadb (
        echo Warning: This will delete all indexed content from the vector store.
        call :confirm "Are you sure you want to continue?" || (
            echo Operation cancelled.
            goto :eof
        )
        echo Removing vector store...
        rmdir /s /q chromadb
        echo Vector store removed.
    ) else (
        echo Vector store not found.
    )
    goto :eof
)

:eof
endlocal 