# ============================================================================
# VERIFY STRICT COUNT - Ensure Exactly 1 Count Per Manual API Call
# ============================================================================

Write-Host "`n╔═══════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         STRICT COUNT VERIFICATION - Zero Tolerance Testing               ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# ----------------------------------------------------------------------------
# TEST 1: Verify OPTIONS requests (CORS preflight) are NOT counted
# ----------------------------------------------------------------------------
Write-Host "[TEST 1] CORS Preflight Filtering (OPTIONS requests should NOT count)`n" -ForegroundColor Yellow

$before = (Invoke-WebRequest -Uri http://localhost:8000/live/stats).Content | ConvertFrom-Json

# Send OPTIONS request (CORS preflight)
try {
    Invoke-WebRequest -Uri http://localhost:8000/login -Method OPTIONS -ErrorAction SilentlyContinue | Out-Null
} catch {}

Start-Sleep -Milliseconds 300

$after = (Invoke-WebRequest -Uri http://localhost:8000/live/stats).Content | ConvertFrom-Json

if ($before.total_requests -eq $after.total_requests) {
    Write-Host "  PASS: OPTIONS request NOT counted (Before: $($before.total_requests), After: $($after.total_requests))" -ForegroundColor Green
} else {
    Write-Host "  FAIL: OPTIONS request WAS counted (Before: $($before.total_requests), After: $($after.total_requests))" -ForegroundColor Red
}

# ----------------------------------------------------------------------------
# TEST 2: Single Manual Request = Exactly +1
# ----------------------------------------------------------------------------
Write-Host "`n[TEST 2] Single Manual Request Increments by EXACTLY 1`n" -ForegroundColor Yellow

$before = (Invoke-WebRequest -Uri http://localhost:8000/live/stats).Content | ConvertFrom-Json

# Send exactly ONE manual request
try {
    Invoke-WebRequest -Uri http://localhost:8000/login -Method POST -Body '{"username":"test","password":"test"}' -ContentType "application/json" -ErrorAction SilentlyContinue | Out-Null
} catch {}

Start-Sleep -Milliseconds 300

$after = (Invoke-WebRequest -Uri http://localhost:8000/live/stats).Content | ConvertFrom-Json

$increment = $after.total_requests - $before.total_requests

if ($increment -eq 1) {
    Write-Host "  PASS: Exactly +1 increment (Before: $($before.total_requests), After: $($after.total_requests))" -ForegroundColor Green
} else {
    Write-Host "  FAIL: Increment was $increment, expected 1 (Before: $($before.total_requests), After: $($after.total_requests))" -ForegroundColor Red
}

# ----------------------------------------------------------------------------
# TEST 3: Multiple Sequential Requests = Exact Count
# ----------------------------------------------------------------------------
Write-Host "`n[TEST 3] 5 Sequential Requests = Exactly +5 Count`n" -ForegroundColor Yellow

$before = (Invoke-WebRequest -Uri http://localhost:8000/live/stats).Content | ConvertFrom-Json

# Send exactly 5 requests
for ($i=1; $i -le 5; $i++) {
    try {
        Invoke-WebRequest -Uri http://localhost:8000/search?query=test$i -ErrorAction SilentlyContinue | Out-Null
    } catch {}
    Start-Sleep -Milliseconds 100
}

Start-Sleep -Milliseconds 500

$after = (Invoke-WebRequest -Uri http://localhost:8000/live/stats).Content | ConvertFrom-Json

$increment = $after.total_requests - $before.total_requests

if ($increment -eq 5) {
    Write-Host "  PASS: Exactly +5 increment (Before: $($before.total_requests), After: $($after.total_requests))" -ForegroundColor Green
} else {
    Write-Host "  FAIL: Increment was $increment, expected 5 (Before: $($before.total_requests), After: $($after.total_requests))" -ForegroundColor Red
}

# ----------------------------------------------------------------------------
# TEST 4: Blacklisted Endpoints = Zero Impact
# ----------------------------------------------------------------------------
Write-Host "`n[TEST 4] Blacklisted Endpoints Have ZERO Impact on Count`n" -ForegroundColor Yellow

$before = (Invoke-WebRequest -Uri http://localhost:8000/live/stats).Content | ConvertFrom-Json

# Call multiple blacklisted endpoints
$blacklist = @("/health", "/", "/docs", "/api/dashboard", "/metrics")
foreach ($endpoint in $blacklist) {
    try {
        Invoke-WebRequest -Uri "http://localhost:8000$endpoint" -ErrorAction SilentlyContinue | Out-Null
    } catch {}
}

Start-Sleep -Milliseconds 500

$after = (Invoke-WebRequest -Uri http://localhost:8000/live/stats).Content | ConvertFrom-Json

if ($before.total_requests -eq $after.total_requests) {
    Write-Host "  PASS: Zero increment from blacklisted endpoints (Count unchanged: $($before.total_requests))" -ForegroundColor Green
} else {
    Write-Host "  FAIL: Count changed (Before: $($before.total_requests), After: $($after.total_requests))" -ForegroundColor Red
}

# ----------------------------------------------------------------------------
# TEST 5: Window Creation Does NOT Inflate Count
# ----------------------------------------------------------------------------
Write-Host "`n[TEST 5] Window Creation/Inference Does NOT Modify Request Count`n" -ForegroundColor Yellow

$before = (Invoke-WebRequest -Uri http://localhost:8000/live/stats).Content | ConvertFrom-Json

# Calculate how many requests needed to fill window
$needed = 10 - $before.current_window_count

if ($needed -le 0) {
    $needed = 10  # Fill new window
}

Write-Host "  Sending $needed requests to fill window..." -ForegroundColor Cyan

# Send exact number to fill window
for ($i=1; $i -le $needed; $i++) {
    $body = @{username="user$i"; password="test"} | ConvertTo-Json
    try {
        Invoke-WebRequest -Uri http://localhost:8000/login -Method POST -Body $body -ContentType "application/json" -ErrorAction SilentlyContinue | Out-Null
    } catch {}
    Start-Sleep -Milliseconds 100
}

Start-Sleep -Seconds 1

$after = (Invoke-WebRequest -Uri http://localhost:8000/live/stats).Content | ConvertFrom-Json

$increment = $after.total_requests - $before.total_requests

if ($increment -eq $needed) {
    Write-Host "  PASS: Count increased by EXACTLY $needed (window creation added 0)" -ForegroundColor Green
    Write-Host "       Before: $($before.total_requests), After: $($after.total_requests)" -ForegroundColor Gray
    Write-Host "       Windows processed: $($before.windows_processed) to $($after.windows_processed)" -ForegroundColor Gray
} else {
    Write-Host "  FAIL: Count increased by $increment, expected $needed" -ForegroundColor Red
    Write-Host "       Possible double-counting or window inflation!" -ForegroundColor Red
}

# ----------------------------------------------------------------------------
# TEST 6: Database Count Matches Live Stats
# ----------------------------------------------------------------------------
Write-Host "`n[TEST 6] Database Count Matches Live Stats (No Discrepancy)`n" -ForegroundColor Yellow

$liveStats = (Invoke-WebRequest -Uri http://localhost:8000/live/stats).Content | ConvertFrom-Json
$dashboardStats = (Invoke-WebRequest -Uri http://localhost:8000/api/dashboard).Content | ConvertFrom-Json

if ($liveStats.total_requests -eq $dashboardStats.total_requests) {
    Write-Host "  PASS: Counts match perfectly" -ForegroundColor Green
    Write-Host "       Live Stats: $($liveStats.total_requests)" -ForegroundColor Gray
    Write-Host "       Database:   $($dashboardStats.total_requests)" -ForegroundColor Gray
} else {
    Write-Host "  FAIL: Count mismatch detected!" -ForegroundColor Red
    Write-Host "       Live Stats: $($liveStats.total_requests)" -ForegroundColor Red
    Write-Host "       Database:   $($dashboardStats.total_requests)" -ForegroundColor Red
}

# ----------------------------------------------------------------------------
# SUMMARY
# ----------------------------------------------------------------------------
Write-Host "`n╔═══════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                         VERIFICATION COMPLETE                             ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "If all tests PASSED:" -ForegroundColor Green
Write-Host "   - Exactly 1 count per manual API call" -ForegroundColor White
Write-Host "   - CORS preflight filtered" -ForegroundColor White
Write-Host "   - Blacklisted endpoints ignored" -ForegroundColor White
Write-Host "   - Window creation doesn't inflate count" -ForegroundColor White
Write-Host "   - Database matches live stats`n" -ForegroundColor White

Write-Host "Current Status:" -ForegroundColor Yellow
$final = (Invoke-WebRequest -Uri http://localhost:8000/live/stats).Content | ConvertFrom-Json
Write-Host "  Total Requests: $($final.total_requests)" -ForegroundColor White
Write-Host "  Windows Processed: $($final.windows_processed)" -ForegroundColor White
Write-Host "  Current Window: $($final.current_window_count)/10" -ForegroundColor White
Write-Host "  Status: $($final.status.ToUpper())`n" -ForegroundColor White
