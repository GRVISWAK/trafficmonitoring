"""
Enhanced ML Training Pipeline with Hybrid Detection
- Isolation Forest (on normal windows only)
- K-Means clustering
- Logistic Regression for misuse classification
- Failure prediction
- Hybrid detection (rules + ML)
- Full evaluation metrics
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import precision_score, recall_score, f1_score, classification_report, confusion_matrix
import joblib
import os
from pathlib import Path
import time


def load_real_datasets():
    """Load processed CSIC dataset"""
    processed_dir = Path(__file__).parent / "datasets" / "processed"
    combined_path = processed_dir / "combined_training_data.csv"
    
    if combined_path.exists():
        df = pd.read_csv(combined_path)
        print(f"\n✅ Loaded REAL DATASET from {combined_path}")
        print(f"📊 Total Training Samples: {len(df)}")
        print(f"📊 Features: {[col for col in df.columns if col != 'is_anomalous']}")
        
        if 'is_anomalous' in df.columns:
            normal_count = (df['is_anomalous'] == 0).sum()
            anomalous_count = (df['is_anomalous'] == 1).sum()
            print(f"📊 Normal windows: {normal_count}")
            print(f"📊 Anomalous windows: {anomalous_count}")
        
        print(f"\n📈 Dataset Statistics:")
        print(df.describe())
        return df
    
    print("\n⚠️ No real datasets found. Run process_csic_csv.py first!")
    return None


def train_isolation_forest_on_normal(X_normal):
    """
    Train Isolation Forest ONLY on normal traffic windows
    This makes it better at detecting anomalies
    """
    print("\n" + "="*70)
    print("TRAINING ISOLATION FOREST (Anomaly Detection)")
    print("="*70)
    print(f"Training on {len(X_normal)} NORMAL windows only...")
    
    # Scale features
    scaler = StandardScaler()
    X_normal_scaled = scaler.fit_transform(X_normal)
    
    # Train Isolation Forest
    iso_forest = IsolationForest(
        n_estimators=300,
        contamination=0.05,  # Expect 5% anomalies in production
        random_state=42,
        n_jobs=-1,
        verbose=1
    )
    
    iso_forest.fit(X_normal_scaled)
    
    # Test on normal data
    scores = iso_forest.score_samples(X_normal_scaled)
    predictions = iso_forest.predict(X_normal_scaled)
    anomalies_detected = (predictions == -1).sum()
    
    print(f"✅ Isolation Forest trained")
    print(f"   Anomalies detected in normal data: {anomalies_detected} ({anomalies_detected/len(X_normal)*100:.1f}%)")
    
    return iso_forest, scaler


def train_kmeans(X):
    """Train K-Means for behavior clustering"""
    print("\n" + "="*70)
    print("TRAINING K-MEANS (Behavior Clustering)")
    print("="*70)
    
    # Determine optimal clusters (elbow method)
    inertias = []
    K_range = range(2, min(11, len(X)//10))
    
    for k in K_range:
        kmeans_temp = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans_temp.fit(X)
        inertias.append(kmeans_temp.inertia_)
    
    # Use 3 clusters by default (Normal, Suspicious, Attack)
    optimal_k = 3
    print(f"Using {optimal_k} clusters: Normal, Suspicious, Attack")
    
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=20, verbose=1)
    kmeans.fit(X)
    
    clusters = kmeans.predict(X)
    print(f"\n✅ K-Means trained")
    print(f"   Cluster distribution:")
    for i in range(optimal_k):
        count = (clusters == i).sum()
        print(f"   Cluster {i}: {count} samples ({count/len(X)*100:.1f}%)")
    
    return kmeans, optimal_k


def train_logistic_regression(X_train, y_train, X_test, y_test):
    """
    Train Logistic Regression for misuse classification
    With full evaluation metrics
    """
    print("\n" + "="*70)
    print("TRAINING LOGISTIC REGRESSION (Misuse Classification)")
    print("="*70)
    print(f"Training samples: {len(X_train)}")
    print(f"Testing samples: {len(X_test)}")
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Logistic Regression
    lr = LogisticRegression(
        max_iter=1000,
        class_weight='balanced',  # Handle class imbalance
        random_state=42,
        verbose=1
    )
    
    start_time = time.time()
    lr.fit(X_train_scaled, y_train)
    training_time = time.time() - start_time
    
    # Evaluate
    start_time = time.time()
    y_pred = lr.predict(X_test_scaled)
    inference_time = (time.time() - start_time) / len(X_test)  # Per-sample latency
    
    # Calculate metrics
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    
    print(f"\n✅ Logistic Regression trained")
    print(f"   Training time: {training_time:.2f}s")
    print(f"   Detection latency: {inference_time*1000:.2f}ms per sample")
    print(f"\n📊 Performance Metrics:")
    print(f"   Precision: {precision:.4f}")
    print(f"   Recall: {recall:.4f}")
    print(f"   F1-Score: {f1:.4f}")
    
    print(f"\n📊 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Normal', 'Anomalous']))
    
    print(f"\n📊 Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"   True Negatives: {cm[0,0]}, False Positives: {cm[0,1]}")
    print(f"   False Negatives: {cm[1,0]}, True Positives: {cm[1,1]}")
    
    return lr, scaler, {
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'training_time': training_time,
        'inference_latency_ms': inference_time * 1000
    }


def train_failure_predictor(df):
    """
    Train model to predict next-window failure
    Uses current window features to predict if next window will fail
    """
    print("\n" + "="*70)
    print("TRAINING FAILURE PREDICTOR (Next-Window Prediction)")
    print("="*70)
    
    # Create next-window labels
    df_shifted = df.copy()
    df_shifted['next_window_failure'] = df_shifted['is_anomalous'].shift(-1)
    
    # Remove last row (no next window)
    df_shifted = df_shifted[:-1].dropna()
    
    # Features: current window, Label: next window failure
    feature_cols = [col for col in df.columns if col not in ['is_anomalous', 'next_window_failure']]
    X = df_shifted[feature_cols].values
    y = df_shifted['next_window_failure'].values.astype(int)
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train
    failure_lr = LogisticRegression(
        max_iter=1000,
        class_weight='balanced',
        random_state=42
    )
    failure_lr.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = failure_lr.predict(X_test_scaled)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    
    print(f"✅ Failure Predictor trained on {len(X_train)} samples")
    print(f"   Precision: {precision:.4f}")
    print(f"   Recall: {recall:.4f}")
    print(f"   F1-Score: {f1:.4f}")
    
    return failure_lr, scaler


def train_all_models():
    """Main training pipeline with enhanced models"""
    print("\n" + "="*70)
    print("🚀 ENHANCED ML TRAINING PIPELINE")
    print("="*70)
    
    # Load dataset
    df = load_real_datasets()
    if df is None:
        return None
    
    # Separate features and labels
    feature_cols = [col for col in df.columns if col != 'is_anomalous']
    X = df[feature_cols].values
    y = df['is_anomalous'].values if 'is_anomalous' in df.columns else np.zeros(len(df))
    
    print(f"\n📊 Feature columns: {feature_cols}")
    print(f"📊 Dataset shape: {X.shape}")
    
    # 1. Train Isolation Forest on NORMAL windows only
    normal_mask = (y == 0)
    X_normal = X[normal_mask]
    print(f"\n🔹 Isolating {len(X_normal)} normal windows for Isolation Forest...")
    
    iso_forest, iso_scaler = train_isolation_forest_on_normal(X_normal)
    
    # 2. Train K-Means on all data
    kmeans, n_clusters = train_kmeans(X)
    
    # 3. Train Logistic Regression with stratified split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    lr_classifier, lr_scaler, lr_metrics = train_logistic_regression(
        X_train, y_train, X_test, y_test
    )
    
    # 4. Train Failure Predictor
    failure_predictor, failure_scaler = train_failure_predictor(df)
    
    # Save all models
    models_dir = Path(__file__).parent / 'models'
    models_dir.mkdir(exist_ok=True)
    
    print(f"\n💾 Saving models to {models_dir}...")
    
    joblib.dump(iso_forest, models_dir / 'isolation_forest.pkl')
    joblib.dump(iso_scaler, models_dir / 'isolation_scaler.pkl')
    joblib.dump(kmeans, models_dir / 'kmeans.pkl')
    joblib.dump(lr_classifier, models_dir / 'logistic_regression.pkl')
    joblib.dump(lr_scaler, models_dir / 'lr_scaler.pkl')
    joblib.dump(failure_predictor, models_dir / 'failure_predictor.pkl')
    joblib.dump(failure_scaler, models_dir / 'failure_scaler.pkl')
    
    # Save metadata
    metadata = {
        'n_clusters': n_clusters,
        'feature_names': feature_cols,
        'metrics': lr_metrics
    }
    joblib.dump(metadata, models_dir / 'metadata.pkl')
    
    print(f"✅ All models saved successfully!")
    print(f"\n📊 Final Performance Summary:")
    print(f"   Precision: {lr_metrics['precision']:.4f}")
    print(f"   Recall: {lr_metrics['recall']:.4f}")
    print(f"   F1-Score: {lr_metrics['f1_score']:.4f}")
    print(f"   Detection Latency: {lr_metrics['inference_latency_ms']:.2f}ms")
    
    return {
        'isolation_forest': iso_forest,
        'isolation_scaler': iso_scaler,
        'kmeans': kmeans,
        'logistic_regression': lr_classifier,
        'lr_scaler': lr_scaler,
        'failure_predictor': failure_predictor,
        'failure_scaler': failure_scaler,
        'metadata': metadata
    }


if __name__ == "__main__":
    train_all_models()
