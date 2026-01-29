# 🚀 QUICK START GUIDE - Complete Enhanced System

## ✅ Project is Already Running!

**Backend:** http://localhost:8000  
**Frontend:** http://localhost:3000  
**Enhanced Dashboard:** http://localhost:3000/comprehensive

---

## 📊 How to Test the Complete System

### 1. Access the Enhanced Dashboard
```
Navigate to: http://localhost:3000/comprehensive
```

### 2. Start Enhanced Simulation
Click the button: **"🚀 Start Enhanced Simulation (200+ RPS)"**

**What Happens:**
- ✅ Generates 200+ requests per second
- ✅ Traffic sent to ALL 6 endpoints simultaneously
- ✅ Anomalies injected (30% rate) with proper types:
  - `/sim/payment` → TIMEOUT (CRITICAL)
  - `/sim/search` → LATENCY_SPIKE (HIGH)
  - `/sim/login` → ERROR_SPIKE (HIGH)
  - `/sim/profile` → TRAFFIC_BURST (MEDIUM)
  - `/sim/signup` → RESOURCE_EXHAUSTION (CRITICAL)
  - `/sim/logout` → LATENCY_SPIKE (LOW)

### 3. Watch Real-Time Updates

**Live Statistics (Top of page):**
- Total Requests (should reach 12,000+ in 60 seconds)
- Current RPS (should show 180-220)
- Anomalies Detected
- Anomalies Injected
- Detection Rate (should be 90%+)

**Graphs Update Automatically:**
1. **Risk Score Timeline** - Shows risk scores over time
2. **Anomalies by Endpoint** - Bar chart of anomaly counts
3. **Anomaly Type Distribution** - Pie chart of types
4. **Severity Distribution** - Pie chart CRITICAL/HIGH/MEDIUM/LOW
5. **Top Affected Endpoints** - Table with composite scores
6. **Resolution Suggestions** - Actionable fixes by severity

### 4. Verify Each Component

#### ✅ Simulation Engine
- Check console output in backend terminal
- Should see:
  ```
  🚀 ENHANCED SIMULATION STARTED
  ⚡ Batch: 200 reqs | Total: 200 | RPS: 200.0
  🚨 Anomaly Detected: /sim/payment | Type: timeout | Severity: CRITICAL
  ```

#### ✅ Anomaly Detection
- Each endpoint should have anomalies detected
- Check terminal for detection messages
- Verify anomaly types match endpoints

#### ✅ Real-Time Updates
- WebSocket connection indicator should be GREEN
- Graphs refresh every 30 seconds
- Stats update every 2 seconds during simulation

#### ✅ Resolution Suggestions
- Click through severity tabs (CRITICAL, HIGH, MEDIUM, LOW)
- Each should show unique, actionable suggestions
- No duplicate suggestions
- Should see 50+ total unique suggestions

### 5. API Endpoints to Test

```bash
# Get risk score timeline
curl http://localhost:8000/api/graphs/risk-score-timeline?hours=24

# Get anomalies by endpoint
curl http://localhost:8000/api/graphs/anomalies-by-endpoint?hours=24

# Get anomaly type distribution
curl http://localhost:8000/api/graphs/anomaly-type-distribution?hours=24

# Get severity distribution  
curl http://localhost:8000/api/graphs/severity-distribution?hours=24

# Get top affected endpoints
curl http://localhost:8000/api/graphs/top-affected-endpoints?limit=10&hours=24

# Get resolution suggestions
curl http://localhost:8000/api/graphs/resolution-suggestions?hours=24

# Start enhanced simulation
curl -X POST "http://localhost:8000/api/simulation/start-enhanced?duration_seconds=60&target_rps=200"

# Get simulation stats
curl http://localhost:8000/api/simulation/stats-enhanced

# Stop simulation
curl -X POST http://localhost:8000/api/simulation/stop-enhanced
```

---

## 🎯 Expected Results

### After 60-Second Simulation:

**Total Requests:** 12,000+ (200 RPS × 60 seconds)

**Per Endpoint (approximately):**
- `/sim/payment`: ~2,000 requests, ~600 anomalies
- `/sim/search`: ~2,000 requests, ~600 anomalies
- `/sim/login`: ~2,000 requests, ~600 anomalies
- `/sim/profile`: ~2,000 requests, ~600 anomalies
- `/sim/signup`: ~2,000 requests, ~600 anomalies
- `/sim/logout`: ~2,000 requests, ~600 anomalies

