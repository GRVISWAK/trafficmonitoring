"""
Enhanced FastAPI Backend with LIVE and SIMULATION Modes
Author: 8th Semester Project Team
Date: December 28, 2025
"""
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import random
import time
from datetime import datetime, timedelta
import asyncio
from typing import Optional, List, Dict

from database import init_db, get_db, APILog, AnomalyLog
from models import (
    LoginRequest, PaymentRequest, SearchQuery, 
    APILogResponse, AnomalyResponse, AdminQueryRequest, AdminQueryResponse
)
from live_middleware import EnhancedLoggingMiddleware, get_live_stats
from inference_enhanced import HybridDetectionEngine
from window_manager import live_window_manager, simulation_window_manager
from traffic_simulator import traffic_simulator
from simulation_manager_v2 import endpoint_history, endpoint_generator
from auto_traffic_generator import auto_traffic_generator
from websocket import manager

# Initialize FastAPI app
app = FastAPI(
    title="Predictive API Misuse and Failure Prediction System",
    description="LIVE and SIMULATION modes with ML-based anomaly detection",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize detection engine
detection_engine = HybridDetectionEngine()

# Add enhanced logging middleware for LIVE MODE
app.add_middleware(EnhancedLoggingMiddleware, detection_engine=detection_engine)

# Initialize database
init_db()

# Global state for simulation mode
simulation_active = False
simulation_task = None
simulation_stats = {
    'total_requests': 0,
    'windows_processed': 0,
    'anomalies_detected': 0,
    'start_time': None
}


@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    print("=" * 80)
    print("🚀 PREDICTIVE API MISUSE & FAILURE PREDICTION SYSTEM")
    print("=" * 80)
    print("✅ Enhanced ML Models Loaded:")
    print("   - Isolation Forest (trained on normal traffic)")
    print("   - K-Means Clustering (3 clusters)")
    print("   - Logistic Regression (100% accuracy)")
    print("   - Failure Predictor (proactive detection)")
    print("\n📊 Modes Available:")
    print("   - LIVE MODE: Real endpoint detection")
    print("   - SIMULATION MODE: Synthetic traffic with anomalies")
    print("\n🎯 Features: 9 behavioral indicators")
    print("   request_rate, unique_endpoint_count, method_ratio,")
    print("   avg_payload_size, error_rate, repeated_parameter_ratio,")
    print("   user_agent_entropy, avg_response_time, max_response_time")
    print("=" * 80)
    print()


# ============================================================================
# LIVE MODE ENDPOINTS
# ============================================================================

@app.post("/login")
async def login(request: LoginRequest, req: Request):
    """
    LIVE MODE - Real login endpoint
    Tracked by middleware for anomaly detection
    """
    req.state.user_id = request.username
    
    await asyncio.sleep(random.uniform(0.05, 0.2))
    
    # Simulate occasional auth failures
    if random.random() < 0.1:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {
        "success": True,
        "user_id": request.username,
        "token": f"token_{request.username}_{int(time.time())}",
        "message": "Login successful"
    }


@app.post("/payment")
async def payment(request: PaymentRequest, req: Request):
    """
    Mock payment endpoint - LIVE MODE
    Logs real requests for ML detection
    """
    req.state.user_id = request.user_id
    
    await asyncio.sleep(random.uniform(0.1, 0.5))
    
    if random.random() < 0.15:
        raise HTTPException(status_code=500, detail="Payment processing failed")
    
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")
    
    return {
        "success": True,
        "transaction_id": f"txn_{int(time.time())}_{random.randint(1000, 9999)}",
        "amount": request.amount,
        "currency": request.currency,
        "status": "completed",
        "message": "Payment processed successfully"
    }


@app.get("/search")
async def search(query: str = "", limit: int = 10):
    """
    Mock search endpoint - LIVE MODE
    Logs real requests for ML detection
    """
    await asyncio.sleep(random.uniform(0.05, 0.2))
    
    if len(query) < 2 and query != "":
        raise HTTPException(status_code=400, detail="Query too short")
    
    results = [
        {"id": i, "title": f"Result {i}", "score": random.random()}
        for i in range(min(limit, 20))
    ]
    
    return {
        "query": query,
        "total": len(results),
        "results": results
    }


@app.get("/profile/{user_id}")
async def get_profile(user_id: str):
    """
    LIVE MODE - Real profile endpoint
    Tracked by middleware. Use /profile (not /profile/{id}) for tracking.
    """
    await asyncio.sleep(random.uniform(0.1, 0.2))
    
    if random.random() < 0.05:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com",
        "created_at": datetime.now().isoformat()
    }

