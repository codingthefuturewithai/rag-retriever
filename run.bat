@echo off
setlocal

:: Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

:: Pass all arguments to the Python script
python rag_retriever.py %* 