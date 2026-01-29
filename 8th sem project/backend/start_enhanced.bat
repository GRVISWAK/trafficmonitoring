@echo off
echo ============================================================
echo ENHANCED ML DASHBOARD - LIVE + SIMULATION MODES
echo ============================================================
echo.
echo Starting backend with enhanced features...
echo.

cd /d "%~dp0"

echo Activating virtual environment...
call "..\.venv\Scripts\activate.bat"

echo.
echo Starting FastAPI server with LIVE and SIMULATION modes...
echo.
echo Available at: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
python -m uvicorn app_enhanced:app --reload --host 0.0.0.0 --port 8000

pause
