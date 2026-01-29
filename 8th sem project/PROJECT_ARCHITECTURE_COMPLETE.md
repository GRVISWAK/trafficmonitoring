# 📊 PROJECT STRUCTURE & COMPONENT GUIDE

## 🏗️ Complete Project Architecture

```
8th sem project/
│
├── 📁 frontend/                          # React + TypeScript Frontend
│   ├── src/
│   │   ├── pages/
│   │   │   └── DashboardEnhanced.tsx    ⭐ MAIN DASHBOARD (LIVE + SIMULATION)
│   │   ├── components/
│   │   │   ├── StatCard.tsx             # Metric display cards
│   │   │   ├── AnomalyTable.tsx         # Anomaly detection table
│   │   │   ├── Charts.tsx               # Risk/endpoint charts
│   │   │   └── EndpointAnomalyChart.tsx ⭐ NEW: Endpoint analysis charts
│   │   ├── hooks/
│   │   │   └── useWebSocket.ts          ⭐ WEBSOCKET: Real-time updates
│   │   ├── services/
│   │   │   └── api.ts                   # Backend API client
│   │   └── types/
│   │       └── index.ts                 # TypeScript interfaces
│   └── package.json                     # Dependencies
│
├── 📁 backend/                           # FastAPI Python Backend
│   ├── app_enhanced.py                  ⭐ MAIN API SERVER (Port 8000)
│   ├── models.py                        ⭐ ML MODELS: Isolation Forest, K-Means, Logistic Regression
│   ├── inference_enhanced.py            ⭐ ML INFERENCE: Hybrid detection engine
│   ├── simulation_manager_v2.py         ⭐ SIMULATION: Endpoint-specific traffic generator
│   ├── traffic_simulator.py             ⭐ SIMULATION: Anomaly injection logic
│   ├── middleware.py                    # Request interception (LIVE mode)
│   ├── live_middleware.py               ⭐ MIDDLEWARE: Sliding window manager (LIVE)
│   ├── websocket.py                     ⭐ WEBSOCKET: Real-time broadcast
│   ├── window_manager.py                ⭐ SLIDING WINDOW: Request aggregation
│   ├── database.py                      # SQLAlchemy models
│   ├── feature_engineering.py           # 9 behavioral features
│   └── requirements.txt                 # Python dependencies
│
└── 📁 datasets/                          # Training data
    ├── csic_database.csv                # CSIC 2010 HTTP dataset
    ├── processed/
    │   ├── combined_training_data.csv   # Merged dataset
    │   └── csic_features.csv            # Extracted features
    └── api_abuse_scenarios.json         # Custom scenarios
```

---

## 🎯 COMPONENT RESPONSIBILITIES

### **Frontend Components**

#### 1️⃣ `DashboardEnhanced.tsx` ⭐ CENTRAL HUB
**Purpose:** Main dashboard with dual-mode support (LIVE + SIMULATION)  
**Features:**
- Toggle between LIVE and SIMULATION modes
- Virtual endpoint selector (5 endpoints)
- Anomaly type selector (6 types)
- Real-time statistics display
- Simulation controls (start/stop)
- WebSocket integration for live updates

**Key State:**
```typescript
- detectionMode: 'live' | 'simulation'
- simulatedEndpoint: '/sim/login' | '/sim/search' | '/sim/profile' | '/sim/payment' | '/sim/signup'
- anomalyType: 'RATE_SPIKE' | 'PAYLOAD_ABUSE' | 'ERROR_BURST' | 'PARAM_REPETITION' | 'ENDPOINT_FLOOD' | 'NORMAL'
- simulationActive: boolean
```

#### 2️⃣ `EndpointAnomalyChart.tsx` ⭐ NEW VISUALIZATION
**Purpose:** Display endpoint-specific anomaly analysis  
**Features:**
- Anomalies by virtual endpoint (bar chart)
- Risk score timeline (line chart)
- Anomaly type distribution (bar chart)
- Top risk endpoints ranking
- Auto-refresh every 3 seconds during simulation

#### 3️⃣ `useWebSocket.ts` ⭐ REAL-TIME CONNECTION
**Purpose:** Maintain WebSocket connection to backend  
**Features:**
- Auto-reconnect on disconnect
- Real-time anomaly notifications
- Toast notifications for high-risk anomalies (>0.8)

---

### **Backend Components**

#### 1️⃣ `app_enhanced.py` ⭐ MAIN API SERVER
**Port:** 8000  
**Endpoints:**

**LIVE MODE (Real endpoints):**
- `POST /login` - User authentication
- `POST /signup` - User registration
- `GET /search` - Search queries
- `GET /profile` - User profile
- `POST /payment` - Payment processing
- `POST /logout` - Session termination

**SIMULATION MODE (Virtual endpoints):**
- `POST /simulation/start` - Start endpoint-specific simulation
- `POST /simulation/stop` - Stop simulation
- `GET /simulation/stats` - Get current simulation statistics
- `GET /simulation/anomaly-history` ⭐ NEW: Get anomaly history with charts
- `POST /simulation/clear-history` - Clear anomaly history

