"""
Manual trigger to run ML anomaly detection immediately.
Use this to force analysis without waiting for the 60-second background task.
"""
import sys
sys.path.insert(0, r'c:\Users\HP\Desktop\8th sem project\backend')

from feature_engineering import extract_features_from_logs
from inference import inference_engine
from database import SessionLocal, AnomalyLog
from datetime import datetime

def run_manual_detection():
    print("🔍 Running manual anomaly detection...")
    print("="*60)
    
    # Extract features from recent logs
    features = extract_features_from_logs(time_window_minutes=1)
    
    if features is None:
        print("❌ No API logs found in the last minute!")
        print("   Make sure you've made some API requests.")
        return
    
    print(f"✅ Features extracted:")
    print(f"   - Endpoint: {features['endpoint']}")
    print(f"   - Method: {features['method']}")
    print(f"   - Request count: {features['req_count']}")
    print(f"   - Error rate: {features['error_rate']:.2%}")
    print(f"   - Avg response time: {features['avg_response_time']:.2f}ms")
    print(f"   - Repeat rate: {features['repeat_rate']:.2%}")
    
    # Run ML inference
    print("\n🤖 Running ML models...")
    prediction = inference_engine.predict(features)
    
    print(f"\n📊 ML Prediction Results:")
    print(f"   - Anomaly Score: {prediction['anomaly_score']:.4f}")
    print(f"   - Is Anomaly: {'YES ⚠️' if prediction['is_anomaly'] else 'NO ✓'}")
    print(f"   - Usage Cluster: {prediction['usage_cluster']} {'(BOT!)' if prediction['usage_cluster'] == inference_engine.bot_cluster else ''}")
    print(f"   - Failure Probability: {prediction['failure_probability']:.2%}")
    print(f"   - RISK SCORE: {prediction['risk_score']:.4f}")
    print(f"   - PRIORITY: {prediction['priority']}")
    
    # Save to database
    db = SessionLocal()
    try:
        anomaly_log = AnomalyLog(
            endpoint=features['endpoint'],
            method=features['method'],
            risk_score=prediction['risk_score'],
            priority=prediction['priority'],
            failure_probability=prediction['failure_probability'],
            anomaly_score=prediction['anomaly_score'],
            is_anomaly=prediction['is_anomaly'],
            usage_cluster=prediction['usage_cluster'],
            req_count=features['req_count'],
            error_rate=features['error_rate'],
            avg_response_time=features['avg_response_time'],
            max_response_time=features['max_response_time'],
            payload_mean=features['payload_mean'],
            unique_endpoints=features['unique_endpoints'],
            repeat_rate=features['repeat_rate'],
            status_entropy=features['status_entropy']
        )
        db.add(anomaly_log)
        db.commit()
        db.refresh(anomaly_log)
        
        print(f"\n✅ Anomaly saved to database (ID: {anomaly_log.id})")
        
        if prediction['risk_score'] >= 0.8:
            print(f"\n🚨 HIGH RISK ALERT!")
            print(f"   Endpoint {features['endpoint']} triggered critical anomaly!")
        
    finally:
        db.close()
    
    print("\n" + "="*60)
    print("✅ Manual detection complete!")
    print("   Check dashboard: http://localhost:3000")
    print("   Or API: http://localhost:8000/api/anomalies")

if __name__ == "__main__":
    run_manual_detection()
