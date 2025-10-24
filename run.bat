@echo off
echo ================================================
echo    Running Jewelry Management System
echo ================================================
echo.

echo Choose how to run:
echo 1. Run from source code (python main.py)
echo 2. Run standalone executable (dist\JewelryManagement.exe)
echo.
set /p choice="Enter your choice (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo Starting from source code...
    python main.py
) else if "%choice%"=="2" (
    echo.
    echo Starting standalone executable...
    echo File size: 92.7 MB
    echo Location: dist\JewelryManagement.exe
    cd dist
    JewelryManagement.exe
) else (
    echo Invalid choice. Starting from source code...
    python main.py
)

echo.
echo Application closed.
pause