**COMMON:**
- `GET /api/anomalies` - Fetch detected anomalies
- `GET /live/stats` - Get LIVE mode statistics
- `WS /ws` - WebSocket connection

#### 2️⃣ `models.py` ⭐ ML MODELS
**Models Trained:**
1. **Isolation Forest** - Anomaly detection (outlier identification)
2. **K-Means Clustering** - Behavioral clustering (3 clusters)
3. **Logistic Regression** - Binary classification (normal vs anomaly)
4. **Failure Predictor** - Proactive failure prediction

**Features Used (9 total):**
```python
1. request_rate          # Requests per second
2. unique_endpoint_count # Distinct endpoints accessed
3. method_ratio          # GET vs POST ratio
4. avg_payload_size      # Average request size
5. error_rate            # HTTP errors (4xx/5xx)
6. repeated_parameter_ratio # Bot detection (repeated params)
7. user_agent_entropy    # Agent diversity
8. avg_response_time     # Average latency
9. max_response_time     # Peak latency
```

#### 3️⃣ `inference_enhanced.py` ⭐ HYBRID DETECTION ENGINE
**Purpose:** Run ensemble ML inference  
**Process:**
1. Receive 9 features from sliding window
2. Run Isolation Forest (anomaly score)
3. Run K-Means (cluster assignment + distance)
4. Run Logistic Regression (probability)
5. Run Failure Predictor (failure probability)
6. Calculate weighted risk score
7. Determine priority (CRITICAL/HIGH/MEDIUM/LOW)
8. Return detection result

**Risk Score Calculation:**
```python
risk_score = (
    anomaly_score * 0.35 +
    failure_prob * 0.30 +
    cluster_distance * 0.20 +
    rule_violations * 0.15
)
```

#### 4️⃣ `simulation_manager_v2.py` ⭐ ENDPOINT-SPECIFIC SIMULATOR
**Purpose:** Generate synthetic traffic for virtual endpoints  
**Virtual Endpoints (Simulation only):**
- `/sim/login`
- `/sim/search`
- `/sim/profile`
- `/sim/payment`
- `/sim/signup`

**Anomaly Types:**
1. **RATE_SPIKE** - DDoS simulation (5x traffic, 500 req/burst)
2. **PAYLOAD_ABUSE** - Large payloads (10KB-50KB)
3. **ERROR_BURST** - High error rate (80% errors)
4. **PARAM_REPETITION** - Bot patterns (repeated params)
5. **ENDPOINT_FLOOD** - Endpoint flooding (10x traffic)
6. **NORMAL** - Baseline traffic

**History Tracking:**
- Stores up to 1000 detections
- Calculates per-endpoint statistics
- Tracks anomaly type distribution
- Maintains emergency rankings

#### 5️⃣ `live_middleware.py` ⭐ SLIDING WINDOW MANAGER
**Purpose:** Aggregate requests into time windows for LIVE mode  
**Configuration:**
- Window size: 10 requests
- Sliding window approach
- Real endpoint tracking only
- Blacklisted endpoints: /health, /ws, /static

**Process:**
1. Intercept incoming HTTP request
2. Extract features (method, path, status, latency, payload)
3. Add to sliding window
4. When window full (10 requests):
   - Calculate 9 aggregate features
   - Trigger ML inference
   - Broadcast result via WebSocket
   - Store in database

#### 6️⃣ `websocket.py` ⭐ REAL-TIME BROADCAST
**Purpose:** Push anomaly detections to frontend  
**Events:**
- New anomaly detected
- Simulation started/stopped
- High-risk alerts (risk_score >= 0.8)

---

## 🔥 RISK SCORE GENERATION

### **Backend (inference_enhanced.py)**
```python
def calculate_risk_score(anomaly_score, failure_prob, cluster_distance):
    """
    Weighted ensemble risk calculation
    
    Components:
    - anomaly_score: Isolation Forest outlier score (0-1)
    - failure_prob: Logistic Regression probability (0-1)
    - cluster_distance: K-Means distance to cluster center (normalized)
    - rule_violations: Rule-based detections (e.g., rate >15, errors >50%)
    
    Formula:
    risk = (anomaly * 0.35) + (failure * 0.30) + (distance * 0.20) + (rules * 0.15)
    """
    risk_score = (anomaly_score * 0.35 + 
                  failure_prob * 0.30 + 
                  cluster_distance * 0.20)
    
    # Priority mapping
    if risk_score >= 0.8: priority = 'CRITICAL'
    elif risk_score >= 0.6: priority = 'HIGH'
    elif risk_score >= 0.4: priority = 'MEDIUM'
    else: priority = 'LOW'
    
    return risk_score, priority
```

### **Frontend Display**
- Timeline chart shows risk evolution
- Color coding: Red (>0.8), Orange (0.6-0.8), Yellow (0.4-0.6), Green (<0.4)
- Toast alerts for CRITICAL risks
- Top risk endpoint ranking

---

## 🌊 TRAFFIC SPIKE INJECTION

