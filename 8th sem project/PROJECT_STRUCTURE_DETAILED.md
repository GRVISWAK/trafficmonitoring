# 🏗️ Complete Project Structure - API Anomaly Detection System

## 📁 Directory Overview

```
8th sem project/
├── 📂 backend/                    # Python FastAPI Backend
│   ├── 🔴 app_enhanced.py         # ⭐ MAIN BACKEND SERVER (Enhanced ML + LIVE/SIMULATION modes)
│   ├── app.py                     # Basic backend (deprecated)
│   │
│   ├── 🤖 ML MODELS & TRAINING
│   │   ├── train_models_enhanced.py    # ⭐ ENHANCED ML PIPELINE - Trains 4 models
│   │   ├── train_models.py             # Basic training (deprecated)
│   │   ├── run_training.py             # Training execution script
│   │   ├── feature_engineering.py      # Feature extraction from requests
│   │   ├── inference_enhanced.py       # ⭐ ENHANCED INFERENCE ENGINE (Hybrid detection)
│   │   ├── inference.py                # Basic inference (deprecated)
│   │   └── run_detection.py            # Detection execution script
│   │
│   ├── 🎬 SIMULATION MODE
│   │   ├── traffic_simulator.py        # ⭐ ENDPOINT-SPECIFIC SIMULATOR
│   │   │                                 # - Generates synthetic API requests
│   │   │                                 # - Virtual endpoints: /sim/login, /sim/search, etc.
│   │   │                                 # - Anomaly injection: RATE_SPIKE, PAYLOAD_ABUSE, etc.
│   │   ├── demo_anomalies.py           # Pre-built anomaly scenarios
│   │   └── inject_anomaly.py           # Manual anomaly injection
│   │
│   ├── 🔌 MIDDLEWARE & WEBSOCKET
│   │   ├── middleware.py               # Basic request interceptor
│   │   ├── live_middleware.py          # ⭐ LIVE MODE MIDDLEWARE
│   │   │                                 # - Captures REAL API traffic
│   │   │                                 # - Sliding window (10 requests)
│   │   │                                 # - Triggers ML inference
│   │   │                                 # - Routes: /live/login, /live/payment, etc.
│   │   └── websocket.py                # ⭐ WEBSOCKET SERVER
│   │                                     # - Real-time anomaly broadcasting
│   │                                     # - Endpoint: ws://localhost:8000/ws
│   │                                     # - Sends detections to dashboard
│   │
│   ├── 💾 DATABASE & DATA
│   │   ├── database.py                 # SQLite database operations
│   │   ├── models.py                   # Database models (AnomalyDetection, Request)
│   │   ├── datasets_manager.py         # Dataset loading and management
│   │   ├── process_csic_dataset.py     # CSIC 2010 dataset processor
│   │   ├── process_csic_csv.py         # CSV export for CSIC data
│   │   └── export_datasets.py          # Dataset export utilities
│   │
│   ├── 🗂️ datasets/
│   │   ├── api_abuse_scenarios.json    # Synthetic attack patterns
│   │   ├── web_attack_payloads.json    # Web attack signatures
│   │   ├── csic_database.csv           # CSIC 2010 HTTP dataset
│   │   ├── DATASET_REPORT.txt          # Dataset statistics
│   │   └── processed/
│   │       ├── combined_training_data.csv    # ⭐ MERGED TRAINING DATA
│   │       ├── csic_features.csv             # CSIC extracted features
│   │       └── synthetic_api_traffic.csv     # Generated synthetic data
│   │
│   ├── 🧠 models/                      # ⭐ TRAINED ML MODELS (Saved here)
│   │   ├── isolation_forest_enhanced.pkl     # Unsupervised anomaly detector
│   │   ├── logistic_regression_enhanced.pkl  # Supervised classifier
│   │   ├── kmeans_enhanced.pkl               # Clustering-based detector
│   │   ├── scaler_enhanced.pkl               # Feature normalization
│   │   └── bot_cluster.txt                   # K-means cluster assignments
│   │
│   ├── 📜 BATCH FILES & SCRIPTS
│   │   ├── start_enhanced.bat          # Start enhanced backend
│   │   ├── start.bat                   # Start basic backend
│   │   ├── train.bat                   # Train models
│   │   ├── process_csic.bat            # Process CSIC dataset
│   │   ├── download_all_datasets.bat   # Download datasets
│   │   ├── view_datasets.bat           # View dataset stats
│   │   ├── export_datasets.bat         # Export datasets
│   │   └── window_manager.py           # Terminal window management
│   │
│   └── requirements.txt                # Python dependencies
│
├── 📂 frontend/                        # React + TypeScript Dashboard
│   ├── 🎨 src/
│   │   ├── 📄 pages/
│   │   │   ├── DashboardEnhanced.tsx   # ⭐ MAIN DASHBOARD
│   │   │   │                             # - LIVE/SIMULATION mode toggle
│   │   │   │                             # - Dual dropdowns (endpoint + anomaly)
│   │   │   │                             # - Real-time stats polling
│   │   │   │                             # - WebSocket anomaly streaming
│   │   │   ├── Analytics.tsx           # Analytics page
│   │   │   └── AdminPanel.tsx          # Admin controls
│   │   │
│   │   ├── 🧩 components/
│   │   │   ├── StatCard.tsx            # Metric display cards
│   │   │   ├── AnomalyTable.tsx        # Anomaly list table
│   │   │   └── Charts.tsx              # Data visualizations
│   │   │
│   │   ├── 🔌 hooks/
│   │   │   └── useWebSocket.ts         # ⭐ WEBSOCKET HOOK
│   │   │                                 # - Connects to ws://localhost:8000/ws
│   │   │                                 # - Receives real-time anomalies
│   │   │                                 # - Auto-reconnection logic
│   │   │
│   │   ├── 🌐 services/
│   │   │   └── api.ts                  # ⭐ REST API CLIENT
│   │   │                                 # - getStats(), getAnomalies()
│   │   │                                 # - startSimulation(), stopSimulation()
│   │   │                                 # - axios instance with base URL
│   │   │
│   │   ├── 📦 types/
│   │   │   └── index.ts                # TypeScript interfaces
│   │   │
│   │   ├── App.tsx                     # Root component
│   │   ├── main.tsx                    # Entry point
│   │   └── index.css                   # Global styles
│   │
│   ├── index.html                      # HTML template
│   ├── package.json                    # Node.js dependencies
│   ├── vite.config.ts                  # Vite bundler config
│   ├── tailwind.config.js              # TailwindCSS config
│   └── tsconfig.json                   # TypeScript config
│
├── 📚 DOCUMENTATION
│   ├── README.md                                   # Project overview
│   ├── PROJECT_COMPLETION_SUMMARY.txt              # Completion checklist
│   ├── QUICK_START_GUIDE.txt                       # Quick start instructions
│   ├── QUICK_REFERENCE_CARD.txt                    # Command reference
│   ├── ENHANCED_ML_PIPELINE_COMPLETE.txt           # ML pipeline details
│   ├── CSIC_DATASET_INTEGRATION_COMPLETE.txt       # Dataset integration guide
│   ├── DATASETS_QUICK_REFERENCE.txt                # Dataset info
│   ├── ENDPOINTS_TESTING_GUIDE.txt                 # API endpoint testing
│   ├── HOW_TO_ACCESS_DASHBOARD.txt                 # Dashboard access guide
│   ├── LIVE_SIMULATION_MODES_GUIDE.txt             # LIVE vs SIMULATION modes
│   └── PROJECT_STRUCTURE_DETAILED.md               # ⭐ THIS FILE
│
├── RUN_PROJECT.bat                     # ⭐ ONE-CLICK LAUNCHER (Backend + Frontend)
├── setup.bat                           # Windows setup script
└── setup.sh                            # Linux/Mac setup script
```

