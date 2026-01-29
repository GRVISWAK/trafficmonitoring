from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import random
import time
from datetime import datetime, timedelta
import asyncio

from database import init_db, get_db, APILog, AnomalyLog, SessionLocal
from models import (
    LoginRequest, PaymentRequest, SearchQuery, 
    APILogResponse, AnomalyResponse, AdminQueryRequest, AdminQueryResponse
)
from middleware import LoggingMiddleware, live_mode_stats
from feature_engineering import extract_features_from_logs
from inference import inference_engine
from websocket import manager
from anomaly_injection import anomaly_injector, inject_anomaly_into_log, ENDPOINT_ANOMALY_MAP
from anomaly_detection import anomaly_detector
from resolution_engine import resolution_engine
from enhanced_simulation import enhanced_simulation_engine
from api_graphs import router as graphs_router

app = FastAPI(title="Predictive API Misuse and Failure Prediction System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)

# Include graph endpoints
app.include_router(graphs_router)

init_db()

# STRICT SEPARATION: Simulation Mode State
# (Live mode stats tracked in middleware.py)

# Simulation mode tracks ONLY synthetic traffic
simulation_active = False
simulation_stats = {
    'total_requests': 0,  # Only simulation-generated requests
    'windows_processed': 0,
    'anomalies_detected': 0,
    'start_time': None,
    'simulated_endpoint': 'none'
}
# Track whether we already persisted an anomaly for a simulated endpoint
simulation_anomaly_recorded = set()


@app.on_event("startup")
async def startup_event():
    """
    Initialize the system on startup.
    Background anomaly detection DISABLED - use simulation mode instead.
    """
    pass  # Disabled automatic detection


async def periodic_anomaly_detection():
    """
    Background task that runs DETERMINISTIC anomaly detection every 60 seconds on LIVE traffic only.
    Extracts features from recent LIVE logs, performs detection, and broadcasts results.
    """
    while True:
        try:
            await asyncio.sleep(60)
            
            # CRITICAL: Only analyze LIVE traffic, never simulation
            features = extract_features_from_logs(time_window_minutes=1, is_simulation=False)
            
            if features is None:
                continue
            
            # Increment windows processed counter
            from middleware import live_mode_stats
            live_mode_stats['windows_processed'] += 1
            
            # Use deterministic detector for live traffic
            detection_result = anomaly_detector.detect(features)
            
            if not detection_result['is_anomaly']:
                continue
            
            # Increment anomaly counter
            live_mode_stats['anomalies_detected'] += 1
            
            # Get anomaly details
            anomaly_type = detection_result['anomaly_type']
            severity = detection_result['severity']
            
            # Generate actionable resolutions
            resolutions = resolution_engine.generate_resolutions(anomaly_type, severity)
            
            db = next(get_db())
            try:
                anomaly_log = AnomalyLog(
                    endpoint=features['endpoint'],
                    method=features['method'],
                    risk_score=detection_result.get('confidence', 0.8) * 100,
                    priority=severity,
                    failure_probability=detection_result['failure_probability'],
                    anomaly_score=detection_result.get('confidence', 0.8),
                    is_anomaly=True,
                    usage_cluster=2,
                    req_count=features['req_count'],
                    error_rate=features['error_rate'],
                    avg_response_time=features['avg_response_time'],
                    max_response_time=features['max_response_time'],
                    payload_mean=features['payload_mean'],
                    unique_endpoints=features['unique_endpoints'],
                    repeat_rate=features['repeat_rate'],
                    status_entropy=features['status_entropy'],
                    anomaly_type=anomaly_type,
                    severity=severity,
                    duration_seconds=60.0,
                    impact_score=detection_result['impact_score'],
                    is_simulation=False  # Live mode anomaly
                )
                db.add(anomaly_log)
                db.commit()
                db.refresh(anomaly_log)
                
                print(f"\n[LIVE] ANOMALY DETECTED: {anomaly_type}")
                print(f"   Endpoint: {features['endpoint']}")
                print(f"   Severity: {severity}")
                print(f"   Impact: {detection_result['impact_score']:.2f}")
                
                await manager.broadcast({
                    'type': 'anomaly',
                    'data': {
                        'id': anomaly_log.id,
                        'timestamp': anomaly_log.timestamp.isoformat(),
                        'endpoint': anomaly_log.endpoint,
                        'method': anomaly_log.method,
                        'risk_score': anomaly_log.risk_score,
                        'priority': anomaly_log.priority,
                        'failure_probability': anomaly_log.failure_probability,
                        'anomaly_score': anomaly_log.anomaly_score,
                        'anomaly_type': anomaly_type,
                        'severity': severity,
                        'duration_seconds': 60.0,
                        'impact_score': detection_result['impact_score'],
                        'resolutions': resolutions[:5],
                        'is_anomaly': anomaly_log.is_anomaly,
                        'usage_cluster': anomaly_log.usage_cluster
                    }
                })
                
            finally:
                db.close()
                
        except Exception as e:
            print(f"Error in periodic anomaly detection: {e}")


@app.post("/login")
async def login(request: LoginRequest, req: Request):
    """
    Mock login endpoint.
    Simulates authentication with variable response times and occasional errors.
    """
    req.state.user_id = request.username
    
    await asyncio.sleep(random.uniform(0.05, 0.3))
    
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
    Mock payment processing endpoint.
    Simulates payment with variable latency and error scenarios.
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
    Mock search endpoint.
    Simulates search with variable response times.
    """
    await asyncio.sleep(random.uniform(0.05, 0.2))
    
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter required")
    
    results = [
        {
            "id": i,
            "title": f"Result {i} for '{query}'",
            "description": f"Description for result {i}",
            "relevance": random.uniform(0.5, 1.0)
        }
        for i in range(1, min(limit, 10) + 1)
    ]
    
    return {
        "query": query,
        "results": results,
        "total": len(results)
    }


@app.get("/health")
async def health():
    """
    Health check endpoint.
    Returns system status and uptime.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@app.get("/api/logs", response_model=list[APILogResponse])
async def get_logs(limit: int = 100, db: Session = Depends(get_db)):
    """
    LIVE MODE ONLY: Retrieve recent API logs from real traffic.
    """
    logs = db.query(APILog).filter(
        (APILog.is_simulation == False) | (APILog.is_simulation == None)
    ).order_by(APILog.timestamp.desc()).limit(limit).all()
    return logs


@app.get("/api/anomalies", response_model=list[AnomalyResponse])
async def get_anomalies(limit: int = 100, db: Session = Depends(get_db)):
    """
    LIVE MODE ONLY: Retrieve anomaly detections from real traffic.
    """
    anomalies = db.query(AnomalyLog).filter(
        (AnomalyLog.is_simulation == False) | (AnomalyLog.is_simulation == None)
    ).order_by(AnomalyLog.timestamp.desc()).limit(limit).all()
    return anomalies


@app.get("/simulation/anomaly-history", response_model=list[AnomalyResponse])
async def get_simulation_anomaly_history(limit: int = 200, db: Session = Depends(get_db)):
    """
    SIMULATION MODE ONLY: Retrieve anomaly history from synthetic traffic.
    """
    anomalies = db.query(AnomalyLog).filter(
        AnomalyLog.is_simulation == True
    ).order_by(AnomalyLog.timestamp.desc()).limit(limit).all()
    return anomalies


@app.get("/api/stats")
@app.get("/api/dashboard")
async def get_stats(db: Session = Depends(get_db)):
    """
    LIVE MODE ONLY: Get system statistics excluding simulation data.
    Returns ONLY real endpoint metrics, never simulation traffic.
    Uses the live_mode_stats counter from middleware for accurate request count.
    """
    # Import to ensure we have the latest value
    from middleware import live_mode_stats as current_live_stats
    
    # Query ONLY live mode logs (is_simulation = False or NULL)
    total_logs = db.query(APILog).filter(
        (APILog.is_simulation == False) | (APILog.is_simulation == None)
    ).count()
    
    # Query ONLY live mode anomalies
    total_anomalies = db.query(AnomalyLog).filter(
        (AnomalyLog.is_simulation == False) | (AnomalyLog.is_simulation == None)
    ).count()
    
    high_priority = db.query(AnomalyLog).filter(
        AnomalyLog.priority == "HIGH",
        (AnomalyLog.is_simulation == False) | (AnomalyLog.is_simulation == None)
    ).count()
    medium_priority = db.query(AnomalyLog).filter(
        AnomalyLog.priority == "MEDIUM",
        (AnomalyLog.is_simulation == False) | (AnomalyLog.is_simulation == None)
    ).count()
    low_priority = db.query(AnomalyLog).filter(
        AnomalyLog.priority == "LOW",
        (AnomalyLog.is_simulation == False) | (AnomalyLog.is_simulation == None)
    ).count()
    
    # Get ONLY live mode recent logs
    recent_logs = db.query(APILog).filter(
        APILog.timestamp >= datetime.utcnow() - timedelta(minutes=5),
        (APILog.is_simulation == False) | (APILog.is_simulation == None)
    ).all()
    
    if recent_logs:
        avg_response = sum(log.response_time_ms for log in recent_logs) / len(recent_logs)
        error_count = sum(1 for log in recent_logs if log.status_code >= 400)
        error_rate = error_count / len(recent_logs) if recent_logs else 0
    else:
        avg_response = 0
        error_rate = 0
    
    # Calculate real-time metrics from middleware
    live_avg_response = sum(current_live_stats['response_times']) / len(current_live_stats['response_times']) if current_live_stats['response_times'] else avg_response
    live_error_rate = current_live_stats['error_count'] / current_live_stats['total_requests'] if current_live_stats['total_requests'] > 0 else error_rate
    
    print(f"[STATS] Live mode counter: {current_live_stats['total_requests']}, DB logs: {total_logs}, Anomalies: {current_live_stats['anomalies_detected']}")
    
    return {
        "mode": "LIVE",
        "total_api_calls": current_live_stats['total_requests'],  # Use middleware counter
        "request_count": current_live_stats['total_requests'],
        "windows_processed": current_live_stats['windows_processed'],
        "total_anomalies": total_anomalies,
        "anomalies_detected": current_live_stats['anomalies_detected'],
        "high_priority": high_priority,
        "medium_priority": medium_priority,
        "low_priority": low_priority,
        "avg_response_time": round(live_avg_response, 2),
        "error_rate": round(live_error_rate, 3),
        "system_health": "healthy" if live_error_rate < 0.1 else "degraded"
    }


@app.get("/api/analytics/endpoint/{endpoint:path}")
async def get_endpoint_analytics(endpoint: str, db: Session = Depends(get_db)):
    """
    LIVE MODE ONLY: Get analytics for a specific endpoint from real traffic.
    """
    if not endpoint.startswith('/'):
        endpoint = '/' + endpoint
    
    logs = db.query(APILog).filter(
        APILog.endpoint == endpoint,
        (APILog.is_simulation == False) | (APILog.is_simulation == None)
    ).all()
    
    if not logs:
        return {
            "endpoint": endpoint,
            "total_requests": 0,
            "error_rate": 0,
            "avg_latency": 0,
            "failure_probability": 0
        }
    
    total_requests = len(logs)
    error_count = sum(1 for log in logs if log.status_code >= 400)
    error_rate = error_count / total_requests
    avg_latency = sum(log.response_time_ms for log in logs) / total_requests
    
    anomalies = db.query(AnomalyLog).filter(
        AnomalyLog.endpoint == endpoint,
        (AnomalyLog.is_simulation == False) | (AnomalyLog.is_simulation == None)
    ).all()
    
    if anomalies:
        avg_failure_prob = sum(a.failure_probability for a in anomalies) / len(anomalies)
    else:
        avg_failure_prob = 0
    
    return {
        "endpoint": endpoint,
        "total_requests": total_requests,
        "error_rate": round(error_rate, 3),
        "avg_latency": round(avg_latency, 2),
        "failure_probability": round(avg_failure_prob, 3)
    }


@app.post("/api/admin/query", response_model=AdminQueryResponse)
async def admin_query(request: AdminQueryRequest, db: Session = Depends(get_db)):
    """
    Process natural language admin queries.
    Supports queries like:
    - "Show high risk APIs in last 10 minutes"
    - "Find anomalies in /payment endpoint"
    - "Show all bot-like behavior"
    """
    query = request.query.lower()
    
    if "high risk" in query or "high priority" in query:
        minutes = 10
        if "last" in query:
            parts = query.split()
            for i, part in enumerate(parts):
                if part == "last" and i + 1 < len(parts):
                    try:
                        minutes = int(parts[i + 1])
                    except:
                        pass
        
        start_time = datetime.utcnow() - timedelta(minutes=minutes)
        anomalies = db.query(AnomalyLog).filter(
            AnomalyLog.priority == "HIGH",
            AnomalyLog.timestamp >= start_time,
            (AnomalyLog.is_simulation == False) | (AnomalyLog.is_simulation == None)
        ).all()
        
        results = [{
            "endpoint": a.endpoint,
            "risk_score": a.risk_score,
            "priority": a.priority,
            "timestamp": a.timestamp.isoformat()
        } for a in anomalies]
        
        return AdminQueryResponse(
            results=results,
            count=len(results),
            query_interpretation=f"Found {len(results)} high risk APIs in last {minutes} minutes"
        )
    
    elif "bot" in query or "cluster 2" in query:
        anomalies = db.query(AnomalyLog).filter(
            AnomalyLog.usage_cluster == 2,
            (AnomalyLog.is_simulation == False) | (AnomalyLog.is_simulation == None)
        ).limit(50).all()
        
        results = [{
            "endpoint": a.endpoint,
            "usage_cluster": a.usage_cluster,
            "req_count": a.req_count,
            "timestamp": a.timestamp.isoformat()
        } for a in anomalies]
        
        return AdminQueryResponse(
            results=results,
            count=len(results),
            query_interpretation=f"Found {len(results)} bot-like behavior patterns"
        )
    
    elif "endpoint" in query or "/" in query:
        endpoint = None
        for part in query.split():
            if part.startswith('/'):
                endpoint = part
                break
        
        if endpoint:
            anomalies = db.query(AnomalyLog).filter(
                AnomalyLog.endpoint == endpoint,
                (AnomalyLog.is_simulation == False) | (AnomalyLog.is_simulation == None)
            ).limit(50).all()
            
            results = [{
                "endpoint": a.endpoint,
                "risk_score": a.risk_score,
                "priority": a.priority,
                "timestamp": a.timestamp.isoformat()
            } for a in anomalies]
            
            return AdminQueryResponse(
                results=results,
                count=len(results),
                query_interpretation=f"Found {len(results)} anomalies for endpoint {endpoint}"
            )
    
    anomalies = db.query(AnomalyLog).filter(
        (AnomalyLog.is_simulation == False) | (AnomalyLog.is_simulation == None)
    ).order_by(AnomalyLog.timestamp.desc()).limit(20).all()
    
    results = [{
        "endpoint": a.endpoint,
        "risk_score": a.risk_score,
        "priority": a.priority,
        "timestamp": a.timestamp.isoformat()
    } for a in anomalies]
    
    return AdminQueryResponse(
        results=results,
        count=len(results),
        query_interpretation="Showing recent anomalies"
    )


@app.post("/api/trigger-detection")
async def trigger_live_detection(db: Session = Depends(get_db)):
    """
    Manually trigger anomaly detection on live traffic.
    Processes the last 1-minute window and broadcasts results.
    """
    from middleware import live_mode_stats
    
    try:
        # Extract features from live traffic
        features = extract_features_from_logs(time_window_minutes=1, is_simulation=False)
        
        if features is None:
            return {
                "success": False,
                "message": "No live traffic data available for analysis",
                "windows_processed": live_mode_stats['windows_processed']
            }
        
        # Increment windows processed
        live_mode_stats['windows_processed'] += 1
        
        # Run detection
        detection_result = anomaly_detector.detect(features)
        
        if detection_result['is_anomaly']:
            # Increment anomaly counter
            live_mode_stats['anomalies_detected'] += 1
            
            anomaly_type = detection_result['anomaly_type']
            severity = detection_result['severity']
            resolutions = resolution_engine.generate_resolutions(anomaly_type, severity)
            
            # Save to database
            anomaly_log = AnomalyLog(
                endpoint=features['endpoint'],
                method=features['method'],
                risk_score=detection_result.get('confidence', 0.8) * 100,
                priority=severity,
                failure_probability=detection_result['failure_probability'],
                anomaly_score=detection_result.get('confidence', 0.8),
                is_anomaly=True,
                usage_cluster=2,
                req_count=features['req_count'],
                error_rate=features['error_rate'],
                avg_response_time=features['avg_response_time'],
                max_response_time=features['max_response_time'],
                payload_mean=features['payload_mean'],
                unique_endpoints=features['unique_endpoints'],
                repeat_rate=features['repeat_rate'],
                status_entropy=features['status_entropy'],
                anomaly_type=anomaly_type,
                severity=severity,
                duration_seconds=60.0,
                impact_score=detection_result['impact_score'],
                is_simulation=False
            )
            db.add(anomaly_log)
            db.commit()
            db.refresh(anomaly_log)
            
            # Broadcast anomaly
            await manager.broadcast({
                'type': 'anomaly',
                'data': {
                    'id': anomaly_log.id,
                    'timestamp': anomaly_log.timestamp.isoformat(),
                    'endpoint': anomaly_log.endpoint,
                    'method': anomaly_log.method,
                    'risk_score': anomaly_log.risk_score,
                    'priority': anomaly_log.priority,
                    'anomaly_type': anomaly_type,
                    'severity': severity,
                    'anomalies_detected': live_mode_stats['anomalies_detected']
                }
            })
            
            return {
                "success": True,
                "anomaly_detected": True,
                "anomaly_type": anomaly_type,
                "severity": severity,
                "windows_processed": live_mode_stats['windows_processed'],
                "anomalies_detected": live_mode_stats['anomalies_detected']
            }
        else:
            return {
                "success": True,
                "anomaly_detected": False,
                "windows_processed": live_mode_stats['windows_processed'],
                "anomalies_detected": live_mode_stats['anomalies_detected']
            }
            
    except Exception as e:
        print(f"[LIVE] Detection error: {e}")
        return {
            "success": False,
            "message": str(e),
            "windows_processed": live_mode_stats['windows_processed']
        }


# ============================================================================
# SIMULATION ENDPOINTS
# ============================================================================

@app.get("/simulation/injection-status")
async def get_injection_status():
    """
    Get status of anomaly injections for all endpoints.
    Shows which anomaly type is assigned to each endpoint and if it's currently active.
    """
    status = anomaly_injector.get_injection_status()
    return {
        "status": "success",
        "injection_map": {
            endpoint: anomaly_type.value 
            for endpoint, anomaly_type in ENDPOINT_ANOMALY_MAP.items()
        },
        "active_injections": status
    }


@app.post("/simulation/reset-injections")
async def reset_injections():
    """
    Reset all anomaly injections with new timings.
    """
    anomaly_injector.reset_injections()
    return {
        "status": "success",
        "message": "Anomaly injections reset with new timings"
    }


@app.post("/simulation/start")
async def start_simulation(
    background_tasks: BackgroundTasks,
    simulated_endpoint: str,
    duration_seconds: int = 60,
    requests_per_window: int = 10
):
    """
    Start simulation with synthetic traffic
    """
    global simulation_active, simulation_stats
    
    if simulation_active:
        raise HTTPException(status_code=400, detail="Simulation already running")
    
    simulation_active = True
    simulation_anomaly_recorded.clear()
    simulation_stats = {
        'total_requests': 0,
        'windows_processed': 0,
        'anomalies_detected': 0,
        'start_time': time.time(),
        'simulated_endpoint': simulated_endpoint
    }
    
    # Start simulation in background
    background_tasks.add_task(
        run_simulation,
        simulated_endpoint=simulated_endpoint,
        duration_seconds=duration_seconds,
        requests_per_window=requests_per_window
    )
    
    return {
        "status": "started",
        "simulated_endpoint": simulated_endpoint,
        "duration_seconds": duration_seconds
    }


@app.post("/simulation/stop")
async def stop_simulation():
    """Stop running simulation and reset tracking"""
    global simulation_active, simulation_stats, simulation_anomaly_recorded
    
    simulation_anomaly_recorded.clear()
    if not simulation_active:
        raise HTTPException(status_code=400, detail="No simulation running")
    
    simulation_active = False
    
    final_stats = simulation_stats.copy()
    
    print(f"[SIMULATION] Stopped. Final stats: {final_stats}")
    
    return {
        "status": "stopped",
        "stats": final_stats
    }


@app.get("/simulation/stats")
async def get_simulation_stats():
    """Get current simulation statistics with detailed tracking"""
    global simulation_stats, simulation_active, simulation_anomaly_recorded
    
    return {
        'mode': 'SIMULATION',
        'active': simulation_active,
        'total_requests': simulation_stats['total_requests'],
        'windows_processed': simulation_stats['windows_processed'],
        'anomalies_detected': simulation_stats['anomalies_detected'],
        'simulated_endpoint': simulation_stats.get('simulated_endpoint', 'none'),
        'start_time': simulation_stats.get('start_time'),
        'anomaly_recorded_for_endpoint': list(simulation_anomaly_recorded)
    }


async def run_simulation(simulated_endpoint: str, duration_seconds: int, requests_per_window: int = 100):
    """
    Run simulation - generates synthetic traffic and detects anomalies
    High-RPS bursts with proper state tracking and console logging
    """
    global simulation_active, simulation_stats
    
    print(f"\n{'='*70}")
    print(f"🎬 SIMULATION STARTED")
    print(f"{'='*70}")
    print(f"   Endpoint: {simulated_endpoint}")
    print(f"   Duration: {duration_seconds}s")
    print(f"   Target RPS: 100+")
    print(f"{'='*70}\n")
    
    start_time = time.time()
    total_requests = 0
    batch_size = 100  # Target >=100 RPS burst size
    
    try:
        while simulation_active and (time.time() - start_time) < duration_seconds:
            # Generate synthetic requests in high-RPS batches
            for i in range(batch_size):
                if not simulation_active:
                    break
                    
                # Create base synthetic log
                base_log = {
                    'endpoint': simulated_endpoint,
                    'method': random.choice(["GET", "POST"]),
                    'response_time_ms': random.uniform(100, 300),  # Normal baseline
                    'status_code': 200,  # Start with success
                    'payload_size': random.randint(500, 2000),  # Normal size
                    'ip_address': f"SIM-{random.randint(1, 255)}",
                    'user_id': f"sim_user_{random.randint(1, 100)}"
                }
                
                # INJECT ANOMALY: Modify log based on endpoint's assigned anomaly
                modified_log = inject_anomaly_into_log(simulated_endpoint, base_log)
                
                # Save to database
                db = SessionLocal()
                try:
                    log_entry = APILog(
                        endpoint=modified_log['endpoint'],
                        method=modified_log['method'],
                        response_time_ms=modified_log['response_time_ms'],
                        status_code=modified_log['status_code'],
                        payload_size=modified_log['payload_size'],
                        ip_address=modified_log['ip_address'],
                        user_id=modified_log['user_id'],
                        is_simulation=True  # CRITICAL: Mark as simulation data
                    )
                    db.add(log_entry)
                    db.commit()
                    total_requests += 1
                    simulation_stats['total_requests'] = total_requests
                    
                    # Log with anomaly indicator
                    if '_injected_anomaly' in modified_log:
                        anomaly_info = modified_log['_injected_anomaly']
                        print(f"[SIM] Request #{total_requests} - {simulated_endpoint} [{anomaly_info['type']} - {anomaly_info['severity']}]")
                    else:
                        print(f"[SIM] Request #{total_requests} - {simulated_endpoint} [NORMAL]")
                    
                finally:
                    db.close()
            
            # Run DETERMINISTIC anomaly detection on SIMULATION data each batch
            features = extract_features_from_logs(time_window_minutes=1, is_simulation=True)
            if features:
                # Use deterministic detector instead of ML model
                detection_result = anomaly_detector.detect(features)
                simulation_stats['windows_processed'] += 1
                
                if detection_result['is_anomaly']:
                    # Enforce at most one persisted anomaly per simulated endpoint per run
                    if simulated_endpoint in simulation_anomaly_recorded:
                        continue
                    simulation_anomaly_recorded.add(simulated_endpoint)
                    simulation_stats['anomalies_detected'] += 1
                    
                    assigned_anomaly = ENDPOINT_ANOMALY_MAP.get(simulated_endpoint)
                    anomaly_type = detection_result['anomaly_type'] if detection_result['anomaly_type'] else (assigned_anomaly.value if assigned_anomaly else 'unknown')
                    severity = detection_result['severity']
                    resolutions = resolution_engine.generate_resolutions(anomaly_type, severity)
                    window_duration = 60.0
                    
                    db = SessionLocal()
                    try:
                        anomaly_log = AnomalyLog(
                            endpoint=features['endpoint'],
                            method=features['method'],
                            risk_score=detection_result.get('confidence', 0.8) * 100,
                            priority=severity,
                            failure_probability=detection_result['failure_probability'],
                            anomaly_score=detection_result.get('confidence', 0.8),
                            is_anomaly=True,
                            usage_cluster=2,
                            req_count=features['req_count'],
                            error_rate=features['error_rate'],
                            avg_response_time=features['avg_response_time'],
                            max_response_time=features['max_response_time'],
                            payload_mean=features['payload_mean'],
                            unique_endpoints=features['unique_endpoints'],
                            repeat_rate=features['repeat_rate'],
                            status_entropy=features['status_entropy'],
                            anomaly_type=anomaly_type,
                            severity=severity,
                            duration_seconds=window_duration,
                            impact_score=detection_result['impact_score'],
                            is_simulation=True
                        )
                        db.add(anomaly_log)
                        db.commit()
                        db.refresh(anomaly_log)
                        
                        await manager.broadcast({
                            'type': 'anomaly',
                            'data': {
                                'id': anomaly_log.id,
                                'timestamp': anomaly_log.timestamp.isoformat(),
                                'endpoint': anomaly_log.endpoint,
                                'anomaly_type': anomaly_type,
                                'severity': severity,
                                'duration_seconds': window_duration,
                                'impact_score': detection_result['impact_score'],
                                'failure_probability': detection_result['failure_probability'],
                                'resolutions': resolutions[:3],
                                'method': anomaly_log.method,
                                'risk_score': anomaly_log.risk_score,
                                'priority': anomaly_log.priority,
                                'failure_probability': anomaly_log.failure_probability,
                                'is_anomaly': anomaly_log.is_anomaly
                            }
                        })
                        
                        print(f"\n🚨 [SIMULATION] Anomaly Detected!")
                        print(f"   Endpoint: {simulated_endpoint}")
                        print(f"   Type: {anomaly_type}")
                        print(f"   Severity: {severity}")
                        print(f"   Impact: {detection_result['impact_score']:.2f}")
                        print(f"   Recorded: {simulated_endpoint in simulation_anomaly_recorded}")
                    finally:
                        db.close()
            
            # Small delay between batches
            # Keep bursts fast; small pause to avoid DB lock
            await asyncio.sleep(0.1)
            
            # Print progress every batch
            elapsed = time.time() - start_time
            rps = total_requests / elapsed if elapsed > 0 else 0
            print(f"[SIM] Progress: {total_requests} requests | {rps:.0f} RPS | {simulation_stats['anomalies_detected']} anomalies")
    
    except Exception as e:
        print(f"\n❌ Simulation error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        simulation_active = False
        elapsed = time.time() - start_time
        print(f"\n{'='*70}")
        print(f"✓ SIMULATION COMPLETED")
        print(f"{'='*70}")
        print(f"   Total Requests: {total_requests}")
        print(f"   Duration: {elapsed:.2f}s")
        print(f"   Avg RPS: {total_requests/elapsed if elapsed > 0 else 0:.0f}")
        print(f"   Anomalies Detected: {simulation_stats['anomalies_detected']}")
        print(f"{'='*70}\n")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time anomaly streaming.
    """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            
            if data == "ping":
                await manager.send_personal_message({"type": "pong"}, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# Enhanced Simulation Endpoints
@app.post("/api/simulation/start-enhanced")
async def start_enhanced_simulation(
    background_tasks: BackgroundTasks,
    duration_seconds: int = 60,
    target_rps: int = 200
):
    """
    Start enhanced high-speed simulation (>150 req/sec)
    Generates traffic for ALL endpoints with proper anomaly injection
    """
    if enhanced_simulation_engine.active:
        raise HTTPException(status_code=400, detail="Simulation already running")
    
    # Set websocket manager for real-time updates
    enhanced_simulation_engine.set_websocket_manager(manager)
    
    # Start simulation in background
    background_tasks.add_task(
        enhanced_simulation_engine.run,
        duration_seconds=duration_seconds,
        target_rps=target_rps
    )
    
    return {
        "status": "started",
        "target_rps": target_rps,
        "duration_seconds": duration_seconds,
        "endpoints": list(enhanced_simulation_engine.ENDPOINT_ANOMALIES.keys())
    }


@app.post("/api/simulation/stop-enhanced")
async def stop_enhanced_simulation():
    """Stop enhanced simulation"""
    if not enhanced_simulation_engine.active:
        raise HTTPException(status_code=400, detail="No simulation running")
    
    enhanced_simulation_engine.stop()
    stats = enhanced_simulation_engine.get_stats()
    
    return {
        "status": "stopped",
        "stats": stats
    }


@app.get("/api/simulation/stats-enhanced")
async def get_enhanced_simulation_stats():
    """Get enhanced simulation statistics"""
    return enhanced_simulation_engine.get_stats()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