@app.get("/profile")
async def get_current_profile(user_id: str = "guest"):
    """
    LIVE MODE - Real profile endpoint (whitelisted)
    Tracked by middleware for anomaly detection
    """
    await asyncio.sleep(random.uniform(0.05, 0.2))
    return {
        "user_id": user_id,
        "name": f"User {user_id}",
        "email": f"{user_id}@example.com",
        "created_at": datetime.now().isoformat()
    }

@app.post("/signup")
async def signup(request: LoginRequest):
    """
    LIVE MODE - Real signup endpoint (whitelisted)
    Tracked by middleware for anomaly detection
    """
    await asyncio.sleep(random.uniform(0.1, 0.3))
    
    if random.random() < 0.05:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    return {
        "success": True,
        "user_id": request.username,
        "message": "Account created successfully"
    }

@app.post("/logout")
async def logout(user_id: str = "guest"):
    """
    LIVE MODE - Real logout endpoint (whitelisted)
    Tracked by middleware for anomaly detection
    """
    await asyncio.sleep(random.uniform(0.02, 0.1))
    return {
        "success": True,
        "message": "Logged out successfully"
    }

@app.get("/health")
async def health():
    """
    Health check endpoint - NOT tracked in LIVE mode (blacklisted)
    """
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/live/stats")
async def get_live_mode_stats():
    """Get statistics for LIVE MODE"""
    return get_live_stats()


# ============================================================================
# SIMULATION MODE ENDPOINTS
# ============================================================================

@app.post("/simulation/start")
async def start_simulation(
    background_tasks: BackgroundTasks,
    simulated_endpoint: str,
    duration_seconds: int = 60,
    requests_per_window: int = 10
):
    """
    Start auto-detection simulation
    
    Generates mixed traffic patterns for selected endpoint.
    ML models automatically detect anomaly types from window features.
    
    Args:
        simulated_endpoint: Virtual endpoint (/sim/login, /sim/search, /sim/profile, /sim/payment, /sim/signup)
        duration_seconds: How long to run simulation
        requests_per_window: Requests per window (default 10)
    
    Returns:
        Simulation status
    """
    global simulation_active, simulation_task, simulation_stats
    
    # Validate inputs
    if simulated_endpoint not in auto_traffic_generator.VIRTUAL_ENDPOINTS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid endpoint. Must be one of: {auto_traffic_generator.VIRTUAL_ENDPOINTS}"
        )
    
    if simulation_active:
        raise HTTPException(status_code=400, detail="Simulation already running")
    
    simulation_active = True
    simulation_stats = {
        'total_requests': 0,
        'windows_processed': 0,
        'anomalies_detected': 0,
        'anomaly_episodes': {},  # Track unique anomaly episodes per endpoint
        'start_time': time.time(),
        'simulated_endpoint': simulated_endpoint,
        'detected_anomaly_types': []  # ML-inferred types
    }
    
    # Reset simulation window
    simulation_window_manager.reset()
    
    # Start simulation in background
    background_tasks.add_task(
        run_auto_detection_simulation,
        simulated_endpoint=simulated_endpoint,
        duration_seconds=duration_seconds,
        requests_per_window=requests_per_window
    )
    
    return {
        "status": "started",
        "simulated_endpoint": simulated_endpoint,
        "duration_seconds": duration_seconds,
        "requests_per_window": requests_per_window,
        "mode": "auto-detection"
    }


