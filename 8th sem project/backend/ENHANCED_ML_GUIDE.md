# 🚀 Enhanced ML Pipeline Guide

## Overview

This project now uses a **hybrid detection system** combining rule-based heuristics with advanced machine learning models to detect API misuse and predict failures.

---

## 📊 Dataset

**CSIC 2010 HTTP Dataset**
- **Total Requests**: 61,065
  - Normal: 36,000 (59%)
  - Anomalous: 25,065 (41%)
- **Window Size**: 10 requests
- **Training Samples**: 6,107 windows
  - Normal windows: 3,600 (59%)
  - Anomalous windows: 2,507 (41%)

---

## 🎯 Features (9 Total)

### Behavioral Features
1. **request_rate** - Requests per time unit (normalized by window duration)
2. **unique_endpoint_count** - Number of distinct endpoints accessed
3. **method_ratio** - Ratio of GET to POST requests

### Payload Features
4. **avg_payload_size** - Average request payload size in bytes
5. **error_rate** - Percentage of 4xx/5xx HTTP errors
6. **repeated_parameter_ratio** - Ratio of repeated parameters (indicates SQL injection patterns)

### Entropy Features
7. **user_agent_entropy** - Shannon entropy of user-agent strings (detects bots)

### Performance Features
8. **avg_response_time** - Average response latency
9. **max_response_time** - Maximum response latency

---

## 🤖 Machine Learning Models

### 1. Isolation Forest (Unsupervised Anomaly Detection)
- **Training Data**: 3,600 normal windows ONLY
- **Purpose**: Detects deviations from normal behavior
- **Contamination**: 5%
- **Estimators**: 300 trees
- **Output**: Anomaly score (-1 for outliers, 1 for inliers)

### 2. K-Means Clustering (Behavioral Grouping)
- **Clusters**: 3
  - Cluster 0: Normal behavior (58.9%)
  - Cluster 1: Suspicious behavior (15.3%)
  - Cluster 2: Attack patterns (25.8%)
- **Purpose**: Groups similar traffic patterns
- **Output**: Cluster assignment and distance from centroid

### 3. Logistic Regression (Supervised Classification)
- **Training**: Stratified 80/20 split (4,885 train / 1,222 test)
- **Class Balancing**: Balanced weights to handle class imbalance
- **Purpose**: Binary classification (Normal vs Anomalous)
- **Performance**:
  - Precision: **1.0000** (no false positives)
  - Recall: **1.0000** (caught all attacks)
  - F1-Score: **1.0000**
  - Confusion Matrix: TN=720, FP=0, FN=0, TP=502
- **Output**: Probability of anomaly (0.0-1.0)

### 4. Failure Predictor (Proactive Detection)
- **Training**: Shifted labels (predicts next-window failure)
- **Purpose**: Predicts if next window will be anomalous
- **Performance**: Precision=1.0, Recall=1.0, F1=1.0
- **Output**: Probability of next-window failure

---

## 🔍 Hybrid Detection System

### Rule-Based Detection (5 Rules)

1. **RATE_SPIKE**
   - Trigger: `request_rate > 15 req/s`
   - Indicates: DDoS or brute force attack

2. **ERROR_BURST**
   - Trigger: `error_rate > 50%`
   - Indicates: Scanning or injection attempts

3. **BOT_PATTERN**
   - Trigger: `user_agent_entropy < 0.5 AND repeated_parameter_ratio > 0.5`
   - Indicates: Automated bot attacks

4. **LARGE_PAYLOAD**
   - Trigger: `avg_payload_size > 5000 bytes`
   - Indicates: Data exfiltration or buffer overflow

5. **ENDPOINT_SCAN**
   - Trigger: `unique_endpoint_count > 20`
   - Indicates: Reconnaissance or directory traversal

### Hybrid Scoring Formula

```
risk_score = (0.30 × rule_score) + 
             (0.25 × isolation_score) + 
             (0.30 × logistic_score) + 
             (0.15 × failure_score)
```

