@echo off
echo ================================================================
echo  RESETTING LIVE MODE - CLEAN START
echo ================================================================
echo.
echo This will:
echo   1. Stop all Python backend processes
echo   2. Delete the database (reset all counters to 0)
echo   3. Restart backend in STRICT LIVE MODE
echo.
pause

echo.
echo [1/3] Stopping Python processes...
taskkill /F /IM python.exe 2>nul
timeout /t 2 >nul

echo [2/3] Deleting database...
cd /d "%~dp0backend"
if exist api_logs.db (
    del /F api_logs.db
    echo    Database deleted
) else (
    echo    No database found
)

echo [3/3] Starting backend in LIVE MODE...
echo.
echo ================================================================
echo  STRICT LIVE MODE RULES:
echo ================================================================
echo  WHITELISTED (tracked):
echo    /login, /signup, /search, /profile, /payment, /logout
echo.
echo  BLACKLISTED (ignored):
echo    /, /health, /metrics, /docs, /api/*, /ws, /simulation/*
echo.
echo  Request count will be ZERO until you make real API calls.
echo ================================================================
echo.

start "Backend - LIVE MODE" cmd /k ""%~dp0.venv\Scripts\python.exe" "%~dp0backend\app_enhanced.py""

echo.
echo ✅ Backend started!
echo.
echo Dashboard: http://localhost:3000
echo Backend:   http://localhost:8000
echo.
echo Make API calls to whitelisted endpoints to see traffic.
echo.
pause
