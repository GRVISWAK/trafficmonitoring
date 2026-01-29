"""
Generate diverse anomalies to populate dashboard charts
"""
import random
from datetime import datetime, timedelta
from database import SessionLocal, AnomalyLog

def populate_dashboard_data():
    """Generate diverse anomalies across multiple endpoints"""
    db = SessionLocal()
    
    try:
        # Clear existing anomalies
        db.query(AnomalyLog).delete()
        db.commit()
        print("✓ Cleared existing anomalies")
        
        # Define endpoints and their characteristics
        endpoints_config = {
            '/api/login': {'high': 8, 'medium': 12, 'low': 5},
            '/api/payment': {'high': 15, 'medium': 10, 'low': 3},
            '/api/search': {'high': 3, 'medium': 15, 'low': 8},
            '/api/profile': {'high': 5, 'medium': 8, 'low': 10},
            '/api/checkout': {'high': 12, 'medium': 8, 'low': 4},
            '/api/admin': {'high': 20, 'medium': 5, 'low': 2},
        }
        
        total_created = 0
        now = datetime.utcnow()
        
        for endpoint, priority_counts in endpoints_config.items():
            # Generate HIGH priority anomalies
            for i in range(priority_counts['high']):
                timestamp = now - timedelta(hours=random.randint(0, 48))
                anomaly = AnomalyLog(
                    endpoint=endpoint,
                    method=random.choice(['POST', 'GET', 'PUT']),
                    risk_score=random.uniform(0.75, 0.99),
                    priority='HIGH',
                    failure_probability=random.uniform(0.7, 0.95),
                    anomaly_score=random.uniform(0.8, 1.0),
                    is_anomaly=True,
                    usage_cluster=random.randint(0, 2),
                    req_count=random.randint(50, 200),
                    error_rate=random.uniform(0.4, 0.8),
                    avg_response_time=random.uniform(800, 2000),
                    max_response_time=random.uniform(2000, 5000),
                    payload_mean=random.uniform(5000, 15000),
                    unique_endpoints=random.randint(1, 3),
                    repeat_rate=random.uniform(0.6, 0.9),
                    status_entropy=random.uniform(1.5, 2.0),
                    timestamp=timestamp
                )
                db.add(anomaly)
                total_created += 1
            
            # Generate MEDIUM priority anomalies
            for i in range(priority_counts['medium']):
                timestamp = now - timedelta(hours=random.randint(0, 48))
                anomaly = AnomalyLog(
                    endpoint=endpoint,
                    method=random.choice(['POST', 'GET', 'PUT', 'DELETE']),
                    risk_score=random.uniform(0.45, 0.74),
                    priority='MEDIUM',
                    failure_probability=random.uniform(0.4, 0.69),
                    anomaly_score=random.uniform(0.5, 0.79),
                    is_anomaly=True,
                    usage_cluster=random.randint(0, 2),
                    req_count=random.randint(30, 100),
                    error_rate=random.uniform(0.2, 0.39),
                    avg_response_time=random.uniform(400, 799),
                    max_response_time=random.uniform(800, 1999),
                    payload_mean=random.uniform(2000, 8000),
                    unique_endpoints=random.randint(2, 5),
                    repeat_rate=random.uniform(0.3, 0.59),
                    status_entropy=random.uniform(1.0, 1.49),
                    timestamp=timestamp
                )
                db.add(anomaly)
                total_created += 1
            
            # Generate LOW priority anomalies
            for i in range(priority_counts['low']):
                timestamp = now - timedelta(hours=random.randint(0, 48))
                anomaly = AnomalyLog(
                    endpoint=endpoint,
                    method=random.choice(['GET', 'POST']),
                    risk_score=random.uniform(0.2, 0.44),
                    priority='LOW',
                    failure_probability=random.uniform(0.1, 0.39),
                    anomaly_score=random.uniform(0.3, 0.49),
                    is_anomaly=True,
                    usage_cluster=random.randint(0, 2),
                    req_count=random.randint(10, 50),
                    error_rate=random.uniform(0.05, 0.19),
                    avg_response_time=random.uniform(200, 399),
                    max_response_time=random.uniform(400, 799),
                    payload_mean=random.uniform(500, 3000),
                    unique_endpoints=random.randint(3, 8),
                    repeat_rate=random.uniform(0.1, 0.29),
                    status_entropy=random.uniform(0.5, 0.99),
                    timestamp=timestamp
                )
                db.add(anomaly)
                total_created += 1
        
        db.commit()
        
        print(f"\n✓ Successfully created {total_created} diverse anomalies!")
        print(f"\nBreakdown by endpoint:")
        for endpoint, counts in endpoints_config.items():
            total = sum(counts.values())
            print(f"  {endpoint}: {total} anomalies (H:{counts['high']}, M:{counts['medium']}, L:{counts['low']})")
        
        # Verify
        high_count = db.query(AnomalyLog).filter(AnomalyLog.priority == 'HIGH').count()
        med_count = db.query(AnomalyLog).filter(AnomalyLog.priority == 'MEDIUM').count()
        low_count = db.query(AnomalyLog).filter(AnomalyLog.priority == 'LOW').count()
        
        print(f"\n✓ Priority Distribution:")
        print(f"  HIGH: {high_count}")
        print(f"  MEDIUM: {med_count}")
        print(f"  LOW: {low_count}")
        print(f"  Total: {high_count + med_count + low_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("POPULATING DASHBOARD WITH TEST DATA")
    print("=" * 60)
    populate_dashboard_data()
    print("\n✓ Dashboard should now display charts!")
    print("  Refresh your browser at http://localhost:3000")
    print("=" * 60)
