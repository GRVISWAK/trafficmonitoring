"""
Dataset Viewer - Interactive exploration of downloaded datasets
For demonstrating to mentors/reviewers
"""

import os
import pandas as pd
import json
from pathlib import Path

class DatasetViewer:
    def __init__(self):
        self.base_dir = Path(__file__).parent / "datasets"
        self.processed_dir = self.base_dir / "processed"
        self.raw_dir = self.base_dir / "raw"
    
    def show_main_menu(self):
        """Main menu for dataset exploration"""
        print("\n" + "="*70)
        print("📊 SECURITY DATASET VIEWER - FOR MENTOR DEMONSTRATION")
        print("="*70)
        print("\n1. View Combined Training Dataset Summary")
        print("2. View Sample Records (with all features)")
        print("3. View Dataset Statistics")
        print("4. View Attack Payload Database")
        print("5. View API Abuse Scenarios")
        print("6. View Dataset Report (for mentors)")
        print("7. Export Dataset to Excel (for presentation)")
        print("8. Exit")
        print("\n" + "="*70)
    
    def view_combined_dataset(self):
        """View the combined training dataset"""
        csv_path = self.processed_dir / "combined_training_data.csv"
        
        if not csv_path.exists():
            print("\n❌ Dataset not found. Run download_all_datasets.bat first!")
            return
        
        df = pd.read_csv(csv_path)
        
        print("\n" + "="*70)
        print("📦 COMBINED TRAINING DATASET")
        print("="*70)
        print(f"\n📊 Total Samples: {len(df)}")
        print(f"📊 Features: {len(df.columns)}")
        print(f"\n📋 Feature Names:")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i}. {col}")
        
        print(f"\n📈 Dataset Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"💾 File Size: {csv_path.stat().st_size / 1024:.2f} KB")
        print(f"📍 Location: {csv_path}")
    
    def view_sample_records(self):
        """View actual data samples"""
        csv_path = self.processed_dir / "combined_training_data.csv"
        
        if not csv_path.exists():
            print("\n❌ Dataset not found!")
            return
        
        df = pd.read_csv(csv_path)
        
        print("\n" + "="*70)
        print("📄 SAMPLE RECORDS (First 10 samples)")
        print("="*70)
        
        # Show first 10 records with all features
        print("\n" + df.head(10).to_string())
        
        print("\n\n" + "="*70)
        print("📄 RANDOM SAMPLES (10 random records)")
        print("="*70)
        print("\n" + df.sample(min(10, len(df))).to_string())
    
    def view_statistics(self):
        """View detailed statistics"""
        csv_path = self.processed_dir / "combined_training_data.csv"
        
        if not csv_path.exists():
            print("\n❌ Dataset not found!")
            return
        
        df = pd.read_csv(csv_path)
        
        print("\n" + "="*70)
        print("📊 DATASET STATISTICS")
        print("="*70)
        
        print("\n📈 Descriptive Statistics:")
        print(df.describe().to_string())
        
        print("\n\n📊 Feature Distributions:")
        for col in df.columns:
            print(f"\n{col}:")
            print(f"  Min: {df[col].min():.2f}")
            print(f"  Max: {df[col].max():.2f}")
            print(f"  Mean: {df[col].mean():.2f}")
            print(f"  Median: {df[col].median():.2f}")
            print(f"  Std Dev: {df[col].std():.2f}")
    
    def view_attack_payloads(self):
        """View attack payload database"""
        json_path = self.raw_dir / "web_attack_payloads.json"
        
        if not json_path.exists():
            print("\n❌ Attack payload database not found!")
            return
        
        with open(json_path, 'r') as f:
            payloads = json.load(f)
        
        print("\n" + "="*70)
        print("🔥 ATTACK PAYLOAD DATABASE")
        print("="*70)
        
        for category, attacks in payloads.items():
            print(f"\n📂 {category.upper().replace('_', ' ')}")
            print(f"   Total Attacks: {len(attacks)}")
            print(f"   Sample Payloads:")
            for i, attack in enumerate(attacks[:3], 1):
                print(f"      {i}. {attack[:80]}..." if len(attack) > 80 else f"      {i}. {attack}")
    
    def view_api_abuse_scenarios(self):
        """View API abuse scenarios"""
        json_path = self.raw_dir / "api_abuse_scenarios.json"
        
        if not json_path.exists():
            print("\n❌ API abuse scenarios not found!")
            return
        
        with open(json_path, 'r') as f:
            scenarios = json.load(f)
        
        print("\n" + "="*70)
        print("🚨 API ABUSE SCENARIOS (OWASP-BASED)")
        print("="*70)
        
        for category, details in scenarios.items():
            print(f"\n📂 {category.upper().replace('_', ' ')}")
            print(f"   Description: {details['description']}")
            print(f"   Total Patterns: {len(details['patterns'])}")
            print(f"   Sample Patterns:")
            for i, pattern in enumerate(details['patterns'][:3], 1):
                print(f"      {i}. Endpoint: {pattern['endpoint']}")
                print(f"         Payload: {str(pattern['payload'])[:60]}...")
    
    def view_dataset_report(self):
        """View the dataset report for mentors"""
        report_path = self.base_dir / "DATASET_REPORT.txt"
        
        if not report_path.exists():
            print("\n❌ Dataset report not found!")
            return
        
        with open(report_path, 'r') as f:
            content = f.read()
        
        print("\n" + "="*70)
        print("📄 DATASET REPORT (FOR MENTORS/REVIEWERS)")
        print("="*70)
        print(content)
    
    def export_to_excel(self):
        """Export dataset to Excel for presentation"""
        csv_path = self.processed_dir / "combined_training_data.csv"
        
        if not csv_path.exists():
            print("\n❌ Dataset not found!")
            return
        
        df = pd.read_csv(csv_path)
        
        # Export to Excel with formatting
        excel_path = self.base_dir / "DATASET_FOR_PRESENTATION.xlsx"
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Full dataset
            df.to_excel(writer, sheet_name='Full Dataset', index=False)
            
            # Statistics
            df.describe().to_excel(writer, sheet_name='Statistics')
            
            # Sample data
            df.head(100).to_excel(writer, sheet_name='First 100 Samples', index=False)
        
        print(f"\n✅ Dataset exported to: {excel_path}")
        print(f"📊 Contains {len(df)} samples across {len(df.columns)} features")
        print("\n💡 You can now open this Excel file and show it to your mentors!")
    
    def run(self):
        """Run the interactive viewer"""
        while True:
            self.show_main_menu()
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == '1':
                self.view_combined_dataset()
            elif choice == '2':
                self.view_sample_records()
            elif choice == '3':
                self.view_statistics()
            elif choice == '4':
                self.view_attack_payloads()
            elif choice == '5':
                self.view_api_abuse_scenarios()
            elif choice == '6':
                self.view_dataset_report()
            elif choice == '7':
                self.export_to_excel()
            elif choice == '8':
                print("\n👋 Exiting dataset viewer. Good luck with your presentation!")
                break
            else:
                print("\n❌ Invalid choice. Please try again.")
            
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    viewer = DatasetViewer()
    viewer.run()
