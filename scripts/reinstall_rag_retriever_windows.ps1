# PowerShell script to uninstall and reinstall RAG Retriever on Windows
# This script handles cleanup, uninstallation, and fresh installation

# Stop on first error
$ErrorActionPreference = "Stop"

Write-Host "RAG Retriever Reinstallation Script for Windows" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
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
            exit 1
        }
    }
    else {
        Write-Host "$description not found at: $path" -ForegroundColor Cyan
    }
}

# Function to check if a command exists
function Test-CommandExists {
    param ($command)
    
    try {
        if (Get-Command $command -ErrorAction Stop) {
            return $true
        }
    }
    catch {
        return $false
    }
    return $false
}

# Function to check Visual Studio Build Tools
function Test-BuildTools {
    $vsPath = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
    if (Test-Path $vsPath) {
        $buildTools = & $vsPath -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -latest
        if ($buildTools) {
            return $true
        }
    }
    return $false
}

# Main Process
Write-Host "Step 1: Checking Prerequisites" -ForegroundColor Yellow
Write-Host "----------------------------" -ForegroundColor Yellow

# Check Python installation
if (-not (Test-CommandExists python)) {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.10-3.12 from python.org and try again" -ForegroundColor Yellow
    exit 1
}

# Check Python version
$pythonVersion = (python --version 2>&1).ToString()
if ($pythonVersion -match '(\d+\.\d+\.\d+)') {
    $version = [version]$matches[1]
    if ($version -lt [version]"3.10" -or $version -ge [version]"3.13") {
        Write-Host "Error: Python version must be between 3.10 and 3.12" -ForegroundColor Red
        Write-Host "Current version: $pythonVersion" -ForegroundColor Yellow
        exit 1
    }
}

# Check Visual Studio Build Tools
if (-not (Test-BuildTools)) {
    Write-Host "Warning: Visual Studio Build Tools with C++ workload might not be installed" -ForegroundColor Yellow
    Write-Host "If installation fails, please install from: https://visualstudio.microsoft.com/visual-cpp-build-tools/" -ForegroundColor Yellow
    Write-Host "Make sure to select 'Desktop development with C++' workload during installation" -ForegroundColor Yellow
    Write-Host ""
    $response = Read-Host "Do you want to continue anyway? (y/n)"
    if ($response -ne "y") {
        exit 1
    }
}

Write-Host ""
Write-Host "Step 2: Uninstallation Process" -ForegroundColor Yellow
Write-Host "-------------------------" -ForegroundColor Yellow

# Try to uninstall Playwright browsers first
Write-Host "Removing Playwright browsers..."
python -m playwright uninstall chromium 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Successfully removed Playwright browsers" -ForegroundColor Green
}

# Uninstall RAG Retriever
Write-Host "Uninstalling RAG Retriever..."
if (Test-CommandExists pipx) {
    pipx uninstall rag-retriever 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Successfully uninstalled RAG Retriever" -ForegroundColor Green
    }
}

# Remove configuration directory
Write-Host "Cleaning up configuration directory..."
Remove-DirectorySafely -path $configPath -description "Configuration directory"

# Remove data directory
Write-Host "Cleaning up data directory..."
Remove-DirectorySafely -path $dataPath -description "Data directory"

Write-Host ""
Write-Host "Step 3: Installation Process" -ForegroundColor Yellow
Write-Host "------------------------" -ForegroundColor Yellow

# Install/Upgrade pipx if needed
if (-not (Test-CommandExists pipx)) {
    Write-Host "Installing pipx..."
    python -m pip install --user pipx
    python -m pipx ensurepath
    Write-Host "Successfully installed pipx" -ForegroundColor Green
    
    # Refresh PATH to include pipx
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","User") + ";" + [System.Environment]::GetEnvironmentVariable("Path","Machine")
}

# Install RAG Retriever
Write-Host "Installing RAG Retriever..."
pipx install rag-retriever
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to install RAG Retriever" -ForegroundColor Red
    exit 1
}

# Initialize configuration
Write-Host "Initializing configuration..."
rag-retriever --init
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Configuration initialization might have failed" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Installation completed!" -ForegroundColor Green
Write-Host "------------------------" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Configure your OpenAI API key in: $configPath\config.yaml" -ForegroundColor Cyan
Write-Host "2. Test the installation by running: rag-retriever --version" -ForegroundColor Cyan
Write-Host ""
Write-Host "If you encounter any issues with Playwright, run:" -ForegroundColor Yellow
Write-Host "python -m playwright install chromium" -ForegroundColor Yellow 