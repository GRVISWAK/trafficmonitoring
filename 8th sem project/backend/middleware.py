from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
from database import SessionLocal, APILog
import sys

# Live mode stats - separate from simulation
live_mode_stats = {
    'total_requests': 0,
    'start_time': None,
    'windows_processed': 0,
    'anomalies_detected': 0,
    'total_response_time': 0.0,
    'error_count': 0,
    'response_times': []  # Keep last 100 for rolling average
}

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
        
        # Track LIVE requests - exclude monitoring/admin endpoints
        excluded_paths = ["/ws", "/docs", "/openapi.json", "/favicon.ico", "/api/", "/simulation/"]
        is_live_request = not any(endpoint.startswith(path) for path in excluded_paths)
        
        if endpoint not in ["/ws", "/docs", "/openapi.json", "/favicon.ico"]:
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
                    is_simulation=False  # This is a REAL live request
                )
                db.add(log_entry)
                db.commit()
                
                # Increment LIVE mode counter ONLY for real endpoint hits
                if is_live_request:
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
                    
                    # Broadcast live metrics update via WebSocket
                    try:
                        from websocket import manager
                        import asyncio
                        
                        metrics_update = {
                            "type": "live_metrics_update",
                            "data": {
                                "request_count": live_mode_stats['total_requests'],
                                "windows_processed": live_mode_stats['windows_processed'],
                                "avg_response_time": round(avg_response_time, 2),
                                "error_rate": round(error_rate * 100, 2),
                                "anomalies_detected": live_mode_stats['anomalies_detected'],
                                "endpoint": endpoint,
                                "method": method,
                                "status_code": status_code
                            }
                        }
                        
                        # Create async task to broadcast (don't await to avoid blocking)
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(manager.broadcast(metrics_update))
                    except Exception as ws_error:
                        print(f"[LIVE] WebSocket broadcast error: {ws_error}")
                    
            except Exception as e:
                print(f"Error logging API call: {e}", file=sys.stderr)
                db.rollback()
            finally:
                db.close()
        
        return response
