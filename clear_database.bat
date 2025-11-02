@echo off
title Jewelry Management - Database Cleaner
color 0B
echo ===============================================
echo   JEWELRY MANAGEMENT DATABASE CLEANER
echo ===============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
)

echo This will PERMANENTLY DELETE all data from the database!
echo.
echo Are you sure you want to continue? (Y/N)
set /p confirm=
if /i "%confirm%" NEQ "Y" (
    echo Operation cancelled.
    pause
    exit /b 0
)

echo.
echo Clearing database...
echo 1 | python test_database.py

echo.
echo Operation completed!
echo Press any key to exit...
pause >nul