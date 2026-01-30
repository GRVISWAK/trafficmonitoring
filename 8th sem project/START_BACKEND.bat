@echo off
cd /d "%~dp0backend"
echo Starting Backend Server...
echo.
call "..\. venv\Scripts\activate.bat"
python -m uvicorn app:app --host 0.0.0.0 --port 8000
pause
