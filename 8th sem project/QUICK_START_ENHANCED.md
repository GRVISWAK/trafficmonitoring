# 🎯 QUICK START GUIDE - Enhanced Simulation System

## 🚀 START SYSTEM (2 Steps)

### Step 1: Start Backend
```bash
cd "C:\Users\HP\Desktop\8th sem project"
.\.venv\Scripts\python.exe .\backend\app_enhanced.py
```
✅ Backend runs on http://localhost:8000

### Step 2: Start Frontend
```bash
cd "C:\Users\HP\Desktop\8th sem project\frontend"
npm run dev
```
✅ Frontend runs on http://localhost:3000

---

## 🎬 RUN SIMULATION (4 Clicks)

1. Open http://localhost:3000
2. Click **"🎬 SIMULATION"** toggle button (top left)
3. Select:
   - **Virtual Endpoint:** `/sim/login` (or any `/sim/*` endpoint)
   - **Anomaly Type:** `RATE_SPIKE` (for heavy traffic spike)
4. Click **"▶️ Start Simulation"**

**Result:**
- Generates **2,500+ requests** in burst mode
- Detects **2,491 anomalies**
- Charts update every 3 seconds
- History stores up to 1000 records

---

## 📊 VIEW CHARTS (Scroll Down)

After starting simulation, scroll down to see:

### 1️⃣ **Anomalies by Virtual Endpoint** (Bar Chart)
- Shows count per endpoint
- Displays average risk score

### 2️⃣ **Risk Score Timeline** (Line Chart)
- X-axis: Time
- Y-axis: Risk (0-1)
- Last 50 detections

### 3️⃣ **Anomaly Type Distribution** (Bar Chart)
- RATE_SPIKE, PAYLOAD_ABUSE, ERROR_BURST, etc.
- Color-coded by type

### 4️⃣ **Top Risk Endpoints** (Ranked List)
- Top 5 by max risk score
- Shows count, avg/max risk

---

## 🔥 ANOMALY TYPES

Choose from 6 types:

| Type | Description | Traffic Volume |
|------|-------------|----------------|
| **RATE_SPIKE** 🚀 | DDoS simulation | **500 req** (5x normal) |
| **ENDPOINT_FLOOD** 🌊 | Single endpoint flooding | **1000 req** (10x normal) |
| **PAYLOAD_ABUSE** 📦 | Large payloads (10KB-50KB) | Normal |
| **ERROR_BURST** 💥 | High error rate (80%) | Normal |
| **PARAM_REPETITION** 🤖 | Bot patterns | Normal |
| **NORMAL** ✅ | Baseline traffic | Normal |

**Recommended for Heavy Traffic:** RATE_SPIKE or ENDPOINT_FLOOD

---

## 🎯 VIRTUAL ENDPOINTS (Simulation Only)

| Endpoint | Icon | Use Case |
|----------|------|----------|
| `/sim/login` | 🔐 | Authentication |
| `/sim/search` | 🔍 | Search queries |
| `/sim/profile` | 👤 | User profiles |
| `/sim/payment` | 💳 | Payments |
| `/sim/signup` | 📝 | Registration |

**Note:** These are **SIMULATION ONLY** - not real API routes

---

## 📈 REAL-TIME FEATURES

✅ **Auto-Refresh:** Charts update every 3 seconds  
✅ **WebSocket:** Live anomaly notifications  
✅ **Toast Alerts:** High-risk warnings (risk >0.8)  
✅ **Status Panel:** Shows active simulation state

---

## 🧪 TEST API DIRECTLY

### Start Simulation (CURL)
```bash
curl -X POST "http://localhost:8000/simulation/start?simulated_endpoint=/sim/login&anomaly_type=RATE_SPIKE&duration=30&requests_per_window=100"
```

### Get Anomaly History
```bash
curl "http://localhost:8000/simulation/anomaly-history?limit=100"
```

### Get Statistics
```bash
curl "http://localhost:8000/simulation/stats"
```