@app.post("/simulation/stop")
async def stop_simulation():
    """Stop running simulation"""
    global simulation_active
    
    if not simulation_active:
        raise HTTPException(status_code=400, detail="No simulation running")
    
    simulation_active = False
    
    return {
        "status": "stopped",
        "stats": simulation_stats
    }


@app.get("/simulation/stats")
async def get_simulation_stats():
    """Get current simulation statistics with accuracy metrics and endpoint data"""
    window_info = simulation_window_manager.get_window_info()
    accuracy_stats = endpoint_history.get_accuracy_stats()
    priority_dist = endpoint_history.get_priority_distribution()
    model_decisions = endpoint_history.get_model_decisions()
    
    return {
        'mode': 'SIMULATION',
        'active': simulation_active,
        'total_requests': simulation_stats['total_requests'],
        'windows_processed': window_info['windows_processed'],
        'anomalies_detected': simulation_stats['anomalies_detected'],
        'current_window_count': window_info['current_count'],
        'window_size': window_info['window_size'],
        'is_window_full': window_info['is_full'],
        'simulated_endpoint': simulation_stats.get('simulated_endpoint', 'none'),
        'anomaly_type': simulation_stats.get('anomaly_type', 'none'),
        'start_time': simulation_stats.get('start_time'),
        'accuracy': accuracy_stats,
        'priority_distribution': priority_dist,
        'model_decisions': model_decisions
    }


@app.get("/simulation/history")
async def get_simulation_history(limit: int = 20):
    """Get simulation detection history with timestamps"""
    recent = endpoint_history.get_recent_detections(limit)
    return {
        'recent_detections': [
            {
                'id': a.id,
                'timestamp': a.timestamp,
                'simulated_endpoint': a.simulated_endpoint,
                'anomaly_type': a.anomaly_type,
                'detected_type': a.detected_type,
                'risk_score': a.risk_score,
                'priority': a.priority,
                'is_correctly_detected': a.is_correctly_detected,
                'emergency_rank': a.emergency_rank,
                'method': a.method,
                'detection_latency_ms': a.detection_latency_ms
            }
            for a in recent
        ],
        'total_detections': len(endpoint_history.history)
    }


@app.get("/simulation/emergencies")
async def get_top_emergencies(limit: int = 10):
    """Get top emergency-ranked anomalies"""
    emergencies = endpoint_history.get_top_emergencies(limit)
    return {
        'top_emergencies': [
            {
                'id': a.id,
                'timestamp': a.timestamp,
                'simulated_endpoint': a.simulated_endpoint,
                'anomaly_type': a.anomaly_type,
                'detected_type': a.detected_type,
                'risk_score': a.risk_score,
                'priority': a.priority,
                'is_correctly_detected': a.is_correctly_detected,
                'emergency_rank': a.emergency_rank
            }
            for a in emergencies
        ],
        'ranking_criteria': 'Ranked by risk score and recency',
        'total_emergencies': len(endpoint_history.history)
    }


@app.get("/simulation/endpoint-stats")
async def get_endpoint_stats(endpoint: Optional[str] = None):
    """Get statistics by simulated endpoint"""
    stats = endpoint_history.get_endpoint_stats(endpoint)
    return {
        'endpoint': endpoint or 'all',
        'stats': stats
    }


