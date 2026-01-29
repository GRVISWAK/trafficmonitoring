"""
Root Cause Analysis and Resolution Suggestion Engine
Uses inference outputs to classify anomaly root causes and provide actionable remediation steps
"""
from typing import Dict, List, Optional


class RootCauseAnalyzer:
    """
    Classifies root causes of anomalies based on inference metrics
    and provides advanced, actionable resolution suggestions
    """
    
    # Define baseline for traffic surge detection (can be adjusted)
    BASELINE_REQ_COUNT = 5  # Normal window has ~5 requests typically
    
    @staticmethod
    def analyze(
        error_rate: float,
        avg_response_time: float,
        req_count: int,
        repeat_rate: float,
        usage_cluster: int,
        failure_probability: float,
        **kwargs  # Accept additional fields without breaking
    ) -> Dict[str, any]:
        """
        Classify root cause based on inference metrics
        
        Root Cause Classification Rules:
        1. avg_response_time > 800ms & error_rate < 0.3 → Latency Bottleneck
        2. error_rate >= 0.3 → Backend Instability
        3. req_count >= 2x baseline → Traffic Surge
        4. repeat_rate > 0.7 or usage_cluster == 2 (bot) → Abuse/Bot Activity
        5. Multiple conditions → System Overload
        
        Args:
            error_rate: Error rate from detection (0.0 - 1.0)
            avg_response_time: Average response time in ms
            req_count: Request count in window
            repeat_rate: Parameter repetition rate (0.0 - 1.0)
            usage_cluster: Cluster ID (0=Normal, 1=Heavy, 2=Bot-like)
            failure_probability: Failure prediction probability
            
        Returns:
            Dict with root_cause, confidence, and resolution_suggestions
        """
        # Convert error_rate to 0-1 range if it's in percentage
        if error_rate > 1.0:
            error_rate = error_rate / 100.0
        
        # Track which conditions are met
        conditions_met = []
        
        # Check each condition
        is_latency_bottleneck = avg_response_time > 800 and error_rate < 0.3
        is_backend_instability = error_rate >= 0.3
        is_traffic_surge = req_count >= (2 * RootCauseAnalyzer.BASELINE_REQ_COUNT)
        is_abuse_bot = repeat_rate > 0.7 or usage_cluster == 2
        
        if is_latency_bottleneck:
            conditions_met.append('latency_bottleneck')
        if is_backend_instability:
            conditions_met.append('backend_instability')
        if is_traffic_surge:
            conditions_met.append('traffic_surge')
        if is_abuse_bot:
            conditions_met.append('abuse_bot')
        
        # Determine primary root cause with priority order
        # Priority: Backend Instability > Abuse/Bot > Latency > Traffic Surge
        root_cause = None
        confidence = 0.0
        
        # Only classify as System Overload if 3+ conditions met
        if len(conditions_met) >= 3:
            root_cause = 'System Overload'
            confidence = min(0.95, 0.75 + len(conditions_met) * 0.1)
        # Prioritize Backend Instability (most critical)
        elif is_backend_instability:
            root_cause = 'Backend Instability'
            confidence = 0.85 + min((error_rate - 0.3) * 0.3, 0.10)
        # Next priority: Abuse/Bot Activity (security issue)
        elif is_abuse_bot:
            root_cause = 'Abuse/Bot Activity'
            bot_confidence = repeat_rate if repeat_rate > 0.7 else 0.9
            confidence = 0.80 + min(bot_confidence * 0.15, 0.15)
        # Next: Latency Bottleneck (performance issue)
        elif is_latency_bottleneck:
            root_cause = 'Latency Bottleneck'
            confidence = 0.75 + min((avg_response_time - 800) / 2000, 0.15)
        # Last: Traffic Surge (capacity issue)
        elif is_traffic_surge:
            root_cause = 'Traffic Surge'
            surge_ratio = req_count / RootCauseAnalyzer.BASELINE_REQ_COUNT
            confidence = 0.70 + min((surge_ratio - 2) * 0.05, 0.20)
        else:
            root_cause = 'Unknown Anomaly'
            confidence = 0.50
        
        # Get resolution suggestions
        suggestions = RootCauseAnalyzer._get_resolution_suggestions(root_cause, conditions_met)
        
        return {
            'root_cause': root_cause,
            'confidence': round(confidence, 2),
            'conditions_met': conditions_met,
            'resolution_suggestions': suggestions,
            'metrics_summary': {
                'error_rate': round(error_rate, 3),
                'avg_response_time_ms': round(avg_response_time, 1),
                'req_count': req_count,
                'repeat_rate': round(repeat_rate, 2),
                'usage_cluster': usage_cluster,
                'failure_probability': round(failure_probability, 3)
            }
        }
    
    @staticmethod
    def _get_resolution_suggestions(root_cause: str, conditions_met: List[str]) -> List[Dict[str, str]]:
        """
        Get actionable resolution suggestions based on root cause
        
        Returns list of suggestions with category and action
        """
        all_suggestions = {
            'Latency Bottleneck': [
                {
                    'category': 'Caching',
                    'action': 'Add Redis read-through cache',
                    'detail': 'Cache frequently accessed data with TTL to reduce database queries',
                    'priority': 'HIGH'
                },
                {
                    'category': 'I/O Optimization',
                    'action': 'Enable async I/O',
                    'detail': 'Use non-blocking async operations for external API calls and database queries',
                    'priority': 'HIGH'
                },
                {
                    'category': 'Database',
                    'action': 'Tune DB indexes',
                    'detail': 'Add composite indexes on frequently queried columns, analyze slow query logs',
                    'priority': 'MEDIUM'
                },
                {
                    'category': 'Concurrency',
                    'action': 'Increase worker concurrency',
                    'detail': 'Scale up Gunicorn/Uvicorn workers or enable thread pooling',
                    'priority': 'MEDIUM'
                }
            ],
            'Backend Instability': [
                {
                    'category': 'Debugging',
                    'action': 'Inspect error traces',
                    'detail': 'Review application logs and stack traces to identify failing code paths',
                    'priority': 'CRITICAL'
                },
                {
                    'category': 'Resilience',
                    'action': 'Enable circuit breaker',
                    'detail': 'Implement circuit breaker pattern to prevent cascade failures (e.g., Hystrix, resilience4j)',
                    'priority': 'HIGH'
                },
                {
                    'category': 'Deployment',
                    'action': 'Rollback recent deploy',
                    'detail': 'Revert to last stable version if errors started after recent deployment',
                    'priority': 'HIGH'
                },
                {
                    'category': 'Dependency Management',
                    'action': 'Isolate failing dependency',
                    'detail': 'Identify and quarantine failing external services, add fallback mechanisms',
                    'priority': 'MEDIUM'
                }
            ],
            'Traffic Surge': [
                {
                    'category': 'Rate Limiting',
                    'action': 'Apply token-bucket rate limiting',
                    'detail': 'Implement per-IP or per-user rate limits with token bucket algorithm',
                    'priority': 'CRITICAL'
                },
                {
                    'category': 'Scaling',
                    'action': 'Autoscale pods/instances',
                    'detail': 'Enable horizontal pod autoscaling (HPA) or auto-scaling groups',
                    'priority': 'HIGH'
                },
                {
                    'category': 'Caching',
                    'action': 'Cache idempotent responses',
                    'detail': 'Cache GET responses at CDN or application layer with appropriate TTL',
                    'priority': 'MEDIUM'
                },
                {
                    'category': 'CDN',
                    'action': 'Enable CDN edge caching',
                    'detail': 'Offload static and cacheable content to CDN (Cloudflare, CloudFront)',
                    'priority': 'MEDIUM'
                }
            ],
            'Abuse/Bot Activity': [
                {
                    'category': 'Rate Limiting',
                    'action': 'Adaptive rate limits',
                    'detail': 'Implement adaptive rate limiting based on user behavior patterns',
                    'priority': 'CRITICAL'
                },
                {
                    'category': 'Security',
                    'action': 'IP reputation filtering',
                    'detail': 'Block traffic from known malicious IPs using threat intelligence feeds',
                    'priority': 'HIGH'
                },
                {
                    'category': 'Authentication',
                    'action': 'Auth throttling & CAPTCHA',
                    'detail': 'Add progressive delays and CAPTCHA challenges for suspicious login attempts',
                    'priority': 'HIGH'
                },
                {
                    'category': 'WAF',
                    'action': 'Configure WAF rules',
                    'detail': 'Update WAF rules to detect and block bot signatures and scraping patterns',
                    'priority': 'MEDIUM'
                }
            ],
            'System Overload': [
                {
                    'category': 'Scaling',
                    'action': 'Horizontal scaling',
                    'detail': 'Add more application instances/pods to distribute load',
                    'priority': 'CRITICAL'
                },
                {
                    'category': 'Queue Management',
                    'action': 'Request queuing',
                    'detail': 'Implement request queue with backpressure to prevent resource exhaustion',
                    'priority': 'HIGH'
                },
                {
                    'category': 'Graceful Degradation',
                    'action': 'Enable graceful degradation',
                    'detail': 'Disable non-critical features, serve cached/stale data temporarily',
                    'priority': 'HIGH'
                },
                {
                    'category': 'Optimization',
                    'action': 'Payload minimization',
                    'detail': 'Reduce response payload size, enable compression (gzip/brotli)',
                    'priority': 'MEDIUM'
                }
            ],
            'Unknown Anomaly': [
                {
                    'category': 'Monitoring',
                    'action': 'Enhanced monitoring',
                    'detail': 'Enable detailed application metrics and distributed tracing',
                    'priority': 'HIGH'
                },
                {
                    'category': 'Analysis',
                    'action': 'Manual investigation',
                    'detail': 'Review logs, metrics, and user reports to identify anomaly pattern',
                    'priority': 'MEDIUM'
                }
            ]
        }
        
        # Start with primary root cause suggestions
        suggestions = all_suggestions.get(root_cause, [])
        
        # For System Overload, also add relevant suggestions from contributing conditions
        if root_cause == 'System Overload':
            # Add top suggestions from each contributing condition
            for condition in conditions_met:
                if condition == 'latency_bottleneck' and len(all_suggestions.get('Latency Bottleneck', [])) > 0:
                    suggestions.append(all_suggestions['Latency Bottleneck'][0])  # Add caching suggestion
                elif condition == 'backend_instability' and len(all_suggestions.get('Backend Instability', [])) > 0:
                    suggestions.append(all_suggestions['Backend Instability'][0])  # Add debugging suggestion
                elif condition == 'traffic_surge' and len(all_suggestions.get('Traffic Surge', [])) > 0:
                    suggestions.append(all_suggestions['Traffic Surge'][0])  # Add rate limiting
                elif condition == 'abuse_bot' and len(all_suggestions.get('Abuse/Bot Activity', [])) > 0:
                    suggestions.append(all_suggestions['Abuse/Bot Activity'][0])  # Add adaptive limits
        
        # Remove duplicates while preserving order
        seen = set()
        unique_suggestions = []
        for suggestion in suggestions:
            key = (suggestion['category'], suggestion['action'])
            if key not in seen:
                seen.add(key)
                unique_suggestions.append(suggestion)
        
        return unique_suggestions


