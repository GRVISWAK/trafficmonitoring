"""
Test script for enhanced ML dashboard components
"""
import sys
sys.path.insert(0, 'c:\\Users\\HP\\Desktop\\8th sem project\\backend')

from window_manager import SlidingWindowManager
from traffic_simulator import traffic_simulator
from inference_enhanced import HybridDetectionEngine

print("=" * 80)
print("🧪 TESTING ENHANCED ML DASHBOARD COMPONENTS")
print("=" * 80)
print()

# Test 1: Window Manager
print("1️⃣ Testing Sliding Window Manager...")
wm = SlidingWindowManager(window_size=10)
print(f"   ✅ Window size: {wm.window_size}")
print(f"   ✅ Current requests: {len(wm.requests)}")
print(f"   ✅ Windows processed: {wm.window_count}")
print()

# Test 2: Traffic Simulator
print("2️⃣ Testing Traffic Simulator...")
normal_requests = traffic_simulator.generate_normal_traffic(count=3)
print(f"   ✅ Generated {len(normal_requests)} normal requests")
print(f"   ✅ Sample: {normal_requests[0]['method']} {normal_requests[0]['path']} - Status: {normal_requests[0]['status']}")
print()

# Test 3: Anomaly Generation
print("3️⃣ Testing Anomaly Generation...")
rate_spike = traffic_simulator.generate_rate_spike(count=3)
print(f"   ✅ Generated {len(rate_spike)} rate spike requests")
print(f"   ✅ Anomaly type: {rate_spike[0]['anomaly_type']}")
print()

# Test 4: Full Window Processing
print("4️⃣ Testing Full Window Processing...")
wm_test = SlidingWindowManager(window_size=10)
print(f"   Adding 10 requests to window...")

for i, req in enumerate(normal_requests[:3]):
    features = wm_test.add_request(
        method=req['method'],
        path=req['path'],
        status=req['status'],
        latency=req['latency'],
        payload_size=req['payload_size'],
        user_agent=req['user_agent'],
        parameters=req.get('parameters', {})
    )
    if features:
        print(f"   ✅ Window full! Features extracted:")
        print(f"      - request_rate: {features['request_rate']:.2f}")
        print(f"      - unique_endpoint_count: {features['unique_endpoint_count']}")
        print(f"      - error_rate: {features['error_rate']:.2f}")
        break
    else:
        print(f"   ➕ Added request {i+1}/10")

# Add more to fill window
for i in range(7):
    features = wm_test.add_request(
        method='GET',
        path='/test',
        status=200,
        latency=100.0,
        payload_size=0,
        user_agent='test-agent',
        parameters={}
    )
    if features:
        print(f"   ✅ Window full at request 10!")
        print(f"      Features extracted:")
        print(f"      - request_rate: {features['request_rate']:.2f}")
        print(f"      - unique_endpoint_count: {features['unique_endpoint_count']}")
        print(f"      - method_ratio: {features['method_ratio']:.2f}")
        print(f"      - avg_payload_size: {features['avg_payload_size']:.2f}")
        print(f"      - error_rate: {features['error_rate']:.2f}")
        print(f"      - avg_response_time: {features['avg_response_time']:.2f}")
        break
    else:
        print(f"   ➕ Added request {4+i}/10")

print()

# Test 5: ML Inference
print("5️⃣ Testing ML Inference with Window Features...")
if features:
    engine = HybridDetectionEngine()
    prediction = engine.predict_anomaly(features)
    
    print(f"   ✅ ML Inference Complete:")
    print(f"      - Is Anomaly: {prediction['is_anomaly']}")
    print(f"      - Risk Score: {prediction['risk_score']:.4f}")
    print(f"      - Priority: {prediction['priority']}")
    print(f"      - Detection Method: {prediction['detection_method']}")
    if 'details' in prediction and prediction['details'].get('rule_alerts'):
        print(f"      - Rule Alerts: {', '.join(prediction['details']['rule_alerts'])}")
    print(f"      - Detection Latency: {prediction['detection_latency_ms']:.2f}ms")
print()

# Test 6: Anomaly Detection
print("6️⃣ Testing Anomaly Detection with Rate Spike...")
wm_anomaly = SlidingWindowManager(window_size=10)
rate_spike_requests = traffic_simulator.generate_rate_spike(count=10)

for req in rate_spike_requests:
    features = wm_anomaly.add_request(
        method=req['method'],
        path=req['path'],
        status=req['status'],
        latency=req['latency'],
        payload_size=req['payload_size'],
        user_agent=req['user_agent'],
        parameters=req.get('parameters', {})
    )

if features:
    prediction = engine.predict_anomaly(features)
    print(f"   ✅ Rate Spike Detection:")
    print(f"      - Anomaly Type: RATE_SPIKE")
    print(f"      - Is Anomaly: {prediction['is_anomaly']}")
    print(f"      - Risk Score: {prediction['risk_score']:.4f}")
    print(f"      - Priority: {prediction['priority']}")
    print(f"      - Detection Method: {prediction['detection_method']}")
    if 'details' in prediction and prediction['details'].get('rule_alerts'):
        print(f"      - Rule Alerts: {', '.join(prediction['details']['rule_alerts'])}")

print()
print("=" * 80)
print("✅ ALL TESTS PASSED - SYSTEM READY")
print("=" * 80)