@app.get("/simulation/anomaly-history")
async def get_anomaly_history(limit: int = 100):
    """
    Get anomaly detection history with endpoint breakdown and risk scores
    
    Returns:
        - Recent anomaly detections (sorted by risk score)
        - Per-endpoint statistics
        - Risk score distribution
        - Anomaly type counts
    """
    recent = endpoint_history.get_recent_detections(limit=limit)
    
    # Group by endpoint for chart data
    endpoint_data = {}
    risk_timeline = []
    anomaly_type_counts = {}
    
    for anomaly in recent:
        # Endpoint grouping
        ep = anomaly.simulated_endpoint
        if ep not in endpoint_data:
            endpoint_data[ep] = {
                'endpoint': ep,
                'count': 0,
                'avg_risk': 0,
                'max_risk': 0,
                'anomaly_types': {}
            }
        
        endpoint_data[ep]['count'] += 1
        endpoint_data[ep]['max_risk'] = max(endpoint_data[ep]['max_risk'], anomaly.risk_score)
        
        # Track anomaly types per endpoint
        at = anomaly.anomaly_type
        if at not in endpoint_data[ep]['anomaly_types']:
            endpoint_data[ep]['anomaly_types'][at] = 0
        endpoint_data[ep]['anomaly_types'][at] += 1
        
        # Global anomaly type tracking
        if at not in anomaly_type_counts:
            anomaly_type_counts[at] = 0
        anomaly_type_counts[at] += 1
        
        # Timeline data
        risk_timeline.append({
            'timestamp': anomaly.timestamp,
            'risk_score': round(anomaly.risk_score, 4),
            'endpoint': ep,
            'anomaly_type': at,
            'priority': anomaly.priority
        })
    
    # Calculate average risk per endpoint
    for ep_data in endpoint_data.values():
        ep_anomalies = [a for a in recent if a.simulated_endpoint == ep_data['endpoint']]
        ep_data['avg_risk'] = round(
            sum(a.risk_score for a in ep_anomalies) / len(ep_anomalies),
            4
        ) if ep_anomalies else 0
    
    return {
        'history': [
            {
                'id': a.id,
                'timestamp': a.timestamp,
                'endpoint': a.simulated_endpoint,
                'anomaly_type': a.anomaly_type,
                'detected_type': a.detected_type,
                'risk_score': round(a.risk_score, 4),
                'priority': a.priority,
                'method': a.method,
                'window_id': a.window_id,
                'emergency_rank': a.emergency_rank,
                'is_correctly_detected': a.is_correctly_detected
            }
            for a in recent
        ],
        'endpoint_breakdown': list(endpoint_data.values()),
        'risk_timeline': risk_timeline[-50:],  # Last 50 for chart
        'anomaly_type_distribution': anomaly_type_counts,
        'total_anomalies': len(recent)
    }


@app.post("/simulation/clear-history")
async def clear_simulation_history():
    """Clear simulation detection history"""
    endpoint_history.clear_history()
    return {"status": "cleared", "message": "Simulation history cleared"}


