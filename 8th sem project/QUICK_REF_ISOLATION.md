# State Isolation - Quick Reference Card

## 🎯 Core Principle
**Live Mode and Simulation Mode are COMPLETELY INDEPENDENT**

---

## 📊 Live Mode

### What Counts?
✅ `/login` (POST)  
✅ `/payment` (POST)  
✅ `/search` (GET)  
✅ `/profile` (GET)  
✅ `/signup` (POST)  
✅ `/logout` (POST)  

### What Doesn't Count?
❌ `/api/stats`  
❌ `/api/logs`  
❌ `/api/anomalies`  
❌ `/simulation/*`  
❌ `/docs`  
❌ `/ws`  

### Check Stats
```bash
curl http://localhost:8000/api/stats
```

### Expected Response
```json
{
  "mode": "LIVE",
  "total_api_calls": 5,
  "request_count": 5,
  "anomalies_detected": 0
}
```

---

## 🔬 Simulation Mode

### Start Simulation
```bash
curl -X POST "http://localhost:8000/simulation/start?simulated_endpoint=/payment&duration_seconds=5"
```

### Stop Simulation
```bash
curl -X POST http://localhost:8000/simulation/stop
```

### Check Stats
```bash
curl http://localhost:8000/simulation/stats
```

### Expected Response
```json
{
  "mode": "SIMULATION",
  "active": false,
  "total_requests": 100,
  "anomalies_detected": 1,
  "simulated_endpoint": "/payment"
}
```

---

## 🔍 Key Differences

| Aspect | Live Mode | Simulation Mode |
|--------|-----------|-----------------|
| **Trigger** | Swagger UI / HTTP | `/simulation/start` |
| **Endpoints** | 6 business endpoints | Any endpoint (synthetic) |
| **Counter** | `live_mode_stats` | `simulation_stats` |
| **DB Flag** | `is_simulation=False` | `is_simulation=True` |
| **Stats API** | `/api/stats` | `/simulation/stats` |
| **Logs API** | `/api/logs` | `/simulation/anomaly-history` |
| **Reset** | Never (cumulative) | On start/stop |

---

## ✅ Verification Tests

### Test 1: Live Counter
```bash
# Hit real endpoint
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'

# Check stats (should increase by 1)
curl http://localhost:8000/api/stats
```

### Test 2: Admin Endpoints Don't Count
```bash
# Hit admin endpoint
curl http://localhost:8000/api/stats

# Check stats again (should NOT increase)
curl http://localhost:8000/api/stats
```

### Test 3: Simulation Isolation
```bash
# Get initial live count
curl http://localhost:8000/api/stats

# Start simulation
curl -X POST "http://localhost:8000/simulation/start?simulated_endpoint=/payment&duration_seconds=5"

# Wait 6 seconds
sleep 6

# Check live stats (should be unchanged)
curl http://localhost:8000/api/stats

# Check simulation stats (should show requests)
curl http://localhost:8000/simulation/stats
```

### Test 4: Automated Verification
```bash
python backend/verify_isolation.py
```

---

## 🐛 Debugging

### Check Live Counter
Look for console logs:
```
[LIVE] Request #1: POST /login - 123.45ms - Status 200
[LIVE] Request #2: POST /payment - 234.56ms - Status 200
```

### Check Simulation Counter
Look for console logs:
```
[SIM] Request #1 - /payment [RATE_SPIKE - HIGH]
[SIM] Request #2 - /payment [RATE_SPIKE - HIGH]
```

### Check Database
```sql
-- Live entries
SELECT COUNT(*) FROM api_logs WHERE is_simulation = 0;

-- Simulation entries
SELECT COUNT(*) FROM api_logs WHERE is_simulation = 1;
```

---

## 🚨 Common Mistakes

### ❌ Wrong: Expecting /api/stats to count
```bash
curl http://localhost:8000/api/stats  # Does NOT increment counter
```

### ✅ Correct: Hit real endpoints
```bash
curl -X POST http://localhost:8000/login  # DOES increment counter
```

### ❌ Wrong: Checking /api/logs for simulation data
```bash
curl http://localhost:8000/api/logs  # Only shows live data
```

### ✅ Correct: Use simulation endpoint
```bash
curl http://localhost:8000/simulation/anomaly-history  # Shows simulation data
```

### ❌ Wrong: Expecting simulation to affect live counter
```bash
# Start simulation
curl -X POST "http://localhost:8000/simulation/start?..."
# Live counter will NOT change
```

### ✅ Correct: Check separate stats
```bash
curl http://localhost:8000/api/stats        # Live stats
curl http://localhost:8000/simulation/stats # Simulation stats
```

---

## 📁 File Locations

### Modified Files
- `backend/middleware.py` - Live mode tracking
- `backend/app.py` - Simulation mode management

### New Files
- `backend/verify_isolation.py` - Automated tests
- `VERIFY_ISOLATION.bat` - Test runner
- `ISOLATION_FIX_COMPLETE.md` - Technical docs
- `BEHAVIOR_SPECIFICATION.md` - Detailed behavior
- `STATE_ISOLATION_FIX_SUMMARY.md` - Complete summary
- `ISOLATION_VISUAL_GUIDE.md` - Visual diagrams

---

## 🎓 Key Code Snippets

### Live Endpoint Definition (middleware.py)
```python
LIVE_ENDPOINTS = {'/login', '/payment', '/search', '/profile', '/signup', '/logout'}

is_live_request = endpoint in LIVE_ENDPOINTS
if is_live_request:
    live_mode_stats['total_requests'] += 1
```

### Simulation State Reset (app.py)
```python
def reset_simulation_state():
    global simulation_active, simulation_stats, simulation_anomaly_recorded
    simulation_active = False
    simulation_stats = {
        'total_requests': 0,
        'windows_processed': 0,
        'anomalies_detected': 0,
        'start_time': None,
        'simulated_endpoint': 'none'
    }
    simulation_anomaly_recorded.clear()
```

### Database Filtering (app.py)
```python
# Live mode query
db.query(APILog).filter(
    (APILog.is_simulation == False) | (APILog.is_simulation == None)
)

# Simulation mode query
db.query(APILog).filter(
    APILog.is_simulation == True
)
```

---

## 📞 Support

### Documentation
- `ISOLATION_FIX_COMPLETE.md` - Full technical details
- `BEHAVIOR_SPECIFICATION.md` - Expected behavior
- `ISOLATION_VISUAL_GUIDE.md` - Visual diagrams

### Testing
- Run: `python backend/verify_isolation.py`
- Or: `VERIFY_ISOLATION.bat`

### Troubleshooting
1. Check console logs for `[LIVE]` and `[SIM]` messages
2. Verify database entries with SQL queries
3. Run automated verification tests
4. Check that backend is running on port 8000

---

## ✨ Summary

```
┌─────────────────────────────────────────────────────────┐
│  Live Mode: Real endpoint hits via Swagger UI          │
│  - Only 6 business endpoints count                     │
│  - Tracked in live_mode_stats                          │
│  - Database: is_simulation=False                       │
│  - Never resets (cumulative)                           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Simulation Mode: Synthetic traffic generation          │
│  - Any endpoint can be simulated                       │
│  - Tracked in simulation_stats                         │
│  - Database: is_simulation=True                        │
│  - Resets on start/stop                                │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Isolation: Complete independence                       │
│  - No shared state                                     │
│  - Separate counters                                   │
│  - Separate database queries                           │
│  - Separate stats endpoints                            │
└─────────────────────────────────────────────────────────┘
```

---

**Last Updated:** 2024  
**Status:** ✅ Complete and Verified
