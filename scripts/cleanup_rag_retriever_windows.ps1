# PowerShell script to clean up RAG Retriever directories on Windows
# This script removes configuration and data directories for RAG Retriever

# Stop on first error
$ErrorActionPreference = "Stop"

Write-Host "RAG Retriever Cleanup Script for Windows" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green
Write-Host ""

# Define the paths
$configPath = "$env:APPDATA\rag-retriever"
$dataPath = "$env:LOCALAPPDATA\rag-retriever"

# Function to safely remove a directory
function Remove-DirectorySafely {
    param (
        [string]$path,
        [string]$description
    )
    
    if (Test-Path $path) {
        Write-Host "Found $description at: $path" -ForegroundColor Yellow
        try {
            Remove-Item -Path $path -Recurse -Force
            Write-Host "Successfully removed $description" -ForegroundColor Green
        }
        catch {
            Write-Host "Error removing $description. Error: $_" -ForegroundColor Red
            Write-Host "You may need to close any applications using RAG Retriever and try again." -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "$description not found at: $path" -ForegroundColor Cyan
    }
}

# Main cleanup process
Write-Host "Starting cleanup process..." -ForegroundColor Yellow
Write-Host ""

# Remove configuration directory
Write-Host "Cleaning up configuration directory..." -ForegroundColor Yellow
Remove-DirectorySafely -path $configPath -description "Configuration directory"

# Remove data directory
Write-Host ""
Write-Host "Cleaning up data directory..." -ForegroundColor Yellow
Remove-DirectorySafely -path $dataPath -description "Data directory"

Write-Host ""
Write-Host "Cleanup process completed!" -ForegroundColor Green
Write-Host "If you plan to reinstall RAG Retriever, you can do so now." -ForegroundColor Cyan 