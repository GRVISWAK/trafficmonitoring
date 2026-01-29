"""
Endpoint-Specific Simulation Manager v2.0
Supports targeted anomaly injection on virtual endpoints only
Author: 8th Semester Project
Date: December 28, 2025
"""
from dataclasses import dataclass
from datetime import datetime
from collections import deque
from typing import Dict, List, Optional
import random
import numpy as np


@dataclass
class SimulatedAnomaly:
    """
    Represents a single simulated anomaly detection with explicit labeling
    """
    id: int
    timestamp: str
    simulated_endpoint: str  # Virtual endpoint (e.g., /sim/login)
    anomaly_type: str  # Injected anomaly type
    detected_type: str  # What ML models detected
    risk_score: float
    priority: str
    is_correctly_detected: bool
    emergency_rank: int  # 1 = highest priority
    window_id: int
    method: str
    detection_latency_ms: float
    details: Dict


class EndpointSpecificHistoryManager:
    """
    Tracks anomaly detections per simulated endpoint with emergency ranking
    """
    
    def __init__(self, max_history=1000):
        self.history = deque(maxlen=max_history)
        self.anomaly_counter = 0
        self.endpoint_stats = {}  # Track per-endpoint metrics
    
    def add_detection(
        self,
        simulated_endpoint: str,
        anomaly_type: str,
        detection_result: Dict,
        method: str,
        window_id: int
    ) -> SimulatedAnomaly:
        """
        Add a new detection to history with correctness check
        
        Args:
            simulated_endpoint: Virtual endpoint (e.g., /sim/login)
            anomaly_type: Injected anomaly type
            detection_result: ML model prediction
            method: HTTP method
            window_id: Window identifier
        
        Returns:
            SimulatedAnomaly record
        """
        self.anomaly_counter += 1
        
        # Check if detection was correct
        detected_type = detection_result.get('detection_method', 'NONE')
        is_correct = self._is_correct_detection(anomaly_type, detection_result)
        
        # Create anomaly record
        anomaly = SimulatedAnomaly(
            id=self.anomaly_counter,
            timestamp=datetime.now().isoformat(),
            simulated_endpoint=simulated_endpoint,
            anomaly_type=anomaly_type,
            detected_type=detected_type,
            risk_score=detection_result.get('risk_score', 0.0),
            priority=detection_result.get('priority', 'LOW'),
            is_correctly_detected=is_correct,
            emergency_rank=0,  # Will be set by ranking
            window_id=window_id,
            method=method,
            detection_latency_ms=detection_result.get('detection_latency_ms', 0.0),
            details=detection_result.get('details', {})
        )
        
        self.history.append(anomaly)
        
        # Update endpoint-specific stats
        if simulated_endpoint not in self.endpoint_stats:
            self.endpoint_stats[simulated_endpoint] = {
                'total': 0,
                'anomalies': 0,
                'correct_detections': 0,
                'by_type': {}
            }
        
        stats = self.endpoint_stats[simulated_endpoint]
        stats['total'] += 1
        if detection_result.get('is_anomaly'):
            stats['anomalies'] += 1
        if is_correct:
            stats['correct_detections'] += 1
        
        # Track by anomaly type
        if anomaly_type not in stats['by_type']:
            stats['by_type'][anomaly_type] = 0
        stats['by_type'][anomaly_type] += 1
        
        # Recalculate emergency rankings
        self._recalculate_rankings()
        
        return anomaly
    
    def _is_correct_detection(self, injected_type: str, detection_result: Dict) -> bool:
        """
        Check if detection was correct
        
        Correct if:
        - Normal traffic → is_anomaly=False
        - Anomaly traffic → is_anomaly=True
        """
        is_anomaly = detection_result.get('is_anomaly', False)
        
        if injected_type == 'NORMAL':
            return not is_anomaly  # Correct if NOT flagged
        else:
            return is_anomaly  # Correct if flagged as anomaly
    
    def _recalculate_rankings(self):
        """
        Recalculate emergency rankings based on risk score + recency
        
        Ranking logic:
        1. Sort by risk_score (descending)
        2. For ties, newer detections rank higher
        3. Assign rank #1, #2, #3, etc.
        """
        # Sort: highest risk first, then newest first
        sorted_history = sorted(
            self.history,
            key=lambda a: (a.risk_score, -a.id),  # Negative id for recency
            reverse=True
        )
        
        # Assign ranks
        for rank, anomaly in enumerate(sorted_history, start=1):
            anomaly.emergency_rank = rank
    
    def get_top_emergencies(self, limit: int = 10) -> List[SimulatedAnomaly]:
        """Get top N emergency-ranked anomalies"""
        sorted_anomalies = sorted(self.history, key=lambda a: a.emergency_rank)
        return list(sorted_anomalies[:limit])
    
    def get_recent_detections(self, limit: int = 10) -> List[SimulatedAnomaly]:
        """Get most recent detections"""
        return list(self.history)[-limit:][::-1]  # Reverse for newest first
    
    def get_endpoint_stats(self, endpoint: Optional[str] = None) -> Dict:
        """Get statistics for specific endpoint or all endpoints"""
        if endpoint:
            return self.endpoint_stats.get(endpoint, {
                'total': 0,
                'anomalies': 0,
                'correct_detections': 0,
                'by_type': {}
            })
        return self.endpoint_stats
    
    def get_accuracy_stats(self) -> Dict:
        """Calculate overall accuracy metrics"""
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
            if a.anomaly_type == 'NORMAL' and not a.is_correctly_detected
        )
        
        # False negatives: Anomaly detected as normal
        false_negatives = sum(
            1 for a in self.history 
            if a.anomaly_type != 'NORMAL' and not a.is_correctly_detected
        )
        
        return {
            'total_detections': total,
            'correct_detections': correct,
            'accuracy_percentage': (correct / total * 100) if total > 0 else 0.0,
            'false_positives': false_positives,
            'false_negatives': false_negatives
        }
    
    def get_priority_distribution(self) -> Dict:
        """Get distribution of anomalies by priority level"""
        distribution = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for anomaly in self.history:
            if anomaly.priority in distribution:
                distribution[anomaly.priority] += 1
        return distribution
    
    def get_model_decisions(self) -> Dict:
        """Get distribution of which models detected anomalies"""
        decisions = {
            'ISOLATION_FOREST': 0,
            'LOGISTIC_REGRESSION': 0,
            'KMEANS': 0,
            'RULE_BASED': 0,
            'COMBINED': 0
        }
        
        for anomaly in self.history:
            detected = anomaly.detected_type
            if 'ISOLATION_FOREST' in detected:
                decisions['ISOLATION_FOREST'] += 1
            if 'LOGISTIC' in detected:
                decisions['LOGISTIC_REGRESSION'] += 1
            if 'KMEANS' in detected or 'CLUSTER' in detected:
                decisions['KMEANS'] += 1
            if 'RULE' in detected:
                decisions['RULE_BASED'] += 1
            if '+' in detected:
                decisions['COMBINED'] += 1
        
        return decisions
    
    def clear_history(self):
        """Clear all history"""
        self.history.clear()
        self.endpoint_stats.clear()
        self.anomaly_counter = 0


