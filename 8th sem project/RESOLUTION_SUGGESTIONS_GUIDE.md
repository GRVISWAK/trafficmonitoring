# Resolution Suggestions Feature - Complete Guide

## Overview
The anomaly detection system now includes **Advanced Root Cause Analysis** with **Actionable Resolution Suggestions**. This feature automatically classifies the root cause of detected anomalies and provides prioritized, expert-level remediation steps.

## How It Works

### 1. Root Cause Classification
The system analyzes anomaly metrics to determine the primary root cause:

#### Classification Rules:
- **Latency Bottleneck**: `avg_response_time > 800ms AND error_rate < 0.3`
- **Backend Instability**: `error_rate >= 0.3` (30% or more errors)
- **Traffic Surge**: `req_count >= 2x baseline` (10+ requests in window)
- **Abuse/Bot Activity**: `repeat_rate > 0.7 OR usage_cluster == 2`
- **System Overload**: Multiple conditions met simultaneously

### 2. Metrics Used
The analyzer uses the following inference outputs:
- `error_rate` - Percentage of 4xx/5xx errors (0.0-1.0)
- `avg_response_time` - Average response time in milliseconds
- `req_count` - Number of requests in the detection window
- `repeat_rate` - Parameter repetition ratio (0.0-1.0)
- `usage_cluster` - ML cluster (0=Normal, 1=Heavy, 2=Bot)
- `failure_probability` - Predicted failure probability (0.0-1.0)

### 3. Resolution Suggestions

Each root cause has 4+ prioritized suggestions:

#### Latency Bottleneck
1. **[HIGH] Caching**: Add Redis read-through cache
   - Cache frequently accessed data with TTL to reduce database queries
2. **[HIGH] I/O Optimization**: Enable async I/O
   - Use non-blocking async operations for external API calls and database queries
3. **[MEDIUM] Database**: Tune DB indexes
   - Add composite indexes on frequently queried columns, analyze slow query logs
4. **[MEDIUM] Concurrency**: Increase worker concurrency
   - Scale up Gunicorn/Uvicorn workers or enable thread pooling

#### Backend Instability
1. **[CRITICAL] Debugging**: Inspect error traces
   - Review application logs and stack traces to identify failing code paths
2. **[HIGH] Resilience**: Enable circuit breaker
   - Implement circuit breaker pattern to prevent cascade failures (e.g., Hystrix, resilience4j)
3. **[HIGH] Deployment**: Rollback recent deploy
   - Revert to last stable version if errors started after recent deployment
4. **[MEDIUM] Dependency Management**: Isolate failing dependency
   - Identify and quarantine failing external services, add fallback mechanisms

#### Traffic Surge
1. **[CRITICAL] Rate Limiting**: Apply token-bucket rate limiting
   - Implement per-IP or per-user rate limits with token bucket algorithm
2. **[HIGH] Scaling**: Autoscale pods/instances
   - Enable horizontal pod autoscaling (HPA) or auto-scaling groups
3. **[MEDIUM] Caching**: Cache idempotent responses
   - Cache GET responses at CDN or application layer with appropriate TTL
4. **[MEDIUM] CDN**: Enable CDN edge caching
   - Offload static and cacheable content to CDN (Cloudflare, CloudFront)

#### Abuse/Bot Activity
1. **[CRITICAL] Rate Limiting**: Adaptive rate limits
   - Implement adaptive rate limiting based on user behavior patterns
2. **[HIGH] Security**: IP reputation filtering
   - Block traffic from known malicious IPs using threat intelligence feeds
3. **[HIGH] Authentication**: Auth throttling & CAPTCHA
   - Add progressive delays and CAPTCHA challenges for suspicious login attempts
4. **[MEDIUM] WAF**: Configure WAF rules
   - Update WAF rules to detect and block bot signatures and scraping patterns

#### System Overload (Multiple Conditions)
1. **[CRITICAL] Scaling**: Horizontal scaling
   - Add more application instances/pods to distribute load
2. **[HIGH] Queue Management**: Request queuing
   - Implement request queue with backpressure to prevent resource exhaustion
3. **[HIGH] Graceful Degradation**: Enable graceful degradation
   - Disable non-critical features, serve cached/stale data temporarily
4. **[MEDIUM] Optimization**: Payload minimization
   - Reduce response payload size, enable compression (gzip/brotli)
5. **Plus top suggestions from contributing conditions**

## Architecture

### Backend Components

