@echo off
echo ==========================================
echo    Jewelry Shop Management System
echo ==========================================
echo.
echo Starting the application...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
python -c "import streamlit, pandas, plotly" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install streamlit pandas plotly
    if errorlevel 1 (
        echo ERROR: Failed to install packages
        pause
        exit /b 1
    )
)

REM Change to the script directory
cd /d "%~dp0"

REM Start the Streamlit application
echo.
echo ==========================================
echo Application starting...
echo ==========================================
echo.
echo The application will open in your default browser.
echo If it doesn't open automatically, visit:
echo http://localhost:8501
echo.
echo Press Ctrl+C to stop the application.
echo ==========================================
echo.

streamlit run app.py

echo.
echo Application stopped.
pause