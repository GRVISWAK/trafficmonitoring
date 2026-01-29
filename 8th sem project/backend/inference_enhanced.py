"""
Enhanced Inference Engine with Hybrid Detection
- Rule-based detection (rate spikes, error bursts)
- ML-based detection (Isolation Forest, Logistic Regression, K-Means)
- Failure prediction
- Combined risk scoring
"""

import joblib
import numpy as np
from pathlib import Path
import time


class HybridDetectionEngine:
    def __init__(self):
        self.models_dir = Path(__file__).parent / 'models'
        self.models_loaded = False
        self.load_models()
    
    def load_models(self):
        """Load all trained models and scalers"""
        try:
            # Load models
            self.iso_forest = joblib.load(self.models_dir / 'isolation_forest.pkl')
            self.iso_scaler = joblib.load(self.models_dir / 'isolation_scaler.pkl')
            self.kmeans = joblib.load(self.models_dir / 'kmeans.pkl')
            self.lr_classifier = joblib.load(self.models_dir / 'logistic_regression.pkl')
            self.lr_scaler = joblib.load(self.models_dir / 'lr_scaler.pkl')
            self.failure_predictor = joblib.load(self.models_dir / 'failure_predictor.pkl')
            self.failure_scaler = joblib.load(self.models_dir / 'failure_scaler.pkl')
            self.metadata = joblib.load(self.models_dir / 'metadata.pkl')
            
            self.models_loaded = True
            print("✅ All models loaded successfully")
            print(f"📊 Features: {self.metadata['feature_names']}")
            print(f"📊 Model Performance: Precision={self.metadata['metrics']['precision']:.4f}, "
                  f"Recall={self.metadata['metrics']['recall']:.4f}, "
                  f"F1={self.metadata['metrics']['f1_score']:.4f}")
            
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            self.models_loaded = False
    
    def rule_based_detection(self, features):
        """
        Simple rule-based detection for obvious anomalies
        - Rate spike: request_rate > threshold
        - Error burst: error_rate > threshold
        - Suspicious patterns
        """
        alerts = []
        rule_score = 0.0
        
        # Handle both dict and array inputs
        if isinstance(features, dict):
            request_rate = features.get('request_rate', 0)
            unique_endpoint_count = features.get('unique_endpoint_count', 0)
            method_ratio = features.get('method_ratio', 0)
            avg_payload_size = features.get('avg_payload_size', 0)
            error_rate = features.get('error_rate', 0)
            repeated_parameter_ratio = features.get('repeated_parameter_ratio', 0)
            user_agent_entropy = features.get('user_agent_entropy', 0)
        else:
            # Feature indices (based on order in CSV)
            request_rate = features[0]
            unique_endpoint_count = features[1]
            method_ratio = features[2]
            avg_payload_size = features[3]
            error_rate = features[4]
            repeated_parameter_ratio = features[5]
            user_agent_entropy = features[6]
        
        # Rule 1: Rate spike detection
        if request_rate > 15:  # More than 15 requests/second
            alerts.append("RATE_SPIKE")
            rule_score += 0.3
        
        # Rule 2: Error burst detection
        if error_rate > 0.5:  # More than 50% errors
            alerts.append("ERROR_BURST")
            rule_score += 0.4
        
        # Rule 3: Suspicious bot behavior
        if user_agent_entropy < 0.1 and repeated_parameter_ratio > 0.7:
            alerts.append("BOT_PATTERN")
            rule_score += 0.3
        
        # Rule 4: Large payload attack
        if avg_payload_size > 5000:
            alerts.append("LARGE_PAYLOAD")
            rule_score += 0.2
        
        # Rule 5: Endpoint scanning
        if unique_endpoint_count > 20:
            alerts.append("ENDPOINT_SCAN")
            rule_score += 0.25
        
        return min(rule_score, 1.0), alerts
    
    def predict_anomaly(self, features):
        """
        Hybrid detection combining rules and ML
        Returns comprehensive threat assessment
        """
        if not self.models_loaded:
            return {
                'is_anomaly': False,
                'risk_score': 0.0,
                'priority': 'LOW',
                'detection_method': 'MODELS_NOT_LOADED',
                'details': {}
            }
        
        start_time = time.time()
        
        # Convert features to array if dict
        if isinstance(features, dict):
            feature_order = ['request_rate', 'unique_endpoint_count', 'method_ratio', 
                           'avg_payload_size', 'error_rate', 'repeated_parameter_ratio', 
                           'user_agent_entropy', 'avg_response_time', 'max_response_time']
            features_array = np.array([features.get(f, 0) for f in feature_order]).reshape(1, -1)
        else:
            features_array = np.array(features).reshape(1, -1)
        
        # 1. Rule-based detection
        rule_score, rule_alerts = self.rule_based_detection(features)
        
        # 2. Isolation Forest (anomaly detection)
        features_scaled_iso = self.iso_scaler.transform(features_array)
        iso_prediction = self.iso_forest.predict(features_scaled_iso)[0]
        iso_score_raw = self.iso_forest.score_samples(features_scaled_iso)[0]
        # Convert to 0-1 range (more negative = more anomalous)
        iso_score = 1 / (1 + np.exp(iso_score_raw))  # Sigmoid transformation
        
        # 3. Logistic Regression (misuse classification)
        features_scaled_lr = self.lr_scaler.transform(features_array)
        lr_prediction = self.lr_classifier.predict(features_scaled_lr)[0]
        lr_probability = self.lr_classifier.predict_proba(features_scaled_lr)[0][1]
        
        # 4. K-Means (behavior clustering)
        cluster = self.kmeans.predict(features_array)[0]
        cluster_distance = np.min(self.kmeans.transform(features_array))
        
        # 5. Failure prediction (next window)
        features_scaled_failure = self.failure_scaler.transform(features_array)
        failure_prediction = self.failure_predictor.predict(features_scaled_failure)[0]
        failure_probability = self.failure_predictor.predict_proba(features_scaled_failure)[0][1]
        
        # Hybrid scoring (weighted combination)
        # 30% rule-based + 25% isolation + 30% logistic + 15% failure prediction
        hybrid_score = (
            0.30 * rule_score +
            0.25 * iso_score +
            0.30 * lr_probability +
            0.15 * failure_probability
        )
        
        # Determine if anomaly
        is_anomaly = hybrid_score >= 0.5 or lr_prediction == 1 or iso_prediction == -1
        
        # Priority assignment
        if hybrid_score >= 0.8:
            priority = 'CRITICAL'
        elif hybrid_score >= 0.6:
            priority = 'HIGH'
        elif hybrid_score >= 0.4:
            priority = 'MEDIUM'
        else:
            priority = 'LOW'
        
        # Detection method
        detection_methods = []
        if rule_score > 0:
            detection_methods.append('RULE_BASED')
        if iso_prediction == -1:
            detection_methods.append('ISOLATION_FOREST')
        if lr_prediction == 1:
            detection_methods.append('LOGISTIC_REGRESSION')
        if failure_prediction == 1:
            detection_methods.append('FAILURE_PREDICTION')
        
        detection_latency_ms = (time.time() - start_time) * 1000
        
        return {
            'is_anomaly': bool(is_anomaly),
            'risk_score': float(hybrid_score),
            'priority': priority,
            'detection_method': '+'.join(detection_methods) if detection_methods else 'ML_ENSEMBLE',
            'detection_latency_ms': detection_latency_ms,
            'details': {
                'rule_score': float(rule_score),
                'rule_alerts': rule_alerts,
                'isolation_forest': {
                    'prediction': int(iso_prediction),
                    'score': float(iso_score)
                },
                'logistic_regression': {
                    'prediction': int(lr_prediction),
                    'probability': float(lr_probability)
                },
                'cluster': {
                    'id': int(cluster),
                    'distance': float(cluster_distance)
                },
                'failure_prediction': {
                    'will_fail_next_window': bool(failure_prediction),
                    'probability': float(failure_probability)
                }
            }
        }
    
    def calculate_risk_score(self, anomaly_score, failure_prob, cluster_distance):
        """Legacy compatibility - now uses hybrid detection"""
        # This is kept for backward compatibility
        # Real scoring is done in predict_anomaly
        return anomaly_score * 0.5 + failure_prob * 0.3 + min(cluster_distance/100, 0.2)
    
    def assign_priority(self, risk_score):
        """Legacy compatibility"""
        if risk_score >= 0.8:
            return 'CRITICAL'
        elif risk_score >= 0.6:
            return 'HIGH'
        elif risk_score >= 0.4:
            return 'MEDIUM'
        else:
            return 'LOW'


