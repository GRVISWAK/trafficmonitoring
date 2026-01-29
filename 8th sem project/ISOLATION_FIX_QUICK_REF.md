# ISOLATION FIX - QUICK REFERENCE

## What Was Fixed

**PROBLEM:** Simulation traffic was contaminating live mode - request counts, dashboard stats, and ML model training were all mixing live and simulation data together.

**SOLUTION:** Complete separation implemented with `is_simulation` database column and separate tracking.

## Key Changes

### 1. Database Schema ✅
- Added `is_simulation` column to `api_logs` table
- Added `is_simulation` column to `anomaly_logs` table  
- All existing data defaults to `is_simulation=False` (live mode)

### 2. Live Mode Tracking ✅
- `live_mode_stats` global variable tracks ONLY real endpoint hits
- Middleware logs all real requests with `is_simulation=False`
- Dashboard filters to show ONLY live data: `WHERE is_simulation=False`

### 3. Simulation Mode Tracking ✅
- `simulation_stats` global variable tracks ONLY synthetic traffic
- Simulation writes logs with `is_simulation=True`
- Uses `SIM-{number}` IP addresses instead of `192.168.1.x`
- Separate endpoint `/simulation/anomaly-history` for simulation data

### 4. ML Model Training ✅
- `extract_features_from_logs(is_simulation=False)` for live mode
- `extract_features_from_logs(is_simulation=True)` for simulation mode
- **NEVER trains on mixed data**

## How to Verify It Works

### Test 1: Check Live Counter
1. Open Dashboard at http://localhost:3000
2. Note the "Total API Calls" count
3. Go to http://localhost:8000/docs (Swagger)
4. Hit `/login` endpoint (POST with {"username":"test", "password":"test123"})
5. Refresh Dashboard
6. **Expected:** Counter increases by 1

### Test 2: Check Simulation Isolation
1. Dashboard shows current live count (e.g., 50 requests)
2. Click "Start Simulation" for any endpoint
3. Let it run for 10 seconds (generates 100+ requests)
4. Check Dashboard live count
5. **Expected:** Live count UNCHANGED (still 50)

### Test 3: Run Automated Tests
```bash
cd backend
python test_live_simulation_isolation.py
```
**Expected:** All 4 tests PASS

## Backend Logs

Watch for these prefixes:
- `[LIVE] Request #X: POST /login` → Real endpoint hit
- `[SIM] Generated request #X for /payment` → Simulation traffic

## API Endpoints

### Live Mode (Real Traffic Only)
- `/api/dashboard` → Live stats with `"mode": "LIVE"`
- `/api/stats` → Live metrics only
- `/api/logs` → Live request logs
- `/api/anomalies` → Live anomalies only
- `/api/analytics/endpoint/{endpoint}` → Live endpoint data

### Simulation Mode (Synthetic Traffic Only)
- `/simulation/stats` → Simulation counters
- `/simulation/anomaly-history` → Simulation anomalies
- `/simulation/start` → Start generating traffic
- `/simulation/stop` → Stop traffic generation

## Database Queries

**Before Fix (BROKEN):**
```sql
SELECT COUNT(*) FROM api_logs;  -- Returns BOTH live and simulation
```

**After Fix (WORKING):**
```sql
-- Live mode
SELECT COUNT(*) FROM api_logs WHERE is_simulation=0;

-- Simulation mode  
SELECT COUNT(*) FROM api_logs WHERE is_simulation=1;
```

## Files Modified

1. `backend/database.py` - Added is_simulation columns
2. `backend/middleware.py` - Tracks live requests with is_simulation=False
3. `backend/app.py` - Separated stats, filtered all queries
4. `backend/feature_engineering.py` - Mode-aware feature extraction
5. `backend/models.py` - Added is_simulation to response models

## Files Created

1. `backend/migrate_add_simulation_flag.py` - Database migration
2. `backend/test_live_simulation_isolation.py` - Verification tests
3. `LIVE_SIMULATION_ISOLATION_FIX.md` - Full documentation

## Troubleshooting

### Issue: Live counter not increasing
**Check:** Are you hitting real endpoints through Swagger or UI?
**Note:** /api/, /simulation/, /ws, /docs endpoints are excluded

### Issue: Simulation shows 0 requests
**Check:** Did you click "Start Simulation" button?
**Note:** Simulation must be manually started for each endpoint

### Issue: Dashboard shows wrong data
**Check:** Clear browser cache and hard refresh (Ctrl+Shift+R)
**Note:** Backend restart required if migration wasn't run

## Migration Already Applied

The database migration has been executed automatically. All existing records are marked as `is_simulation=False` (live mode).

If you need to rerun migration:
```bash
cd backend
python migrate_add_simulation_flag.py
```

## Summary

**Live Mode:**
- Only counts REAL endpoint hits
- Dashboard shows ONLY live traffic
- ML models train on PURE live data
- WebSocket updates for live anomalies

**Simulation Mode:**
- Completely isolated from live mode
- Generates 100+ req/sec synthetic traffic  
- Separate counters and stats
- NEVER affects live mode

**Guaranteed:** No contamination between live and simulation modes.