### Stop Simulation
```bash
curl -X POST "http://localhost:8000/simulation/stop"
```

---

## 📊 RISK SCORE GUIDE

| Risk Score | Priority | Color | Meaning |
|------------|----------|-------|---------|
| **0.8 - 1.0** | CRITICAL | 🔴 Red | Severe threat |
| **0.6 - 0.8** | HIGH | 🟠 Orange | High risk |
| **0.4 - 0.6** | MEDIUM | 🟡 Yellow | Moderate |
| **0.0 - 0.4** | LOW | 🟢 Green | Minor/Normal |

**Calculation:**
```
risk = (anomaly_score × 0.35) + 
       (failure_prob × 0.30) + 
       (cluster_distance × 0.20) + 
       (rule_violations × 0.15)
```

---

## 🔧 TROUBLESHOOTING

### ❌ "Failed to start simulation"
**Solution:**
1. Check backend is running (http://localhost:8000/health)
2. Restart backend: `python backend/app_enhanced.py`
3. Clear browser cache
4. Try again

### ❌ "Charts not updating"
**Solution:**
1. Ensure SIMULATION mode is selected
2. Wait 3 seconds for auto-refresh
3. Check browser console for errors
4. Verify anomaly history endpoint: `curl http://localhost:8000/simulation/anomaly-history`

### ❌ "No anomalies detected"
**Solution:**
1. Use RATE_SPIKE or ENDPOINT_FLOOD for visible results
2. Increase `requests_per_window` to 100+
3. Wait longer (20+ seconds duration)

---

## 📁 KEY FILES

### Frontend
- **Dashboard:** `frontend/src/pages/DashboardEnhanced.tsx`
- **Charts:** `frontend/src/components/EndpointAnomalyChart.tsx`
- **WebSocket:** `frontend/src/hooks/useWebSocket.ts`

### Backend
- **API Server:** `backend/app_enhanced.py`
- **Simulation:** `backend/simulation_manager_v2.py`
- **ML Models:** `backend/inference_enhanced.py`
- **Middleware:** `backend/live_middleware.py`

---

## 🎓 PROJECT INFO

**Title:** Predictive API Misuse & Failure Prediction System  
**Version:** 2.0.0 Enhanced  
**Date:** December 29, 2025  

**Features:**
- ✅ LIVE mode (real endpoints)
- ✅ SIMULATION mode (virtual endpoints)
- ✅ Heavy traffic spikes (2,500+ req/burst)
- ✅ 4 ML models (Isolation Forest, K-Means, Logistic, Failure Predictor)
- ✅ 9 behavioral features
- ✅ Real-time WebSocket updates
- ✅ 4 chart types for endpoint analysis
- ✅ Risk score generation
- ✅ Anomaly history storage (1,000 records)

---

## 📞 QUICK COMMANDS

### PowerShell (Windows)
```powershell
# Start backend
cd "C:\Users\HP\Desktop\8th sem project"
.\.venv\Scripts\python.exe .\backend\app_enhanced.py

# Start frontend (new window)
cd "C:\Users\HP\Desktop\8th sem project\frontend"
npm run dev

# Test simulation
curl -X POST "http://localhost:8000/simulation/start?simulated_endpoint=/sim/login&anomaly_type=RATE_SPIKE&duration=20&requests_per_window=100"

# Check stats
curl "http://localhost:8000/simulation/stats"

# Get anomaly history
curl "http://localhost:8000/simulation/anomaly-history?limit=100"
```

---

## ✅ CHECKLIST

Before demonstration:
- [ ] Backend running (port 8000)
- [ ] Frontend running (port 3000)
- [ ] Browser opened to http://localhost:3000
- [ ] SIMULATION mode selected
- [ ] Endpoint selected (e.g., /sim/login)
- [ ] Anomaly type selected (e.g., RATE_SPIKE)
- [ ] Ready to click "Start Simulation"

---

**🎉 YOUR SYSTEM IS READY!**

Open http://localhost:3000 and start simulating heavy traffic spikes!
