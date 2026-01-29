"""
Sliding Window Manager for Request Aggregation and ML Inference
Supports both LIVE and SIMULATION modes
"""
import time
import numpy as np
from collections import deque
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import hashlib


class RequestWindow:
    """Stores data for a single request in the sliding window"""
    def __init__(self, method: str, path: str, status: int, latency: float, 
                 payload_size: int, user_agent: str, timestamp: float, parameters: Dict = None):
        self.method = method
        self.path = path
        self.status = status
        self.latency = latency
        self.payload_size = payload_size
        self.user_agent = user_agent
        self.timestamp = timestamp
        self.parameters = parameters or {}


class SlidingWindowManager:
    """
    Manages sliding windows of requests for ML inference
    
    Features:
    - Maintains window of last N requests
    - Extracts 9 behavioral features per window
    - Triggers ML inference when window is full
    - Supports LIVE and SIMULATION modes
    """
    
    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.requests = deque(maxlen=window_size)
        self.window_count = 0
        self.last_inference_time = None
        
    def add_request(self, method: str, path: str, status: int, latency: float,
                   payload_size: int, user_agent: str, parameters: Dict = None) -> Optional[Dict]:
        """
        Add a request to the sliding window (FEATURE EXTRACTION ONLY)
        
        NOTE: This method DOES NOT increment request counters.
        Request counting happens in middleware BEFORE calling this method.
        This only aggregates requests for ML feature extraction.
        
        Returns:
            Features dict if window is full and ready for inference, None otherwise
        """
        request = RequestWindow(
            method=method,
            path=path,
            status=status,
            latency=latency,
            payload_size=payload_size,
            user_agent=user_agent,
            timestamp=time.time(),
            parameters=parameters
        )
        
        self.requests.append(request)
        
        # Extract features when window is full (window_count is for tracking windows, not requests)
        if len(self.requests) >= self.window_size:
            self.window_count += 1  # Increment window counter (NOT request counter)
            features = self._extract_features()
            self.last_inference_time = time.time()
            return features
        
        return None
    
    def _extract_features(self) -> Dict:
        """
        Extract 9 behavioral features from current window
        
        Features:
        1. request_rate - Requests per time unit
        2. unique_endpoint_count - Distinct endpoints accessed
        3. method_ratio - GET/POST ratio
        4. avg_payload_size - Average payload size
        5. error_rate - Percentage of 4xx/5xx errors
        6. repeated_parameter_ratio - Parameter repetition
        7. user_agent_entropy - Shannon entropy of user agents
        8. avg_response_time - Average latency
        9. max_response_time - Max latency
        """
        if len(self.requests) == 0:
            return None
        
        requests_list = list(self.requests)
        
        # 1. request_rate (requests per second)
        time_span = max(requests_list[-1].timestamp - requests_list[0].timestamp, 0.1)
        request_rate = len(requests_list) / time_span
        
        # 2. unique_endpoint_count
        unique_endpoints = len(set(r.path for r in requests_list))
        
        # 3. method_ratio (GET to POST ratio)
        get_count = sum(1 for r in requests_list if r.method == 'GET')
        post_count = sum(1 for r in requests_list if r.method == 'POST')
        method_ratio = get_count / max(post_count, 1)
        
        # 4. avg_payload_size
        avg_payload_size = np.mean([r.payload_size for r in requests_list])
        
        # 5. error_rate (4xx and 5xx errors)
        error_count = sum(1 for r in requests_list if r.status >= 400)
        error_rate = error_count / len(requests_list)
        
        # 6. repeated_parameter_ratio
        repeated_parameter_ratio = self._calculate_parameter_repetition(requests_list)
        
        # 7. user_agent_entropy
        user_agent_entropy = self._calculate_entropy([r.user_agent for r in requests_list])
        
        # 8. avg_response_time
        avg_response_time = np.mean([r.latency for r in requests_list])
        
        # 9. max_response_time
        max_response_time = np.max([r.latency for r in requests_list])
        
        return {
            'request_rate': float(request_rate),
            'unique_endpoint_count': int(unique_endpoints),
            'method_ratio': float(method_ratio),
            'avg_payload_size': float(avg_payload_size),
            'error_rate': float(error_rate),
            'repeated_parameter_ratio': float(repeated_parameter_ratio),
            'user_agent_entropy': float(user_agent_entropy),
            'avg_response_time': float(avg_response_time),
            'max_response_time': float(max_response_time),
            'window_id': self.window_count,
            'timestamp': datetime.now().isoformat(),
            'request_count': len(requests_list)
        }
    
    def _calculate_parameter_repetition(self, requests: List[RequestWindow]) -> float:
        """Calculate ratio of repeated parameters across requests"""
        all_params = []
        for req in requests:
            if req.parameters:
                all_params.extend(req.parameters.keys())
        
        if len(all_params) == 0:
            return 0.0
        
        unique_params = len(set(all_params))
        return 1.0 - (unique_params / len(all_params))
    
    def _calculate_entropy(self, values: List[str]) -> float:
        """Calculate Shannon entropy of string values"""
        if not values:
            return 0.0
        
        # Count occurrences
        value_counts = {}
        for val in values:
            value_counts[val] = value_counts.get(val, 0) + 1
        
        # Calculate entropy
        total = len(values)
        entropy = 0.0
        for count in value_counts.values():
            if count > 0:
                p = count / total
                entropy -= p * np.log2(p)
        
        return float(entropy)
    
    def get_window_info(self) -> Dict:
        """Get current window status"""
        return {
            'window_size': self.window_size,
            'current_count': len(self.requests),
            'windows_processed': self.window_count,
            'is_full': len(self.requests) >= self.window_size,
            'last_inference': self.last_inference_time
        }
    
    def reset(self):
        """Clear the window"""
        self.requests.clear()
        self.window_count = 0


# Global window managers for different modes
live_window_manager = SlidingWindowManager(window_size=10)
simulation_window_manager = SlidingWindowManager(window_size=10)
