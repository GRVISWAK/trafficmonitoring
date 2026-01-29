"""
Async Simulation Engine for High-Speed Traffic Generation (>150 req/sec)
Generates continuous traffic to all endpoints with various anomaly types
"""
import asyncio
import random
import time
from datetime import datetime
from typing import List, Dict, Tuple
from enum import Enum

class AnomalyType(Enum):
    LATENCY_SPIKE = "latency_spike"
    ERROR_SPIKE = "error_spike"
    TRAFFIC_BURST = "traffic_burst"
    TIMEOUT = "timeout"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    NORMAL = "normal"

class Severity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class AsyncSimulationEngine:
    """Generates high-speed async traffic with anomaly injection"""
    
    ENDPOINTS = [
        '/sim/login',
        '/sim/signup',
        '/sim/search',
        '/sim/profile',
        '/sim/payment',
        '/sim/logout'
    ]
    
    METHODS = ['GET', 'POST', 'PUT', 'DELETE']
    
    # Anomaly injection probabilities (per endpoint)
    ANOMALY_PROBABILITIES = {
        '/sim/login': 0.15,
        '/sim/signup': 0.12,
        '/sim/search': 0.18,
        '/sim/profile': 0.10,
        '/sim/payment': 0.25,  # Highest anomaly rate
        '/sim/logout': 0.08
    }
    
    def __init__(self):
        self.active = False
        self.total_requests = 0
        self.start_time = None
        self.anomaly_injections = []
        
    def get_anomaly_config(self, endpoint: str) -> Dict:
        """Get anomaly configuration for endpoint"""
        configs = {
            '/sim/payment': {
                'types': [AnomalyType.TIMEOUT, AnomalyType.ERROR_SPIKE, AnomalyType.RESOURCE_EXHAUSTION],
                'weights': [0.4, 0.4, 0.2],
                'severity_dist': {Severity.CRITICAL: 0.6, Severity.HIGH: 0.3, Severity.MEDIUM: 0.1}
            },
            '/sim/search': {
                'types': [AnomalyType.LATENCY_SPIKE, AnomalyType.RESOURCE_EXHAUSTION, AnomalyType.TRAFFIC_BURST],
                'weights': [0.5, 0.3, 0.2],
                'severity_dist': {Severity.HIGH: 0.5, Severity.MEDIUM: 0.4, Severity.LOW: 0.1}
            },
            '/sim/login': {
                'types': [AnomalyType.ERROR_SPIKE, AnomalyType.LATENCY_SPIKE, AnomalyType.TRAFFIC_BURST],
                'weights': [0.5, 0.3, 0.2],
                'severity_dist': {Severity.HIGH: 0.6, Severity.MEDIUM: 0.3, Severity.LOW: 0.1}
            },
            '/sim/profile': {
                'types': [AnomalyType.LATENCY_SPIKE, AnomalyType.TRAFFIC_BURST],
                'weights': [0.6, 0.4],
                'severity_dist': {Severity.MEDIUM: 0.6, Severity.LOW: 0.4}
            },
            '/sim/signup': {
                'types': [AnomalyType.ERROR_SPIKE, AnomalyType.RESOURCE_EXHAUSTION],
                'weights': [0.6, 0.4],
                'severity_dist': {Severity.HIGH: 0.5, Severity.MEDIUM: 0.3, Severity.LOW: 0.2}
            },
            '/sim/logout': {
                'types': [AnomalyType.LATENCY_SPIKE, AnomalyType.ERROR_SPIKE],
                'weights': [0.5, 0.5],
                'severity_dist': {Severity.MEDIUM: 0.5, Severity.LOW: 0.5}
            }
        }
        return configs.get(endpoint, {
            'types': [AnomalyType.LATENCY_SPIKE],
            'weights': [1.0],
            'severity_dist': {Severity.MEDIUM: 1.0}
        })
    
    def should_inject_anomaly(self, endpoint: str) -> bool:
        """Determine if anomaly should be injected"""
        prob = self.ANOMALY_PROBABILITIES.get(endpoint, 0.1)
        return random.random() < prob
    
    def generate_anomaly(self, endpoint: str) -> Dict:
        """Generate anomaly parameters"""
        config = self.get_anomaly_config(endpoint)
        anomaly_type = random.choices(config['types'], weights=config['weights'])[0]
        
        # Select severity based on distribution
        severities = list(config['severity_dist'].keys())
        weights = list(config['severity_dist'].values())
        severity = random.choices(severities, weights=weights)[0]
        
        # Generate anomaly metrics based on type and severity
        if anomaly_type == AnomalyType.LATENCY_SPIKE:
            base_latency = {'CRITICAL': 5000, 'HIGH': 3000, 'MEDIUM': 1500, 'LOW': 800}
            response_time = base_latency[severity.value] + random.randint(-500, 1000)
            error_rate = random.uniform(0.05, 0.15)
            status_codes = [200] * 70 + [500, 503, 504] * 30
            
        elif anomaly_type == AnomalyType.ERROR_SPIKE:
            base_error_rate = {'CRITICAL': 0.8, 'HIGH': 0.6, 'MEDIUM': 0.4, 'LOW': 0.2}
            error_rate = base_error_rate[severity.value] + random.uniform(-0.1, 0.1)
            response_time = random.randint(200, 800)
            status_codes = [500, 503, 502, 504] * 70 + [200] * 30
            
        elif anomaly_type == AnomalyType.TRAFFIC_BURST:
            response_time = random.randint(500, 1200)
            error_rate = random.uniform(0.1, 0.3)
            status_codes = [200] * 60 + [429, 503] * 40  # Rate limiting
            
        elif anomaly_type == AnomalyType.TIMEOUT:
            response_time = random.randint(8000, 15000)
            error_rate = random.uniform(0.7, 0.95)
            status_codes = [504, 408] * 80 + [200] * 20
            
        elif anomaly_type == AnomalyType.RESOURCE_EXHAUSTION:
            response_time = random.randint(3000, 7000)
            error_rate = random.uniform(0.5, 0.8)
            status_codes = [503, 507, 500] * 70 + [200] * 30
            
        else:  # NORMAL
            response_time = random.randint(50, 300)
            error_rate = random.uniform(0.0, 0.05)
            status_codes = [200] * 95 + [400, 401, 404] * 5
        
        duration = random.uniform(10, 60) if severity in [Severity.CRITICAL, Severity.HIGH] else random.uniform(5, 30)
        
        # Calculate impact score (0-1 scale)
        severity_weights = {Severity.CRITICAL: 1.0, Severity.HIGH: 0.75, Severity.MEDIUM: 0.5, Severity.LOW: 0.25}
        impact_score = severity_weights[severity] * (0.4 * error_rate + 0.3 * min(response_time / 10000, 1.0) + 0.3)
        
        return {
            'type': anomaly_type,
            'severity': severity.value,
            'response_time': response_time,
            'error_rate': error_rate,
            'status_codes': status_codes,
            'duration_seconds': duration,
            'impact_score': min(impact_score, 1.0)
        }
    
    def generate_normal_request(self, endpoint: str) -> Dict:
        """Generate normal request parameters"""
        return {
            'type': AnomalyType.NORMAL,
            'severity': 'NORMAL',
            'response_time': random.randint(50, 250),
            'error_rate': random.uniform(0.0, 0.03),
            'status_codes': [200] * 95 + [400, 401, 404] * 5,
            'duration_seconds': 0,
            'impact_score': 0.0
        }
    
    async def generate_request(self, endpoint: str) -> Dict:
        """Generate a single request asynchronously"""
        # Choose HTTP method based on endpoint
        if endpoint in ['/sim/login', '/sim/payment', '/sim/signup']:
            method = 'POST'
        else:
            method = 'GET'
        
        # Decide if anomaly
        if self.should_inject_anomaly(endpoint):
            params = self.generate_anomaly(endpoint)
            anomaly_type = params['type'].value
        else:
            params = self.generate_normal_request(endpoint)
            anomaly_type = 'normal'
        
        status_code = random.choice(params['status_codes'])
        
        request = {
            'timestamp': datetime.utcnow(),
            'endpoint': endpoint,
            'method': method,
            'response_time_ms': params['response_time'],
            'status_code': status_code,
            'payload_size': random.randint(100, 5000),
            'ip_address': f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            'user_id': f"user_{random.randint(1000, 9999)}",
            'anomaly_type': anomaly_type,
            'severity': params['severity'],
            'duration_seconds': params['duration_seconds'],
            'impact_score': params['impact_score']
        }
        
        self.total_requests += 1
        return request
    
    async def generate_batch(self, batch_size: int = 200) -> List[Dict]:
        """Generate a batch of requests concurrently"""
        # Distribute requests across all endpoints
        endpoint_counts = {ep: batch_size // len(self.ENDPOINTS) for ep in self.ENDPOINTS}
        # Add remainder to random endpoints
        remainder = batch_size % len(self.ENDPOINTS)
        for i in range(remainder):
            endpoint_counts[self.ENDPOINTS[i]] += 1
        
        tasks = []
        for endpoint, count in endpoint_counts.items():
            for _ in range(count):
                tasks.append(self.generate_request(endpoint))
        
        requests = await asyncio.gather(*tasks)
        return requests
    
    async def run_continuous_simulation(self, target_rps: int = 200, duration_seconds: int = 60):
        """Run continuous high-speed simulation"""
        self.active = True
        self.start_time = time.time()
        self.total_requests = 0
        
        batch_size = target_rps  # Generate target_rps requests per second
        interval = 1.0  # 1 second interval
        
        print(f"🚀 Starting async simulation: {target_rps} req/sec target for {duration_seconds}s")
        
        end_time = time.time() + duration_seconds
        
        while self.active and time.time() < end_time:
            batch_start = time.time()
            
            # Generate batch asynchronously
            requests = await self.generate_batch(batch_size)
            
            # Yield requests for processing
            yield requests
            
            # Calculate actual speed
            elapsed = time.time() - self.start_time
            current_rps = self.total_requests / elapsed if elapsed > 0 else 0
            
            print(f"⚡ Generated {len(requests)} requests | Total: {self.total_requests} | Speed: {current_rps:.1f} req/s")
            
            # Sleep to maintain target rate
            batch_time = time.time() - batch_start
            sleep_time = max(0, interval - batch_time)
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        elapsed_total = time.time() - self.start_time
        final_rps = self.total_requests / elapsed_total if elapsed_total > 0 else 0
        print(f"✅ Simulation complete: {self.total_requests} requests in {elapsed_total:.1f}s ({final_rps:.1f} req/s)")
        self.active = False
    
    def stop(self):
        """Stop the simulation"""
        self.active = False
