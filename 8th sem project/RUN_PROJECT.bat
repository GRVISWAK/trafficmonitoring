@echo off
echo ===============================================
echo  PREDICTIVE API MISUSE DETECTION SYSTEM
echo ===============================================
echo.

echo Step 1: Training ML Models...
cd /d "c:\Users\HP\Desktop\8th sem project\backend"
"C:/Users/HP/Desktop/8th sem project/.venv/Scripts/python.exe" run_training.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Model training failed!
    pause
    exit /b 1
)

echo.
echo ===============================================
echo Step 2: Starting Backend Server...
echo ===============================================
echo.
echo Backend will start on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

start "API Backend" cmd /k ""C:/Users/HP/Desktop/8th sem project/.venv/Scripts/python.exe" app.py"

echo.
echo ===============================================
echo  READY TO START FRONTEND
echo ===============================================
echo.
echo Next steps:
echo   1. Open a new terminal
echo   2. Run: cd "c:\Users\HP\Desktop\8th sem project\frontend"
echo   3. Run: npm install (if not done)
echo   4. Run: npm run dev
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
pause