class EndpointSpecificTrafficGenerator:
    """
    Generates synthetic traffic for VIRTUAL endpoints only with targeted anomaly injection
    
    Virtual Endpoints (simulation only, NOT real API routes):
    - /sim/login
    - /sim/search
    - /sim/profile
    - /sim/payment
    - /sim/signup
    
    Anomaly Types:
    - RATE_SPIKE: High request rate (DDoS simulation)
    - PAYLOAD_ABUSE: Oversized payloads (10KB-50KB)
    - ERROR_BURST: High error rate (70-90% errors)
    - PARAM_REPETITION: Repeated parameters (bot pattern)
    - ENDPOINT_FLOOD: Rapid requests to single endpoint
    - NORMAL: Clean baseline traffic
    """
    
    # VIRTUAL endpoints only (completely separate from real API)
    VIRTUAL_ENDPOINTS = ['/sim/login', '/sim/search', '/sim/profile', '/sim/payment', '/sim/signup']
    
    ANOMALY_TYPES = ['RATE_SPIKE', 'PAYLOAD_ABUSE', 'ERROR_BURST', 'PARAM_REPETITION', 'ENDPOINT_FLOOD', 'NORMAL']
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
            'Python-requests/2.31.0',
            'curl/7.88.1',
            'PostmanRuntime/7.32.0',
            'bot/1.0',  # For bot detection
        ]
    
    def generate_targeted_traffic(
        self,
        simulated_endpoint: str,
        anomaly_type: str,
        count: int = 10
    ) -> List[Dict]:
        """
        Generate synthetic traffic for a specific virtual endpoint with targeted anomaly injection
        
        Args:
            simulated_endpoint: Virtual endpoint (e.g., /sim/login)
            anomaly_type: Type of anomaly to inject
            count: Number of requests to generate
        
        Returns:
            List of synthetic request dictionaries
        """
        if simulated_endpoint not in self.VIRTUAL_ENDPOINTS:
            raise ValueError(f"Invalid endpoint. Must be one of: {self.VIRTUAL_ENDPOINTS}")
        
        if anomaly_type not in self.ANOMALY_TYPES:
            raise ValueError(f"Invalid anomaly type. Must be one of: {self.ANOMALY_TYPES}")
        
        # Generate requests based on anomaly type
        if anomaly_type == 'NORMAL':
            return self._generate_normal(simulated_endpoint, count)
        elif anomaly_type == 'RATE_SPIKE':
            return self._generate_rate_spike(simulated_endpoint, count)
        elif anomaly_type == 'PAYLOAD_ABUSE':
            return self._generate_payload_abuse(simulated_endpoint, count)
        elif anomaly_type == 'ERROR_BURST':
            return self._generate_error_burst(simulated_endpoint, count)
        elif anomaly_type == 'PARAM_REPETITION':
            return self._generate_param_repetition(simulated_endpoint, count)
        elif anomaly_type == 'ENDPOINT_FLOOD':
            return self._generate_endpoint_flood(simulated_endpoint, count)
        else:
            return self._generate_normal(simulated_endpoint, count)
    
    def _generate_normal(self, endpoint: str, count: int) -> List[Dict]:
        """Generate normal baseline traffic"""
        requests = []
        for i in range(count):
            requests.append({
                'method': 'POST' if endpoint in ['/sim/login', '/sim/payment', '/sim/signup'] else 'GET',
                'path': endpoint,
                'status': random.choice([200, 200, 200, 201]),  # Mostly success
                'latency': random.uniform(0.05, 0.3),  # 50-300ms
                'payload_size': random.randint(100, 500),  # Small payloads
                'user_agent': random.choice(self.user_agents[:5]),  # Normal agents
                'parameters': {'id': f'user_{i}', 'session': f'sess_{random.randint(1000, 9999)}'},
                'anomaly_type': 'NORMAL'
            })
        return requests
    
    def _generate_rate_spike(self, endpoint: str, count: int) -> List[Dict]:
        """Generate DDoS-like traffic (high rate) - EXTREME TRAFFIC SPIKE"""
        requests = []
        # Generate 5x more requests for heavy traffic spike simulation
        actual_count = count * 5
        for i in range(actual_count):
            requests.append({
                'method': 'POST',
                'path': endpoint,
                'status': random.choice([200, 429, 503, 503, 503]),  # More rate limits/errors
                'latency': random.uniform(0.001, 0.02),  # Extremely fast (1-20ms)
                'payload_size': random.randint(20, 100),  # Tiny payloads for DDoS
                'user_agent': random.choice(self.user_agents),
                'parameters': {'burst': 'true', 'ddos_wave': f'{i // 100}', 'id': f'req_{i}'},
                'anomaly_type': 'RATE_SPIKE'
            })
        return requests
    
    def _generate_payload_abuse(self, endpoint: str, count: int) -> List[Dict]:
        """Generate oversized payload attacks (data exfiltration)"""
        requests = []
        for i in range(count):
            requests.append({
                'method': 'POST',
                'path': endpoint,
                'status': random.choice([200, 413, 400]),  # Payload too large
                'latency': random.uniform(0.5, 2.0),  # Slow due to size
                'payload_size': random.randint(10000, 50000),  # 10KB-50KB
                'user_agent': random.choice(self.user_agents),
                'parameters': {'data': 'x' * 1000, 'bulk': 'true'},
                'anomaly_type': 'PAYLOAD_ABUSE'
            })
        return requests
    
    def _generate_error_burst(self, endpoint: str, count: int) -> List[Dict]:
        """Generate scanning/probing traffic (high error rate)"""
        requests = []
        for i in range(count):
            error_rate = 0.8  # 80% errors
            requests.append({
                'method': random.choice(['GET', 'POST', 'PUT', 'DELETE']),
                'path': endpoint,
                'status': 404 if random.random() < error_rate else 200,
                'latency': random.uniform(0.02, 0.1),
                'payload_size': random.randint(0, 100),
                'user_agent': random.choice(self.user_agents),
                'parameters': {'probe': f'scan_{i}', 'test': 'true'},
                'anomaly_type': 'ERROR_BURST'
            })
        return requests
    
    def _generate_param_repetition(self, endpoint: str, count: int) -> List[Dict]:
        """Generate bot-like traffic (repeated parameters, low entropy)"""
        # Use same parameters repeatedly (bot pattern)
        repeated_params = {'user_id': '12345', 'token': 'abc123', 'action': 'login'}
        requests = []
        for i in range(count):
            requests.append({
                'method': 'POST',
                'path': endpoint,
                'status': 200,
                'latency': random.uniform(0.05, 0.15),
                'payload_size': random.randint(100, 300),
                'user_agent': 'bot/1.0',  # Bot user agent
                'parameters': repeated_params,  # Same params every time
                'anomaly_type': 'PARAM_REPETITION'
            })
        return requests
    
    def _generate_endpoint_flood(self, endpoint: str, count: int) -> List[Dict]:
        """Generate flooding attack (rapid requests to single endpoint) - EXTREME FLOOD"""
        requests = []
        # Generate 10x more requests for extreme flooding
        actual_count = count * 10
        for i in range(actual_count):
            requests.append({
                'method': 'POST',
                'path': endpoint,  # Same endpoint repeatedly
                'status': random.choice([200, 429, 503, 503, 503, 500]),  # More errors
                'latency': random.uniform(0.001, 0.015),  # Extremely fast
                'payload_size': random.randint(30, 150),
                'user_agent': random.choice(self.user_agents),
                'parameters': {'flood': 'true', 'wave': f'{i // 50}', 'seq': i},
                'anomaly_type': 'ENDPOINT_FLOOD'
            })
        return requests


# Global instances for endpoint-specific simulation
endpoint_history = EndpointSpecificHistoryManager(max_history=1000)
endpoint_generator = EndpointSpecificTrafficGenerator()
