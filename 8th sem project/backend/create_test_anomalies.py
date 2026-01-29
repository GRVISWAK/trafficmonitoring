"""
Generate test anomalies with resolution suggestions
"""
from database import SessionLocal, AnomalyLog, init_db
from datetime import datetime
import random

# Initialize DB
init_db()
db = SessionLocal()

# Create test anomalies with various patterns
test_anomalies = [
    {
        'endpoint': '/payment',
        'method': 'POST',
        'risk_score': 0.875,
        'priority': 'HIGH',
        'failure_probability': 0.7,
        'anomaly_score': 0.82,
        'is_anomaly': True,
        'usage_cluster': 1,
        'req_count': 12,
        'error_rate': 0.4,  # Backend instability
        'avg_response_time': 1200,  # Latency bottleneck
        'max_response_time': 2500,
        'payload_mean': 450,
        'unique_endpoints': 3,
        'repeat_rate': 0.3,
        'status_entropy': 1.2
    },
    {
        'endpoint': '/login',
        'method': 'POST',
        'risk_score': 0.92,
        'priority': 'HIGH',
        'failure_probability': 0.85,
        'anomaly_score': 0.88,
        'is_anomaly': True,
        'usage_cluster': 2,  # Bot cluster
        'req_count': 8,
        'error_rate': 0.15,
        'avg_response_time': 350,
        'max_response_time': 800,
        'payload_mean': 200,
        'unique_endpoints': 1,
        'repeat_rate': 0.85,  # High repeat - bot activity
        'status_entropy': 0.5
    },
    {
        'endpoint': '/search',
        'method': 'GET',
        'risk_score': 0.78,
        'priority': 'MEDIUM',
        'failure_probability': 0.45,
        'anomaly_score': 0.72,
        'is_anomaly': True,
        'usage_cluster': 0,
        'req_count': 15,  # Traffic surge
        'error_rate': 0.12,
        'avg_response_time': 450,
        'max_response_time': 900,
        'payload_mean': 320,
        'unique_endpoints': 2,
        'repeat_rate': 0.25,
        'status_entropy': 1.8
    },
    {
        'endpoint': '/profile',
        'method': 'GET',
        'risk_score': 0.81,
        'priority': 'HIGH',
        'failure_probability': 0.62,
        'anomaly_score': 0.75,
        'is_anomaly': True,
        'usage_cluster': 0,
        'req_count': 7,
        'error_rate': 0.08,
        'avg_response_time': 1500,  # High latency
        'max_response_time': 3200,
        'payload_mean': 850,
        'unique_endpoints': 1,
        'repeat_rate': 0.15,
        'status_entropy': 1.1
    }
]

try:
    # Clear existing anomalies (optional)
    current_count = db.query(AnomalyLog).count()
    print(f"Current anomalies in DB: {current_count}")
    
    # Add test anomalies
    for i, data in enumerate(test_anomalies, 1):
        anomaly = AnomalyLog(**data)
        db.add(anomaly)
        db.commit()
        print(f"✅ Created test anomaly #{i}: {data['endpoint']} (Error: {data['error_rate']*100}%, Latency: {data['avg_response_time']}ms)")
    
    total = db.query(AnomalyLog).count()
    print(f"\n✅ Total anomalies now: {total}")
    print(f"✅ Test anomalies created successfully!")
    print(f"\n💡 Refresh your browser to see the resolution suggestions!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
