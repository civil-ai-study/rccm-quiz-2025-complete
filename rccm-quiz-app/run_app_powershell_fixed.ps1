# ULTRA SYNC Task 3: PowerShell Execution Script
# Zero Side Effects Application Launcher

Write-Host "ULTRA SYNC PowerShell Execution Script" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Set working directory
Set-Location -Path $PSScriptRoot
Write-Host "Working Directory: $(Get-Location)" -ForegroundColor Cyan

# Set Python environment
$env:PYTHONPATH = "."
$env:FLASK_ENV = "development"

Write-Host ""
Write-Host "Detecting Python environment..." -ForegroundColor Yellow

# Function: Test Python Command
function Test-PythonCommand {
    param([string]$Command)
    
    try {
        $result = & $Command --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Available: $Command - $result" -ForegroundColor Green
            return $true
        }
    }
    catch {
        # Command not found
    }
    
    Write-Host "Not available: $Command" -ForegroundColor Red
    return $false
}

# Function: Start Application
function Start-Application {
    param([string]$PythonCommand)
    
    Write-Host ""
    Write-Host "Starting application..." -ForegroundColor Green
    Write-Host "Command: $PythonCommand app.py" -ForegroundColor Cyan
    Write-Host ""
    
    try {
        & $PythonCommand app.py
    }
    catch {
        Write-Host "Failed to start application: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Test Python commands in priority order
$pythonCommands = @("python", "py", "python.exe", "python3")

foreach ($cmd in $pythonCommands) {
    if (Test-PythonCommand -Command $cmd) {
        Start-Application -PythonCommand $cmd
        Write-Host ""
        Write-Host "ULTRA SYNC execution script completed" -ForegroundColor Green
        exit 0
    }
}

# Test common Python paths
$commonPaths = @(
    "C:\Python39\python.exe",
    "C:\Python38\python.exe",
    "C:\Python37\python.exe",
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python39\python.exe",
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python38\python.exe"
)

foreach ($path in $commonPaths) {
    if (Test-Path $path) {
        Write-Host "Available: $path" -ForegroundColor Green
        Start-Application -PythonCommand $path
        Write-Host ""
        Write-Host "ULTRA SYNC execution script completed" -ForegroundColor Green
        exit 0
    }
}

# All methods failed
Write-Host ""
Write-Host "Python not found" -ForegroundColor Red
Write-Host ""
Write-Host "Solutions:" -ForegroundColor Yellow
Write-Host "1. Install Python (https://python.org)" -ForegroundColor White
Write-Host "2. Add Python to PATH" -ForegroundColor White
Write-Host "3. Or specify the full Python path" -ForegroundColor White
Write-Host ""
Write-Host "For detailed diagnostics, run:" -ForegroundColor Yellow
Write-Host "   python ultrasync_environment_diagnostic.py" -ForegroundColor White
Write-Host ""
Write-Host "ULTRA SYNC execution script completed" -ForegroundColor Green

# PowerShell execution policy information
Write-Host ""
Write-Host "PowerShell execution policy check:" -ForegroundColor Yellow
Write-Host "   Get-ExecutionPolicy" -ForegroundColor White
Write-Host "   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor White