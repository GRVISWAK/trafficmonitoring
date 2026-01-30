"""
Enhanced Request Logging Middleware for LIVE MODE
Captures detailed request data and feeds to sliding window
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
from database import SessionLocal, APILog
from window_manager import live_window_manager
from inference_enhanced import HybridDetectionEngine
from mode_isolation import live_manager
from typing import Optional
import json


class EnhancedLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for LIVE MODE - STRICT WHITELISTING
    
    ONLY tracks real API traffic to whitelisted endpoints.
    NO background jobs, schedulers, or synthetic traffic.
    
    WHITELIST: /login, /signup, /search, /profile, /payment, /logout
    BLACKLIST: Everything else (/, /health, /metrics, /docs, /api/*, /ws, etc.)
    """
    
    # WHITELIST - ONLY these endpoints are tracked
    WHITELISTED_ENDPOINTS = {
        '/login',
        '/signup', 
        '/search',
        '/profile',
        '/payment',
        '/logout'
    }
    
    def __init__(self, app, detection_engine: Optional[HybridDetectionEngine] = None):
        super().__init__(app)
        self.detection_engine = detection_engine or HybridDetectionEngine()
        
    async def dispatch(self, request: Request, call_next):
        # STRICT FILTERING
        # 1. Ignore CORS preflight requests (OPTIONS method)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # 2. Ignore non-whitelisted endpoints
        if request.url.path not in self.WHITELISTED_ENDPOINTS:
            return await call_next(request)
        
        # 3. Only GET/POST allowed (prevent HEAD, TRACE, etc.)
        if request.method not in ["GET", "POST"]:
            return await call_next(request)
        
        start_time = time.time()
        
        # Extract request data
        method = request.method
        path = request.url.path
        user_agent = request.headers.get('user-agent', 'unknown')
        
        # Extract query parameters
        parameters = dict(request.query_params)
        
        # Get payload size for POST/PUT/PATCH
        body = None
        payload_size = 0
        
        if method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                payload_size = len(body) if body else 0
                
                # Try to parse parameters from JSON body
                if body:
                    try:
                        body_params = json.loads(body)
                        if isinstance(body_params, dict):
                            parameters.update(body_params)
                    except:
                        pass
                
                # Restore body for endpoint processing
                async def receive():
                    return {"type": "http.request", "body": body}
                
                request._receive = receive
            except:
                payload_size = 0
        
        # Process request
        response = await call_next(request)
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        status_code = response.status_code
        
        # Store in database (exactly once per whitelisted request)
        db = SessionLocal()
        try:
            log_entry = APILog(
                endpoint=path,
                method=method,
                response_time_ms=latency_ms,
                status_code=status_code,
                payload_size=payload_size,
                ip_address=request.client.host if request.client else "unknown",
                user_id=getattr(request.state, "user_id", None)
            )
            db.add(log_entry)
            db.commit()
            
            # Increment live manager counter ONLY after successful DB commit
            # This ensures exactly 1 count per manual API call
            live_manager.increment_request(path, latency_ms, status_code)
        except Exception as e:
            print(f"Error logging to database: {e}")
            # If DB fails, don't increment counter
        finally:
            db.close()
        
        # Feed to sliding window (LIVE MODE) - ONLY for feature extraction
        features = live_window_manager.add_request(
            method=method,
            path=path,
            status=status_code,
            latency=latency_ms,
            payload_size=payload_size,
            user_agent=user_agent,
            parameters=parameters
        )
        
        # If window is full, run ML inference
        if features:
            try:
                prediction = self.detection_engine.predict_anomaly(features)
                
                # Store prediction result
                print(f"\n🔍 LIVE MODE DETECTION (Window #{features['window_id']}):")
                print(f"   Risk Score: {prediction['risk_score']:.4f}")
                print(f"   Priority: {prediction['priority']}")
                print(f"   Is Anomaly: {prediction['is_anomaly']}")
                print(f"   Detection Method: {prediction['detection_method']}")
                if 'details' in prediction and prediction['details'].get('rule_alerts'):
                    print(f"   Rule Alerts: {', '.join(prediction['details']['rule_alerts'])}")
                print(f"   Latency: {prediction['detection_latency_ms']:.2f}ms\n")
                
                # Broadcast via WebSocket (will implement in app.py)
                # This will be handled by the app when we update it
                
            except Exception as e:
                print(f"Error in ML inference: {e}")
        
        return response


def get_live_stats():
    """
    Uses isolated live manager for strict mode separation.
    Returns zero counts if no real traffic has occurred.
    """
    window_info = live_window_manager.get_window_info()
    live_stats = live_manager.get_stats()

    return {
        'mode': 'LIVE',
        'total_requests': live_stats['total_requests'],
        'current_window_count': window_info['current_count'],
        'windows_processed': window_info['windows_processed'],
        'window_size': window_info['window_size'],
        'is_window_full': window_info['is_full'],
        'last_inference': window_info['last_inference'],
        'status': 'active' if live_stats['total_requests'] > 0 else 'idle'
    }
