@echo off
setlocal

:: Get the directory where the batch file is located
set "SCRIPT_DIR=%~dp0"
:: Remove trailing backslash
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
:: Get the parent directory (project root)
for %%I in ("%SCRIPT_DIR%\..") do set "PROJECT_ROOT=%%~fI"

:: Use the venv Python directly without activating
"%PROJECT_ROOT%\venv\Scripts\python.exe" "%PROJECT_ROOT%\rag_retriever.py" %* 