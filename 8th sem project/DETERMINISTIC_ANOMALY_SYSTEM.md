# DETERMINISTIC ANOMALY SYSTEM - COMPLETE IMPLEMENTATION

## Overview
Implemented a **fully deterministic anomaly injection and detection system** that replaces all random/placeholder logic with strict, threshold-based detection.

## Core Components

### 1. Anomaly Injection System (`anomaly_injection.py`)

**Per-Endpoint Anomaly Mapping (Deterministic):**
```python
ENDPOINT_ANOMALY_MAP = {
    '/login': ERROR_SPIKE,
    '/payment': LATENCY_SPIKE,
    '/search': TRAFFIC_BURST,
    '/profile': TIMEOUT,
    '/signup': RESOURCE_EXHAUSTION,
    '/logout': ERROR_SPIKE,
}
```

**Each endpoint gets EXACTLY ONE anomaly type permanently assigned.**

### 2. Anomaly Types (5 Types)

1. **LATENCY_SPIKE**
   - Response times 5x higher than baseline
   - Severity: HIGH
   - Impact Score: 0.75
   - Duration: 120 seconds
   - Failure Probability: 15%

2. **ERROR_SPIKE**
   - Error rate exceeds 40%
   - Severity: CRITICAL
   - Impact Score: 0.90
   - Duration: 90 seconds
   - Failure Probability: 60%

3. **TIMEOUT**
   - Requests timing out after 5+ seconds
   - Severity: HIGH
   - Impact Score: 0.80
   - Duration: 150 seconds
   - Failure Probability: 50%

4. **TRAFFIC_BURST**
   - Traffic volume 10x above baseline
   - Severity: MEDIUM
   - Impact Score: 0.60
   - Duration: 60 seconds
   - Failure Probability: 25%

5. **RESOURCE_EXHAUSTION**
   - Memory/bandwidth exhaustion from oversized requests
   - Severity: CRITICAL
   - Impact Score: 0.95
   - Duration: 180 seconds
   - Failure Probability: 70%

### 3. Severity Classification (Strict Hierarchy)

```
CRITICAL (4) > HIGH (3) > MEDIUM (2) > LOW (1)
```

**Severity determines:**
- Resolution priority
- Impact score multiplier
- Failure probability baseline
- Alert urgency

### 4. Deterministic Detection (`anomaly_detection.py`)

**Detection Thresholds:**
- Latency Spike: >3x baseline (600ms)
- Error Spike: >25% error rate
- Timeout: >4 seconds max response time
- Traffic Burst: >5x baseline requests
- Resource Exhaustion: >5x baseline payload size

**Detection Logic:**
```python
if avg_response_time > 600ms:
    → LATENCY_SPIKE detected

if error_rate > 0.25:
    → ERROR_SPIKE detected (severity based on rate)

if max_response_time > 4000ms:
    → TIMEOUT detected

if request_count > 50 per minute:
    → TRAFFIC_BURST detected

if avg_payload > 7500 bytes:
    → RESOURCE_EXHAUSTION detected
```

### 5. Resolution Engine (`resolution_engine.py`)

**Generates 3-5 actionable resolutions per anomaly type and severity.**

Example for **LATENCY_SPIKE - CRITICAL**:
1. **IMMEDIATE** - Enable auto-scaling (Add 3-5 server instances)
2. **IMMEDIATE** - Activate CDN caching (Cache at edge locations)
3. **IMMEDIATE** - Enable connection pooling (Reuse DB connections)
4. **OPTIMIZATION** - Optimize slow queries (Add database indexes)
5. **MONITORING** - Set up latency alerts (Alert when p95 > 500ms)

Example for **ERROR_SPIKE - CRITICAL**:
1. **IMMEDIATE** - Rollback deployment (Revert to stable version)
2. **IMMEDIATE** - Enable circuit breaker (Stop cascading failures)
3. **IMMEDIATE** - Activate backup database (Switch to read replica)
4. **INVESTIGATION** - Analyze error logs (Check last 1000 errors)
5. **COMMUNICATION** - Notify stakeholders (Send incident alert)

## Complete Anomaly Data Structure

Each detected anomaly includes **ALL required fields**:

```python
{
    'endpoint': '/payment',
    'anomaly_type': 'latency_spike',
    'severity': 'HIGH',
    'timestamp': '2026-01-29T12:34:56',
    'duration_seconds': 120.0,
    'failure_probability': 0.60,
    'impact_score': 0.82,
    'confidence': 0.87,
    'metric_value': 1500,  # ms
    'threshold': 600,  # ms
    'resolutions': [
        {
            'category': 'IMMEDIATE',
            'action': 'Enable auto-scaling',
            'detail': 'Add 3-5 additional server instances',
            'priority': 'CRITICAL'
        },
        # ... more resolutions
    ]
}
```

## How It Works

### Simulation Mode (Per-Endpoint Injection)

```
1. User starts simulation for /payment endpoint
   ↓
2. Anomaly Injector checks: /payment → LATENCY_SPIKE assigned
   ↓
3. For each generated request:
   - Base log: response_time = 150ms
   - Injection: response_time *= 5 = 750ms
   - Save to DB with is_simulation=True
   ↓
4. Every 10 requests, run detection:
   - Extract features (is_simulation=True)
   - Detector: avg_response = 750ms > 600ms threshold
   - DETECTION: LATENCY_SPIKE confirmed
   ↓
5. Generate resolutions for LATENCY_SPIKE + HIGH severity
   ↓
6. Save anomaly log with:
   - anomaly_type: 'latency_spike'
   - severity: 'HIGH'
   - duration_seconds: 120
   - impact_score: 0.75
   - failure_probability: 0.60
   - resolutions: [5 actionable steps]
   ↓
7. Broadcast via WebSocket to dashboard
```

