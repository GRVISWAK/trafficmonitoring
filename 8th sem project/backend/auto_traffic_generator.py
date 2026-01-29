"""
Auto-Detection Traffic Simulator
Generates mixed traffic patterns for ML-based anomaly detection
NO pre-labeled anomaly types - ML models determine the anomaly category
"""
import random
import time
from typing import Dict, List


class AutoDetectionTrafficGenerator:
    """
    Generates realistic traffic with mixed patterns:
    - Normal baseline traffic
    - Rate variations (bursts, spikes)
    - Payload variations (small, large)
    - Error patterns (scattered, bursts)
    - Parameter repetitions (bot-like)
    - Timing variations (fast, slow)
    
    ML models analyze the aggregated window features to detect anomaly type.
    """
    
    # Virtual endpoints (simulation only)
    VIRTUAL_ENDPOINTS = ['/sim/login', '/sim/search', '/sim/profile', '/sim/payment', '/sim/signup']
    
    # User agents for diversity
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/96.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1',
        'Mozilla/5.0 (X11; Linux x86_64) Firefox/95.0',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0) Safari/604.1',
        'Mozilla/5.0 (Android 12; Mobile) Chrome/96.0',
        'PostmanRuntime/7.28.4',
        'curl/7.64.1',
        'python-requests/2.26.0',
        'bot/1.0',
        'scanner/2.0'
    ]
    
    def __init__(self):
        self.pattern_counter = 0
        self.session_params = {}  # For simulating repeated params
    
    def generate_traffic(self, simulated_endpoint: str, count: int = 10) -> List[Dict]:
        """
        Generate mixed traffic patterns for a single endpoint.
        
        Randomly selects from different traffic behaviors:
        - 40% Normal baseline
        - 15% Rate burst (fast requests)
        - 15% Large payloads
        - 10% Error-prone (scanning/probing)
        - 10% Bot-like (repeated params)
        - 10% Mixed anomalies
        
        Args:
            simulated_endpoint: Virtual endpoint to target
            count: Number of requests to generate
        
        Returns:
            List of request dictionaries
        """
        if simulated_endpoint not in self.VIRTUAL_ENDPOINTS:
            raise ValueError(f"Invalid endpoint. Must be one of: {self.VIRTUAL_ENDPOINTS}")
        
        requests = []
        
        # Decide traffic pattern for this batch
        pattern_choice = random.random()
        
        if pattern_choice < 0.40:
            # 40% Normal baseline traffic
            requests = self._generate_normal_baseline(simulated_endpoint, count)
        elif pattern_choice < 0.55:
            # 15% Rate burst (DDoS-like)
            requests = self._generate_rate_burst(simulated_endpoint, count)
        elif pattern_choice < 0.70:
            # 15% Large payloads (data exfiltration)
            requests = self._generate_payload_variation(simulated_endpoint, count)
        elif pattern_choice < 0.80:
            # 10% Error-prone (scanning/probing)
            requests = self._generate_error_pattern(simulated_endpoint, count)
        elif pattern_choice < 0.90:
            # 10% Bot-like (repeated params)
            requests = self._generate_bot_pattern(simulated_endpoint, count)
        else:
            # 10% Mixed anomalies
            requests = self._generate_mixed_patterns(simulated_endpoint, count)
        
        self.pattern_counter += 1
        return requests
    
    def _generate_normal_baseline(self, endpoint: str, count: int) -> List[Dict]:
        """Generate normal, clean baseline traffic"""
        requests = []
        for i in range(count):
            requests.append({
                'method': 'POST' if endpoint in ['/sim/login', '/sim/payment', '/sim/signup'] else 'GET',
                'path': endpoint,
                'status': random.choice([200, 200, 200, 201]),  # Mostly 200
                'latency': random.uniform(0.05, 0.3),  # Normal latency (50-300ms)
                'payload_size': random.randint(100, 800),  # Small payloads
                'user_agent': random.choice(self.USER_AGENTS[:6]),  # Normal browsers
                'parameters': self._generate_varied_params(i),
                'timestamp': time.time()
            })
        return requests
    
    def _generate_rate_burst(self, endpoint: str, count: int) -> List[Dict]:
        """Generate high-rate traffic burst (DDoS pattern)"""
        requests = []
        # Generate MORE requests to simulate burst
        actual_count = count * 3  # 3x multiplier for rate spike
        
        for i in range(actual_count):
            requests.append({
                'method': 'POST',
                'path': endpoint,
                'status': random.choice([200, 429, 503, 503]),  # More rate limits
                'latency': random.uniform(0.001, 0.02),  # Very fast (1-20ms)
                'payload_size': random.randint(50, 200),  # Small payloads
                'user_agent': random.choice(self.USER_AGENTS),
                'parameters': {'burst_id': i, 'wave': self.pattern_counter},
                'timestamp': time.time()
            })
        return requests
    
    def _generate_payload_variation(self, endpoint: str, count: int) -> List[Dict]:
        """Generate traffic with large payload variations"""
        requests = []
        for i in range(count):
            # Mix of normal and large payloads
            is_large = random.random() < 0.7  # 70% large payloads
            
            requests.append({
                'method': 'POST',
                'path': endpoint,
                'status': random.choice([200, 413, 400]) if is_large else 200,
                'latency': random.uniform(0.5, 2.0) if is_large else random.uniform(0.05, 0.3),
                'payload_size': random.randint(8000, 50000) if is_large else random.randint(100, 800),
                'user_agent': random.choice(self.USER_AGENTS),
                'parameters': {'data_size': 'large' if is_large else 'normal'},
                'timestamp': time.time()
            })
        return requests
    
    def _generate_error_pattern(self, endpoint: str, count: int) -> List[Dict]:
        """Generate traffic with high error rate (scanning/probing)"""
        requests = []
        error_rate = 0.75  # 75% errors
        
        for i in range(count):
            is_error = random.random() < error_rate
            
            requests.append({
                'method': random.choice(['GET', 'POST', 'PUT', 'DELETE']),
                'path': endpoint,
                'status': random.choice([400, 401, 403, 404, 500]) if is_error else 200,
                'latency': random.uniform(0.02, 0.15),
                'payload_size': random.randint(0, 300),
                'user_agent': random.choice(self.USER_AGENTS),
                'parameters': {'probe': f'scan_{i}', 'test': random.randint(1, 100)},
                'timestamp': time.time()
            })
        return requests
    
    def _generate_bot_pattern(self, endpoint: str, count: int) -> List[Dict]:
        """Generate bot-like traffic (repeated parameters, low entropy)"""
        requests = []
        
        # Use SAME parameters for all requests (bot signature)
        if endpoint not in self.session_params:
            self.session_params[endpoint] = {
                'user_id': f'user_{random.randint(1000, 9999)}',
                'session': f'sess_{random.randint(10000, 99999)}',
                'token': f'tok_{random.randint(100000, 999999)}'
            }
        
        repeated_params = self.session_params[endpoint]
        bot_agent = random.choice(['bot/1.0', 'scanner/2.0', 'automated-tool'])
        
        for i in range(count):
            requests.append({
                'method': 'POST',
                'path': endpoint,
                'status': random.choice([200, 401, 403]),
                'latency': random.uniform(0.03, 0.12),  # Consistent timing
                'payload_size': random.randint(200, 400),  # Consistent size
                'user_agent': bot_agent,  # SAME agent
                'parameters': repeated_params,  # SAME params
                'timestamp': time.time()
            })
        return requests
    
    def _generate_mixed_patterns(self, endpoint: str, count: int) -> List[Dict]:
        """Generate mixed anomaly patterns in one batch"""
        requests = []
        
        for i in range(count):
            # Randomly select a pattern for each request
            pattern = random.choice(['rate', 'payload', 'error', 'bot'])
            
            if pattern == 'rate':
                req = self._generate_rate_burst(endpoint, 1)[0]
            elif pattern == 'payload':
                req = self._generate_payload_variation(endpoint, 1)[0]
            elif pattern == 'error':
                req = self._generate_error_pattern(endpoint, 1)[0]
            else:  # bot
                req = self._generate_bot_pattern(endpoint, 1)[0]
            
            requests.append(req)
        
        return requests
    
    def _generate_varied_params(self, index: int) -> Dict:
        """Generate varied parameters for normal traffic"""
        return {
            'user_id': f'user_{random.randint(1000, 9999)}',
            'session': f'sess_{random.randint(10000, 99999)}',
            'request_id': f'req_{index}_{random.randint(100, 999)}',
            'timestamp': int(time.time())
        }


# Global instance
auto_traffic_generator = AutoDetectionTrafficGenerator()
