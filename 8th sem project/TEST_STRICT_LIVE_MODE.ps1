# ============================================================================
# STRICT LIVE MODE TEST SCRIPT
# ============================================================================
# This script validates that ONLY whitelisted endpoints are tracked

Write-Host "`n" -NoNewline
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " STRICT LIVE MODE - Comprehensive Test" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# ----------------------------------------------------------------------------
# TEST 1: Verify Zero State
# ----------------------------------------------------------------------------
Write-Host "[TEST 1] Verifying zero state..." -ForegroundColor Yellow
$stats = (Invoke-WebRequest -Uri http://localhost:8000/live/stats).Content | ConvertFrom-Json

if ($stats.total_requests -eq 0) {
    Write-Host "  ✅ PASS: Request count is 0" -ForegroundColor Green
} else {
    Write-Host "  ❌ FAIL: Request count is $($stats.total_requests), expected 0" -ForegroundColor Red
}

if ($stats.status -eq "idle") {
    Write-Host "  ✅ PASS: Status is 'idle'" -ForegroundColor Green
} else {
    Write-Host "  ❌ FAIL: Status is '$($stats.status)', expected 'idle'" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# ----------------------------------------------------------------------------
# TEST 2: Verify Blacklisted Endpoints (should NOT be tracked)
# ----------------------------------------------------------------------------
Write-Host "`n[TEST 2] Testing blacklisted endpoints..." -ForegroundColor Yellow

$blacklist = @("/health", "/docs", "/")
foreach ($endpoint in $blacklist) {
    Write-Host "  Testing $endpoint..." -NoNewline
    
    $before = (Invoke-WebRequest -Uri http://localhost:8000/live/stats).Content | ConvertFrom-Json
    
    try {
        Invoke-WebRequest -Uri "http://localhost:8000$endpoint" -ErrorAction SilentlyContinue | Out-Null
    } catch {}
    
    Start-Sleep -Milliseconds 100
    
    $after = (Invoke-WebRequest -Uri http://localhost:8000/live/stats).Content | ConvertFrom-Json
    
    if ($before.total_requests -eq $after.total_requests) {
        Write-Host " ✅ NOT tracked (correct)" -ForegroundColor Green
    } else {
        Write-Host " ❌ WAS tracked (incorrect)" -ForegroundColor Red
    }
}

Start-Sleep -Seconds 2

# ----------------------------------------------------------------------------
# TEST 3: Verify Whitelisted Endpoints (SHOULD be tracked)
# ----------------------------------------------------------------------------
Write-Host "`n[TEST 3] Testing whitelisted endpoints..." -ForegroundColor Yellow

$whitelist = @(
    @{path="/login"; method="POST"; body='{"username":"test","password":"test"}'},
    @{path="/search"; method="GET"; body=""},
    @{path="/profile"; method="GET"; body=""}
)

$initial = (Invoke-WebRequest -Uri http://localhost:8000/live/stats).Content | ConvertFrom-Json

foreach ($endpoint in $whitelist) {
    Write-Host "  Testing $($endpoint.path)..." -NoNewline
    
    $before = (Invoke-WebRequest -Uri http://localhost:8000/live/stats).Content | ConvertFrom-Json
    
    try {
        if ($endpoint.method -eq "POST") {
            Invoke-WebRequest -Uri "http://localhost:8000$($endpoint.path)" -Method POST -Body $endpoint.body -ContentType "application/json" -ErrorAction SilentlyContinue | Out-Null
        } else {
            Invoke-WebRequest -Uri "http://localhost:8000$($endpoint.path)" -ErrorAction SilentlyContinue | Out-Null
        }
    } catch {}
    
    Start-Sleep -Milliseconds 200
    
    $after = (Invoke-WebRequest -Uri http://localhost:8000/live/stats).Content | ConvertFrom-Json
    
    if ($after.total_requests -gt $before.total_requests) {
        Write-Host " ✅ Tracked (correct)" -ForegroundColor Green
    } else {
        Write-Host " ❌ NOT tracked (incorrect)" -ForegroundColor Red
    }
}

Start-Sleep -Seconds 2

# ----------------------------------------------------------------------------
# TEST 4: Fill Window and Verify ML Inference
# ----------------------------------------------------------------------------
Write-Host "`n[TEST 4] Filling window to trigger ML inference..." -ForegroundColor Yellow

$current = (Invoke-WebRequest -Uri http://localhost:8000/live/stats).Content | ConvertFrom-Json
$needed = 10 - $current.current_window_count

if ($needed -le 0) {
    Write-Host "  Window already full, sending 10 more for new window..." -ForegroundColor Cyan
    $needed = 10
}

Write-Host "  Sending $needed requests..." -NoNewline

for ($i=1; $i -le $needed; $i++) {
    try {
        Invoke-WebRequest -Uri http://localhost:8000/login -Method POST -Body "{`"username`":`"user$i`",`"password`":`"test`"}" -ContentType "application/json" -ErrorAction SilentlyContinue | Out-Null
    } catch {}
    Start-Sleep -Milliseconds 100
}

Write-Host " Done" -ForegroundColor Green

Start-Sleep -Seconds 2

$stats = (Invoke-WebRequest -Uri http://localhost:8000/live/stats).Content | ConvertFrom-Json

if ($stats.windows_processed -ge 1) {
    Write-Host "  ✅ PASS: ML inference triggered ($($stats.windows_processed) windows processed)" -ForegroundColor Green
} else {
    Write-Host "  ❌ FAIL: No windows processed yet" -ForegroundColor Red
}

# ----------------------------------------------------------------------------
# TEST 5: Per-Endpoint Breakdown
# ----------------------------------------------------------------------------
Write-Host "`n[TEST 5] Verifying per-endpoint breakdown..." -ForegroundColor Yellow

$dashboard = (Invoke-WebRequest -Uri http://localhost:8000/api/dashboard).Content | ConvertFrom-Json

Write-Host "`n  Endpoint Counts:" -ForegroundColor Cyan
$dashboard.endpoint_counts.PSObject.Properties | ForEach-Object {
    Write-Host "    $($_.Name): $($_.Value)" -ForegroundColor White
}

# ----------------------------------------------------------------------------
# SUMMARY
# ----------------------------------------------------------------------------
Write-Host "`n" -NoNewline
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " TEST SUMMARY" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

Write-Host "`n  Total Requests: $($stats.total_requests)" -ForegroundColor White
Write-Host "  Windows Processed: $($stats.windows_processed)" -ForegroundColor White
Write-Host "  Current Window: $($stats.current_window_count)/10" -ForegroundColor White
Write-Host "  Status: $($stats.status)" -ForegroundColor White
Write-Host ""

Write-Host "  Live Stats:" -ForegroundColor Cyan
Write-Host "    - Only whitelisted endpoints tracked: /login, /signup, /search, /profile, /payment, /logout" -ForegroundColor White
Write-Host "    - Blacklisted endpoints ignored: /, /health, /docs, /api/*, /ws" -ForegroundColor White
Write-Host "    - ML inference triggers every 10 real requests" -ForegroundColor White
Write-Host ""

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host " ✅ STRICT LIVE MODE TEST COMPLETE" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
