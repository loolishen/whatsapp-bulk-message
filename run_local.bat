@echo off
echo 🎯 WhatsApp Bulk Message - Local Development
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Run the local development setup
python run_local.py

pause
