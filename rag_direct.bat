@echo off
setlocal

:: Get the directory where the batch file is located
set "SCRIPT_DIR=%~dp0"
:: Remove trailing backslash
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

:: Use the venv Python directly without activating
"%SCRIPT_DIR%\venv\Scripts\python.exe" "%SCRIPT_DIR%\rag_retriever.py" %* 