# 🎯 QUICK REFERENCE: LIVE vs SIMULATION MODE

## 🔴 LIVE MODE - Real Traffic Monitoring

### When to Use
- Monitor actual user API calls
- Track real endpoint usage
- Detect genuine anomalies in production

### Whitelisted Endpoints (Only These Count)
```
/login
/signup
/search
/profile
/payment
/logout
```

### How It Works
1. Make manual API call to whitelisted endpoint
2. Counter increments by exactly +1
3. ML models analyze traffic in real-time
4. Dashboard updates automatically

### Example
```bash
# Check current count
curl http://localhost:8000/live/stats

# Make API call
curl "http://localhost:8000/search?q=test"

# Verify increment (+1)
curl http://localhost:8000/live/stats
```

### Key Metrics
- `total_requests`: Number of manual API calls made
- `status`: `active` (count > 0) or `idle` (count = 0)
- `anomalies_detected`: Real anomalies found

---

## 🔵 SIMULATION MODE - Synthetic Testing

### When to Use
- Test ML model performance
- Train on labeled anomaly data
- Measure detection accuracy
- Demonstrate system capabilities

### Anomaly Types Available
1. **normal** - Clean baseline traffic
2. **rate_spike** - DDoS simulation (10-50 req/sec)
3. **error_burst** - Scanning (70-90% 404s)
4. **bot_attack** - Low entropy patterns
5. **large_payload** - Data exfiltration (10KB-50KB)
6. **endpoint_scan** - Reconnaissance
7. **mixed** - Random combination

### How It Works
1. Start simulation with chosen anomaly type
2. System generates synthetic traffic
3. Each request explicitly labeled (e.g., "BOT_ATTACK")
4. ML models detect anomalies
5. System compares injected vs detected
6. Accuracy calculated automatically

### Quick Start
```bash
# Start simulation (20 seconds, bot attack)
curl -X POST "http://localhost:8000/simulation/start?mode=bot_attack&duration=20&requests_per_window=10"

# Wait for completion
sleep 22

# Check results
curl http://localhost:8000/simulation/stats
```