**Anomalies Detected:** Should detect ~3,000-3,600 anomalies (90%+ detection rate)

**Graphs Populated:**
- ✅ Risk Score Timeline: Should show spikes
- ✅ Anomalies by Endpoint: All 6 endpoints visible
- ✅ Anomaly Type Distribution: All 5 types present
- ✅ Severity Distribution: Mix of CRITICAL/HIGH/MEDIUM/LOW
- ✅ Top Affected Endpoints: Payment and Signup at top (CRITICAL severity)
- ✅ Resolution Suggestions: 50+ unique suggestions

---

## 🔍 Troubleshooting

### Frontend Not Loading?
```bash
cd frontend
npm run dev
```

### Backend Errors?
```bash
cd backend
..\..venv\Scripts\Activate.ps1
python app.py
```

### WebSocket Not Connecting?
- Check backend is running on port 8000
- Check browser console for errors
- Green dot should appear when connected

### No Graphs Showing?
- Start a simulation first to generate data
- Wait 10-20 seconds for detection
- Refresh page if needed

### Low RPS?
- System may be under load
- Close other applications
- Check Task Manager for CPU/Memory usage

---

## 📈 Performance Benchmarks

**System Specifications:**
- Minimum: 4GB RAM, Dual-core CPU
- Recommended: 8GB RAM, Quad-core CPU

**Expected Performance:**
- Simulation RPS: 180-220 (target: 200)
- Detection Latency: <100ms
- Graph Load Time: <2 seconds
- WebSocket Latency: <50ms

---

## 🎨 Dashboard Features

### Main Dashboard (/)
- Standard simulation controls
- Live/Simulation mode toggle
- Basic statistics
- Anomaly table

### Comprehensive Analytics (/comprehensive)
- **Enhanced simulation (200+ RPS)**
- **6 visualization graphs**
- **Real-time statistics**
- **Resolution suggestions**
- **Endpoint breakdown**
- **WebSocket updates**

### Endpoint Analytics (/analytics)
- Individual endpoint analysis
- Historical metrics
- Trend analysis

### Admin Panel (/admin)
- Natural language queries
- System administration
- Advanced controls

---

## 🏆 Success Criteria Checklist

Run through this checklist to verify everything works:

- [ ] Frontend loads at http://localhost:3000
- [ ] Backend responds at http://localhost:8000
- [ ] Enhanced dashboard accessible at /comprehensive
- [ ] Click "Start Enhanced Simulation" works
- [ ] Live stats update every 2 seconds
- [ ] RPS shows 180-220
- [ ] Total requests reaches 12,000+ after 60s
- [ ] All 6 endpoints show traffic
- [ ] Anomalies detected (3,000+)
- [ ] Risk Score Timeline graph shows data
- [ ] Anomalies by Endpoint graph shows all 6 endpoints
- [ ] Anomaly Type Distribution shows all 5 types
- [ ] Severity Distribution shows mix of levels
- [ ] Top Affected Endpoints table populated
- [ ] Resolution Suggestions show 50+ unique items
- [ ] Can switch between severity tabs
- [ ] WebSocket indicator is GREEN
- [ ] Endpoint Statistics section shows breakdown
- [ ] No duplicate anomalies in database
- [ ] Backend console shows detection messages
- [ ] Simulation completes successfully
- [ ] All graphs auto-refresh

---

## 🎯 Next Steps

1. **Try Different Simulations:**
   - Adjust duration (30s, 120s, etc.)
   - Modify target RPS (150, 250, 300)
   - Test multiple runs

2. **Explore Analytics:**
   - Check different time ranges (1h, 6h, 24h)
   - Filter by specific endpoints
   - Review resolution suggestions

3. **Test API Directly:**
   - Use curl or Postman
   - Test each graph endpoint
   - Verify JSON responses

4. **Monitor Performance:**
   - Watch CPU/Memory usage
   - Check detection accuracy
   - Measure response times

---

## 📝 Notes

- **Backend runs on:** Port 8000 (FastAPI + Uvicorn)
- **Frontend runs on:** Port 3000 (Vite + React)
- **Database:** SQLite (api_logs.db)
- **WebSocket:** Port 8000/ws
- **Auto-refresh:** Graphs update every 30 seconds
- **Detection interval:** Every 10 seconds during simulation

---

**Status:** ✅ SYSTEM FULLY OPERATIONAL  
**Last Updated:** January 29, 2026  
**Version:** Enhanced Comprehensive System v2.0
