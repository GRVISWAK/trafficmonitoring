"""
Real-time Dashboard Monitor - Shows live updates
"""
import requests
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

print("=" * 80)
print(" REAL-TIME DASHBOARD MONITOR")
print("=" * 80)
print("\nPress Ctrl+C to stop\n")

last_request_count = 0
last_anomaly_count = 0

try:
    while True:
        # Get simulation stats
        sim_stats = requests.get(f"{BASE_URL}/simulation/stats").json()
        
        # Get simulation anomalies
        sim_anomalies = requests.get(f"{BASE_URL}/simulation/anomaly-history?limit=10").json()
        
        # Clear screen (Windows)
        print("\033[2J\033[H", end="")
        
        print("=" * 80)
        print(f" LIVE MONITOR - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 80)
        
        # Simulation Status
        print(f"\n📊 SIMULATION STATUS:")
        print(f"   Active: {'✅ YES' if sim_stats.get('active') else '❌ NO'}")
        print(f"   Endpoint: {sim_stats.get('simulated_endpoint', 'N/A')}")
        print(f"   Requests Generated: {sim_stats.get('total_requests', 0)}")
        print(f"   Windows Processed: {sim_stats.get('windows_processed', 0)}")
        print(f"   Anomalies Detected: {sim_stats.get('anomalies_detected', 0)}")
        
        # Check for new data
        current_requests = sim_stats.get('total_requests', 0)
        current_anomalies = sim_stats.get('anomalies_detected', 0)
        
        if current_requests > last_request_count:
            print(f"\n   🔄 NEW: +{current_requests - last_request_count} requests")
            last_request_count = current_requests
        
        if current_anomalies > last_anomaly_count:
            print(f"   ⚠️  NEW: +{current_anomalies - last_anomaly_count} anomalies detected!")
            last_anomaly_count = current_anomalies
        
        # Recent Anomalies
        if sim_anomalies:
            print(f"\n🚨 RECENT ANOMALIES ({len(sim_anomalies)}):")
            for i, anomaly in enumerate(sim_anomalies[:3], 1):
                print(f"\n   [{i}] {anomaly.get('endpoint', 'N/A')}")
                print(f"       Type: {anomaly.get('anomaly_type', 'unknown')}")
                print(f"       Severity: {anomaly.get('severity', 'unknown')}")
                print(f"       Impact: {anomaly.get('impact_score', 0):.2f}")
                print(f"       Time: {anomaly.get('timestamp', 'N/A')[:19]}")
        
        print("\n" + "=" * 80)
        print("Refreshing every 2 seconds... (Ctrl+C to stop)")
        
        time.sleep(2)
        
except KeyboardInterrupt:
    print("\n\n✓ Monitor stopped")
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nMake sure backend is running on http://localhost:8000")
