@echo off
echo ================================================
echo    Building Jewelry Management System EXE
echo ================================================
echo.

echo Installing/Updating dependencies...
pip install -r requirements.txt

echo.
echo Building executable...
python build_exe.py

echo.
echo Build process completed!
pause