---

## 🤖 ML MODELS - Deep Dive

### 📍 Location: `backend/models/`

### 🧠 Model Files

| File | Type | Purpose | Input Features |
|------|------|---------|----------------|
| `isolation_forest_enhanced.pkl` | Unsupervised | Anomaly detection via isolation | 8 features |
| `logistic_regression_enhanced.pkl` | Supervised | Binary classification (normal/anomaly) | 8 features |
| `kmeans_enhanced.pkl` | Clustering | Behavior-based grouping | 8 features |
| `scaler_enhanced.pkl` | Preprocessing | MinMaxScaler for normalization | 8 features |
| `bot_cluster.txt` | Metadata | K-means cluster assignments | N/A |

### 🔬 Feature Engineering (8 Features)

**File:** `backend/feature_engineering.py`

```python
Features Extracted:
1. request_rate        # Requests per second in window
2. unique_endpoints    # Number of distinct endpoints hit
3. method_ratio        # POST/GET ratio
4. payload_size        # Average request body size
5. error_rate          # 4xx/5xx response ratio
6. param_repetition    # Duplicate parameter frequency
7. user_agent_entropy  # Shannon entropy of User-Agent
8. latency             # Average response time
```

### 🏋️ Training Pipeline

**File:** `backend/train_models_enhanced.py`

