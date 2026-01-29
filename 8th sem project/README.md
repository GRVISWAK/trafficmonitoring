# Predictive API Misuse and Failure Prediction System

A production-grade ML-powered system for real-time API monitoring, anomaly detection, and failure prediction.

**🎓 FOR MENTOR/VIVA DEMONSTRATION**: See [Dataset Documentation](#-dataset-documentation) below

## Tech Stack

### Backend
- **Python 3.9+**
- **FastAPI** - High-performance web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL/SQLite** - Database
- **WebSockets** - Real-time communication
- **Scikit-learn** - Machine learning models
- **Pandas/NumPy** - Data processing

### Frontend
- **React 18** with TypeScript
- **Tailwind CSS** - Dark theme UI
- **Recharts** - Data visualization
- **Axios** - HTTP client
- **React Router** - Navigation
- **React Hot Toast** - Notifications

## 📊 Dataset Documentation (For Mentors/Reviewers)

### Training Data Sources:
1. **Combined Training Dataset**: 1000+ samples
2. **CSIC 2010 HTTP Dataset**: Web application attack patterns (attempted, fallback to synthetic)
3. **Web Attack Payload Database**: 47+ attack patterns
   - SQL Injection, XSS, Path Traversal, Command Injection, LDAP Injection, XML Injection
4. **OWASP API Abuse Scenarios**: Based on OWASP API Security Top 10
5. **Synthetic Traffic Patterns**: Realistic user behavior (60% normal, 25% heavy, 15% bot)

### View Datasets:
```bash
# Interactive dataset viewer
cd backend
view_datasets.bat

# Export for presentation
export_datasets.bat
```

### Exported Files (READY FOR DEMONSTRATION):
📁 Location: `backend/datasets/EXPORT_FOR_MENTORS/`

1. **TRAINING_DATASET.xlsx** - Main dataset with statistics
   - 1000 samples × 8 features
   - Includes: Full dataset, Statistics, Sample data, Feature correlation
   
2. **COMPLETE_DATASET_REPORT.txt** - Comprehensive documentation
   - Dataset overview and sources
   - ML model details
   - Real-time detection pipeline
   - Feature descriptions

3. **DATASET_SUMMARY.csv** - Quick feature reference
   - Min, Max, Mean, Std Dev for each feature

### 8 Engineered Features:
1. **req_count**: Number of API requests in time window
2. **error_rate**: Percentage of failed requests (4xx/5xx status codes)
3. **avg_response_time**: Average response time in milliseconds
4. **max_response_time**: Maximum response time in milliseconds
5. **payload_mean**: Average payload size in bytes
6. **unique_endpoints**: Number of distinct endpoints accessed
7. **repeat_rate**: Rate of repeated identical requests (bot indicator)
8. **status_entropy**: Entropy of HTTP status codes (measures randomness)

## ML Models

### 1. Isolation Forest (Anomaly Detection)
- **Purpose**: Detect unusual API usage patterns
- **Parameters**: 
  - n_estimators=300
  - contamination=0.05
  - StandardScaler normalization
- **Output**: Anomaly score and binary classification

### 2. K-Means Clustering (Usage Classification)
- **Purpose**: Classify usage patterns into clusters
- **Clusters**:
  - Cluster 0: Normal users
  - Cluster 1: Heavy users
  - Cluster 2: Bot-like behavior
- **Method**: Elbow method for optimal k

### 3. Random Forest (Failure Prediction)
- **Purpose**: Predict API failure probability
- **Parameters**:
  - n_estimators=300
  - max_depth=15
  - class_weight='balanced'
- **Labels**: error_rate > 0.3 OR avg_response_time > 800ms

### 4. Ensemble Risk Scoring
```
risk_score = 0.45 * anomaly_score + 0.35 * failure_prob + 0.20 * is_bot
```

**Priority Levels**:
- HIGH: risk_score >= 0.8
- MEDIUM: 0.5 <= risk_score < 0.8
- LOW: risk_score < 0.5

## Features

### Automatic Logging
All API calls are automatically logged via FastAPI middleware:
- Timestamp
- Endpoint & Method
- Response time (ms)
- Status code
- Payload size
- IP address
- User ID

### Feature Engineering
1-minute sliding window aggregation:
- Request count
- Error rate
- Average response time
- Max response time
- Payload mean
- Unique endpoints
- Repeat rate
- Status entropy

### Real-time Monitoring
- WebSocket streaming of anomalies
- Live dashboard updates
- Instant alert notifications for high-risk events

### Admin Query Panel
Natural language queries:
- "Show high risk APIs in last 10 minutes"
- "Find anomalies in /payment endpoint"
- "Show all bot-like behavior"

## Setup Instructions

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Train ML models:
```bash
python train_models.py
```

5. Run the server:
```bash
python app.py
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`

## API Endpoints

### REST APIs

**Mock Endpoints** (for testing):
- `POST /login` - User authentication
- `POST /payment` - Payment processing
- `GET /search` - Search functionality
- `GET /health` - Health check

**System APIs**:
- `GET /api/stats` - System statistics
- `GET /api/anomalies` - Retrieve anomalies
- `GET /api/logs` - API call logs
- `GET /api/analytics/endpoint/{endpoint}` - Endpoint analytics
- `POST /api/admin/query` - Admin natural language queries

**WebSocket**:
- `WS /ws` - Real-time anomaly streaming

## Architecture

```
Client Request
      ↓
FastAPI Endpoint
      ↓
Logging Middleware → Database (APILog)
      ↓
Response to Client

[Background Task Every 60s]
      ↓
Extract Features (1-min window)
      ↓
ML Inference (3 models)
      ↓
Ensemble Risk Scoring
      ↓
Save to Database (AnomalyLog)
      ↓
WebSocket Broadcast → Frontend Dashboard
```

## Dashboard Features

### Overview Page
- Total API calls counter
- Anomaly count with detection rate
- Priority distribution (HIGH/MEDIUM/LOW)
- System health indicator
- Real-time connection status

### Visualizations
- **Risk Score Over Time**: Line chart tracking risk trends
- **Anomalies by Endpoint**: Bar chart of endpoint distribution
- **Priority Distribution**: Pie chart of risk levels
- **Model Metrics**: Anomaly detection rate, avg risk score, bot detection rate

### Analytics Page
- Per-endpoint metrics
- Request frequency
- Error rate analysis
- Latency statistics
- Failure probability
- Performance insights

### Admin Panel
- Natural language query interface
- Example queries for quick access
- Tabular result display
- Query interpretation

### Real-time Features
- WebSocket connection with auto-reconnect
- Live anomaly feed
- Alert toasts for HIGH risk events (risk_score >= 0.8)

## Database Schema

### APILog Table
- id (Primary Key)
- timestamp
- endpoint
- method
- response_time_ms
- status_code
- payload_size
- ip_address
- user_id

### AnomalyLog Table
- id (Primary Key)
- timestamp
- endpoint
- method
- risk_score
- priority
- failure_probability
- anomaly_score
- is_anomaly
- usage_cluster
- [All 8 feature columns]

## Production Considerations

### Security
- Add authentication/authorization
- Rate limiting
- Input validation
- CORS configuration
- Environment variable management

### Scalability
- Database indexing on timestamp and endpoint
- Redis for caching
- Message queue for async processing
- Load balancing
- Model versioning

### Monitoring
- Application logging
- Performance metrics
- Model drift detection
- Database query optimization

## License

MIT License
