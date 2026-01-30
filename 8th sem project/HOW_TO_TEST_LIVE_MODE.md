# QUICK START - Test Live Mode Counter

## 🎯 How to Increment Live Mode Counter

The Live Mode counter **ONLY** tracks these real endpoints:

### ✅ Real Endpoints (Count in Live Mode):
```bash
# 1. Login
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "test123"}'

# 2. Search
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test search term"}'

# 3. Payment
curl -X POST http://localhost:8000/payment \
  -H "Content-Type: application/json" \
  -d '{"amount": 100.50, "currency": "USD", "card": "4111111111111111"}'

# 4. Profile
curl http://localhost:8000/profile

# 5. Signup
curl -X POST http://localhost:8000/signup \
  -H "Content-Type: application/json" \
  -d '{"username": "newuser", "email": "user@test.com", "password": "pass123"}'

# 6. Logout
curl -X POST http://localhost:8000/logout \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser"}'
```

**After each request:**
- Live Mode counter increments
- Console shows: `[LIVE] Request #X: POST /endpoint - XXms - Status XXX`
- Dashboard updates automatically

---

## ❌ These Do NOT Count (Excluded):

```bash
# API monitoring endpoints - excluded
curl http://localhost:8000/api/dashboard
curl http://localhost:8000/api/anomalies
curl http://localhost:8000/api/graphs/risk-score-timeline

# Simulation endpoints - excluded
curl http://localhost:8000/api/simulation/start-enhanced
curl http://localhost:8000/simulation/stats

# Admin endpoints - excluded
curl http://localhost:8000/admin/query
```

---

## 🧪 Quick Test Sequence

```bash
# Test 1: Check initial state (should be 0)
curl http://localhost:8000/api/dashboard | jq '.total_api_calls'
# Expected: 0

# Test 2: Hit login 3 times
for i in {1..3}; do
  curl -X POST http://localhost:8000/login \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"user$i\", \"password\": \"pass$i\"}"
done

# Test 3: Check counter again (should be 3)
curl http://localhost:8000/api/dashboard | jq '.total_api_calls'
# Expected: 3

# Test 4: Hit search 5 times
for i in {1..5}; do
  curl -X POST http://localhost:8000/search \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"search term $i\"}"
done

# Test 5: Check counter (should be 8)
curl http://localhost:8000/api/dashboard | jq '.total_api_calls'
# Expected: 8

# Test 6: Hit payment 2 times
for i in {1..2}; do
  curl -X POST http://localhost:8000/payment \
    -H "Content-Type: application/json" \
    -d '{"amount": 99.99, "currency": "USD"}'
done

# Test 7: Final check (should be 10)
curl http://localhost:8000/api/dashboard | jq '.total_api_calls'
# Expected: 10
```

---

## 🎮 Using Browser (Alternative)

### Method 1: Use Postman/Insomnia
1. Create POST request to `http://localhost:8000/login`
2. Body (JSON):
   ```json
   {
     "username": "testuser",
     "password": "test123"
   }
   ```
3. Send request
4. Refresh dashboard - counter should increment

### Method 2: Use Dashboard Test Buttons
1. Go to `http://localhost:3000`
2. Look for "Test Live Endpoints" section (if implemented)
3. Click buttons to hit real endpoints

---

## 🔍 Monitor Live Counter in Real-Time

### PowerShell Script:
```powershell
# Watch Live Mode counter update
while ($true) {
    $stats = Invoke-RestMethod -Uri "http://localhost:8000/api/dashboard"
    Write-Host "Live Mode Counter: $($stats.total_api_calls)" -ForegroundColor Green
    Start-Sleep -Seconds 2
}
```

### Bash Script:
```bash
# Watch Live Mode counter update
while true; do
  curl -s http://localhost:8000/api/dashboard | jq '.total_api_calls'
  sleep 2
done
```

---

## 🚀 Batch Test (Generate Traffic)

### PowerShell:
```powershell
# Generate 50 login requests
1..50 | ForEach-Object {
    $body = @{
        username = "user$_"
        password = "pass$_"
    } | ConvertTo-Json
    
    Invoke-RestMethod -Uri "http://localhost:8000/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body
        
    Write-Host "Sent request $_/50"
    Start-Sleep -Milliseconds 100
}

# Check final counter
$stats = Invoke-RestMethod -Uri "http://localhost:8000/api/dashboard"
Write-Host "Final Live Mode Counter: $($stats.total_api_calls)" -ForegroundColor Cyan
```

### Bash:
```bash
# Generate 50 login requests
for i in {1..50}; do
  curl -X POST http://localhost:8000/login \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"user$i\", \"password\": \"pass$i\"}" \
    -s > /dev/null
  echo "Sent request $i/50"
  sleep 0.1
done

# Check final counter
curl -s http://localhost:8000/api/dashboard | jq '.total_api_calls'
```

---

## ✅ Expected Console Output

When you hit a live endpoint, you should see:
```
[LIVE] Request #1: POST /login - 45.23ms - Status 200
[LIVE] Request #2: POST /search - 38.91ms - Status 200
[LIVE] Request #3: POST /payment - 52.17ms - Status 200
...
```

---

## 🎯 Summary

**To increment Live Mode counter:**
1. Hit `/login`, `/payment`, `/search`, `/profile`, `/signup`, or `/logout`
2. Use POST for login/payment/search/signup/logout
3. Use GET for profile
4. Include proper JSON body for POST requests

**Counter will NOT increment for:**
- `/api/*` endpoints (monitoring/graphs)
- `/simulation/*` endpoints
- `/admin/*` endpoints
- WebSocket connections

**Backend is currently running on port 8000 - Start testing now!**
