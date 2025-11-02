@echo off
REM Watchdog Auto-Builder for Jewelry Management System
REM This script starts the automatic rebuild process

echo ========================================
echo Jewelry Management System - Auto Builder
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
)

REM Check if watchdog is installed
python -c "import watchdog" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing watchdog dependency...
    pip install watchdog>=3.0.0
    if %errorlevel% neq 0 (
        echo Error: Failed to install watchdog
        echo Please run: pip install watchdog
        pause
        exit /b 1
    )
)

echo Starting file monitoring for automatic builds...
echo.
echo Instructions:
echo - The system will automatically rebuild when Python files change
echo - Press Ctrl+C to stop monitoring
echo - Build logs are saved to 'watchdog_build.log'
echo.

REM Start the watchdog
python watchdog_builder.py

echo.
echo Monitoring stopped.
pause