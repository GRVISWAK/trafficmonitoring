"""
Auto-Detection Simulation Test Script

This script tests the auto-detection simulation system by:
1. Starting a simulation for a virtual endpoint
2. Polling simulation stats
3. Verifying ML-detected anomaly types
4. Stopping the simulation

Usage:
    python test_auto_detection.py
"""

import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_auto_detection():
    print("=" * 80)
    print("AUTO-DETECTION SIMULATION TEST")
    print("=" * 80)
    
    # Test 1: Start simulation (NO anomaly type specified)
    print("\n[TEST 1] Starting auto-detection simulation for /sim/login...")
    endpoint = "/sim/login"
    duration = 30  # 30 seconds for faster testing
    requests_per_window = 10
    
    try:
        response = requests.post(
            f"{BASE_URL}/simulation/start",
            params={
                "simulated_endpoint": endpoint,
                "duration_seconds": duration,
                "requests_per_window": requests_per_window
            }
        )
        
        if response.status_code == 200:
            print(f"✅ Simulation started successfully")
            result = response.json()
            print(f"   Message: {result.get('message', 'N/A')}")
            print(f"   Duration: {result.get('duration_seconds', 'N/A')}s")
            print(f"   Requests/Window: {result.get('requests_per_window', 'N/A')}")
        else:
            print(f"❌ Failed to start simulation: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error starting simulation: {e}")
        return False
    
    # Test 2: Monitor simulation stats
    print("\n[TEST 2] Monitoring simulation stats (10 second intervals)...")
    for i in range(3):  # Poll 3 times
        time.sleep(10)
        
        try:
            response = requests.get(f"{BASE_URL}/simulation/stats")
            if response.status_code == 200:
                stats = response.json()
                print(f"\n📊 Stats at T+{(i+1)*10}s:")
                print(f"   Active: {stats.get('active', False)}")
                print(f"   Endpoint: {stats.get('simulated_endpoint', 'N/A')}")
                print(f"   Total Requests: {stats.get('total_requests', 0)}")
                print(f"   Windows Processed: {stats.get('windows_processed', 0)}")
                print(f"   Anomaly Episodes: {stats.get('anomalies_detected', 0)}")
                print(f"   Detected Types: {stats.get('detected_anomaly_types', [])}")
                
                # Verify ML-detected types (should NOT be pre-labeled)
                detected_types = stats.get('detected_anomaly_types', [])
                if detected_types:
                    print(f"   ✅ ML models detected {len(detected_types)} anomaly type(s)")
                else:
                    print(f"   ℹ️  No anomalies detected yet (this is normal for early windows)")
                    
        except Exception as e:
            print(f"   ❌ Error fetching stats: {e}")
    
    # Test 3: Stop simulation
    print("\n[TEST 3] Stopping simulation...")
    try:
        response = requests.post(f"{BASE_URL}/simulation/stop")
        if response.status_code == 200:
            print(f"✅ Simulation stopped successfully")
            result = response.json()
            print(f"   Message: {result.get('message', 'N/A')}")
        else:
            print(f"❌ Failed to stop simulation: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error stopping simulation: {e}")
    
    # Test 4: Final stats check
    print("\n[TEST 4] Final statistics...")
    try:
        response = requests.get(f"{BASE_URL}/simulation/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"\n📊 Final Stats:")
            print(f"   Total Requests: {stats.get('total_requests', 0)}")
            print(f"   Windows Processed: {stats.get('windows_processed', 0)}")
            print(f"   Anomaly Episodes: {stats.get('anomalies_detected', 0)}")
            print(f"   Detected Types: {stats.get('detected_anomaly_types', [])}")
            
            # Verify episode counting
            episodes = stats.get('anomalies_detected', 0)
            if episodes > 0:
                print(f"\n✅ SUCCESS: {episodes} anomaly episode(s) detected by ML models!")
                print(f"   Types identified: {', '.join(stats.get('detected_anomaly_types', []))}")
            else:
                print(f"\n⚠️  WARNING: No anomalies detected (might need longer simulation)")
                
    except Exception as e:
        print(f"❌ Error fetching final stats: {e}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print("\n💡 Tips:")
    print("   • If no anomalies detected, traffic was genuinely normal")
    print("   • ML models determine anomaly types (not pre-labeled)")
    print("   • Episode count should be less than window count (aggregation)")
    print("   • Check backend logs for 'ML Detected: [TYPE]' messages")
    
    return True


if __name__ == "__main__":
    print("\n🔧 Prerequisites:")
    print("   1. Backend running on http://localhost:8000")
    print("   2. ML models loaded successfully")
    print("   3. Auto-detection module imported\n")
    
    input("Press Enter to start test...")
    
    test_auto_detection()
