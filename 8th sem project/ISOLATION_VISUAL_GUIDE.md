# State Isolation Architecture - Visual Guide

## Request Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         INCOMING HTTP REQUEST                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │   LoggingMiddleware           │
                    │   (middleware.py)             │
                    └───────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │ Is endpoint in LIVE_ENDPOINTS?│
                    │ {/login, /payment, /search,   │
                    │  /profile, /signup, /logout}  │
                    └───────────────────────────────┘
                            │               │
                    ┌───────┘               └───────┐
                    │ YES                           │ NO
                    ▼                               ▼
        ┌─────────────────────────┐    ┌─────────────────────────┐
        │  LIVE MODE TRACKING     │    │  SKIP TRACKING          │
        │                         │    │                         │
        │  1. Log to database     │    │  - No database entry    │
        │     is_simulation=False │    │  - No counter increment │
        │                         │    │  - Just pass through    │
        │  2. Increment counter   │    │                         │
        │     live_mode_stats++   │    │  Examples:              │
        │                         │    │  - /api/stats           │
        │  3. Print [LIVE] log    │    │  - /api/logs            │
        │                         │    │  - /simulation/*        │
        │  4. Track metrics       │    │  - /docs                │
        │     - Response time     │    │  - /ws                  │
        │     - Error rate        │    │                         │
        └─────────────────────────┘    └─────────────────────────┘
                    │                               │
                    └───────────┬───────────────────┘
                                ▼
                    ┌───────────────────────────────┐
                    │   Return HTTP Response        │
                    └───────────────────────────────┘
```

## Simulation Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    POST /simulation/start                                │
│              ?simulated_endpoint=/payment&duration_seconds=5             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │  reset_simulation_state()     │
                    │  - Clear all counters         │
                    │  - Reset to defaults          │
                    │  - Clear anomaly tracking     │
                    └───────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │  Set simulation_active=True   │
                    │  Initialize simulation_stats  │
                    └───────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │  Start Background Task        │
                    │  run_simulation()             │
                    └───────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
        ┌─────────────────────────┐    ┌─────────────────────────┐
        │  Generate Synthetic     │    │  Track Simulation State │
        │  Traffic                │    │                         │
        │                         │    │  simulation_stats:      │
        │  For each request:      │    │  - total_requests++     │
        │  1. Create log data     │    │  - windows_processed++  │
        │  2. Inject anomaly      │    │  - anomalies_detected++ │
        │  3. Save to database    │    │                         │
        │     is_simulation=True  │    │  Print [SIM] logs       │
        │  4. Increment counter   │    │                         │
        │                         │    │  NEVER affects:         │
        │  NEVER affects:         │    │  - live_mode_stats      │
        │  - live_mode_stats      │    │                         │
        └─────────────────────────┘    └─────────────────────────┘
                    │                               │
                    └───────────┬───────────────────┘
                                ▼
                    ┌───────────────────────────────┐
                    │  Duration Complete or         │
                    │  POST /simulation/stop        │
                    └───────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │  Set simulation_active=False  │
                    │  Copy final stats             │
                    └───────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │  reset_simulation_state()     │
                    │  - Clean up for next run      │
                    └───────────────────────────────┘
```

## State Isolation Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         APPLICATION STATE                                │
└─────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────┐    ┌────────────────────────────────┐
│        LIVE MODE STATE         │    │     SIMULATION MODE STATE      │
│      (middleware.py)           │    │         (app.py)               │
├────────────────────────────────┤    ├────────────────────────────────┤
│                                │    │                                │
│  live_mode_stats = {           │    │  simulation_stats = {          │
│    'total_requests': 0,        │    │    'total_requests': 0,        │
│    'windows_processed': 0,     │    │    'windows_processed': 0,     │
│    'anomalies_detected': 0,    │    │    'anomalies_detected': 0,    │
│    'start_time': None,         │    │    'start_time': None,         │
│    'error_count': 0,           │    │    'simulated_endpoint': None  │
│    'response_times': []        │    │  }                             │
│  }                             │    │                                │
│                                │    │  simulation_active = False     │
│  LIVE_ENDPOINTS = {            │    │                                │
│    '/login',                   │    │  simulation_anomaly_recorded   │
│    '/payment',                 │    │    = set()                     │
│    '/search',                  │    │                                │
│    '/profile',                 │    │                                │
│    '/signup',                  │    │  reset_simulation_state()      │
│    '/logout'                   │    │    - Resets all values         │
│  }                             │    │    - Called on start/stop      │
│                                │    │                                │
│  ✓ Never reset                 │    │  ✓ Reset on start/stop         │
│  ✓ Cumulative tracking         │    │  ✓ Fresh state each run        │
│  ✓ Only real endpoints         │    │  ✓ Only synthetic traffic      │
│                                │    │                                │
└────────────────────────────────┘    └────────────────────────────────┘
            │                                      │
            │         NO INTERACTION               │
            │         NO SHARED STATE              │
            │         COMPLETE ISOLATION           │
            │                                      │
            └──────────────┬───────────────────────┘
                           ▼
            ┌──────────────────────────────────────┐
            │         DATABASE LAYER               │
            │                                      │
            │  ┌────────────────────────────────┐ │
            │  │         api_logs               │ │
            │  ├────────────────────────────────┤ │
            │  │  id | endpoint | is_simulation │ │
            │  │  1  | /login   | False         │ │ ← Live
            │  │  2  | /payment | False         │ │ ← Live
            │  │  3  | /payment | True          │ │ ← Simulation
            │  │  4  | /payment | True          │ │ ← Simulation
            │  │  5  | /search  | False         │ │ ← Live
            │  └────────────────────────────────┘ │
            │                                      │
            │  Queries filter by is_simulation:   │
            │  - Live: WHERE is_simulation=False  │
            │  - Sim:  WHERE is_simulation=True   │
            └──────────────────────────────────────┘
```

## Stats Endpoint Comparison

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         GET /api/stats                                   │
│                         (LIVE MODE)                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  {                                                                       │
│    "mode": "LIVE",                                                       │
│    "total_api_calls": 5,        ← Only real endpoint hits               │
│    "request_count": 5,          ← Same as total_api_calls               │
│    "windows_processed": 0,      ← Live detection windows                │
│    "anomalies_detected": 0,     ← Live anomalies only                   │
│    "avg_response_time": 150.23, ← From live traffic                     │
│    "error_rate": 0.05           ← From live traffic                     │
│  }                                                                       │
│                                                                          │
│  Data Source:                                                            │
│  - live_mode_stats dictionary                                           │
│  - Database: WHERE is_simulation=False                                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                      GET /simulation/stats                               │
│                      (SIMULATION MODE)                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  {                                                                       │
│    "mode": "SIMULATION",                                                 │
│    "active": false,             ← Is simulation running?                 │
│    "total_requests": 0,         ← Only synthetic traffic                 │
│    "windows_processed": 0,      ← Simulation detection windows           │
│    "anomalies_detected": 0,     ← Simulation anomalies only              │
│    "simulated_endpoint": "none",← Which endpoint was simulated           │
│    "start_time": null           ← When simulation started                │
│  }                                                                       │
│                                                                          │
│  Data Source:                                                            │
│  - simulation_stats dictionary                                           │
│  - Database: WHERE is_simulation=True                                   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Counter Increment Logic

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    LIVE MODE COUNTER INCREMENT                           │
└─────────────────────────────────────────────────────────────────────────┘

Request: POST /login
    │
    ├─→ Middleware intercepts
    │
    ├─→ Check: endpoint in LIVE_ENDPOINTS?
    │       └─→ YES (/login is in the set)
    │
    ├─→ Log to database (is_simulation=False)
    │
    ├─→ live_mode_stats['total_requests'] += 1
    │
    └─→ Print: [LIVE] Request #1: POST /login - 123.45ms - Status 200

Request: GET /api/stats
    │
    ├─→ Middleware intercepts
    │
    ├─→ Check: endpoint in LIVE_ENDPOINTS?
    │       └─→ NO (/api/stats is NOT in the set)
    │
    ├─→ Skip logging
    │
    ├─→ live_mode_stats['total_requests'] unchanged
    │
    └─→ No print (not tracked)

┌─────────────────────────────────────────────────────────────────────────┐
│                 SIMULATION MODE COUNTER INCREMENT                        │
└─────────────────────────────────────────────────────────────────────────┘

Simulation Start: POST /simulation/start?simulated_endpoint=/payment
    │
    ├─→ reset_simulation_state()
    │       └─→ simulation_stats['total_requests'] = 0
    │
    ├─→ simulation_active = True
    │
    └─→ Start background task: run_simulation()
            │
            ├─→ Generate synthetic request
            │
            ├─→ Log to database (is_simulation=True)
            │
            ├─→ simulation_stats['total_requests'] += 1
            │
            ├─→ Print: [SIM] Request #1 - /payment [ANOMALY_TYPE]
            │
            └─→ Repeat until duration complete

Simulation Stop: POST /simulation/stop
    │
    ├─→ simulation_active = False
    │
    ├─→ Copy final stats
    │
    └─→ reset_simulation_state()
            └─→ simulation_stats['total_requests'] = 0
```

## Database Query Filtering

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      DATABASE QUERY PATTERNS                             │
└─────────────────────────────────────────────────────────────────────────┘

LIVE MODE QUERIES:
┌─────────────────────────────────────────────────────────────────────────┐
│  Endpoint: GET /api/logs                                                 │
│                                                                          │
│  Query:                                                                  │
│    db.query(APILog).filter(                                             │
│      (APILog.is_simulation == False) |                                  │
│      (APILog.is_simulation == None)                                     │
│    ).order_by(APILog.timestamp.desc()).limit(100)                       │
│                                                                          │
│  Returns: Only real endpoint hits                                       │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  Endpoint: GET /api/anomalies                                            │
│                                                                          │
│  Query:                                                                  │
│    db.query(AnomalyLog).filter(                                         │
│      (AnomalyLog.is_simulation == False) |                              │
│      (AnomalyLog.is_simulation == None)                                 │
│    ).order_by(AnomalyLog.timestamp.desc()).limit(100)                   │
│                                                                          │
│  Returns: Only live anomalies                                           │
└─────────────────────────────────────────────────────────────────────────┘

SIMULATION MODE QUERIES:
┌─────────────────────────────────────────────────────────────────────────┐
│  Endpoint: GET /simulation/anomaly-history                               │
│                                                                          │
│  Query:                                                                  │
│    db.query(AnomalyLog).filter(                                         │
│      AnomalyLog.is_simulation == True                                   │
│    ).order_by(AnomalyLog.timestamp.desc()).limit(200)                   │
│                                                                          │
│  Returns: Only simulation anomalies                                     │
└─────────────────────────────────────────────────────────────────────────┘

RESULT: No overlap between Live and Simulation data
```

## Testing Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    VERIFICATION TEST FLOW                                │
└─────────────────────────────────────────────────────────────────────────┘

Test 1: Live Mode Counting
    │
    ├─→ Get initial stats
    │       └─→ initial_count = 0
    │
    ├─→ POST /login (should count)
    │       └─→ live_mode_stats['total_requests'] = 1
    │
    ├─→ GET /api/stats (should NOT count)
    │       └─→ live_mode_stats['total_requests'] = 1 (unchanged)
    │
    └─→ Verify: final_count - initial_count == 1 ✓

Test 2: Simulation Isolation
    │
    ├─→ Get initial live count
    │       └─→ initial_live = 0
    │
    ├─→ Start simulation (5 seconds)
    │       └─→ Generates ~100 synthetic requests
    │
    ├─→ Wait for completion
    │
    ├─→ Check simulation stats
    │       └─→ simulation_stats['total_requests'] = 100
    │
    ├─→ Check live stats
    │       └─→ live_mode_stats['total_requests'] = 0 (unchanged)
    │
    └─→ Verify: live count unchanged ✓

Test 3: Simulation Reset
    │
    ├─→ Start first simulation
    │       └─→ simulation_stats['total_requests'] = 50
    │
    ├─→ Stop simulation
    │       └─→ reset_simulation_state() called
    │       └─→ simulation_stats['total_requests'] = 0
    │
    ├─→ Start second simulation
    │       └─→ simulation_stats['total_requests'] starts at 0
    │
    └─→ Verify: Second run starts fresh ✓

Test 4: Database Isolation
    │
    ├─→ Query live logs
    │       └─→ SELECT * WHERE is_simulation=False
    │       └─→ Returns only real endpoint hits
    │
    ├─→ Query simulation history
    │       └─→ SELECT * WHERE is_simulation=True
    │       └─→ Returns only synthetic traffic
    │
    └─→ Verify: No overlap ✓
```

## Summary

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ISOLATION GUARANTEES                             │
└─────────────────────────────────────────────────────────────────────────┘

✓ Live Mode and Simulation Mode have separate state dictionaries
✓ Live Mode only counts 6 specific business endpoints
✓ Simulation Mode only counts synthetic traffic
✓ Database entries tagged with is_simulation flag
✓ Queries filter by is_simulation to prevent mixing
✓ Simulation state resets on start/stop
✓ No shared counters or state between modes
✓ Complete isolation guaranteed
```