```
Flow:
1. Load datasets (CSIC + Synthetic + API logs)
2. Extract 8 features from raw HTTP requests
3. Normalize features (MinMaxScaler)
4. Train 4 models in parallel:
   - IsolationForest (contamination=0.1)
   - LogisticRegression (class_weight='balanced')
   - KMeans (n_clusters=3)
   - RuleBased (threshold-based heuristics)
5. Save models to backend/models/
6. Generate bot_cluster.txt metadata
```

**Command:** `python backend/train_models_enhanced.py`

### 🔍 Inference Engine

**File:** `backend/inference_enhanced.py`

```python
Hybrid Detection Strategy:
├── Rule-Based Layer (Fast)
│   ├── Request rate > 100/s → CRITICAL
│   ├── Payload size > 10MB → HIGH
│   ├── Error rate > 50% → MEDIUM
│   └── User-Agent entropy < 2.0 → LOW
│
└── ML Ensemble (Accurate)
    ├── IsolationForest → anomaly_score
    ├── LogisticRegression → probability
    ├── KMeans → cluster_distance
    └── Voting: If 2+ models flag → ANOMALY
```

**Decision Logic:**
- **CRITICAL:** Rule violations OR 3+ ML models agree
- **HIGH:** 2+ ML models agree
- **MEDIUM:** 1 ML model flags
- **NORMAL:** No flags

---

## 🎬 SIMULATION MODE - Deep Dive

### 📍 Files

| File | Location | Purpose |
|------|----------|---------|
| `traffic_simulator.py` | `backend/` | ⭐ Core simulator engine |
| `demo_anomalies.py` | `backend/` | Pre-built attack scenarios |
| `inject_anomaly.py` | `backend/` | Manual anomaly injection |
| `DashboardEnhanced.tsx` | `frontend/src/pages/` | UI controls |

### 🎯 Virtual Endpoints

**Defined in:** `backend/traffic_simulator.py`

```python
SIMULATED_ENDPOINTS = [
    '/sim/login',      # Authentication endpoint
    '/sim/search',     # Search functionality
    '/sim/profile',    # User profile access
    '/sim/payment',    # Payment processing
    '/sim/signup'      # User registration
]
```

**Note:** These endpoints DO NOT EXIST in the real API. They are synthetic routes created ONLY for simulation testing.

### 💥 Anomaly Types

| Type | Description | Attack Pattern |
|------|-------------|----------------|
| `RATE_SPIKE` | Sudden traffic burst | 500 requests in 5 seconds |
| `PAYLOAD_ABUSE` | Large request bodies | 15MB payloads |
| `ERROR_BURST` | Repeated 4xx/5xx errors | 80% error rate |
| `PARAM_REPETITION` | Identical parameters | Same key=value 20x |
| `ENDPOINT_FLOOD` | Single endpoint spam | 1000 requests to /sim/login |
| `NORMAL` | Benign traffic | Realistic patterns |

### 🔄 Simulation Flow

```
1. User selects endpoint + anomaly on Dashboard
   ↓
2. Frontend sends: POST /simulation/start?simulated_endpoint=/sim/login&anomaly_type=RATE_SPIKE
   ↓
3. Backend (traffic_simulator.py) starts background thread
   ↓
4. Generates synthetic HTTP requests every 100ms
   ↓
5. Requests flow through middleware (live_middleware.py)
   ↓
6. Sliding window accumulates 10 requests
   ↓
7. Trigger inference_enhanced.py for detection
   ↓
8. Anomalies sent via WebSocket to Dashboard
   ↓
9. Dashboard polls /simulation/stats every 2 seconds
   ↓
10. Simulation stops after 60 seconds (default)
```