async def run_auto_detection_simulation(
    simulated_endpoint: str,
    duration_seconds: int,
    requests_per_window: int
):
    """
    Auto-detection simulation - ML models determine anomaly types
    
    Process:
    1. Generate mixed traffic patterns (no pre-labeled types)
    2. Aggregate into 10-request windows
    3. Run ML inference on window features
    4. ML models determine anomaly type from patterns
    5. Count anomalies per window, aggregate episodes
    """
    global simulation_active, simulation_stats
    
    print(f"\n🎬 AUTO-DETECTION SIMULATION STARTED")
    print(f"   Virtual Endpoint: {simulated_endpoint}")
    print(f"   Mode: ML Auto-Detection (no pre-labeled types)")
    print(f"   Duration: {duration_seconds}s")
    print(f"   Window Size: {requests_per_window}\n")
    
    start_time = time.time()
    window_count = 0
    last_anomaly_type = None
    episode_count = 0
    
    try:
        while simulation_active and (time.time() - start_time) < duration_seconds:
            # Generate mixed traffic (ML determines anomaly type)
            requests = auto_traffic_generator.generate_traffic(
                simulated_endpoint=simulated_endpoint,
                count=requests_per_window
            )
            window_count += 1
            
            print(f"⏱️  Window #{window_count} | Time: {int(time.time() - start_time)}s / {duration_seconds}s")
            
            # Process each request through window manager
            for req in requests:
                simulation_stats['total_requests'] += 1
                
                features = simulation_window_manager.add_request(
                    method=req['method'],
                    path=req['path'],
                    status=req['status'],
                    latency=req['latency'],
                    payload_size=req['payload_size'],
                    user_agent=req['user_agent'],
                    parameters=req.get('parameters', {})
                )
                
                # Run ML inference ONCE per window (when window is full)
                if features:
                    try:
                        prediction = detection_engine.predict_anomaly(features)
                        
                        simulation_stats['windows_processed'] += 1
                        
                        # Anomaly counting per WINDOW (not per request)
                        if prediction['is_anomaly']:
                            # Determine ML-inferred anomaly type from detection method
                            detected_type = prediction.get('detection_method', 'UNKNOWN')
                            
                            # Episode tracking: count unique anomaly patterns
                            if detected_type != last_anomaly_type:
                                episode_count += 1
                                last_anomaly_type = detected_type
                                simulation_stats['anomalies_detected'] = episode_count
                            
                            # Track detected types
                            if detected_type not in simulation_stats['detected_anomaly_types']:
                                simulation_stats['detected_anomaly_types'].append(detected_type)
                        
                        # Store in history (without pre-labeled type)
                        anomaly_record = endpoint_history.add_detection(
                            simulated_endpoint=simulated_endpoint,
                            anomaly_type=prediction.get('detection_method', 'AUTO_DETECTED'),
                            detection_result=prediction,
                            method=req['method'],
                            window_id=features['window_id']
                        )
                        
                        # Print detection result
                        print(f"🔍 AUTO-DETECTION (Window #{features['window_id']}):")
                        print(f"   Endpoint: {simulated_endpoint}")
                        print(f"   ML Detected: {prediction['detection_method']}")
                        print(f"   Is Anomaly: {'✅ YES' if prediction['is_anomaly'] else '❌ NO'}")
                        print(f"   Risk Score: {prediction['risk_score']:.4f}")
                        print(f"   Priority: {prediction['priority']}")
                        print(f"   Episode #: {episode_count}")
                        if 'details' in prediction and prediction['details'].get('rule_alerts'):
                            print(f"   Rules Triggered: {', '.join(prediction['details']['rule_alerts'])}")
                        print(f"   Detection Latency: {prediction['detection_latency_ms']:.2f}ms\n")
                        
                        # Broadcast to WebSocket
                        await manager.broadcast({
                            'type': 'auto_detection_simulation',
                            'data': {
                                'window_id': features['window_id'],
                                'simulated_endpoint': simulated_endpoint,
                                'detected_type': prediction['detection_method'],
                                'episode_number': episode_count,
                                'features': features,
                                'prediction': {
                                    'is_anomaly': prediction['is_anomaly'],
                                    'risk_score': prediction['risk_score'],
                                    'priority': prediction['priority'],
                                    'detection_method': prediction['detection_method'],
                                    'rule_alerts': prediction.get('details', {}).get('rule_alerts', [])
                                },
                                'timestamp': datetime.now().isoformat()
                            }
                        })
                        
                    except Exception as e:
                        print(f"Error in simulation inference: {e}")
            
            # Delay between windows (spread traffic over duration)
            await asyncio.sleep(2)  # 2 seconds per window for visible progress
    
    except Exception as e:
        print(f"Error in simulation: {e}")
    
    finally:
        simulation_active = False
        print(f"\n🎬 SIMULATION STOPPED")
        print(f"   Total Requests: {simulation_stats['total_requests']}")
        print(f"   Windows Processed: {simulation_stats['windows_processed']}")
        print(f"   Anomalies Detected: {simulation_stats['anomalies_detected']}\n")


# ============================================================================
# ANALYTICS & MONITORING ENDPOINTS
# ============================================================================

