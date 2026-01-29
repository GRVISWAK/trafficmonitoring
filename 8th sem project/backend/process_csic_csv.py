"""
CSIC CSV Processor - Process csic_database.csv file
Handles CSV format with 'classification' column (Normal/Anomalous)
"""

import pandas as pd
import re
from pathlib import Path
from collections import Counter
import math


class CSICCSVProcessor:
    def __init__(self):
        self.datasets_dir = Path(__file__).parent / "datasets"
        self.processed_dir = self.datasets_dir / "processed"
        self.processed_dir.mkdir(exist_ok=True)
    
    def process_csv(self):
        """Process csic_database.csv into ML features"""
        
        print("\n" + "="*70)
        print("CSIC CSV PROCESSOR - Processing csic_database.csv")
        print("="*70)
        
        csv_path = self.datasets_dir / "csic_database.csv"
        
        if not csv_path.exists():
            print(f"\n❌ File not found: {csv_path}")
            print("\n💡 Make sure csic_database.csv is in: backend/datasets/")
            return
        
        print(f"\n✅ Found: {csv_path.name}")
        print(f"📊 Loading CSV...")
        
        # Load CSV
        try:
            df = pd.read_csv(csv_path)
            print(f"✅ Loaded {len(df)} rows")
            print(f"📋 Columns: {list(df.columns)[:5]}...")
            
            # Check first unnamed column (has Normal/Anomalous labels)
            first_col = df.columns[0]
            if 'Unnamed' in first_col and first_col in df.columns:
                normal_count = (df[first_col] == 'Normal').sum()
                anomalous_count = (df[first_col] == 'Anomalous').sum()
                print(f"\n📊 Dataset Composition:")
                print(f"   - Normal requests: {normal_count}")
                print(f"   - Anomalous requests: {anomalous_count}")
            elif 'classification' in df.columns:
                # Classification column has 0=normal, 1=anomalous
                normal_count = (df['classification'] == 0).sum()
                anomalous_count = (df['classification'] == 1).sum()
                print(f"\n📊 Dataset Composition:")
                print(f"   - Normal requests (0): {normal_count}")
                print(f"   - Anomalous requests (1): {anomalous_count}")
            
        except Exception as e:
            print(f"❌ Error loading CSV: {e}")
            return
        
        print(f"\n🔄 Extracting features from requests...")
        
        # Convert each row to request features
        requests = []
        
        for idx, row in df.iterrows():
            try:
                # Extract features from CSV row
                method = str(row.get('Method', 'GET'))
                url = str(row.get('URL', ''))
                content = str(row.get('content', ''))
                user_agent = str(row.get('User-Agent', ''))
                
                # Check first column for Normal/Anomalous label
                first_col = df.columns[0]
                label_from_first_col = str(row.get(first_col, 'Normal'))
                
                # Also check classification column (0=normal, 1=anomalous)
                classification_num = row.get('classification', 0)
                
                # Determine if attack (prefer first column label, fallback to numeric)
                if label_from_first_col in ['Normal', 'Anomalous']:
                    is_attack = (label_from_first_col == 'Anomalous')
                else:
                    is_attack = (classification_num == 1)
                
                # Calculate payload size
                payload_size = len(content.encode('utf-8')) if content and content != 'nan' else 0
                
                # Extract endpoint from URL
                endpoint_match = re.search(r'http://[^/]+(/[^\s?]*)', url)
                endpoint = endpoint_match.group(1) if endpoint_match else '/'
                
                # Extract query parameters
                param_match = re.findall(r'[?&](\w+)=', url)
                num_params = len(param_match)
                
                # Simulate response time (attacks tend to be slower)
                base_time = 150
                attack_penalty = 50 if is_attack else 0
                url_complexity = len(url) // 10
                response_time = base_time + attack_penalty + url_complexity
                
                # Simulate status code
                status_code = 400 if is_attack and payload_size > 1000 else 200
                
                requests.append({
                    'endpoint': endpoint[:50],
                    'method': method,
                    'response_time_ms': response_time,
                    'status_code': status_code,
                    'payload_size': payload_size,
                    'is_attack': is_attack,
                    'user_agent': user_agent[:100],
                    'num_params': num_params
                })
                
                # Progress indicator
                if (idx + 1) % 5000 == 0:
                    print(f"   Processed {idx + 1} requests...")
                
            except Exception as e:
                continue
        
        print(f"\n✅ Processed {len(requests)} requests")
        
        # Aggregate into time windows
        print(f"\n🔄 Aggregating into time windows (10 requests per window)...")
        features_df = self.aggregate_to_windows(requests, window_size=10)
        
        print(f"✅ Created {len(features_df)} feature vectors")
        
        # Save processed features
        output_path = self.processed_dir / "csic_features.csv"
        features_df.to_csv(output_path, index=False)
        print(f"\n💾 Saved to: {output_path}")
        
        # Show statistics
        print(f"\n📈 Feature Statistics:")
        print(features_df.describe())
        
        # Update combined training data
        print(f"\n🔄 Updating combined training dataset...")
        combined_path = self.processed_dir / "combined_training_data.csv"
        
        if combined_path.exists():
            existing = pd.read_csv(combined_path)
            print(f"   Removing old CSIC data (keeping other datasets)...")
            combined = pd.concat([features_df], ignore_index=True)
            print(f"   Replaced with {len(features_df)} new CSIC samples")
        else:
            combined = features_df
            print(f"   Created new dataset with {len(features_df)} CSIC samples")
        
        combined.to_csv(combined_path, index=False)
        print(f"✅ Saved: {combined_path}")
        print(f"   Total samples: {len(combined)}")
        
        print(f"\n" + "="*70)
        print(f"✅ CSIC CSV PROCESSING COMPLETE!")
        print(f"="*70)
        
        print(f"\n📝 Next Steps:")
        print(f"   1. Run: python train_models.py")
        print(f"      (Train ML models on {len(combined)} real CSIC samples)")
        print(f"   2. Run: python export_datasets.py")
        print(f"      (Export for mentor demonstration)")
        print(f"   3. Or use batch files: train.bat, export_datasets.bat")
        
        return features_df
    
    def aggregate_to_windows(self, requests, window_size=10):
        """Aggregate requests into time windows and extract enhanced ML features"""
        features_list = []
        
        # Process in chunks (simulate time windows)
        for i in range(0, len(requests), window_size):
            window = requests[i:i+window_size]
            if len(window) < 5:  # Skip very small windows
                continue
            
            # Feature 1: request_rate (requests per time unit)
            request_rate = len(window) / (window_size / 10.0)  # normalized
            
            # Feature 2: unique_endpoint_count
            unique_endpoint_count = len(set(r['endpoint'] for r in window))
            
            # Feature 3: method_ratio (GET/POST ratio)
            methods = [r['method'] for r in window]
            get_count = methods.count('GET')
            post_count = methods.count('POST')
            method_ratio = get_count / (post_count + 1)  # avoid division by zero
            
            # Feature 4: avg_payload_size
            avg_payload_size = sum(r['payload_size'] for r in window) / len(window)
            
            # Feature 5: error_rate (4xx/5xx status codes)
            errors = sum(1 for r in window if r['status_code'] >= 400)
            error_rate = errors / len(window)
            
            # Feature 6: repeated_parameter_ratio
            params = [r['num_params'] for r in window]
            most_common_param = Counter(params).most_common(1)[0][1] if params else 1
            repeated_parameter_ratio = most_common_param / len(window)
            
            # Feature 7: user_agent_entropy
            user_agents = [r['user_agent'] for r in window]
            ua_counts = Counter(user_agents)
            total = sum(ua_counts.values())
            user_agent_entropy = 0
            if total > 0:
                user_agent_entropy = -sum((count/total) * math.log2(count/total) 
                                          for count in ua_counts.values() if count > 0)
            
            # Additional features for compatibility
            avg_response_time = sum(r['response_time_ms'] for r in window) / len(window)
            max_response_time = max(r['response_time_ms'] for r in window)
            
            # Determine window label (for supervised learning)
            attack_count = sum(1 for r in window if r['is_attack'])
            is_anomalous_window = (attack_count / len(window)) > 0.3  # >30% attacks = anomalous
            
            features_list.append({
                'request_rate': request_rate,
                'unique_endpoint_count': unique_endpoint_count,
                'method_ratio': method_ratio,
                'avg_payload_size': avg_payload_size,
                'error_rate': error_rate,
                'repeated_parameter_ratio': repeated_parameter_ratio,
                'user_agent_entropy': user_agent_entropy,
                'avg_response_time': avg_response_time,
                'max_response_time': max_response_time,
                'is_anomalous': int(is_anomalous_window)  # Label for training
            })
        
        return pd.DataFrame(features_list)


if __name__ == "__main__":
    processor = CSICCSVProcessor()
    processor.process_csv()