**Weights Breakdown**:
- **30%** Rule-based (fast, catches known patterns)
- **25%** Isolation Forest (unsupervised anomaly detection)
- **30%** Logistic Regression (supervised classification)
- **15%** Failure prediction (proactive alerting)

### Risk Priority Levels

- **CRITICAL**: `risk_score > 0.75` - Immediate action required
- **HIGH**: `risk_score > 0.55` - Investigate urgently
- **MEDIUM**: `risk_score > 0.35` - Monitor closely
- **LOW**: `risk_score ≤ 0.35` - Normal with minor anomalies

---

## 🔧 Usage

### 1. Process Dataset

```bash
cd backend
process_csic.bat
```

This creates `combined_training_data.csv` with 6,107 samples.

### 2. Train Models

```bash
train.bat
```

**Output**:
- `isolation_forest.pkl` + `isolation_scaler.pkl`
- `kmeans.pkl`
- `logistic_regression.pkl` + `lr_scaler.pkl`
- `failure_predictor.pkl` + `failure_scaler.pkl`
- `metadata.pkl`

### 3. Test Detection

```python
from inference_enhanced import HybridDetectionEngine

# Initialize
engine = HybridDetectionEngine()

# Prepare features (9 features)
features = {
    'request_rate': 12.5,
    'unique_endpoint_count': 5,
    'method_ratio': 0.8,
    'avg_payload_size': 500,
    'error_rate': 0.1,
    'repeated_parameter_ratio': 0.2,
    'user_agent_entropy': 2.5,
    'avg_response_time': 150,
    'max_response_time': 300
}

# Predict
result = engine.predict_anomaly(features)

print(f"Is Anomaly: {result['is_anomaly']}")
print(f"Risk Score: {result['risk_score']:.4f}")
print(f"Priority: {result['priority']}")
print(f"Detection Method: {result['detection_method']}")
print(f"Latency: {result['detection_latency_ms']:.2f}ms")
```

**Example Output**:
```
Is Anomaly: True
Risk Score: 0.4661
Priority: MEDIUM
Detection Method: RULE_BASED+ISOLATION_FOREST
Latency: 23.83ms
```

---

## 📈 Performance Metrics

### Training Performance
- **Training Time**: <1 second (all 4 models)
- **Dataset Size**: 6,107 samples
- **Feature Extraction**: Instant (pandas vectorized operations)

### Detection Performance
- **Precision**: 1.0000 (100% - no false positives)
- **Recall**: 1.0000 (100% - caught all attacks)
- **F1-Score**: 1.0000 (perfect balance)
- **Detection Latency**:
  - Logistic Regression: <1ms
  - Full Hybrid (all models + rules): 23-145ms

### Model Sizes
- Total: ~2MB (all 8 files)
- Load time: ~145ms (first prediction)
- Subsequent predictions: ~24ms

---

## 🎓 For Viva/Mentor Demonstration

### Key Points to Highlight

1. **Feature Engineering**:
   - "We designed 9 features capturing request patterns, error rates, payload characteristics, and behavioral entropy"
   - "User-agent entropy detects automated bots"
   - "Repeated parameter ratio catches SQL injection patterns"

2. **ML Architecture**:
   - "Isolation Forest trained ONLY on normal traffic (unsupervised)"
   - "K-Means groups behaviors into 3 clusters"
   - "Logistic Regression provides supervised classification"
   - "Failure Predictor enables proactive detection"

3. **Hybrid Approach**:
   - "Combines rule-based (fast, known patterns) with ML (novel attacks)"
   - "5 simple rules + 4 ML models"
   - "Weighted ensemble: 30% rules + 70% ML"

4. **Performance**:
   - "100% precision and recall on test set"
   - "Sub-150ms detection latency"
   - "Trained on 6,107 real samples from CSIC 2010"

5. **Advanced Techniques**:
   - "StandardScaler for feature normalization"
   - "Stratified splitting maintains class distribution"
   - "Class balancing handles imbalanced data"
   - "Model persistence with joblib"

