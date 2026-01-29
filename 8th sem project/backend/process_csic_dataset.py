"""
CSIC Dataset Processor - Handles combined or separate CSIC 2010 files
Extract your CSIC dataset to: backend/datasets/
Supported filenames:
  - csic_combined.txt (if all traffic in one file)
  - normalTrafficTraining.txt (original CSIC normal traffic)
  - anomalousTrafficTest.txt (original CSIC attack traffic)
  - csic_normal.txt + csic_attacks.txt
"""

import pandas as pd
import re
from pathlib import Path
from collections import Counter
import math


class CSICProcessor:
    def __init__(self):
        self.datasets_dir = Path(__file__).parent / "datasets"
        self.raw_dir = self.datasets_dir
        self.processed_dir = self.datasets_dir / "processed"
        self.processed_dir.mkdir(exist_ok=True)
    
    def find_csic_files(self):
        """Find CSIC files in datasets directory"""
        possible_files = [
            'csic_combined.txt',
            'normalTrafficTraining.txt',
            'anomalousTrafficTest.txt',
            'csic_normal.txt',
            'csic_attacks.txt'
        ]
        
        found = []
        for filename in possible_files:
            path = self.raw_dir / filename
            if path.exists():
                found.append(path)
                print(f"✅ Found: {filename}")
        
        return found
    
    def parse_http_request(self, request_text):
        """Parse a single HTTP request into features"""
        try:
            # Extract method and path
            first_line = request_text.split('\n')[0] if '\n' in request_text else request_text
            method_match = re.search(r'(GET|POST|PUT|DELETE|HEAD)', first_line)
            method = method_match.group(1) if method_match else 'GET'
            
            # Extract path
            path_match = re.search(r'(GET|POST|PUT|DELETE|HEAD)\s+(\S+)', first_line)
            path = path_match.group(2) if path_match else '/'
            
            # Extract payload size (approximation)
            payload_size = len(request_text.encode('utf-8'))
            
            # Count parameters
            param_count = len(re.findall(r'[?&]\w+=', path))
            
            # Detect attack patterns
            attack_patterns = [
                r'<script', r'javascript:', r'onerror=', r'onload=',  # XSS
                r'SELECT.*FROM', r'UNION.*SELECT', r'DROP\s+TABLE', r"'.*OR.*'",  # SQL injection
                r'\.\./', r'\.\.\textbackslash', r'etc/passwd', r'cmd\.exe',  # Path traversal
                r'exec\(', r'eval\(', r'system\(', r';.*ls', r';.*cat',  # Command injection
                r'%27', r'%3C', r'%3E', r'%22'  # URL encoded attacks
            ]
            
            is_attack = any(re.search(pattern, request_text, re.IGNORECASE) for pattern in attack_patterns)
            
            # Simulate response time (higher for attacks)
            response_time = 150 + (50 if is_attack else 0) + (param_count * 10)
            
            # Simulate status code
            status_code = 400 if is_attack and payload_size > 1000 else 200
            
            return {
                'endpoint': path[:50],  # Truncate long paths
                'method': method,
                'response_time_ms': response_time,
                'status_code': status_code,
                'payload_size': payload_size,
                'is_attack': is_attack
            }
        
        except Exception as e:
            return None
    
    def aggregate_to_windows(self, requests, window_size=60):
        """Aggregate requests into time windows and extract 8 ML features"""
        features_list = []
        
        # Process in chunks (simulate time windows)
        for i in range(0, len(requests), window_size):
            window = requests[i:i+window_size]
            if len(window) < 5:  # Skip very small windows
                continue
            
            # Feature 1: req_count
            req_count = len(window)
            
            # Feature 2: error_rate
            errors = sum(1 for r in window if r['status_code'] >= 400)
            error_rate = errors / len(window) if window else 0
            
            # Feature 3: avg_response_time
            avg_response_time = sum(r['response_time_ms'] for r in window) / len(window)
            
            # Feature 4: max_response_time
            max_response_time = max(r['response_time_ms'] for r in window)
            
            # Feature 5: payload_mean
            payload_mean = sum(r['payload_size'] for r in window) / len(window)
            
            # Feature 6: unique_endpoints
            unique_endpoints = len(set(r['endpoint'] for r in window))
            
            # Feature 7: repeat_rate
            endpoints = [r['endpoint'] for r in window]
            most_common_count = Counter(endpoints).most_common(1)[0][1] if endpoints else 1
            repeat_rate = most_common_count / len(window) if window else 0
            
            # Feature 8: status_entropy
            status_codes = [r['status_code'] for r in window]
            status_counts = Counter(status_codes)
            total = sum(status_counts.values())
            entropy = -sum((count/total) * math.log2(count/total) for count in status_counts.values() if count > 0)
            
            features_list.append({
                'req_count': req_count,
                'error_rate': error_rate,
                'avg_response_time': avg_response_time,
                'max_response_time': max_response_time,
                'payload_mean': payload_mean,
                'unique_endpoints': unique_endpoints,
                'repeat_rate': repeat_rate,
                'status_entropy': entropy
            })
        
        return pd.DataFrame(features_list)
    
    def process(self):
        """Main processing function"""
        print("\n" + "="*70)
        print("CSIC 2010 DATASET PROCESSOR")
        print("="*70)
        
        # Find files
        files = self.find_csic_files()
        
        if not files:
            print("\n❌ No CSIC files found!")
            print("\n📝 Instructions:")
            print("1. Extract your CSIC dataset ZIP file")
            print("2. Copy the .txt files to: backend/datasets/")
            print("3. Supported filenames:")
            print("   - normalTrafficTraining.txt")
            print("   - anomalousTrafficTest.txt")
            print("   - csic_combined.txt (if combined)")
            print("\n4. Run this script again")
            return
        
        print(f"\n📊 Processing {len(files)} file(s)...")
        
        all_requests = []
        
        for file_path in files:
            print(f"\n📄 Processing: {file_path.name}")
            
            try:
                # Read file (try different encodings)
                encodings = ['latin-1', 'utf-8', 'iso-8859-1', 'cp1252']
                content = None
                
                for encoding in encodings:
                    try:
                        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                            content = f.read()
                        break
                    except:
                        continue
                
                if not content:
                    print(f"   ❌ Could not read file")
                    continue
                
                # Detect section headers: "normal" followed by "anomalous"
                current_section = 'normal'  # Default to normal
                
                # Check if file has section headers
                has_sections = bool(re.search(r'^(normal|anomalous)\s*$', content, re.MULTILINE | re.IGNORECASE))
                
                # Split requests - CSIC uses different separators
                if '\n\n' in content:
                    requests_text = content.split('\n\n')
                elif 'GET ' in content or 'POST ' in content:
                    requests_text = re.split(r'\n(?=GET |POST )', content)
                else:
                    requests_text = content.split('\n')
                
                print(f"   Found {len(requests_text)} potential requests")
                if has_sections:
                    print(f"   ✅ Detected section headers (normal/anomalous)")
                
                # Parse each request
                parsed_count = 0
                normal_count = 0
                attack_count = 0
                
                for req_text in requests_text:
                    if not req_text.strip():
                        continue
                    
                    # Check for section header
                    section_match = re.match(r'^(normal|anomalous)\s*$', req_text.strip(), re.IGNORECASE)
                    if section_match:
                        current_section = section_match.group(1).lower()
                        print(f"   📍 Switched to {current_section} section")
                        continue
                    
                    # Skip very short lines
                    if len(req_text) < 10:
                        continue
                    
                    parsed = self.parse_http_request(req_text)
                    if parsed:
                        # Override attack detection with section info if available
                        if has_sections:
                            parsed['is_attack'] = (current_section == 'anomalous')
                        
                        all_requests.append(parsed)
                        parsed_count += 1
                        
                        if parsed['is_attack']:
                            attack_count += 1
                        else:
                            normal_count += 1
                    
                    # Limit to prevent memory issues
                    if parsed_count >= 10000:
                        print(f"   ⚠️ Limiting to 10,000 requests per file")
                        break
                
                print(f"   ✅ Successfully parsed {parsed_count} requests")
                print(f"      - Normal: {normal_count}")
                print(f"      - Attacks: {attack_count}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                continue
        
        if not all_requests:
            print("\n❌ No requests could be parsed!")
            print("💡 Your CSIC file might have a different format.")
            print("💡 Please share the first few lines of your file for analysis.")
            return
        
        print(f"\n📊 Total requests parsed: {len(all_requests)}")
        
        # Count attacks
        attack_count = sum(1 for r in all_requests if r['is_attack'])
        print(f"   - Normal requests: {len(all_requests) - attack_count}")
        print(f"   - Attack requests: {attack_count}")
        
        # Aggregate into ML features
        print(f"\n🔄 Aggregating into time windows...")
        df = self.aggregate_to_windows(all_requests)
        
        print(f"✅ Created {len(df)} feature vectors (8 features each)")
        
        # Save
        output_path = self.processed_dir / "csic_features.csv"
        df.to_csv(output_path, index=False)
        print(f"\n💾 Saved to: {output_path}")
        
        # Show statistics
        print(f"\n📈 Dataset Statistics:")
        print(df.describe())
        
        # Update combined training data
        print(f"\n🔄 Updating combined training dataset...")
        combined_path = self.processed_dir / "combined_training_data.csv"
        
        # If combined exists, append; otherwise create new
        if combined_path.exists():
            existing = pd.read_csv(combined_path)
            combined = pd.concat([existing, df], ignore_index=True)
            print(f"   Added {len(df)} samples to existing {len(existing)} samples")
        else:
            combined = df
            print(f"   Created new dataset with {len(df)} samples")
        
        combined.to_csv(combined_path, index=False)
        print(f"✅ Saved combined dataset: {combined_path}")
        print(f"   Total samples: {len(combined)}")
        
        print(f"\n✅ CSIC DATASET READY FOR TRAINING!")
        print(f"\n📝 Next steps:")
        print(f"   1. Run: python train_models.py (to train on CSIC data)")
        print(f"   2. Run: python export_datasets.py (to export for mentors)")
        print(f"   3. Or use: train.bat")


if __name__ == "__main__":
    processor = CSICProcessor()
    processor.process()