# For backward compatibility
class MLInferenceEngine(HybridDetectionEngine):
    """Alias for backward compatibility"""
    pass


if __name__ == "__main__":
    # Test the engine
    engine = HybridDetectionEngine()
    
    # Test with sample features
    print("\n" + "="*70)
    print("TESTING HYBRID DETECTION ENGINE")
    print("="*70)
    
    # Normal traffic
    normal_features = [10, 5, 2.5, 300, 0.0, 0.2, 1.5, 150, 200]
    print("\n🔹 Testing NORMAL traffic:")
    result = engine.predict_anomaly(normal_features)
    print(f"   Risk Score: {result['risk_score']:.4f}")
    print(f"   Priority: {result['priority']}")
    print(f"   Is Anomaly: {result['is_anomaly']}")
    print(f"   Detection Method: {result['detection_method']}")
    print(f"   Latency: {result['detection_latency_ms']:.2f}ms")
    
    # Anomalous traffic (high rate + errors)
    anomalous_features = [25, 15, 5.0, 8000, 0.8, 0.9, 0.05, 250, 400]
    print("\n🔹 Testing ANOMALOUS traffic (rate spike + error burst):")
    result = engine.predict_anomaly(anomalous_features)
    print(f"   Risk Score: {result['risk_score']:.4f}")
    print(f"   Priority: {result['priority']}")
    print(f"   Is Anomaly: {result['is_anomaly']}")
    print(f"   Detection Method: {result['detection_method']}")
    print(f"   Rule Alerts: {result['details']['rule_alerts']}")
    print(f"   Latency: {result['detection_latency_ms']:.2f}ms")
    
    print("\n✅ Hybrid detection engine ready!")
