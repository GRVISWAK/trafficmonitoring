from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
from database import SessionLocal, APILog
import sys

# Live mode stats - ONLY real endpoint hits
live_mode_stats = {
    'total_requests': 0,
    'start_time': None,
    'windows_processed': 0,
    'anomalies_detected': 0,
    'total_response_time': 0.0,
    'error_count': 0,
    'response_times': []
}

# ONLY these endpoints count as live traffic
LIVE_ENDPOINTS = {'/login', '/payment', '/search', '/profile', '/signup', '/logout'}

class LoggingMiddleware(BaseHTTPMiddleware):
    """Tracks ONLY LIVE MODE requests from real endpoint hits."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        body = None
        payload_size = 0
        
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                payload_size = len(body) if body else 0
                
                async def receive():
                    return {"type": "http.request", "body": body}
                
                request._receive = receive
            except:
                payload_size = 0
        
        response = await call_next(request)
        
        process_time = (time.time() - start_time) * 1000
        
        endpoint = request.url.path
        method = request.method
        status_code = response.status_code
        ip_address = request.client.host if request.client else "unknown"
        
        user_id = None
        if hasattr(request.state, "user_id"):
            user_id = request.state.user_id
        
        # CRITICAL: Only count real business endpoints as live traffic
        is_live_request = endpoint in LIVE_ENDPOINTS
        
        # Only log and count LIVE endpoints
        if is_live_request:
            db = SessionLocal()
            try:
                log_entry = APILog(
                    endpoint=endpoint,
                    method=method,
                    response_time_ms=process_time,
                    status_code=status_code,
                    payload_size=payload_size,
                    ip_address=ip_address,
                    user_id=user_id,
                    is_simulation=False
                )
                db.add(log_entry)
                db.commit()
                
                # Increment LIVE mode counter
                if True:
                    global live_mode_stats
                    live_mode_stats['total_requests'] += 1
                    if live_mode_stats['start_time'] is None:
                        live_mode_stats['start_time'] = time.time()
                    
                    # Track response time
                    live_mode_stats['total_response_time'] += process_time
                    live_mode_stats['response_times'].append(process_time)
                    if len(live_mode_stats['response_times']) > 100:
                        live_mode_stats['response_times'].pop(0)
                    
                    # Track errors
                    if status_code >= 400:
                        live_mode_stats['error_count'] += 1
                    
                    # Calculate metrics
                    avg_response_time = sum(live_mode_stats['response_times']) / len(live_mode_stats['response_times']) if live_mode_stats['response_times'] else 0
                    error_rate = live_mode_stats['error_count'] / live_mode_stats['total_requests'] if live_mode_stats['total_requests'] > 0 else 0
                    
                    print(f"[LIVE] Request #{live_mode_stats['total_requests']}: {method} {endpoint} - {process_time:.2f}ms - Status {status_code}")
                    
            except Exception as e:
                print(f"Error logging API call: {e}", file=sys.stderr)
                db.rollback()
            finally:
                db.close()
        
        return response
