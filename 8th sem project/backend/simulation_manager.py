"""
SIMULATION MODE Manager - Isolated from LIVE MODE
Generates synthetic traffic with labeled anomaly injection
Maintains detection history with emergency ranking
"""
import time
import random
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
from collections import deque
from dataclasses import dataclass, asdict
import json


@dataclass
class SimulatedAnomaly:
    """Represents a detected anomaly in simulation mode"""
    id: int
    timestamp: str
    injected_type: str  # What we injected
    detected_type: str  # What ML detected
    risk_score: float
    priority: str  # LOW, MEDIUM, HIGH
    is_correctly_detected: bool
    detection_latency_ms: float
    endpoint: str
    method: str
    emergency_rank: int  # 1 = highest emergency
    window_id: int
    details: Dict
    
    def to_dict(self):
        return asdict(self)


class SimulationHistoryManager:
    """Manages detection history and emergency ranking"""
    
    def __init__(self, max_history: int = 100):
        self.history: List[SimulatedAnomaly] = []
        self.max_history = max_history
        self.anomaly_counter = 0
        
    def add_detection(self, injected_type: str, detection_result: Dict, 
                     endpoint: str, method: str, window_id: int) -> SimulatedAnomaly:
        """Add a detection to history with emergency ranking"""
        self.anomaly_counter += 1
        
        # Determine if detection was correct
        is_correct = self._is_detection_correct(injected_type, detection_result)
        
        anomaly = SimulatedAnomaly(
            id=self.anomaly_counter,
            timestamp=datetime.now().isoformat(),
            injected_type=injected_type,
            detected_type=detection_result.get('detection_method', 'UNKNOWN'),
            risk_score=detection_result.get('risk_score', 0.0),
            priority=detection_result.get('priority', 'LOW'),
            is_correctly_detected=is_correct,
            detection_latency_ms=detection_result.get('detection_latency_ms', 0.0),
            endpoint=endpoint,
            method=method,
            emergency_rank=0,  # Will be calculated
            window_id=window_id,
            details=detection_result.get('details', {})
        )
        
        self.history.append(anomaly)
        
        # Keep only max_history items
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        # Recalculate emergency rankings
        self._recalculate_rankings()
        
        return anomaly
    
    def _is_detection_correct(self, injected: str, detected: Dict) -> bool:
        """Check if ML correctly detected the injected anomaly"""
        if injected == 'NORMAL':
            return not detected.get('is_anomaly', False)
        else:
            # For anomalies, check if it was detected as anomaly
            return detected.get('is_anomaly', False)
    
    def _recalculate_rankings(self):
        """Recalculate emergency rankings based on risk score and recency"""
        # Sort by risk score (descending) and timestamp (most recent first)
        sorted_anomalies = sorted(
            self.history,
            key=lambda x: (x.risk_score, x.timestamp),
            reverse=True
        )
        
        # Assign ranks
        for rank, anomaly in enumerate(sorted_anomalies, 1):
            anomaly.emergency_rank = rank
    
    def get_top_emergencies(self, limit: int = 10) -> List[Dict]:
        """Get top N highest emergency anomalies"""
        sorted_anomalies = sorted(self.history, key=lambda x: x.emergency_rank)
        return [a.to_dict() for a in sorted_anomalies[:limit]]
    
    def get_recent_history(self, limit: int = 20) -> List[Dict]:
        """Get most recent detections"""
        recent = sorted(self.history, key=lambda x: x.timestamp, reverse=True)
        return [a.to_dict() for a in recent[:limit]]
    
    def get_accuracy_stats(self) -> Dict:
        """Calculate detection accuracy metrics"""
        if not self.history:
            return {
                'total_detections': 0,
                'correct_detections': 0,
                'accuracy_percentage': 0.0,
                'false_positives': 0,
                'false_negatives': 0
            }
        
        total = len(self.history)
        correct = sum(1 for a in self.history if a.is_correctly_detected)
        
        # False positives: Normal traffic detected as anomaly
        false_positives = sum(
            1 for a in self.history 
            if a.injected_type == 'NORMAL' and not a.is_correctly_detected
        )
        
        # False negatives: Anomaly detected as normal
        false_negatives = sum(
            1 for a in self.history 
            if a.injected_type != 'NORMAL' and not a.is_correctly_detected
        )
        
        return {
            'total_detections': total,
            'correct_detections': correct,
            'accuracy_percentage': (correct / total * 100) if total > 0 else 0.0,
            'false_positives': false_positives,
            'false_negatives': false_negatives
        }
    
    def clear_history(self):
        """Clear all history"""
        self.history.clear()
        self.anomaly_counter = 0