### 📊 API Endpoints

**Backend:** `app_enhanced.py`

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/simulation/start` | Start simulation with query params |
| POST | `/simulation/stop` | Stop active simulation |
| GET | `/simulation/stats` | Get current simulation stats |
| POST | `/simulation/clear-history` | Reset detection history |

**Request Example:**
```bash
POST http://localhost:8000/simulation/start?simulated_endpoint=/sim/login&anomaly_type=RATE_SPIKE&duration=60&requests_per_window=10
```

**Response:**
```json
{
  "status": "started",
  "simulated_endpoint": "/sim/login",
  "anomaly_type": "RATE_SPIKE",
  "duration_seconds": 60,
  "requests_per_window": 10,
  "message": "Simulation started successfully"
}
```

---

## 🔌 MIDDLEWARE & WEBSOCKET - Deep Dive

### 🛡️ LIVE Mode Middleware

**File:** `backend/live_middleware.py`

```python
Purpose:
- Intercepts REAL API traffic on LIVE endpoints
- Applies sliding window logic (default: 10 requests)
- Extracts features and triggers ML inference
- Stores detections in SQLite database

LIVE Endpoints (Real API):
├── /live/login      → User authentication
├── /live/payment    → Payment processing
├── /live/search     → Search queries
└── /live/profile    → Profile access

Request Flow:
1. Client → POST /live/login (real traffic)
2. Middleware captures request metadata
3. Add to sliding window buffer
4. When window is full (10 requests):
   ├── Extract 8 features
   ├── Run inference_enhanced.py
   ├── Get anomaly prediction
   └── If anomaly detected:
       ├── Save to database
       ├── Broadcast via WebSocket
       └── Return response to client
```

**Key Code:**
```python
@app.post("/live/{endpoint_name}")
async def live_endpoint(endpoint_name: str, request: Request):
    # Capture request
    body = await request.body()
    request_data = {
        'endpoint': f'/live/{endpoint_name}',
        'method': request.method,
        'payload_size': len(body),
        'timestamp': time.time()
    }
    
    # Add to window
    window_manager.add_request(request_data)
    
    # Check if window is full
    if window_manager.is_full():
        features = extract_features(window_manager.get_window())
        prediction = inference_engine.predict(features)
        
        if prediction['is_anomaly']:
            # Save to DB
            database.save_anomaly(prediction)
            
            # Broadcast via WebSocket
            await websocket_manager.broadcast(prediction)
    
    return {"status": "ok", "endpoint": endpoint_name}
```

### 🌐 WebSocket Server

**File:** `backend/websocket.py`

```python
Purpose:
- Real-time bidirectional communication
- Pushes anomaly alerts to Dashboard
- Connection management with auto-reconnect

WebSocket Endpoint:
ws://localhost:8000/ws

Message Format (Server → Client):
{
  "type": "anomaly",
  "data": {
    "id": 123,
    "endpoint": "/live/login",
    "severity": "CRITICAL",
    "confidence": 0.95,
    "timestamp": "2025-12-29T19:00:00Z",
    "features": {...},
    "models_triggered": ["isolation_forest", "rule_based"]
  }
}

Connection States:
├── CONNECTING → Initial handshake
├── CONNECTED  → Active, can send/receive
├── DISCONNECTED → Lost connection, retrying
└── CLOSED → Manually closed
```

**Implementation:**
```python
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle client messages
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
```

### 🎯 Frontend WebSocket Hook

**File:** `frontend/src/hooks/useWebSocket.ts`

```typescript
Purpose:
- Connects to backend WebSocket
- Listens for anomaly broadcasts
- Auto-reconnects on disconnect
- Updates React state in real-time

Usage in Dashboard:
const { anomalies, connected } = useWebSocket();

Connection Logic:
1. Create WebSocket: new WebSocket('ws://localhost:8000/ws')
2. On message → Parse JSON → Add to anomalies state
3. On close → Retry after 3 seconds
4. On error → Log and attempt reconnect
5. Cleanup → Close socket on component unmount

