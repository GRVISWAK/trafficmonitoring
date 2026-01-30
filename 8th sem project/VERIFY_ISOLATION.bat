@echo off
echo ========================================
echo  Live/Simulation Isolation Verification
echo ========================================
echo.
echo Make sure the backend is running on http://localhost:8000
echo.
pause

cd /d "%~dp0backend"

echo.
echo Running isolation tests...
echo.

python verify_isolation.py

echo.
echo ========================================
echo  Tests Complete
echo ========================================
echo.
pause
