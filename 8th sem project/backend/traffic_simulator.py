"""
Traffic Simulation Module
Generates synthetic API traffic with configurable anomaly injection
"""
import random
import time
import numpy as np
from typing import Dict, List
from datetime import datetime


class TrafficSimulator:
    """
    Generates synthetic API traffic for testing and demonstration
    
    Modes:
    - NORMAL: Typical API usage patterns
    - RATE_SPIKE: DDoS-like traffic bursts
    - ERROR_BURST: High error rates (scanning/injection)
    - BOT_ATTACK: Low entropy user agents + repeated parameters
    - LARGE_PAYLOAD: Data exfiltration patterns
    - ENDPOINT_SCAN: Reconnaissance behavior
    - MIXED: Combination of anomalies
    """
    
    ENDPOINTS = [
        '/login', '/payment', '/search', '/profile', '/settings',
        '/logout', '/data', '/upload', '/download', '/admin',
        '/users', '/products', '/orders', '/cart', '/checkout'
    ]
    
    METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/96.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1',
        'Mozilla/5.0 (X11; Linux x86_64) Firefox/95.0',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0) Safari/604.1',
        'Mozilla/5.0 (Android 12; Mobile) Chrome/96.0',
        'PostmanRuntime/7.28.4',
        'curl/7.64.1',
        'python-requests/2.26.0'
    ]
    
    BOT_AGENTS = [
        'bot-scanner-v1.0',
        'automated-tool',
        'python-bot'
    ]
    
    def __init__(self):
        self.request_count = 0
        
    def generate_normal_traffic(self, count: int = 10) -> List[Dict]:
        """Generate normal API traffic"""
        requests = []
        
        for _ in range(count):
            endpoint = random.choice(self.ENDPOINTS[:5])  # Common endpoints
            method = random.choices(['GET', 'POST'], weights=[0.7, 0.3])[0]
            status = random.choices([200, 201, 400, 404], weights=[0.85, 0.05, 0.05, 0.05])[0]
            latency = random.uniform(50, 300)
            payload_size = random.randint(100, 1000) if method == 'POST' else 0
            user_agent = random.choice(self.USER_AGENTS)
            
            requests.append({
                'method': method,
                'path': endpoint,
                'status': status,
                'latency': latency,
                'payload_size': payload_size,
                'user_agent': user_agent,
                'parameters': self._generate_normal_params(),
                'timestamp': time.time(),
                'anomaly_type': 'NORMAL'
            })
            
            time.sleep(0.1)  # Normal rate
        
        return requests
    
    def generate_rate_spike(self, count: int = 10) -> List[Dict]:
        """Generate DDoS-like rate spike (>15 req/s)"""
        requests = []
        
        for _ in range(count):
            endpoint = random.choice(self.ENDPOINTS[:3])
            method = 'GET'
            status = random.choices([200, 429, 503], weights=[0.5, 0.3, 0.2])[0]
            latency = random.uniform(10, 100)  # Fast requests
            payload_size = 0
            user_agent = random.choice(self.USER_AGENTS)
            
            requests.append({
                'method': method,
                'path': endpoint,
                'status': status,
                'latency': latency,
                'payload_size': payload_size,
                'user_agent': user_agent,
                'parameters': {},
                'timestamp': time.time(),
                'anomaly_type': 'RATE_SPIKE'
            })
            
            time.sleep(0.01)  # Very fast (100 req/s)
        
        return requests
    
    def generate_error_burst(self, count: int = 10) -> List[Dict]:
        """Generate scanning/injection patterns (>50% errors)"""
        requests = []
        
        for _ in range(count):
            endpoint = random.choice(self.ENDPOINTS)
            method = random.choice(['GET', 'POST'])
            status = random.choices([400, 401, 403, 404, 500], weights=[0.3, 0.2, 0.2, 0.2, 0.1])[0]
            latency = random.uniform(20, 150)
            payload_size = random.randint(200, 2000) if method == 'POST' else 0
            user_agent = random.choice(self.USER_AGENTS)
            
            # Injection-like parameters
            params = {
                'id': f"1' OR '1'='1",
                'query': '<script>alert(1)</script>',
                'search': f'../../../etc/passwd'
            }
            
            requests.append({
                'method': method,
                'path': endpoint,
                'status': status,
                'latency': latency,
                'payload_size': payload_size,
                'user_agent': user_agent,
                'parameters': params,
                'timestamp': time.time(),
                'anomaly_type': 'ERROR_BURST'
            })
            
            time.sleep(0.05)
        
        return requests
    
    def generate_bot_attack(self, count: int = 10) -> List[Dict]:
        """Generate bot attack (low entropy + repeated params)"""
        requests = []
        bot_agent = random.choice(self.BOT_AGENTS)
        repeated_params = {'token': 'same_value', 'session': 'fixed_session'}
        
        for _ in range(count):
            endpoint = random.choice(self.ENDPOINTS[:3])
            method = 'POST'
            status = random.choices([200, 401, 403], weights=[0.3, 0.5, 0.2])[0]
            latency = random.uniform(30, 80)  # Consistent timing
            payload_size = random.randint(500, 1500)
            
            requests.append({
                'method': method,
                'path': endpoint,
                'status': status,
                'latency': latency,
                'payload_size': payload_size,
                'user_agent': bot_agent,  # Same agent
                'parameters': repeated_params,  # Same params
                'timestamp': time.time(),
                'anomaly_type': 'BOT_ATTACK'
            })
            
            time.sleep(0.05)
        
        return requests
    
    def generate_large_payload(self, count: int = 10) -> List[Dict]:
        """Generate data exfiltration (>5000 bytes payload)"""
        requests = []
        
        for _ in range(count):
            endpoint = random.choice(['/upload', '/data', '/export'])
            method = 'POST'
            status = random.choices([200, 413, 500], weights=[0.7, 0.2, 0.1])[0]
            latency = random.uniform(200, 800)  # Slower due to size
            payload_size = random.randint(5000, 15000)  # Large payload
            user_agent = random.choice(self.USER_AGENTS)
            
            requests.append({
                'method': method,
                'path': endpoint,
                'status': status,
                'latency': latency,
                'payload_size': payload_size,
                'user_agent': user_agent,
                'parameters': {'data': 'x' * 1000},
                'timestamp': time.time(),
                'anomaly_type': 'LARGE_PAYLOAD'
            })
            
            time.sleep(0.1)
        
        return requests
    
    def generate_endpoint_scan(self, count: int = 10) -> List[Dict]:
        """Generate reconnaissance (>20 unique endpoints)"""
        requests = []
        
        # Access many different endpoints
        for i in range(count):
            endpoint = self.ENDPOINTS[i % len(self.ENDPOINTS)]
            method = 'GET'
            status = random.choices([200, 404, 403], weights=[0.3, 0.5, 0.2])[0]
            latency = random.uniform(20, 100)
            payload_size = 0
            user_agent = random.choice(self.USER_AGENTS)
            
            requests.append({
                'method': method,
                'path': endpoint,
                'status': status,
                'latency': latency,
                'payload_size': payload_size,
                'user_agent': user_agent,
                'parameters': {},
                'timestamp': time.time(),
                'anomaly_type': 'ENDPOINT_SCAN'
            })
            
            time.sleep(0.03)
        
        return requests
    
    def generate_mixed_anomalies(self, count: int = 10) -> List[Dict]:
        """Generate mixed anomaly patterns"""
        anomaly_types = [
            self.generate_rate_spike,
            self.generate_error_burst,
            self.generate_bot_attack,
            self.generate_large_payload,
            self.generate_endpoint_scan
        ]
        
        requests = []
        per_type = max(count // len(anomaly_types), 2)
        
        for anomaly_func in anomaly_types:
            requests.extend(anomaly_func(per_type))
        
        return requests[:count]
    
    def _generate_normal_params(self) -> Dict:
        """Generate realistic API parameters"""
        param_sets = [
            {'user_id': str(random.randint(1, 1000))},
            {'query': random.choice(['products', 'users', 'orders'])},
            {'page': str(random.randint(1, 10)), 'limit': '20'},
            {'id': str(random.randint(1, 500))},
            {}
        ]
        return random.choice(param_sets)
    
    def generate_traffic(self, mode: str = 'normal', count: int = 10) -> List[Dict]:
        """
        Generate traffic based on mode
        
        Args:
            mode: 'normal', 'rate_spike', 'error_burst', 'bot_attack', 
                  'large_payload', 'endpoint_scan', 'mixed'
            count: Number of requests to generate
        
        Returns:
            List of request dictionaries
        """
        mode = mode.lower()
        
        generators = {
            'normal': self.generate_normal_traffic,
            'rate_spike': self.generate_rate_spike,
            'error_burst': self.generate_error_burst,
            'bot_attack': self.generate_bot_attack,
            'large_payload': self.generate_large_payload,
            'endpoint_scan': self.generate_endpoint_scan,
            'mixed': self.generate_mixed_anomalies
        }
        
        generator = generators.get(mode, self.generate_normal_traffic)
        return generator(count)


# Global simulator instance
traffic_simulator = TrafficSimulator()
