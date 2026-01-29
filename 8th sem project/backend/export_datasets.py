"""
Export datasets to multiple formats for mentor/viva demonstration
Creates Excel, CSV summary, and detailed report
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime


def export_all_datasets():
    """Export all datasets in multiple formats"""
    
    base_dir = Path(__file__).parent / "datasets"
    processed_dir = base_dir / "processed"
    raw_dir = base_dir / "raw"
    export_dir = base_dir / "EXPORT_FOR_MENTORS"
    export_dir.mkdir(exist_ok=True)
    
    print("\n" + "="*70)
    print("📦 EXPORTING DATASETS FOR MENTOR DEMONSTRATION")
    print("="*70)
    
    # 1. Export main training dataset to Excel
    csv_path = processed_dir / "combined_training_data.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        
        excel_path = export_dir / "TRAINING_DATASET.xlsx"
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Full dataset
            df.to_excel(writer, sheet_name='Full Dataset', index=False)
            
            # Statistics
            df.describe().to_excel(writer, sheet_name='Statistics')
            
            # First 100 samples
            df.head(100).to_excel(writer, sheet_name='Sample Data', index=False)
            
            # Feature correlation
            df.corr().to_excel(writer, sheet_name='Feature Correlation')
        
        print(f"\n✅ Exported training dataset to Excel: {excel_path}")
        print(f"   - Total Samples: {len(df)}")
        print(f"   - Features: {len(df.columns)}")
        print(f"   - File Size: {excel_path.stat().st_size / 1024:.2f} KB")
    
    # 2. Export attack payloads summary
    attack_path = raw_dir / "web_attack_payloads.json"
    if attack_path.exists():
        with open(attack_path, 'r') as f:
            payloads = json.load(f)
        
        # Convert to DataFrame for Excel
        attack_data = []
        for category, attacks in payloads.items():
            for attack in attacks:
                attack_data.append({
                    'Category': category,
                    'Payload': attack
                })
        
        attack_df = pd.DataFrame(attack_data)
        attack_excel = export_dir / "ATTACK_PAYLOADS.xlsx"
        attack_df.to_excel(attack_excel, index=False)
        
        print(f"\n✅ Exported attack payloads: {attack_excel}")
        print(f"   - Total Payloads: {len(attack_data)}")
        print(f"   - Categories: {len(payloads)}")
    
    # 3. Export API abuse scenarios
    abuse_path = raw_dir / "api_abuse_scenarios.json"
    if abuse_path.exists():
        with open(abuse_path, 'r') as f:
            scenarios = json.load(f)
        
        # Convert to DataFrame
        scenario_data = []
        for category, details in scenarios.items():
            for pattern in details['patterns']:
                scenario_data.append({
                    'Category': category,
                    'Description': details['description'],
                    'Endpoint': pattern['endpoint'],
                    'Method': pattern['method'],
                    'Payload': str(pattern.get('payload', ''))[:100]
                })
        
        scenario_df = pd.DataFrame(scenario_data)
        scenario_excel = export_dir / "API_ABUSE_SCENARIOS.xlsx"
        scenario_df.to_excel(scenario_excel, index=False)
        
        print(f"\n✅ Exported API abuse scenarios: {scenario_excel}")
        print(f"   - Total Scenarios: {len(scenario_data)}")
    
    # 4. Create comprehensive report
    report_path = export_dir / "COMPLETE_DATASET_REPORT.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("PREDICTIVE API MISUSE AND FAILURE PREDICTION SYSTEM\n")
        f.write("DATASET DOCUMENTATION - FOR MENTOR/VIVA PRESENTATION\n")
        f.write("="*70 + "\n\n")
        
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("="*70 + "\n")
        f.write("1. TRAINING DATASET OVERVIEW\n")
        f.write("="*70 + "\n\n")
        
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            f.write(f"Total Samples: {len(df)}\n")
            f.write(f"Number of Features: {len(df.columns)}\n")
            f.write(f"Features: {', '.join(df.columns)}\n\n")
            
            f.write("Feature Descriptions:\n")
            descriptions = {
                'req_count': 'Number of API requests in time window',
                'error_rate': 'Percentage of failed requests (4xx/5xx)',
                'avg_response_time': 'Average response time in milliseconds',
                'max_response_time': 'Maximum response time in milliseconds',
                'payload_mean': 'Average payload size in bytes',
                'unique_endpoints': 'Number of distinct endpoints accessed',
                'repeat_rate': 'Rate of repeated identical requests',
                'status_entropy': 'Entropy of HTTP status codes (measures randomness)'
            }
            for col in df.columns:
                if col in descriptions:
                    f.write(f"  - {col}: {descriptions[col]}\n")
            
            f.write("\n\nDataset Statistics:\n")
            f.write(df.describe().to_string())
            f.write("\n\n")
        
        f.write("="*70 + "\n")
        f.write("2. DATA SOURCES\n")
        f.write("="*70 + "\n\n")
        
        f.write("This system uses real-world security datasets:\n\n")
        
        f.write("a) CSIC 2010 HTTP Dataset (attempted):\n")
        f.write("   - Source: Spanish Research National Council\n")
        f.write("   - Contains: 36,000 normal requests + 25,000 attack requests\n")
        f.write("   - Attack types: SQL injection, XSS, CRLF injection, etc.\n")
        f.write("   - Status: Connection timeout (fallback to synthetic)\n\n")
        
        f.write("b) Web Attack Payload Database:\n")
        if attack_path.exists():
            with open(attack_path, 'r') as pf:
                payloads = json.load(pf)
                total = sum(len(v) for v in payloads.values())
                f.write(f"   - Total Payloads: {total}\n")
                f.write(f"   - Categories: {', '.join(payloads.keys())}\n")
                f.write("   - Used for: Training models to detect malicious patterns\n\n")
        
        f.write("c) API Abuse Scenarios (OWASP-Based):\n")
        if abuse_path.exists():
            with open(abuse_path, 'r') as af:
                scenarios = json.load(af)
                f.write(f"   - Total Categories: {len(scenarios)}\n")
                f.write("   - Based on: OWASP API Security Top 10\n")
                f.write("   - Covers: BOLA, Authentication failures, Rate limiting, etc.\n\n")
        
        f.write("d) Synthetic Traffic Generation:\n")
        f.write("   - Generated: 1000 samples with realistic patterns\n")
        f.write("   - Patterns: Normal users (60%), Heavy users (25%), Bots (15%)\n")
        f.write("   - Purpose: Ensure sufficient training data\n\n")
        
        f.write("="*70 + "\n")
        f.write("3. MACHINE LEARNING MODELS\n")
        f.write("="*70 + "\n\n")
        
        f.write("Three models trained on this dataset:\n\n")
        
        f.write("a) Isolation Forest (Anomaly Detection):\n")
        f.write("   - Algorithm: Tree-based ensemble\n")
        f.write("   - Parameters: 300 estimators, 5% contamination\n")
        f.write("   - Purpose: Detect unusual API behavior patterns\n")
        f.write("   - Output: Anomaly score (-1 to 1)\n\n")
        
        f.write("b) K-Means Clustering (Usage Patterns):\n")
        f.write("   - Algorithm: Unsupervised clustering\n")
        f.write("   - Clusters: 3 (Normal, Heavy, Bot)\n")
        f.write("   - Purpose: Identify bot-like behavior\n")
        f.write("   - Output: Cluster assignment + distance\n\n")
        
        f.write("c) Random Forest (Failure Prediction):\n")
        f.write("   - Algorithm: Decision tree ensemble\n")
        f.write("   - Parameters: 300 estimators, max depth 15\n")
        f.write("   - Purpose: Predict API failure probability\n")
        f.write("   - Output: Failure probability (0 to 1)\n\n")
        
        f.write("="*70 + "\n")
        f.write("4. REAL-TIME DETECTION PIPELINE\n")
        f.write("="*70 + "\n\n")
        
        f.write("1. Request Logging: All API requests logged automatically\n")
        f.write("2. Feature Extraction: Aggregate into 1-minute windows\n")
        f.write("3. ML Inference: Three models run in parallel\n")
        f.write("4. Risk Scoring: Weighted ensemble (45% anomaly + 35% failure + 20% bot)\n")
        f.write("5. Alert Generation: High-risk (≥0.8) triggers WebSocket alerts\n")
        f.write("6. Dashboard Update: Real-time visualization\n\n")
        
        f.write("="*70 + "\n")
        f.write("5. FILES FOR REVIEW\n")
        f.write("="*70 + "\n\n")
        
        f.write("All dataset files located in: backend/datasets/\n\n")
        f.write("For Mentor Demonstration:\n")
        f.write("  - TRAINING_DATASET.xlsx: Main training data with statistics\n")
        f.write("  - ATTACK_PAYLOADS.xlsx: Database of attack patterns\n")
        f.write("  - API_ABUSE_SCENARIOS.xlsx: OWASP-based abuse scenarios\n")
        f.write("  - COMPLETE_DATASET_REPORT.txt: This comprehensive report\n\n")
        
        f.write("To View Interactively:\n")
        f.write("  - Run: view_datasets.bat\n")
        f.write("  - Interactive menu to explore all datasets\n\n")
        
        f.write("="*70 + "\n")
        f.write("END OF REPORT\n")
        f.write("="*70 + "\n")
    
    print(f"\n✅ Created comprehensive report: {report_path}")
    
    # 5. Create quick reference CSV
    summary_path = export_dir / "DATASET_SUMMARY.csv"
    summary_data = []
    
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        for col in df.columns:
            summary_data.append({
                'Feature': col,
                'Min': df[col].min(),
                'Max': df[col].max(),
                'Mean': df[col].mean(),
                'Std Dev': df[col].std()
            })
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(summary_path, index=False)
    print(f"\n✅ Created feature summary: {summary_path}")
    
    print("\n" + "="*70)
    print("✅ EXPORT COMPLETE!")
    print("="*70)
    print(f"\nAll files saved to: {export_dir}")
    print("\n📁 Files ready for mentor demonstration:")
    print("   1. TRAINING_DATASET.xlsx - Main dataset with statistics")
    print("   2. ATTACK_PAYLOADS.xlsx - Security attack patterns")
    print("   3. API_ABUSE_SCENARIOS.xlsx - OWASP abuse scenarios")
    print("   4. COMPLETE_DATASET_REPORT.txt - Comprehensive documentation")
    print("   5. DATASET_SUMMARY.csv - Quick feature reference")
    print("\n💡 You can now show these files to your mentors/reviewers!")
    print("💡 Run view_datasets.bat for interactive exploration")


if __name__ == "__main__":
    export_all_datasets()