### **Enhanced Rate Spike (5x Amplification)**
```python
def _generate_rate_spike(endpoint, count):
    """
    Generate 5x more requests than normal to simulate DDoS attack
    
    Original: 10 requests
    Enhanced: 50 requests (500 requests in heavy mode)
    
    Characteristics:
    - Extremely fast latency (1-20ms)
    - High error rate (503 Service Unavailable)
    - Tiny payloads (20-100 bytes)
    - Burst waves (grouped by 100)
    """
```

### **Enhanced Endpoint Flood (10x Amplification)**
```python
def _generate_endpoint_flood(endpoint, count):
    """
    Generate 10x more requests to single endpoint
    
    Original: 10 requests
    Enhanced: 100 requests (1000 requests in extreme mode)
    
    Characteristics:
    - Single endpoint hammering
    - Ultra-fast requests (1-15ms)
    - Flood waves (grouped by 50)
    """
```

---

## 📜 ANOMALY HISTORY STORAGE

### **Backend Endpoint**
`GET /simulation/anomaly-history?limit=100`

**Response Structure:**
```json
{
  "history": [
    {
      "id": 1,
      "timestamp": "2025-12-29T10:30:45",
      "endpoint": "/sim/login",
      "anomaly_type": "RATE_SPIKE",
      "detected_type": "ISOLATION_FOREST+RULE",
      "risk_score": 0.8542,
      "priority": "CRITICAL",
      "method": "POST",
      "window_id": 123,
      "emergency_rank": 1,
      "is_correctly_detected": true
    }
  ],
  "endpoint_breakdown": [
    {
      "endpoint": "/sim/login",
      "count": 45,
      "avg_risk": 0.7234,
      "max_risk": 0.9123,
      "anomaly_types": {
        "RATE_SPIKE": 30,
        "PAYLOAD_ABUSE": 15
      }
    }
  ],
  "risk_timeline": [...],  // Last 50 for chart
  "anomaly_type_distribution": {
    "RATE_SPIKE": 120,
    "PAYLOAD_ABUSE": 45,
    "ERROR_BURST": 30
  },
  "total_anomalies": 195
}
```

### **Storage Implementation**
- `EndpointSpecificHistoryManager` class (simulation_manager_v2.py)
- In-memory deque with max 1000 records
- Auto-ranking by risk score
- Per-endpoint statistics aggregation

---

## 📊 ENDPOINT CHART DISPLAY

### **Charts Rendered (EndpointAnomalyChart.tsx)**

#### 1. Anomalies by Virtual Endpoint (Bar Chart)
- X-axis: Endpoint names
- Y-axis: Count + Average Risk Score
- Data: Per-endpoint anomaly statistics

#### 2. Risk Score Timeline (Line Chart)
- X-axis: Timestamp
- Y-axis: Risk Score (0-1)
- Shows last 50 detections
- Color-coded by priority

#### 3. Anomaly Type Distribution (Bar Chart)
- X-axis: Anomaly types
- Y-axis: Detection count
- Color-coded by type

#### 4. Top Risk Endpoints (Ranked List)
- Sorted by maximum risk score
- Shows endpoint, count, max risk
- Top 5 displayed

---

## 🚀 HOW TO RUN

### **Start Backend**
```bash
cd backend
python app_enhanced.py
# Backend runs on http://localhost:8000
```

### **Start Frontend**
```bash
cd frontend
npm install
npm run dev
# Frontend runs on http://localhost:3000
```

### **Test Simulation**
1. Open http://localhost:3000
2. Toggle to "🎬 SIMULATION" mode
3. Select endpoint (e.g., `/sim/login`)
4. Select anomaly type (e.g., `RATE_SPIKE`)
5. Click "▶️ Start Simulation"
6. Watch real-time charts update
7. View anomaly history in charts below

---

## 🔐 SECURITY NOTE

**IMPORTANT:** Virtual endpoints (`/sim/*`) are SIMULATION ONLY and do NOT affect real API routes. Simulation mode runs completely isolated from LIVE mode to prevent cross-contamination.

---

## 📞 COMPONENT COMMUNICATION FLOW

```
Frontend (Dashboard)
    ↓ HTTP POST
Backend (/simulation/start)
    ↓ Triggers
Traffic Simulator (Generates 500 requests for RATE_SPIKE)
    ↓ Processes
Window Manager (Aggregates to 10-request windows)
    ↓ Triggers
ML Inference Engine (Runs 4 models, calculates risk score)
    ↓ Stores
History Manager (Tracks in-memory deque)
    ↓ Broadcasts
WebSocket (Sends to frontend)
    ↓ Displays
Dashboard + Charts (Real-time updates)
    ↓ User queries
Backend (/simulation/anomaly-history)
    ↓ Returns
Chart Data (Endpoint breakdown, risk timeline, type distribution)
    ↓ Renders
EndpointAnomalyChart Component
```

---

**Created:** December 29, 2025  
**Project:** 8th Semester - Predictive API Misuse & Failure Prediction System  
**Version:** 2.0.0 Enhanced