### Key Metrics
- `total_requests`: Synthetic requests generated
- `accuracy_percentage`: Detection accuracy (0-100%)
- `false_positives`: Normal traffic flagged as anomaly
- `false_negatives`: Anomalies missed
- `emergency_rank`: Priority ranking (#1 = highest)

---

## 📊 COMPARISON TABLE

| Feature | LIVE MODE | SIMULATION MODE |
|---------|-----------|-----------------|
| **Traffic Source** | Manual API calls | Synthetic generator |
| **Counter** | `_live_mode_request_counter` | `total_requests` |
| **Isolation** | ✅ Separate | ✅ Separate |
| **Anomaly Labeling** | Unknown (real data) | ✅ Explicit labels |
| **Accuracy Tracking** | ❌ No ground truth | ✅ Yes (100% in tests) |
| **Emergency Ranking** | By risk score only | ✅ Risk + recency |
| **History** | Database logs | ✅ In-memory deque |
| **Use Case** | Production monitoring | ML testing & demo |

---

## 🛠️ COMMON WORKFLOWS

### Workflow 1: Test New ML Model
```bash
# 1. Clear previous history
curl -X POST http://localhost:8000/simulation/clear-history

# 2. Run simulation with specific anomaly
curl -X POST "http://localhost:8000/simulation/start?mode=rate_spike&duration=30"

# 3. Check accuracy
curl http://localhost:8000/simulation/stats | jq '.accuracy'

# 4. View top emergencies
curl "http://localhost:8000/simulation/emergencies?limit=5"
```

### Workflow 2: Demo System Capabilities
```bash
# Test all anomaly types in sequence
for mode in normal rate_spike error_burst bot_attack large_payload endpoint_scan
do
  echo "Testing: $mode"
  curl -X POST "http://localhost:8000/simulation/start?mode=$mode&duration=10"
  sleep 12
  curl -X POST http://localhost:8000/simulation/stop
done

# Show final results
curl http://localhost:8000/simulation/stats
```

### Workflow 3: Monitor Real Traffic
```bash
# Watch LIVE mode counter
watch -n 2 'curl -s http://localhost:8000/live/stats | jq'

# In another terminal, make API calls
curl "http://localhost:8000/search?q=test1"
curl "http://localhost:8000/search?q=test2"
curl "http://localhost:8000/profile?user_id=123"

# Counter should increment by 3 (one per call)
```

---

## 🚨 EMERGENCY RANKING EXPLAINED

### How It Works
After each detection:
1. Calculate `risk_score` (0.0 - 1.0) from ML models
2. Sort all detections by:
   - Primary: `risk_score` (descending)
   - Secondary: `timestamp` (newer first)
3. Assign ranks: #1, #2, #3, etc.

### Example Ranking
```
Rank | Risk  | Time     | Type
-----|-------|----------|-------------
#1   | 0.826 | 21:03:38 | ERROR_BURST  <- HIGHEST PRIORITY
#2   | 0.826 | 21:03:35 | ERROR_BURST
#3   | 0.736 | 21:03:37 | ERROR_BURST
#4   | 0.343 | 20:59:02 | BOT_ATTACK   <- Lower risk
```

### Use Cases
- **Dashboard**: Show top 5 emergencies
- **Alerts**: Notify on rank #1-3 only
- **Triage**: Handle highest rank first

---

## 📡 ALL ENDPOINTS

### LIVE MODE
```bash
GET  /live/stats              # Get request counter and status
```

### SIMULATION MODE
```bash
POST /simulation/start        # Start synthetic traffic
POST /simulation/stop         # Stop running simulation
GET  /simulation/stats        # Get stats + accuracy
GET  /simulation/history      # Get detection history
GET  /simulation/emergencies  # Get top emergencies
POST /simulation/clear-history # Clear all history
```

### OTHER
```bash
GET  /api/dashboard          # Dashboard stats
GET  /api/anomalies          # Anomaly list
POST /login                  # LIVE endpoint
POST /search                 # LIVE endpoint
POST /profile                # LIVE endpoint
POST /payment                # LIVE endpoint
```

---

## ⚙️ DEFAULT PARAMETERS

### Simulation
- `duration_seconds`: 60
- `requests_per_window`: 10
- `mode`: "normal"

### History
- `limit`: 10 (emergencies)
- `max_history_size`: 1000 (deque)

### Window
- `window_size`: 10 requests

---

## 🎓 Best Practices

### LIVE MODE
✅ DO:
- Use for real production monitoring
- Track only whitelisted endpoints
- Monitor counter for genuine usage

❌ DON'T:
- Mix with simulation traffic
- Manually manipulate counter
- Track non-whitelisted endpoints

### SIMULATION MODE
✅ DO:
- Test ML models before deployment
- Use explicit anomaly modes
- Clear history between tests
- Check accuracy metrics

❌ DON'T:
- Run simultaneously with LIVE mode (isolation is automatic, but avoid confusion)
- Expect simulation to affect LIVE counters
- Use for production monitoring

---

## 🐛 Troubleshooting

### Issue: LIVE counter not incrementing
**Check**:
1. Is endpoint whitelisted? (`/login`, `/signup`, `/search`, `/profile`, `/payment`, `/logout`)
2. Is method GET or POST?
3. Did request succeed (not CORS preflight)?

### Issue: Simulation accuracy is 0%
**Check**:
1. Are ML models loaded? (Check startup logs)
2. Is window size correct? (Default: 10)
3. Is mode valid? (See anomaly types above)

### Issue: Emergency rankings seem random
**Explanation**: Rankings update after EACH detection. Newer high-risk anomalies overtake older ones.

---

## 📞 Support

**Documentation**:
- Full Guide: `SIMULATION_MODE_COMPLETE.md`
- Test Results: `VERIFICATION_TEST_RESULTS.md`
- Quick Start: `QUICK_START_GUIDE.txt`

**Logs**:
- Backend console shows real-time detections
- Check for `🔍 SIMULATION DETECTION` messages
- LIVE mode logs to database (`api_logs.db`)

---

*Quick Reference v2.0 - December 28, 2025*
