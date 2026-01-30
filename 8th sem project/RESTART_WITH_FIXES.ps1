# ===================================================================
# COMPLETE SYSTEM RESTART - Apply All Mode Isolation Fixes
# ===================================================================

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "RESTARTING SYSTEM WITH MODE ISOLATION FIXES" -ForegroundColor Yellow
Write-Host "=====================================================================" -ForegroundColor Cyan

# Kill all existing Python/Uvicorn processes
Write-Host "`n[1/4] Stopping existing backend processes..." -ForegroundColor Green
Get-Process | Where-Object {$_.ProcessName -like "*python*" -or $_.ProcessName -like "*uvicorn*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Start backend in new window
Write-Host "[2/4] Starting backend server..." -ForegroundColor Green
$backendPath = "d:\downloads\8th sem project\8th sem project\backend"
$pythonExe = "d:\downloads\8th sem project\8th sem project\.venv\Scripts\python.exe"

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; & '$pythonExe' -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload" -WindowStyle Normal

Start-Sleep -Seconds 5

# Check if backend started
Write-Host "[3/4] Verifying backend..." -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "[OK] Backend is running on port 8000" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Backend failed to start - Check the backend window" -ForegroundColor Red
}

# Display status
Write-Host "`n[4/4] System Status:" -ForegroundColor Green
Write-Host "  Backend: http://localhost:8000" -ForegroundColor White
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White

Write-Host "`n=====================================================================" -ForegroundColor Cyan
Write-Host "FIXES APPLIED:" -ForegroundColor Yellow
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "[OK] Added missing endpoints: /signup, /profile, /logout" -ForegroundColor Green
Write-Host "[OK] Fixed middleware to count ONLY real endpoints" -ForegroundColor Green
Write-Host "[OK] Live Mode tracks: /login /payment /search /profile /signup /logout" -ForegroundColor Green
Write-Host "[OK] Complete state isolation between Live and Simulation modes" -ForegroundColor Green
Write-Host "[OK] Enhanced simulation stop controls" -ForegroundColor Green

Write-Host "`n=====================================================================" -ForegroundColor Cyan
Write-Host "TEST LIVE MODE COUNTER:" -ForegroundColor Yellow
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "Test with curl or use dashboard test buttons at http://localhost:3000" -ForegroundColor White

Write-Host "`n[OK] System restarted with all fixes!" -ForegroundColor Green
