"""
Demo script to generate various API usage patterns including anomalies.
This simulates different types of traffic to trigger ML-based anomaly detection.
"""
import requests
import random
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def normal_traffic():
    """Simulate normal user behavior"""
    print("✓ Generating normal traffic...")
    endpoints = ["/login", "/search", "/health"]
    
    for _ in range(5):
        endpoint = random.choice(endpoints)
        if endpoint == "/login":
            requests.post(f"{BASE_URL}/login", json={
                "username": f"user_{random.randint(1, 100)}",
                "password": "password123"
            })
        elif endpoint == "/search":
            requests.get(f"{BASE_URL}/search?query=test&limit=5")
        else:
            requests.get(f"{BASE_URL}/health")
        time.sleep(0.3)

def bot_like_traffic():
    """Simulate bot-like behavior - rapid, repetitive requests"""
    print("🤖 Generating BOT-LIKE traffic (high volume, repetitive)...")
    
    for _ in range(50):
        requests.post(f"{BASE_URL}/login", json={
            "username": "bot_user",
            "password": "bot123"
        })
        time.sleep(0.05)

def error_heavy_traffic():
    """Simulate traffic with high error rates"""
    print("⚠️  Generating ERROR-HEAVY traffic...")
    
    for _ in range(20):
        try:
            requests.post(f"{BASE_URL}/payment", json={
                "user_id": "error_user",
                "amount": -100,  # Invalid amount
                "currency": "USD",
                "card_number": "1234"
            })
        except:
            pass
        time.sleep(0.2)

def slow_response_pattern():
    """Generate traffic that may have slow responses"""
    print("🐌 Generating traffic with potential latency issues...")
    
    for _ in range(15):
        requests.post(f"{BASE_URL}/payment", json={
            "user_id": f"user_{random.randint(1, 50)}",
            "amount": random.uniform(10, 1000),
            "currency": "USD",
            "card_number": "4111111111111111"
        })
        time.sleep(0.4)

def mixed_anomaly_burst():
    """Create a burst of mixed anomalous patterns"""
    print("💥 Generating MIXED ANOMALY burst...")
    
    # Rapid fire from single IP
    for _ in range(30):
        endpoint = random.choice(["/login", "/search", "/payment"])
        if endpoint == "/login":
            requests.post(f"{BASE_URL}/login", json={
                "username": "attacker",
                "password": f"pass{random.randint(1, 1000)}"
            })
        elif endpoint == "/search":
            requests.get(f"{BASE_URL}/search?query=exploit")
        else:
            requests.post(f"{BASE_URL}/payment", json={
                "user_id": "attacker",
                "amount": 0.01,
                "currency": "USD",
                "card_number": "0000"
            })
        time.sleep(0.02)

def run_demo():
    print("\n" + "="*60)
    print("  ANOMALY DETECTION DEMO")
    print("  Generating various traffic patterns...")
    print("="*60 + "\n")
    
    try:
        # Test connection
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ Backend not running! Start the backend first.")
            return
        
        print(f"✅ Connected to API at {BASE_URL}\n")
        
        # Phase 1: Normal baseline
        print("PHASE 1: Establishing normal baseline")
        normal_traffic()
        time.sleep(2)
        
        # Phase 2: Bot attack
        print("\nPHASE 2: Simulating bot attack")
        bot_like_traffic()
        time.sleep(2)
        
        # Phase 3: Error burst
        print("\nPHASE 3: Simulating error burst")
        error_heavy_traffic()
        time.sleep(2)
        
        # Phase 4: Slow traffic
        print("\nPHASE 4: Simulating slow response pattern")
        slow_response_pattern()
        time.sleep(2)
        
        # Phase 5: Mixed anomalies
        print("\nPHASE 5: Simulating mixed attack pattern")
        mixed_anomaly_burst()
        
        print("\n" + "="*60)
        print("✅ DEMO COMPLETE!")
        print("="*60)
        print("\nCheck your dashboard at http://localhost:3000")
        print("You should see:")
        print("  - Increased API call count")
        print("  - Multiple HIGH RISK anomalies detected")
        print("  - Bot-like behavior flagged")
        print("  - Elevated failure predictions")
        print("\nWait 60 seconds for ML models to analyze the patterns!")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to backend!")
        print("Make sure the backend is running on http://localhost:8000")
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_demo()
