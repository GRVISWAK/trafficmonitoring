@echo off
echo ============================================================
echo DATASET VIEWER - FOR MENTOR DEMONSTRATION
echo ============================================================
echo.

cd /d "%~dp0"

echo Activating virtual environment...
call "..\.venv\Scripts\activate.bat"

echo.
echo Launching dataset viewer...
python view_datasets.py

pause