Real-time Update Flow:
Backend detects anomaly 
  → websocket.broadcast(anomaly)
  → Frontend useWebSocket receives
  → Updates anomalies state
  → Dashboard re-renders
  → User sees alert instantly
```

**Code:**
```typescript
export const useWebSocket = () => {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.onopen = () => setConnected(true);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'anomaly') {
        setAnomalies(prev => [data.data, ...prev].slice(0, 100));
      }
    };
    
    ws.onclose = () => {
      setConnected(false);
      setTimeout(() => {
        // Reconnect after 3 seconds
      }, 3000);
    };
    
    return () => ws.close();
  }, []);

  return { anomalies, connected };
};
```

---

## 🔄 LIVE vs SIMULATION Mode Comparison

| Feature | LIVE Mode | SIMULATION Mode |
|---------|-----------|-----------------|
| **Traffic Source** | Real API requests | Synthetic generated requests |
| **Endpoints** | `/live/login`, `/live/payment`, etc. | `/sim/login`, `/sim/search`, etc. |
| **Purpose** | Monitor production traffic | Test detection without real data |
| **Middleware** | `live_middleware.py` | `traffic_simulator.py` |
| **Trigger** | User/application makes requests | Dashboard start button |
| **Data Flow** | External → API → Middleware → ML | Simulator → Middleware → ML |
| **Persistence** | Saved to database | Saved to database (isolated) |
| **WebSocket** | Yes, real-time alerts | Yes, real-time alerts |
| **Impact** | Affects real users | Isolated testing environment |
| **Dashboard Toggle** | "🎯 LIVE" button | "🎬 SIMULATION" button |

---

## 📡 Data Flow Architecture

### End-to-End Request Journey

#### LIVE Mode Flow
```
External User/App
    ↓
POST /live/login
    ↓
live_middleware.py
    ├── Capture: method, endpoint, payload, headers
    ├── Add to sliding window (10 requests)
    └── When window full:
        ↓
    feature_engineering.py
        ├── Extract 8 features
        └── Return feature vector [f1, f2, ..., f8]
            ↓
    inference_enhanced.py
        ├── Load 4 models
        ├── Run predictions
        └── Hybrid decision (Rule + ML)
            ↓
    If ANOMALY detected:
        ├── database.py → Save to SQLite
        ├── websocket.py → Broadcast to Dashboard
        └── Return flagged response
            ↓
    Dashboard (DashboardEnhanced.tsx)
        ├── useWebSocket hook receives alert
        ├── Update anomaly table
        └── Show toast notification
```

#### SIMULATION Mode Flow
```
Dashboard User
    ↓
Clicks "Start Simulation"
    ↓
POST /simulation/start?simulated_endpoint=/sim/login&anomaly_type=RATE_SPIKE
    ↓
app_enhanced.py
    ↓
traffic_simulator.py
    ├── Start background thread
    └── Generate synthetic requests:
        ├── Endpoint: /sim/login
        ├── Anomaly: RATE_SPIKE (500 req/s)
        └── Send to middleware every 100ms
            ↓
    live_middleware.py (same path as LIVE)
        ├── Cannot distinguish simulation from real traffic
        └── Process normally through sliding window
            ↓
    feature_engineering.py
        └── Extract features
            ↓
    inference_enhanced.py
        └── Detect anomaly
            ↓
    database.py + websocket.py
        └── Save and broadcast
            ↓
    Dashboard
        ├── Poll /simulation/stats every 2 seconds
        ├── Show: windows_processed, accuracy, endpoint, anomaly_type
        └── Display anomalies in real-time via WebSocket
```

---

## 🚀 Quick Start Commands

### Backend
```bash
# Start enhanced backend (LIVE + SIMULATION modes)
cd backend
python app_enhanced.py

# Train ML models
python train_models_enhanced.py

# Process CSIC dataset
python process_csic_dataset.py
```

### Frontend
```bash
# Start React dashboard
cd frontend
npm install
npm run dev

