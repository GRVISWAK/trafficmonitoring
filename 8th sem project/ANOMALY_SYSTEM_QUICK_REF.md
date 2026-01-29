# ANOMALY SYSTEM - QUICK REFERENCE

## ✅ System Status: FULLY OPERATIONAL

All tests passed. The deterministic anomaly system is working correctly.

## Per-Endpoint Anomaly Assignments

| Endpoint   | Anomaly Type          | Severity | Impact | Duration |
|------------|-----------------------|----------|--------|----------|
| `/login`   | ERROR_SPIKE           | CRITICAL | 0.90   | 90s      |
| `/payment` | LATENCY_SPIKE         | HIGH     | 0.75   | 120s     |
| `/search`  | TRAFFIC_BURST         | MEDIUM   | 0.60   | 60s      |
| `/profile` | TIMEOUT               | HIGH     | 0.80   | 150s     |
| `/signup`  | RESOURCE_EXHAUSTION   | CRITICAL | 0.95   | 180s     |
| `/logout`  | ERROR_SPIKE           | CRITICAL | 0.90   | 90s      |

## How to Test

### 1. Start Simulation
```bash
# Start simulation for /payment (will inject LATENCY_SPIKE)
curl -X POST "http://localhost:8000/simulation/start" \
  -H "Content-Type: application/json" \
  -d '{"simulated_endpoint": "/payment", "duration_seconds": 60}'
```

**Expected Behavior:**
- Generates 100+ requests in 60 seconds
- All requests have 5x response times (750ms instead of 150ms)
- LATENCY_SPIKE detected with HIGH severity
- 4 actionable resolutions generated
- Anomaly includes: `anomaly_type`, `severity`, `duration_seconds`, `impact_score`, `failure_probability`

### 2. Check Injection Status
```bash
curl http://localhost:8000/simulation/injection-status
```

**Response:**
```json
{
  "injection_map": {
    "/login": "error_spike",
    "/payment": "latency_spike",
    ...
  },
  "active_injections": {
    "/payment": {
      "is_active": true,
      "time_remaining_seconds": 45,
      "severity": "HIGH",
      "impact_score": 0.75
    }
  }
}
```

### 3. View Detected Anomalies
```bash
curl "http://localhost:8000/simulation/anomaly-history?limit=10"
```

**Each anomaly includes:**
- ✅ `endpoint`: `/payment`
- ✅ `anomaly_type`: `latency_spike`
- ✅ `severity`: `HIGH` (or CRITICAL/MEDIUM/LOW)
- ✅ `timestamp`: `2026-01-29T12:34:56`
- ✅ `duration_seconds`: `120.0`
- ✅ `failure_probability`: `0.60`
- ✅ `impact_score`: `0.75`
- ✅ `resolutions`: Array of 3-5 actionable steps

## Detection Thresholds

| Anomaly Type          | Detection Rule                          |
|-----------------------|-----------------------------------------|
| LATENCY_SPIKE         | avg_response_time > 600ms               |
| ERROR_SPIKE           | error_rate > 25%                        |
| TIMEOUT               | max_response_time > 4000ms              |
| TRAFFIC_BURST         | request_count > 50/minute               |
| RESOURCE_EXHAUSTION   | avg_payload_size > 7500 bytes           |

## Resolution Examples

### LATENCY_SPIKE (HIGH Severity)
1. **SCALING** - Scale horizontally (Add 2 more instances)
2. **CACHING** - Implement Redis caching (5-minute TTL)
3. **OPTIMIZATION** - Review N+1 queries (Eliminate redundant calls)
4. **INFRASTRUCTURE** - Upgrade database tier (Increase IOPS)

### ERROR_SPIKE (CRITICAL Severity)
1. **IMMEDIATE** - Rollback deployment (Revert to stable version)
2. **IMMEDIATE** - Enable circuit breaker (Stop cascading failures)
3. **IMMEDIATE** - Activate backup database (Switch to replica)
4. **INVESTIGATION** - Analyze error logs (Last 1000 errors)
5. **COMMUNICATION** - Notify stakeholders (Send incident alert)

### RESOURCE_EXHAUSTION (CRITICAL Severity)
1. **IMMEDIATE** - Restart application servers (Clear memory leaks)
2. **IMMEDIATE** - Limit request payload size (Max 10MB)
3. **IMMEDIATE** - Enable memory monitoring (Kill at 80% usage)
4. **SCALING** - Upgrade server resources (8GB → 16GB RAM)
5. **INVESTIGATION** - Profile memory usage (Heap analysis)

## Backend Status

**Backend Server:** Running on port 8000  
**Frontend Dashboard:** http://localhost:3000

**Verification Test Results:**
- ✅ Per-endpoint mapping: 6 endpoints configured
- ✅ Injection system: All injections initialized
- ✅ Detection system: Deterministic thresholds working
- ✅ Resolution generation: 3-5 actions per anomaly
- ✅ Severity classification: CRITICAL > HIGH > MEDIUM > LOW
- ✅ Live/Simulation separation: Complete isolation

## Run Verification Test

```bash
cd backend
python test_anomaly_system.py
```

Expected output: **All 7 tests PASS**

## Key Features

### ✅ Deterministic (No Random Logic)
- Fixed anomaly assignments per endpoint
- Strict threshold-based detection
- Consistent results every time

### ✅ Complete Data
Every anomaly includes ALL required fields:
- `endpoint`, `anomaly_type`, `severity`
- `timestamp`, `duration_seconds`
- `failure_probability`, `impact_score`
- `resolutions` (3-5 actionable steps)

### ✅ Actionable Resolutions
- Severity-ranked (CRITICAL to LOW)
- Category-tagged (IMMEDIATE, SCALING, OPTIMIZATION, etc.)
- Detailed implementation steps
- Priority indicators

### ✅ Works for Both Modes
- **Simulation:** Injects and detects synthetic anomalies
- **Live:** Detects real anomalies in production traffic
- **Isolated:** Separate pipelines (is_simulation flag)

## Files

**New Files Created:**
1. `backend/anomaly_injection.py` - Injection system
2. `backend/anomaly_detection.py` - Detection system
3. `backend/resolution_engine.py` - Resolution generator
4. `backend/test_anomaly_system.py` - Verification tests

**Modified:**
1. `backend/app.py` - Integrated new system

**Documentation:**
1. `DETERMINISTIC_ANOMALY_SYSTEM.md` - Complete technical docs
2. `ANOMALY_SYSTEM_QUICK_REF.md` - This file

## Troubleshooting

### Anomaly not detected?
- Check if enough requests generated (need 10+ for detection)
- Verify metrics exceed thresholds (see Detection Thresholds table)
- Run test_anomaly_system.py to verify system health

### Wrong anomaly type?
- Each endpoint has FIXED assignment (see table above)
- Cannot be changed without modifying ENDPOINT_ANOMALY_MAP

### Missing fields?
- All fields populated automatically
- If NULL, check backend logs for errors
- Verify database migration ran successfully

## Summary

**Status:** ✅ READY FOR USE

The anomaly system is fully functional with:
- Per-endpoint anomaly injection
- Deterministic threshold-based detection
- Complete anomaly data (all required fields)
- 3-5 unique, actionable resolutions per anomaly
- Strict severity classification
- Independent live/simulation pipelines
- Zero random or placeholder logic

Start a simulation and watch anomalies get detected with complete data and actionable resolutions!
