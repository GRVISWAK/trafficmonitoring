import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os
from pathlib import Path
from feature_engineering import prepare_training_data


def load_real_datasets():
    """
    Load and combine multiple real security datasets
    Priority order:
    1. Combined processed dataset (with CSIC + attack payloads + API abuse)
    2. Individual CSIC features
    3. Synthetic data (fallback)
    """
    processed_dir = Path(__file__).parent / "datasets" / "processed"
    
    # Try to load combined dataset first (highest priority)
    combined_path = processed_dir / "combined_training_data.csv"
    if combined_path.exists():
        df = pd.read_csv(combined_path)
        print(f"\n✅ Loaded REAL DATASET from {combined_path}")
        print(f"📊 Total Training Samples: {len(df)}")
        print(f"📊 Features: {list(df.columns)}")
        print(f"📊 Data Sources: Combined security datasets (CSIC + Attack Payloads + API Abuse)")
        print(f"\n📈 Dataset Statistics:")
        print(df.describe())
        return df
    
    # Try individual CSIC dataset
    csic_path = processed_dir / "csic_features.csv"
    if csic_path.exists():
        df = pd.read_csv(csic_path)
        print(f"\n✅ Loaded CSIC 2010 dataset from {csic_path}")
        print(f"📊 Total Training Samples: {len(df)}")
        return df
    
    # Fallback to synthetic if no real datasets available
    print("\n⚠️ No real datasets found. Generating synthetic data...")
    print("💡 Run 'download_all_datasets.bat' to download real security datasets")
    from feature_engineering import generate_synthetic_data
    return generate_synthetic_data(n_samples=500)


def train_isolation_forest(X):
    """
    Train Isolation Forest for anomaly detection.
    
    Parameters:
    - n_estimators=300: More trees for better anomaly detection
    - contamination=0.05: Assume 5% of data are anomalies
    - random_state=42: For reproducibility
    
    Returns anomaly scores where:
    - Negative scores indicate anomalies
    - Positive scores indicate normal behavior
    """
    print("Training Isolation Forest for anomaly detection...")
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    iso_forest = IsolationForest(
        n_estimators=300,
        contamination=0.05,
        random_state=42,
        n_jobs=-1
    )
    
    iso_forest.fit(X_scaled)
    
    return iso_forest, scaler


def determine_optimal_clusters(X, max_k=10):
    """
    Use elbow method to determine optimal number of clusters.
    For this system, we typically expect 3 clusters:
    - Cluster 0: Normal users
    - Cluster 1: Heavy users
    - Cluster 2: Bot-like behavior
    """
    inertias = []
    K_range = range(2, min(max_k + 1, len(X)))
    
    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X)
        inertias.append(kmeans.inertia_)
    
    if len(inertias) < 2:
        return 3
    
    diffs = np.diff(inertias)
    diffs2 = np.diff(diffs)
    
    if len(diffs2) > 0:
        elbow_point = np.argmax(np.abs(diffs2)) + 2
        return min(elbow_point, 3)
    
    return 3


def train_kmeans(X):
    """
    Train K-Means clustering for usage behavior analysis.
    
    Uses elbow method but defaults to n_clusters=3:
    - Cluster 0: Normal usage (low request rate, low errors)
    - Cluster 1: Heavy usage (high request rate, moderate errors)
    - Cluster 2: Bot-like (very high request rate, high repeat rate)
    
    Bot cluster is identified by highest req_count mean.
    """
    print("Training K-Means for usage clustering...")
    
    optimal_k = determine_optimal_clusters(X)
    print(f"Optimal clusters determined: {optimal_k}")
    
    kmeans = KMeans(
        n_clusters=optimal_k,
        random_state=42,
        n_init=10,
        max_iter=300
    )
    
    kmeans.fit(X)
    
    cluster_labels = kmeans.predict(X)
    cluster_stats = []
    
    for i in range(optimal_k):
        cluster_mask = cluster_labels == i
        cluster_data = X[cluster_mask]
        
        mean_req_count = cluster_data[:, 0].mean() if len(cluster_data) > 0 else 0
        cluster_stats.append((i, mean_req_count))
    
    cluster_stats.sort(key=lambda x: x[1], reverse=True)
    bot_cluster = cluster_stats[0][0]
    
    print(f"Identified bot cluster: {bot_cluster}")
    
    return kmeans, bot_cluster


