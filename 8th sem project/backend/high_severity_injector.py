"""
High-Severity Anomaly Injector
Generates targeted, realistic failure-prone anomalies per endpoint
150+ requests/second capability
"""
import random
import time
from typing import Dict, List


class SeverityLevel:
    """Anomaly severity configurations"""
    CRITICAL = {
        'error_rate': (0.6, 0.9),  # 60-90% errors
        'latency_ms': (3000, 8000),  # 3-8 second delays
        'failure_probability': (0.75, 0.95),  # High failure risk
        'priority': 'CRITICAL'
    }
    HIGH = {
        'error_rate': (0.4, 0.6),
        'latency_ms': (1500, 3000),
        'failure_probability': (0.50, 0.75),
        'priority': 'HIGH'
    }
    MEDIUM = {
        'error_rate': (0.2, 0.4),
        'latency_ms': (800, 1500),
        'failure_probability': (0.25, 0.50),
        'priority': 'MEDIUM'
    }


class HighSeverityInjector:
    """
    Injects specific high-severity anomalies per endpoint
    Each endpoint gets ONE specific anomaly type
    """
    
    # Map endpoints to specific severe anomaly patterns
    ENDPOINT_ANOMALY_MAP = {
        '/sim/payment': {
            'type': 'DATABASE_DEADLOCK',
            'severity': SeverityLevel.CRITICAL,
            'description': 'Database deadlock causing payment failures',
            'error_codes': [500, 503, 504],
            'repeat_rate': 0.9,  # High bot-like activity
            'cluster': 2  # Bot cluster
        },
        '/sim/login': {
            'type': 'AUTHENTICATION_FAILURE',
            'severity': SeverityLevel.HIGH,
            'description': 'Brute force attack causing auth failures',
            'error_codes': [401, 429, 503],
            'repeat_rate': 0.95,  # Very high repetition
            'cluster': 2
        },
        '/sim/search': {
            'type': 'MEMORY_LEAK',
            'severity': SeverityLevel.HIGH,
            'description': 'Memory leak causing slow responses',
            'error_codes': [500, 503],
            'repeat_rate': 0.3,
            'cluster': 1  # Heavy usage
        },
        '/sim/profile': {
            'type': 'API_RATE_LIMIT',
            'severity': SeverityLevel.MEDIUM,
            'description': 'Rate limit exceeded',
            'error_codes': [429, 503],
            'repeat_rate': 0.85,
            'cluster': 2
        },
        '/sim/signup': {
            'type': 'BACKEND_OVERLOAD',
            'severity': SeverityLevel.CRITICAL,
            'description': 'Backend service overload',
            'error_codes': [503, 504, 500],
            'repeat_rate': 0.4,
            'cluster': 1
        }
    }
    
    @staticmethod
    def generate_high_severity_batch(endpoint: str, batch_size: int = 100) -> List[Dict]:
        """
        Generate batch of high-severity anomalous requests
        
        Args:
            endpoint: Target endpoint
            batch_size: Number of requests (default 100 for speed)
            
        Returns:
            List of request dictionaries with severe anomaly patterns
        """
        if endpoint not in HighSeverityInjector.ENDPOINT_ANOMALY_MAP:
            endpoint = '/sim/payment'  # Default to payment
        
        config = HighSeverityInjector.ENDPOINT_ANOMALY_MAP[endpoint]
        severity = config['severity']
        
        requests = []
        session_id = f"session_{int(time.time())}"
        
        for i in range(batch_size):
            # Determine if this request fails
            error_rate = random.uniform(*severity['error_rate'])
            is_error = random.random() < error_rate
            
            # Select status code
            if is_error:
                status = random.choice(config['error_codes'])
            else:
                status = random.choice([200, 201])
            
            # Generate latency
            if is_error:
                # Errors have higher latency
                latency = random.uniform(*severity['latency_ms'])
            else:
                # Success but still slow (degraded performance)
                latency = random.uniform(
                    severity['latency_ms'][0] * 0.6,
                    severity['latency_ms'][1] * 0.3
                )
            
            # Payload size (errors have smaller payloads)
            if is_error:
                payload_size = random.randint(50, 200)  # Error messages
            else:
                payload_size = random.randint(500, 2000)
            
            # Repeated parameters (bot-like)
            if random.random() < config['repeat_rate']:
                user_id = f"bot_user_{session_id}"
                params = {"session": session_id, "retry": "true"}
            else:
                user_id = f"user_{random.randint(1, 50)}"
                params = {"session": f"sess_{random.randint(1, 100)}"}
            
            request = {
                'method': 'POST' if endpoint in ['/sim/payment', '/sim/login', '/sim/signup'] else 'GET',
                'path': endpoint,
                'status': status,
                'latency': latency,
                'payload_size': payload_size,
                'user_agent': _get_bot_user_agent() if random.random() < 0.7 else _get_normal_user_agent(),
                'parameters': params,
                'user_id': user_id,
                'error_rate': error_rate,
                'is_severe': True,
                'anomaly_type': config['type']
            }
            
            requests.append(request)
        
        return requests
    
    @staticmethod
    def get_expected_metrics(endpoint: str) -> Dict:
        """Get expected metrics for the anomaly"""
        config = HighSeverityInjector.ENDPOINT_ANOMALY_MAP.get(endpoint, 
                                                                 HighSeverityInjector.ENDPOINT_ANOMALY_MAP['/sim/payment'])
        severity = config['severity']
        
        return {
            'expected_error_rate': sum(severity['error_rate']) / 2,
            'expected_latency': sum(severity['latency_ms']) / 2,
            'expected_failure_probability': sum(severity['failure_probability']) / 2,
            'expected_priority': severity['priority'],
            'anomaly_type': config['type'],
            'description': config['description']
        }


def _get_bot_user_agent() -> str:
    """Get bot-like user agent"""
    return random.choice([
        'bot/1.0',
        'scanner/2.0',
        'curl/7.64.1',
        'python-requests/2.26.0',
        'automated-test/1.0'
    ])


def _get_normal_user_agent() -> str:
    """Get normal user agent"""
    return random.choice([
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/96.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1',
        'Mozilla/5.0 (X11; Linux x86_64) Firefox/95.0',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0) Safari/604.1',
    ])
