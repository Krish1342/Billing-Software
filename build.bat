@echo off
REM Build script for Roopkala Jewellers Billing System
REM This batch file builds the Windows executable using PyInstaller

echo ========================================
echo Roopkala Jewellers Billing System
echo Executable Builder
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo Python found: 
python --version
echo.

REM Check if required packages are installed
echo Checking dependencies...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo ERROR: PyInstaller is not installed
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo All dependencies are installed.
echo.

REM Run the build script
echo Starting build process...
echo This may take 2-5 minutes. Please wait...
echo.
python build_exe.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo BUILD FAILED!
    echo ========================================
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo BUILD SUCCESSFUL!
echo ========================================
echo.
echo The executable has been created in the 'dist' folder:
echo   dist\RoopkalaBillingSystem.exe
echo.
echo Next steps:
echo 1. Test the executable by running it
echo 2. Copy it along with settings.json for distribution
echo 3. See BUILD_README.md for more details
echo.

REM Ask if user wants to open the dist folder
set /p OPENFOLDER="Open dist folder now? (Y/N): "
if /i "%OPENFOLDER%"=="Y" (
    explorer dist
)

echo.
echo Press any key to exit...
pause >nul
