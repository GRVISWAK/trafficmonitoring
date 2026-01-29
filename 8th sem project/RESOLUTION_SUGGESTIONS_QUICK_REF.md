# Resolution Suggestions - Quick Reference Card

## 🎯 Root Cause Classification Rules

| Root Cause | Trigger Condition | Priority |
|------------|------------------|----------|
| **Latency Bottleneck** | avg_response_time > 800ms AND error_rate < 0.3 | Medium-High |
| **Backend Instability** | error_rate >= 0.3 (30%+) | Critical |
| **Traffic Surge** | req_count >= 2x baseline (10+ requests) | High |
| **Abuse/Bot Activity** | repeat_rate > 0.7 OR usage_cluster == 2 | Critical |
| **System Overload** | Multiple conditions met | Critical |

## 💡 Quick Resolution Matrix

### Latency Bottleneck
```
Priority  Category              Action
[HIGH]    Caching              Add Redis read-through cache
[HIGH]    I/O Optimization     Enable async I/O
[MEDIUM]  Database             Tune DB indexes
[MEDIUM]  Concurrency          Increase worker concurrency
```

### Backend Instability
```
Priority    Category                Action
[CRITICAL]  Debugging              Inspect error traces
[HIGH]      Resilience             Enable circuit breaker
[HIGH]      Deployment             Rollback recent deploy
[MEDIUM]    Dependency Mgmt        Isolate failing dependency
```

### Traffic Surge
```
Priority    Category           Action
[CRITICAL]  Rate Limiting      Apply token-bucket rate limiting
[HIGH]      Scaling            Autoscale pods/instances
[MEDIUM]    Caching            Cache idempotent responses
[MEDIUM]    CDN                Enable CDN edge caching
```

### Abuse/Bot Activity
```
Priority    Category           Action
[CRITICAL]  Rate Limiting      Adaptive rate limits
[HIGH]      Security           IP reputation filtering
[HIGH]      Authentication     Auth throttling & CAPTCHA
[MEDIUM]    WAF                Configure WAF rules
```

### System Overload
```
Priority    Category              Action
[CRITICAL]  Scaling              Horizontal scaling
[HIGH]      Queue Management     Request queuing
[HIGH]      Graceful Degrad.     Enable graceful degradation
[MEDIUM]    Optimization         Payload minimization
+ Top suggestions from contributing conditions
```

## 🔍 How to Use

### In Dashboard
1. Navigate to Dashboard (LIVE or SIMULATION mode)
2. Scroll to Anomaly Table
3. Click **▶ Details** button on any anomaly
4. View root cause and suggestions
5. Implement by priority: CRITICAL → HIGH → MEDIUM → LOW

### Example Flow
```
Anomaly Detected
    ↓
Click "▶ Details"
    ↓
Root Cause: "System Overload" (Confidence: 90%)
    ↓
Conditions: backend_instability, traffic_surge
    ↓
Top Suggestion: [CRITICAL] Horizontal scaling
    ↓
Implement: Add more pods/instances
    ↓
Monitor metrics for improvement
```

## 📊 Metrics Summary Display

When you expand an anomaly, you'll see:

```
┌─────────────────────────────────────────────────────┐
│ 🔍 Root Cause Analysis                              │
│ Root Cause: System Overload     Confidence: 90%    │
├─────────────────────────────────────────────────────┤
│ Error Rate │ Avg Resp │ Req Count │ Repeat │ ...   │
│   40.0%    │  1200ms  │    12     │  30%   │ ...   │
├─────────────────────────────────────────────────────┤
│ ⚡ Conditions: BACKEND_INSTABILITY, TRAFFIC_SURGE    │
├─────────────────────────────────────────────────────┤
│ 💡 Resolution Suggestions:                          │
│ [CRITICAL] Scaling: Horizontal scaling              │
│ [HIGH] Queue Management: Request queuing            │
│ [HIGH] Graceful Degradation: Enable graceful deg.   │
│ ...                                                  │
└─────────────────────────────────────────────────────┘
```

## 🚀 API Usage

### Get Anomalies with Suggestions
```bash
GET http://localhost:8000/api/anomalies?limit=50
```

Response includes `root_cause_analysis` field:
```json
{
  "root_cause_analysis": {
    "root_cause": "Latency Bottleneck",
    "confidence": 0.88,
    "conditions_met": ["latency_bottleneck"],
    "resolution_suggestions": [
      {
        "category": "Caching",
        "action": "Add Redis read-through cache",
        "detail": "Cache frequently accessed data...",
        "priority": "HIGH"
      }
    ]
  }
}
```

## 🎨 Priority Color Codes

| Priority | Color | Badge |
|----------|-------|-------|
| CRITICAL | Red | 🔴 |
| HIGH | Orange | 🟠 |
| MEDIUM | Yellow | 🟡 |
| LOW | Blue | 🔵 |

## 🔧 Customization

### Adjust Traffic Surge Baseline
```python
# backend/root_cause_analyzer.py
RootCauseAnalyzer.BASELINE_REQ_COUNT = 10  # Default: 5
```

### Add Custom Root Cause
```python
# In analyze() method
is_custom = custom_metric > threshold
if is_custom:
    conditions_met.append('custom_condition')
```

## 📝 Files Changed

| File | Change |
|------|--------|
| `backend/root_cause_analyzer.py` | ✅ NEW - Core analyzer |
| `backend/models.py` | ✅ Added RootCauseAnalysis models |
| `backend/app_enhanced.py` | ✅ Integrated into API & WebSocket |
| `frontend/src/types/index.ts` | ✅ Added TypeScript interfaces |
| `frontend/src/components/AnomalyTable.tsx` | ✅ Expandable rows UI |

## ⚡ Quick Test

```bash
# Test analyzer
cd backend
python root_cause_analyzer.py

# Expected output:
# ✅ 5 test cases pass
# ✅ All root causes classified correctly
# ✅ Suggestions generated for each
```

## 📖 Full Documentation
See [RESOLUTION_SUGGESTIONS_GUIDE.md](RESOLUTION_SUGGESTIONS_GUIDE.md) for complete details.

---
**Version**: 1.0.0 | **Status**: ✅ Production Ready | **Date**: January 11, 2026