#### 1. `root_cause_analyzer.py`
```python
from root_cause_analyzer import RootCauseAnalyzer

# Analyze anomaly
result = RootCauseAnalyzer.analyze(
    error_rate=0.4,
    avg_response_time=1200,
    req_count=15,
    repeat_rate=0.3,
    usage_cluster=1,
    failure_probability=0.8
)

# Result structure:
{
    'root_cause': 'System Overload',
    'confidence': 0.90,
    'conditions_met': ['backend_instability', 'traffic_surge'],
    'resolution_suggestions': [
        {
            'category': 'Scaling',
            'action': 'Horizontal scaling',
            'detail': 'Add more application instances/pods to distribute load',
            'priority': 'CRITICAL'
        },
        ...
    ],
    'metrics_summary': {
        'error_rate': 0.4,
        'avg_response_time_ms': 1200,
        'req_count': 15,
        'repeat_rate': 0.3,
        'usage_cluster': 1,
        'failure_probability': 0.8
    }
}
```

#### 2. Updated Models (`models.py`)
```python
class ResolutionSuggestion(BaseModel):
    category: str
    action: str
    detail: str
    priority: str

class RootCauseAnalysis(BaseModel):
    root_cause: str
    confidence: float
    conditions_met: List[str]
    resolution_suggestions: List[ResolutionSuggestion]
    metrics_summary: MetricsSummary

class AnomalyResponse(BaseModel):
    # ... existing fields ...
    root_cause_analysis: Optional[RootCauseAnalysis] = None
```

#### 3. API Integration (`app_enhanced.py`)
The `/api/anomalies` endpoint now includes root cause analysis:
```python
@app.get("/api/anomalies")
async def get_anomalies(limit: int = 50, db: Session = Depends(get_db)):
    anomalies = db.query(AnomalyLog).order_by(AnomalyLog.timestamp.desc()).limit(limit).all()
    
    result = []
    for anomaly in anomalies:
        # Perform root cause analysis
        root_cause_result = RootCauseAnalyzer.analyze(
            error_rate=anomaly.error_rate,
            avg_response_time=anomaly.avg_response_time,
            req_count=anomaly.req_count,
            repeat_rate=anomaly.repeat_rate,
            usage_cluster=anomaly.usage_cluster,
            failure_probability=anomaly.failure_probability
        )
        
        anomaly_data = {
            # ... existing fields ...
            "root_cause_analysis": root_cause_result
        }
        result.append(anomaly_data)
    
    return result
```

WebSocket broadcasts also include root cause analysis for real-time updates.

### Frontend Components

#### 1. Updated Types (`types/index.ts`)
```typescript
export interface ResolutionSuggestion {
  category: string;
  action: string;
  detail: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
}

export interface RootCauseAnalysis {
  root_cause: string;
  confidence: number;
  conditions_met: string[];
  resolution_suggestions: ResolutionSuggestion[];
  metrics_summary: {
    error_rate: number;
    avg_response_time_ms: number;
    req_count: number;
    repeat_rate: number;
    usage_cluster: number;
    failure_probability: number;
  };
}

export interface Anomaly {
  // ... existing fields ...
  root_cause_analysis?: RootCauseAnalysis;
}
```

#### 2. Enhanced AnomalyTable (`components/AnomalyTable.tsx`)
- **Expandable Rows**: Click "▶ Details" button to expand
- **Root Cause Header**: Shows root cause and confidence level
- **Metrics Summary**: 6 key metrics in visual cards
- **Conditions Detected**: Visual badges for triggered conditions
- **Resolution Suggestions**: Prioritized list with color-coded priorities
- **Implementation Guidance**: Notes for proper deployment

## Usage

### In the Dashboard

1. **Navigate to Dashboard** (LIVE or SIMULATION mode)
2. **Scroll to Anomaly Table** at the bottom
3. **Click "▶ Details"** on any anomaly row
4. **View Root Cause Analysis**:
   - Root cause classification
   - Confidence score
   - Key metrics summary
   - Detected conditions
   - Prioritized resolution suggestions
5. **Implement Suggestions** based on priority (CRITICAL → HIGH → MEDIUM → LOW)

### Example Scenarios

#### Scenario 1: Latency Spike
**Metrics**:
- avg_response_time: 1250ms
- error_rate: 0.15
- req_count: 7

**Root Cause**: Latency Bottleneck (Confidence: 92%)

**Top Suggestions**:
1. Add Redis read-through cache
2. Enable async I/O
3. Tune DB indexes

#### Scenario 2: Error Storm
**Metrics**:
- error_rate: 0.65
- avg_response_time: 450ms
- req_count: 8

**Root Cause**: Backend Instability (Confidence: 95%)

**Top Suggestions**:
1. Inspect error traces
2. Enable circuit breaker
3. Rollback recent deploy

#### Scenario 3: DDoS Attack
**Metrics**:
- req_count: 25 (5x baseline)
- error_rate: 0.45
- avg_response_time: 1800ms
- repeat_rate: 0.9