# Access at: http://localhost:3000
```

### All-in-One
```bash
# Run both backend + frontend
RUN_PROJECT.bat
```

---

## 🔑 Key Files Summary

### ⭐ MUST-KNOW FILES

| File | Role | Why Critical |
|------|------|--------------|
| `backend/app_enhanced.py` | Main server | FastAPI routes, mode switching |
| `backend/inference_enhanced.py` | ML brain | Hybrid detection logic |
| `backend/live_middleware.py` | Traffic interceptor | Captures LIVE requests |
| `backend/traffic_simulator.py` | Anomaly generator | Creates SIMULATION traffic |
| `backend/websocket.py` | Real-time comms | Pushes alerts to frontend |
| `frontend/src/pages/DashboardEnhanced.tsx` | UI controller | Mode toggle, simulation controls |
| `frontend/src/hooks/useWebSocket.ts` | WebSocket client | Receives real-time alerts |
| `backend/models/*.pkl` | Trained models | 4 ML models for detection |

---

## 🎯 How to Test Simulation

### Step-by-Step

1. **Start Backend**
   ```bash
   cd backend
   python app_enhanced.py
   ```

2. **Start Frontend**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open Dashboard**
   - Navigate to `http://localhost:3000`

4. **Switch to SIMULATION Mode**
   - Click "🎬 SIMULATION" button (top of dashboard)

5. **Configure Simulation**
   - **Virtual Endpoint:** Select `/sim/login`
   - **Anomaly Type:** Select `RATE_SPIKE`

6. **Start Simulation**
   - Click "▶️ Start Simulation" button

7. **Observe Real-Time Updates**
   - Stats panel updates every 2 seconds
   - Anomaly table shows detections
   - Toast notifications for events

8. **Monitor Backend Console**
   ```
   INFO:     Simulation started: /sim/login + RATE_SPIKE
   INFO:     Generated 100 requests
   INFO:     Windows processed: 10
   INFO:     Anomalies detected: 10 (100% accuracy)
   ```

9. **Check Database**
   ```bash
   # View saved anomalies
   python backend/database.py
   ```

---

## 🛠️ Troubleshooting

### Simulation Not Starting
1. **Check backend logs** - Look for errors in terminal
2. **Verify endpoint format** - Must be `/sim/login` (with slash)
3. **Check anomaly type** - Must be uppercase: `RATE_SPIKE`
4. **Clear browser cache** - Force refresh: Ctrl+Shift+R

### No WebSocket Connection
1. **Check backend running** - `http://localhost:8000/health`
2. **Verify WebSocket port** - Should be same as backend (8000)
3. **Check browser console** - Look for WS connection errors
4. **Firewall/antivirus** - May block WebSocket connections

### Models Not Loading
1. **Train models first** - `python backend/train_models_enhanced.py`
2. **Check file paths** - Models should be in `backend/models/`
3. **Verify model files** - Should have `.pkl` extension

---

## 📊 Database Schema

**File:** `backend/database.py`

```sql
CREATE TABLE anomaly_detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    endpoint TEXT NOT NULL,
    severity TEXT,  -- CRITICAL, HIGH, MEDIUM, LOW
    confidence REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    features TEXT,  -- JSON serialized
    models_triggered TEXT,  -- Comma-separated
    mode TEXT  -- LIVE or SIMULATION
);

CREATE TABLE requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    endpoint TEXT,
    method TEXT,
    payload_size INTEGER,
    status_code INTEGER,
    timestamp DATETIME,
    mode TEXT
);
```

---

## 🎓 Project Architecture Summary

This system implements a **Hybrid ML-based API Anomaly Detection** platform with:

1. **Dual Operating Modes**
   - LIVE: Real-time production monitoring
   - SIMULATION: Controlled testing environment

2. **4-Model ML Ensemble**
   - IsolationForest (unsupervised)
   - LogisticRegression (supervised)
   - KMeans (clustering)
   - RuleBased (heuristics)

3. **Real-Time Communication**
   - WebSocket for instant alerts
   - REST API for data retrieval
   - Polling for simulation stats

4. **Feature Engineering**
   - 8 extracted features from HTTP requests
   - Sliding window aggregation (10 requests)
   - MinMax normalization

5. **Interactive Dashboard**
   - Mode switching (LIVE/SIMULATION)
   - Endpoint-specific simulation controls
   - Real-time anomaly visualization
   - Stats monitoring

---

**Last Updated:** December 29, 2025  
**Version:** 2.0 Enhanced  
**Status:** Production Ready ✅