class SimulationTrafficGenerator:
    """
    Generates synthetic traffic with explicit anomaly labeling
    COMPLETELY ISOLATED from LIVE MODE
    """
    
    # Only track whitelisted endpoints (same as LIVE mode for consistency)
    WHITELISTED_ENDPOINTS = [
        '/login', '/signup', '/search', '/profile', '/payment', '/logout'
    ]
    
    def __init__(self):
        self.request_count = 0
        
    def generate_traffic(self, mode: str, count: int = 10) -> List[Dict]:
        """
        Generate synthetic traffic with labeled anomalies
        
        Args:
            mode: 'normal', 'rate_spike', 'error_burst', 'bot_attack', 
                  'large_payload', 'endpoint_scan', 'mixed'
            count: Number of requests to generate
        
        Returns:
            List of synthetic requests with anomaly labels
        """
        if mode == 'normal':
            return self._generate_normal(count)
        elif mode == 'rate_spike':
            return self._generate_rate_spike(count)
        elif mode == 'error_burst':
            return self._generate_error_burst(count)
        elif mode == 'bot_attack':
            return self._generate_bot_attack(count)
        elif mode == 'large_payload':
            return self._generate_large_payload(count)
        elif mode == 'endpoint_scan':
            return self._generate_endpoint_scan(count)
        elif mode == 'mixed':
            return self._generate_mixed(count)
        else:
            return self._generate_normal(count)
    
    def _generate_normal(self, count: int) -> List[Dict]:
        """Generate normal traffic (no anomalies)"""
        requests = []
        for _ in range(count):
            endpoint = random.choice(self.WHITELISTED_ENDPOINTS)
            method = random.choice(['GET', 'POST'])
            status = random.choices([200, 201], weights=[0.9, 0.1])[0]
            latency = random.uniform(50, 200)
            payload_size = random.randint(100, 500) if method == 'POST' else 0
            
            requests.append({
                'method': method,
                'path': endpoint,
                'status': status,
                'latency': latency,
                'payload_size': payload_size,
                'user_agent': self._random_user_agent(),
                'parameters': self._random_params(),
                'anomaly_type': 'NORMAL',  # LABEL
                'timestamp': time.time()
            })
        return requests
    
    def _generate_rate_spike(self, count: int) -> List[Dict]:
        """Generate high-frequency requests (DDoS simulation)"""
        requests = []
        # Spike: Much faster than normal
        for _ in range(count):
            endpoint = random.choice(['/login', '/search'])  # Target specific endpoints
            requests.append({
                'method': 'POST',
                'path': endpoint,
                'status': 200,
                'latency': random.uniform(10, 50),  # Very fast
                'payload_size': random.randint(50, 200),
                'user_agent': self._random_user_agent(),
                'parameters': self._random_params(),
                'anomaly_type': 'RATE_SPIKE',  # LABEL
                'timestamp': time.time()
            })
        return requests
    
    def _generate_error_burst(self, count: int) -> List[Dict]:
        """Generate high error rates (scanning/injection attempts)"""
        requests = []
        for _ in range(count):
            endpoint = random.choice(self.WHITELISTED_ENDPOINTS)
            # High error rates
            status = random.choices([400, 401, 403, 404, 500], 
                                   weights=[0.3, 0.2, 0.2, 0.2, 0.1])[0]
            requests.append({
                'method': random.choice(['GET', 'POST']),
                'path': endpoint,
                'status': status,
                'latency': random.uniform(100, 300),
                'payload_size': random.randint(100, 500),
                'user_agent': self._random_user_agent(),
                'parameters': self._random_params(),
                'anomaly_type': 'ERROR_BURST',  # LABEL
                'timestamp': time.time()
            })
        return requests
    
    def _generate_bot_attack(self, count: int) -> List[Dict]:
        """Generate bot-like behavior (low entropy, repeated params)"""
        requests = []
        bot_agent = 'python-bot/1.0'  # Same agent for all
        repeated_param = {'user_id': 'bot123', 'token': 'AAAA'}  # Same params
        
        for _ in range(count):
            endpoint = random.choice(['/login', '/profile'])
            requests.append({
                'method': 'POST',
                'path': endpoint,
                'status': random.choice([200, 401]),
                'latency': random.uniform(50, 150),
                'payload_size': random.randint(100, 300),
                'user_agent': bot_agent,  # Low entropy
                'parameters': repeated_param,  # High repetition
                'anomaly_type': 'BOT_ATTACK',  # LABEL
                'timestamp': time.time()
            })
        return requests
    
    def _generate_large_payload(self, count: int) -> List[Dict]:
        """Generate large payload requests (data exfiltration)"""
        requests = []
        for _ in range(count):
            endpoint = random.choice(['/upload', '/payment', '/profile'])
            requests.append({
                'method': 'POST',
                'path': endpoint,
                'status': 200,
                'latency': random.uniform(200, 500),  # Slower due to size
                'payload_size': random.randint(5000, 50000),  # VERY LARGE
                'user_agent': self._random_user_agent(),
                'parameters': self._random_params(),
                'anomaly_type': 'LARGE_PAYLOAD',  # LABEL
                'timestamp': time.time()
            })
        return requests
    
    def _generate_endpoint_scan(self, count: int) -> List[Dict]:
        """Generate endpoint scanning behavior (reconnaissance)"""
        requests = []
        # Hit all endpoints rapidly
        for _ in range(count):
            endpoint = random.choice(self.WHITELISTED_ENDPOINTS)  # Scan all
            requests.append({
                'method': 'GET',
                'path': endpoint,
                'status': random.choice([200, 404]),
                'latency': random.uniform(50, 150),
                'payload_size': 0,
                'user_agent': 'scanner-tool/1.0',
                'parameters': {},
                'anomaly_type': 'ENDPOINT_SCAN',  # LABEL
                'timestamp': time.time()
            })
        return requests
    
    def _generate_mixed(self, count: int) -> List[Dict]:
        """Generate mixed anomalies"""
        modes = ['rate_spike', 'error_burst', 'bot_attack', 'large_payload', 'endpoint_scan']
        all_requests = []
        
        per_mode = count // len(modes)
        for mode in modes:
            all_requests.extend(self.generate_traffic(mode, per_mode))
        
        # Fill remainder with normal traffic
        remainder = count - len(all_requests)
        if remainder > 0:
            all_requests.extend(self._generate_normal(remainder))
        
        random.shuffle(all_requests)
        return all_requests
    
    def _random_user_agent(self) -> str:
        """Generate random user agent"""
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/96.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1',
            'Mozilla/5.0 (X11; Linux x86_64) Firefox/95.0',
            'curl/7.64.1',
            'PostmanRuntime/7.28.4'
        ]
        return random.choice(agents)
    
    def _random_params(self) -> Dict:
        """Generate random parameters"""
        return {
            'user_id': f'user{random.randint(1, 100)}',
            'session': f'sess{random.randint(1000, 9999)}'
        }


# Global instances (isolated from LIVE mode)
simulation_history = SimulationHistoryManager()
simulation_generator = SimulationTrafficGenerator()