**Root Cause**: System Overload (Confidence: 95%)
**Conditions**: traffic_surge, backend_instability, abuse_bot

**Top Suggestions**:
1. Horizontal scaling
2. Apply token-bucket rate limiting
3. Adaptive rate limits
4. Enable graceful degradation

## Testing

### Test the Root Cause Analyzer
```bash
cd backend
python root_cause_analyzer.py
```

This will run 5 test cases covering all root cause types.

### Test in Live System
1. Start backend: `backend\start_enhanced.bat`
2. Start frontend: `frontend\npm run dev`
3. Navigate to Dashboard
4. Click test endpoints or start simulation
5. Wait for anomaly detection
6. Click "▶ Details" on detected anomalies

## API Response Example

```json
{
  "id": 42,
  "timestamp": "2026-01-11T10:30:00",
  "endpoint": "/payment",
  "method": "POST",
  "risk_score": 0.875,
  "priority": "HIGH",
  "failure_probability": 0.7,
  "anomaly_score": 0.82,
  "is_anomaly": true,
  "usage_cluster": 1,
  "req_count": 12,
  "error_rate": 0.4,
  "avg_response_time": 1200,
  "max_response_time": 2500,
  "payload_mean": 450,
  "unique_endpoints": 3,
  "repeat_rate": 0.3,
  "status_entropy": 1.2,
  "root_cause_analysis": {
    "root_cause": "System Overload",
    "confidence": 0.90,
    "conditions_met": [
      "backend_instability",
      "latency_bottleneck",
      "traffic_surge"
    ],
    "resolution_suggestions": [
      {
        "category": "Scaling",
        "action": "Horizontal scaling",
        "detail": "Add more application instances/pods to distribute load",
        "priority": "CRITICAL"
      },
      {
        "category": "Queue Management",
        "action": "Request queuing",
        "detail": "Implement request queue with backpressure to prevent resource exhaustion",
        "priority": "HIGH"
      },
      ...
    ],
    "metrics_summary": {
      "error_rate": 0.4,
      "avg_response_time_ms": 1200,
      "req_count": 12,
      "repeat_rate": 0.3,
      "usage_cluster": 1,
      "failure_probability": 0.7
    }
  }
}
```

## Benefits

1. **Actionable Intelligence**: Move from "we detected an anomaly" to "here's exactly what to do"
2. **Prioritized Remediation**: CRITICAL/HIGH/MEDIUM/LOW priorities guide implementation order
3. **Expert Knowledge**: Built-in DevOps and SRE best practices
4. **Context-Aware**: Suggestions adapt to specific root cause
5. **Educational**: Learn infrastructure best practices while resolving issues
6. **Time-Saving**: No need to debug or research solutions manually
7. **Confidence Scoring**: Transparency in diagnostic accuracy

## Customization

### Adjust Baseline
```python
# In root_cause_analyzer.py
RootCauseAnalyzer.BASELINE_REQ_COUNT = 10  # Default is 5
```

### Add Custom Suggestions
```python
# In root_cause_analyzer.py, _get_resolution_suggestions method
all_suggestions['Custom Root Cause'] = [
    {
        'category': 'Custom Category',
        'action': 'Custom action',
        'detail': 'Custom detail',
        'priority': 'HIGH'
    }
]
```

### Modify Classification Rules
```python
# In root_cause_analyzer.py, analyze method
is_custom_condition = custom_metric > threshold
if is_custom_condition:
    conditions_met.append('custom_condition')
```

## Files Modified

### Backend
- ✅ `backend/root_cause_analyzer.py` (NEW)
- ✅ `backend/models.py` (Updated: Added RootCauseAnalysis models)
- ✅ `backend/app_enhanced.py` (Updated: Integrated analyzer into /api/anomalies and WebSocket)

### Frontend
- ✅ `frontend/src/types/index.ts` (Updated: Added RootCauseAnalysis interface)
- ✅ `frontend/src/components/AnomalyTable.tsx` (Updated: Expandable rows with suggestions)

## Future Enhancements

1. **Machine Learning-Based Suggestions**: Train model to recommend suggestions based on historical success rates
2. **Automated Remediation**: One-click implementation of suggestions (e.g., auto-scale, enable caching)
3. **Custom Playbooks**: User-defined resolution workflows
4. **Integration with Incident Management**: Export to Jira, PagerDuty, etc.
5. **A/B Testing**: Track which suggestions work best
6. **Cost Analysis**: Estimate implementation cost for each suggestion

## Support

For questions or issues:
1. Check console logs for root cause analyzer output
2. Verify metrics are within expected ranges
3. Ensure backend models are properly imported
4. Check browser console for TypeScript errors

---

**Status**: ✅ Complete and Production-Ready
**Version**: 1.0.0
**Date**: January 11, 2026
