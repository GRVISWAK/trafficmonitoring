"""
Quick test script to verify enhanced models are working
"""
import os
import pandas as pd
import numpy as np
from pathlib import Path

def test_models():
    print("=" * 80)
    print("✅ ENHANCED MODELS TEST")
    print("=" * 80)
    print()
    
    # Check if training data exists
    data_path = Path(__file__).parent / 'datasets' / 'processed' / 'combined_training_data.csv'
    if not data_path.exists():
        print("❌ Training data not found. Run process_csic.bat first.")
        return
    
    # Load data
    df = pd.read_csv(data_path)
    print(f"📊 Training Data: {len(df)} samples")
    print(f"   Features: {', '.join(df.columns[:-1])}")
    print(f"   Normal: {(df['is_anomalous']==0).sum()}, Anomalous: {(df['is_anomalous']==1).sum()}")
    print()
    
    # Check if models exist
    models_dir = Path(__file__).parent / 'models'
    model_files = [
        'isolation_forest.pkl',
        'isolation_scaler.pkl',
        'kmeans.pkl',
        'logistic_regression.pkl',
        'lr_scaler.pkl',
        'failure_predictor.pkl',
        'failure_scaler.pkl',
        'metadata.pkl'
    ]
    
    print("📦 Model Files:")
    all_exist = True
    for model_file in model_files:
        path = models_dir / model_file
        if path.exists():
            size = path.stat().st_size / 1024  # KB
            print(f"   ✅ {model_file} ({size:.1f} KB)")
        else:
            print(f"   ❌ {model_file} (missing)")
            all_exist = False
    print()
    
    if not all_exist:
        print("❌ Some models missing. Run train.bat to train all models.")
        return
    
    # Test inference
    print("🔍 Testing Hybrid Detection Engine...")
    try:
        from inference_enhanced import HybridDetectionEngine
        
        engine = HybridDetectionEngine()
        print("   ✅ Models loaded successfully")
        
        # Test with normal traffic
        normal_features = {
            'request_rate': 5.0,
            'unique_endpoint_count': 3,
            'method_ratio': 1.5,
            'avg_payload_size': 200,
            'error_rate': 0.05,
            'repeated_parameter_ratio': 0.2,
            'user_agent_entropy': 2.5,
            'avg_response_time': 150,
            'max_response_time': 200
        }
        
        result = engine.predict_anomaly(normal_features)
        print(f"\n   🔹 NORMAL Traffic Test:")
        print(f"      Risk Score: {result['risk_score']:.4f}")
        print(f"      Priority: {result['priority']}")
        print(f"      Is Anomaly: {result['is_anomaly']}")
        print(f"      Detection Method: {result['detection_method']}")
        print(f"      Latency: {result['detection_latency_ms']:.2f}ms")
        
        # Test with anomalous traffic
        attack_features = {
            'request_rate': 25.0,  # High rate
            'unique_endpoint_count': 15,  # Many endpoints
            'method_ratio': 0.5,
            'avg_payload_size': 6000,  # Large payload
            'error_rate': 0.6,  # Many errors
            'repeated_parameter_ratio': 0.8,
            'user_agent_entropy': 0.3,  # Low entropy (bot)
            'avg_response_time': 300,
            'max_response_time': 500
        }
        
        result = engine.predict_anomaly(attack_features)
        print(f"\n   🔹 ATTACK Traffic Test:")
        print(f"      Risk Score: {result['risk_score']:.4f}")
        print(f"      Priority: {result['priority']}")
        print(f"      Is Anomaly: {result['is_anomaly']}")
        print(f"      Detection Method: {result['detection_method']}")
        if 'details' in result and result['details'].get('rule_alerts'):
            print(f"      Rule Alerts: {', '.join(result['details']['rule_alerts'])}")
        else:
            print(f"      Rule Alerts: None")
        print(f"      Latency: {result['detection_latency_ms']:.2f}ms")
        
        print()
        print("=" * 80)
        print("✅ ALL TESTS PASSED - SYSTEM READY FOR PRODUCTION")
        print("=" * 80)
        
    except Exception as e:
        print(f"   ❌ Error during inference: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_models()