# Test the analyzer
if __name__ == "__main__":
    print("=" * 80)
    print("ROOT CAUSE ANALYZER - TEST CASES")
    print("=" * 80)
    
    # Test Case 1: Latency Bottleneck
    print("\n🔹 Test 1: Latency Bottleneck")
    result = RootCauseAnalyzer.analyze(
        error_rate=0.1,
        avg_response_time=950,
        req_count=6,
        repeat_rate=0.3,
        usage_cluster=0,
        failure_probability=0.2
    )
    print(f"Root Cause: {result['root_cause']} (Confidence: {result['confidence']})")
    print(f"Suggestions: {len(result['resolution_suggestions'])} actions")
    for i, suggestion in enumerate(result['resolution_suggestions'], 1):
        print(f"  {i}. [{suggestion['priority']}] {suggestion['category']}: {suggestion['action']}")
    
    # Test Case 2: Backend Instability
    print("\n🔹 Test 2: Backend Instability")
    result = RootCauseAnalyzer.analyze(
        error_rate=0.55,
        avg_response_time=300,
        req_count=5,
        repeat_rate=0.2,
        usage_cluster=0,
        failure_probability=0.7
    )
    print(f"Root Cause: {result['root_cause']} (Confidence: {result['confidence']})")
    print(f"Suggestions: {len(result['resolution_suggestions'])} actions")
    
    # Test Case 3: Traffic Surge
    print("\n🔹 Test 3: Traffic Surge")
    result = RootCauseAnalyzer.analyze(
        error_rate=0.15,
        avg_response_time=450,
        req_count=12,  # 2.4x baseline
        repeat_rate=0.3,
        usage_cluster=1,
        failure_probability=0.3
    )
    print(f"Root Cause: {result['root_cause']} (Confidence: {result['confidence']})")
    print(f"Suggestions: {len(result['resolution_suggestions'])} actions")
    
    # Test Case 4: Abuse/Bot Activity
    print("\n🔹 Test 4: Abuse/Bot Activity")
    result = RootCauseAnalyzer.analyze(
        error_rate=0.1,
        avg_response_time=200,
        req_count=7,
        repeat_rate=0.85,  # High repetition
        usage_cluster=2,  # Bot cluster
        failure_probability=0.2
    )
    print(f"Root Cause: {result['root_cause']} (Confidence: {result['confidence']})")
    print(f"Suggestions: {len(result['resolution_suggestions'])} actions")
    
    # Test Case 5: System Overload (multiple conditions)
    print("\n🔹 Test 5: System Overload")
    result = RootCauseAnalyzer.analyze(
        error_rate=0.4,  # Backend instability
        avg_response_time=1200,  # Latency bottleneck
        req_count=15,  # Traffic surge
        repeat_rate=0.3,
        usage_cluster=1,
        failure_probability=0.8
    )
    print(f"Root Cause: {result['root_cause']} (Confidence: {result['confidence']})")
    print(f"Conditions Met: {', '.join(result['conditions_met'])}")
    print(f"Suggestions: {len(result['resolution_suggestions'])} actions")
    for i, suggestion in enumerate(result['resolution_suggestions'], 1):
        print(f"  {i}. [{suggestion['priority']}] {suggestion['category']}: {suggestion['action']}")
    
    print("\n✅ Root Cause Analyzer ready!")