def create_failure_labels(df):
    """
    Create binary labels for failure prediction.
    
    Label = 1 if:
    - error_rate > 0.3 (30% of requests are errors), OR
    - avg_response_time > 800ms (service degradation)
    
    This captures both error-based and latency-based failures.
    """
    labels = ((df['error_rate'] > 0.3) | (df['avg_response_time'] > 800)).astype(int)
    return labels


def train_random_forest(X, y):
    """
    Train Random Forest for failure prediction.
    
    Parameters:
    - n_estimators=300: More trees for better predictions
    - max_depth=15: Prevent overfitting while capturing complexity
    - class_weight='balanced': Handle class imbalance (failures are rare)
    - random_state=42: Reproducibility
    
    Returns probability of failure for each sample.
    """
    print("Training Random Forest for failure prediction...")
    
    print(f"Class distribution: {np.bincount(y)}")
    
    rf_classifier = RandomForestClassifier(
        n_estimators=300,
        max_depth=15,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    
    rf_classifier.fit(X, y)
    
    return rf_classifier


def train_all_models():
    """
    Main training pipeline that orchestrates all model training.
    
    Process:
    1. Prepare training data from historical logs
    2. Train Isolation Forest for anomaly detection
    3. Train K-Means for usage clustering
    4. Train Random Forest for failure prediction
    5. Save all models and scalers to disk
    """
    print("Starting ML training pipeline...")
    
    df = prepare_training_data(hours_back=24)
    
    print(f"Training data shape: {df.shape}")
    
    feature_columns = [
        'req_count', 'error_rate', 'avg_response_time', 'max_response_time',
        'payload_mean', 'unique_endpoints', 'repeat_rate', 'status_entropy'
    ]
    
    X = df[feature_columns].values
    
    # Try to load real datasets first
    print("\n" + "="*70)
    print("🚀 STARTING MODEL TRAINING")
    print("="*70)
    
    df_real = load_real_datasets()
    if df_real is not None and len(df_real) > 0:
        print(f"\n✅ Using REAL dataset with {len(df_real)} samples")
        df = df_real
        # Extract only feature columns, excluding the label 'is_anomalous'
        feature_cols = [col for col in df.columns if col != 'is_anomalous']
        X = df[feature_cols].values
    else:
        print(f"\n⚠️ Using prepared data from database")
    
    iso_forest, iso_scaler = train_isolation_forest(X)
    
    kmeans, bot_cluster = train_kmeans(X)
    
    y = create_failure_labels(df)
    rf_classifier = train_random_forest(X, y)
    
    models_dir = os.path.join(os.path.dirname(__file__), 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    joblib.dump(iso_forest, os.path.join(models_dir, 'isolation_forest.pkl'))
    joblib.dump(iso_scaler, os.path.join(models_dir, 'isolation_scaler.pkl'))
    joblib.dump(kmeans, os.path.join(models_dir, 'kmeans.pkl'))
    joblib.dump(rf_classifier, os.path.join(models_dir, 'random_forest.pkl'))
    
    with open(os.path.join(models_dir, 'bot_cluster.txt'), 'w') as f:
        f.write(str(bot_cluster))
    
    print("All models trained and saved successfully!")
    print(f"Models saved to: {models_dir}")
    
    return {
        'isolation_forest': iso_forest,
        'isolation_scaler': iso_scaler,
        'kmeans': kmeans,
        'random_forest': rf_classifier,
        'bot_cluster': bot_cluster
    }


if __name__ == "__main__":
    train_all_models()