### Demo Flow

1. **Show Dataset Processing**:
   ```bash
   python process_csic_csv.py
   ```
   - Explain: "We process 61,065 HTTP requests into 6,107 windows"

2. **Show Training**:
   ```bash
   python train_models_enhanced.py
   ```
   - Highlight: "4 models trained in under 1 second with 100% accuracy"

3. **Show Detection**:
   ```bash
   python inference_enhanced.py
   ```
   - Demonstrate: Normal traffic (LOW risk) vs Anomalous (MEDIUM/HIGH risk)
   - Show: Rule alerts (RATE_SPIKE, ERROR_BURST, etc.)

4. **Show Model Files**:
   ```bash
   dir models
   ```
   - Explain: "8 files - models + scalers + metadata"

---

## 🔬 Technical Details

### Standardization

All features are standardized using `StandardScaler`:

```
z = (x - μ) / σ
```

Where:
- `x` = feature value
- `μ` = mean of training data
- `σ` = standard deviation of training data

**Why?** Different features have different scales (e.g., request_rate vs user_agent_entropy). Standardization ensures all features contribute equally to the model.

### Stratified Split

Training/testing split maintains class distribution:

```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
```

**Why?** Ensures both train and test sets have the same proportion of normal/anomalous samples (59% / 41%).

### Class Balancing

Logistic Regression uses balanced weights:

```python
LogisticRegression(class_weight='balanced', max_iter=1000)
```

**Why?** Gives more weight to minority class (anomalous 41%), preventing model bias towards majority class (normal 59%).

### Isolation Forest on Normal Only

```python
normal_windows = X_train[y_train == 0]
isolation_forest.fit(normal_windows)
```

**Why?** Isolation Forest learns "what is normal" and flags deviations. Training on mixed data would confuse the model.

---

## 📦 Model Files

All models saved in `backend/models/`:

```
isolation_forest.pkl       - Anomaly detection (2.1 MB)
isolation_scaler.pkl       - Feature scaler for IF (2 KB)
kmeans.pkl                 - Clustering model (5 KB)
logistic_regression.pkl    - Binary classifier (2 KB)
lr_scaler.pkl              - Feature scaler for LR (2 KB)
failure_predictor.pkl      - Failure prediction (2 KB)
failure_scaler.pkl         - Feature scaler for FP (2 KB)
metadata.pkl               - Performance metrics (1 KB)
```

---

## ✅ Production Checklist

- [x] Enhanced features (9 features)
- [x] Isolation Forest on normal windows only
- [x] K-Means clustering (3 clusters)
- [x] Logistic Regression with full metrics
- [x] Hybrid detection (rules + ML)
- [x] Failure prediction
- [x] Standardization
- [x] Stratified split
- [x] Model evaluation (precision, recall, F1, detection latency)
- [x] All models saved with joblib
- [x] 100% precision and recall achieved
- [x] Sub-150ms detection latency
- [x] Comprehensive documentation

---

## 🚀 Next Steps (Optional Enhancements)

1. **Real-time Learning**: Retrain models periodically with new data
2. **Explainability**: Add SHAP/LIME for feature importance
3. **Ensemble Voting**: Add voting mechanism for model disagreement
4. **Threshold Tuning**: Adjust risk thresholds based on production data
5. **Multi-class Classification**: Classify attack types (SQLi, XSS, etc.)
6. **Sequence Models**: Use LSTM/GRU for temporal patterns
7. **Anomaly Clustering**: Cluster anomalies to identify attack families

---

## 📚 References

- **CSIC 2010 Dataset**: [Information Security Institute, CSIC](http://www.isi.csic.es/dataset/)
- **Isolation Forest**: Liu et al., "Isolation Forest" (2008)
- **K-Means**: MacQueen, "Some Methods for Classification and Analysis" (1967)
- **Logistic Regression**: Cox, "The Regression Analysis of Binary Sequences" (1958)

---

**Author**: 8th Semester Project Team  
**Date**: December 2025  
**Status**: ✅ Production Ready