### Live Mode (Deterministic Detection)

```
1. Background task runs every 60 seconds
   ↓
2. Extract features from LIVE traffic (is_simulation=False)
   ↓
3. Detector analyzes metrics:
   - error_rate = 0.35 (35%)
   - Threshold: 0.25 (25%)
   - DETECTION: ERROR_SPIKE
   ↓
4. Classification:
   - Severity: CRITICAL (error_rate > 40%)
   - Impact: 0.90
   - Failure Probability: 0.60
   ↓
5. Generate resolutions for ERROR_SPIKE + CRITICAL
   ↓
6. Save and broadcast anomaly
```

## API Endpoints

### Get Injection Status
```
GET /simulation/injection-status

Response:
{
    "injection_map": {
        "/login": "error_spike",
        "/payment": "latency_spike",
        "/search": "traffic_burst",
        "/profile": "timeout",
        "/signup": "resource_exhaustion"
    },
    "active_injections": {
        "/payment": {
            "anomaly_type": "latency_spike",
            "is_active": true,
            "time_remaining_seconds": 85,
            "severity": "HIGH",
            "impact_score": 0.75
        }
    }
}
```

### Reset Injections
```
POST /simulation/reset-injections

Response:
{
    "status": "success",
    "message": "Anomaly injections reset with new timings"
}
```

## Key Features

### ✅ No Random Logic
- Detection uses strict thresholds
- No probability-based decisions
- Deterministic outcomes every time

### ✅ Per-Endpoint Assignment
- Each endpoint gets ONE specific anomaly type
- Consistent behavior across runs
- Easy to test and verify

### ✅ Complete Anomaly Data
Every anomaly includes:
- `endpoint` - Which API endpoint
- `anomaly_type` - Specific type (latency_spike, error_spike, etc.)
- `severity` - Strict classification (CRITICAL/HIGH/MEDIUM/LOW)
- `timestamp` - When detected
- `duration_seconds` - How long it lasted
- `failure_probability` - Likelihood of system failure (0.0-1.0)
- `impact_score` - Business impact (0.0-1.0)

### ✅ Actionable Resolutions
- 3-5 unique resolutions per anomaly
- Severity-ranked (CRITICAL → LOW)
- Category-tagged (IMMEDIATE, OPTIMIZATION, MONITORING, etc.)
- Detailed action steps with specifics

### ✅ Works for Both Modes
- **Live Mode:** Detects real anomalies in production traffic
- **Simulation Mode:** Injects and detects synthetic anomalies
- **Strictly Separated:** is_simulation flag prevents contamination

## Testing

### Test Simulation
```bash
# Start simulation for /payment (LATENCY_SPIKE assigned)
curl -X POST http://localhost:8000/simulation/start \
  -H "Content-Type: application/json" \
  -d '{"simulated_endpoint": "/payment", "duration_seconds": 60}'

# Expected:
# - 100+ requests generated
# - All have 5x response times
# - LATENCY_SPIKE detected with HIGH severity
# - 4-5 resolutions generated
```

### Check Injection Status
```bash
curl http://localhost:8000/simulation/injection-status

# Expected:
# - Shows all endpoint → anomaly type mappings
# - Active injections with time remaining
# - Severity and impact scores
```

### Verify Detection
```bash
curl http://localhost:8000/simulation/anomaly-history?limit=10

# Expected:
# - Each anomaly has anomaly_type field
# - Severity is CRITICAL/HIGH/MEDIUM/LOW
# - duration_seconds populated
# - impact_score between 0-1
# - failure_probability between 0-1
```

## Files Created

1. **`backend/anomaly_injection.py`** (189 lines)
   - AnomalyType enum
   - Severity enum
   - ENDPOINT_ANOMALY_MAP
   - ANOMALY_CONFIGS
   - AnomalyInjector class
   - inject_anomaly_into_log() function

2. **`backend/anomaly_detection.py`** (155 lines)
   - AnomalyDetector class
   - Deterministic threshold-based detection
   - Severity classification logic
   - Impact score calculation
   - Failure probability calculation

3. **`backend/resolution_engine.py`** (188 lines)
   - ResolutionEngine class
   - 5 anomaly types × 3 severity levels = 15 resolution sets
   - 3-5 unique resolutions per set
   - Category-tagged actions
   - Priority rankings

## Files Modified

1. **`backend/app.py`**
   - Imported anomaly modules
   - Updated simulation to use injection system
   - Replaced ML detection with deterministic detector
   - Added anomaly_type, severity, duration, impact_score fields
   - Generate and save resolutions
   - Added injection status endpoints

## Migration Notes

**No database migration needed** - The columns already exist from previous work:
- `anomaly_type` VARCHAR(100)
- `severity` VARCHAR(20)
- `duration_seconds` FLOAT
- `impact_score` FLOAT

## Summary

**Before:**
- Random anomaly generation
- ML-based detection (inconsistent)
- Missing anomaly_type, severity, duration fields
- No actionable resolutions
- Placeholder/dummy logic

**After:**
- Deterministic per-endpoint anomaly injection
- Threshold-based detection (100% consistent)
- ALL required fields populated correctly
- 3-5 unique, actionable resolutions per anomaly
- Strict severity classification
- Works independently for live and simulation modes
- Zero random or placeholder logic

**Result:** Complete, production-ready anomaly system with deterministic behavior and comprehensive data.