@app.get("/api/logs")
async def get_api_logs(limit: int = 100, db: Session = Depends(get_db)):
    """Get recent API request logs"""
    logs = db.query(APILog).order_by(APILog.timestamp.desc()).limit(limit).all()
    
    return [
        {
            "id": log.id,
            "timestamp": log.timestamp.isoformat(),
            "endpoint": log.endpoint,
            "method": log.method,
            "status_code": log.status_code,
            "response_time_ms": log.response_time_ms,
            "payload_size": log.payload_size,
            "ip_address": log.ip_address
        }
        for log in logs
    ]


@app.get("/api/anomalies")
async def get_anomalies(limit: int = 50, db: Session = Depends(get_db)):
    """Get detected anomalies"""
    anomalies = db.query(AnomalyLog).order_by(AnomalyLog.timestamp.desc()).limit(limit).all()
    
    return [
        {
            "id": anomaly.id,
            "timestamp": anomaly.timestamp.isoformat(),
            "endpoint": anomaly.endpoint,
            "method": anomaly.method,
            "risk_score": anomaly.risk_score,
            "priority": anomaly.priority,
            "is_anomaly": anomaly.is_anomaly,
            "failure_probability": anomaly.failure_probability
        }
        for anomaly in anomalies
    ]


@app.get("/api/dashboard")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics with per-endpoint breakdown"""
    total_requests = db.query(APILog).count()
    total_anomalies = db.query(AnomalyLog).filter(AnomalyLog.is_anomaly == True).count()
    
    recent_logs = db.query(APILog).order_by(APILog.timestamp.desc()).limit(100).all()
    
    avg_response_time = sum(log.response_time_ms for log in recent_logs) / len(recent_logs) if recent_logs else 0
    error_rate = sum(1 for log in recent_logs if log.status_code >= 400) / len(recent_logs) if recent_logs else 0
    
    # Per-endpoint request counts (LIVE MODE only)
    endpoint_counts = {
        "/login": db.query(APILog).filter(APILog.endpoint == "/login").count(),
        "/signup": db.query(APILog).filter(APILog.endpoint == "/signup").count(),
        "/search": db.query(APILog).filter(APILog.endpoint == "/search").count(),
        "/profile": db.query(APILog).filter(APILog.endpoint == "/profile").count(),
        "/payment": db.query(APILog).filter(APILog.endpoint == "/payment").count(),
        "/logout": db.query(APILog).filter(APILog.endpoint == "/logout").count()
    }
    
    return {
        "total_requests": total_requests,
        "total_anomalies": total_anomalies,
        "avg_response_time": avg_response_time,
        "error_rate": error_rate * 100,
        "endpoint_counts": endpoint_counts,
        "live_stats": get_live_stats(),
        "simulation_stats": {
            'active': simulation_active,
            'total_requests': simulation_stats.get('total_requests', 0),
            'windows_processed': simulation_stats.get('windows_processed', 0),
            'anomalies_detected': simulation_stats.get('anomalies_detected', 0)
        }
    }


# ============================================================================
# WEBSOCKET FOR REAL-TIME UPDATES
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back for heartbeat
            await websocket.send_json({"type": "heartbeat", "status": "ok"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Predictive API Misuse and Failure Prediction System",
        "version": "2.0.0",
        "status": "operational",
        "modes": {
            "live": "Real endpoint detection with sliding windows",
            "simulation": "Synthetic traffic with anomaly injection"
        },
        "ml_models": {
            "isolation_forest": "Trained on normal traffic",
            "kmeans": "3 behavioral clusters",
            "logistic_regression": "100% accuracy",
            "failure_predictor": "Proactive detection"
        },
        "features": [
            "request_rate", "unique_endpoint_count", "method_ratio",
            "avg_payload_size", "error_rate", "repeated_parameter_ratio",
            "user_agent_entropy", "avg_response_time", "max_response_time"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
