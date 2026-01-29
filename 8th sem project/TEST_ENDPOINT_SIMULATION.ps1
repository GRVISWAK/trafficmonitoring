# Endpoint-Specific Simulation Test Script
# Tests all virtual endpoints with different anomaly types

Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  ENDPOINT-SPECIFIC SIMULATION - COMPREHENSIVE TEST      ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Clear previous history
Write-Host "Clearing previous simulation history..." -ForegroundColor Yellow
curl.exe -X POST http://localhost:8000/simulation/clear-history -s | Out-Null
Start-Sleep 1

# Test combinations
$tests = @(
    @{endpoint="/sim/login"; anomaly="RATE_SPIKE"},
    @{endpoint="/sim/search"; anomaly="PARAM_REPETITION"},
    @{endpoint="/sim/profile"; anomaly="ERROR_BURST"},
    @{endpoint="/sim/payment"; anomaly="PAYLOAD_ABUSE"},
    @{endpoint="/sim/signup"; anomaly="ENDPOINT_FLOOD"}
)

Write-Host "Running 5 targeted simulations...`n" -ForegroundColor Green

foreach($test in $tests) {
    Write-Host "Testing: $($test.endpoint) + $($test.anomaly)" -ForegroundColor Yellow
    
    # Start simulation
    $params = @{
        simulated_endpoint = $test.endpoint
        anomaly_type = $test.anomaly
        duration = 8
        requests_per_window = 10
    }
    $uri = "http://localhost:8000/simulation/start?" + (($params.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join '&')
    Invoke-RestMethod -Uri $uri -Method POST | Out-Null
    
    # Wait for processing
    Start-Sleep 4
    
    # Stop simulation
    Invoke-RestMethod -Uri "http://localhost:8000/simulation/stop" -Method POST | Out-Null
    Start-Sleep 1
}

Write-Host "`n✅ All endpoint-specific simulations complete!`n" -ForegroundColor Green

# Get final stats
Write-Host "📊 FINAL STATISTICS:`n" -ForegroundColor Cyan
$stats = Invoke-RestMethod -Uri http://localhost:8000/simulation/stats

Write-Host "Total Detections: $($stats.accuracy.total_detections)" -ForegroundColor White
Write-Host "Correct Detections: $($stats.accuracy.correct_detections)" -ForegroundColor Green
Write-Host "Accuracy: $($stats.accuracy.accuracy_percentage)%" -ForegroundColor Green
Write-Host "False Positives: $($stats.accuracy.false_positives)" -ForegroundColor $(if($stats.accuracy.false_positives -eq 0){'Green'}else{'Red'})
Write-Host "False Negatives: $($stats.accuracy.false_negatives)`n" -ForegroundColor $(if($stats.accuracy.false_negatives -eq 0){'Green'}else{'Red'})

# Get endpoint-specific stats
Write-Host "📍 PER-ENDPOINT STATISTICS:`n" -ForegroundColor Cyan
$endpointStats = Invoke-RestMethod -Uri "http://localhost:8000/simulation/endpoint-stats"
$endpointStats.stats.PSObject.Properties | ForEach-Object {
    $ep = $_.Name
    $data = $_.Value
    Write-Host "$ep :" -ForegroundColor Yellow
    Write-Host "  Total: $($data.total)"
    Write-Host "  Anomalies: $($data.anomalies)"
    Write-Host "  Accuracy: $([math]::Round(($data.correct_detections / $data.total * 100), 1))%"
    Write-Host "  Types: $($data.by_type.PSObject.Properties.Name -join ', ')"
    Write-Host ""
}

# Get priority distribution
Write-Host "🎯 PRIORITY DISTRIBUTION:`n" -ForegroundColor Cyan
$stats.priority_distribution.PSObject.Properties | ForEach-Object {
    Write-Host "  $($_.Name): $($_.Value)"
}

Write-Host "`n🤖 MODEL DECISIONS:`n" -ForegroundColor Cyan
$stats.model_decisions.PSObject.Properties | ForEach-Object {
    Write-Host "  $($_.Name): $($_.Value)"
}

# Get top emergencies
Write-Host "`n🚨 TOP 5 EMERGENCIES:`n" -ForegroundColor Red
$emergencies = Invoke-RestMethod -Uri "http://localhost:8000/simulation/emergencies?limit=5"
$emergencies.top_emergencies | Select-Object @{N='Rank';E={"#$($_.emergency_rank)"}}, simulated_endpoint, anomaly_type, @{N='Risk';E={[math]::Round($_.risk_score,3)}}, priority | Format-Table -AutoSize

Write-Host "`n✅ Endpoint-specific simulation test complete!" -ForegroundColor Green
Write-Host "All virtual endpoints tested with targeted anomalies." -ForegroundColor White
Write-Host "No real API routes affected." -ForegroundColor White
