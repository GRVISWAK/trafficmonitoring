"""
Targeted anomaly injection script.
Creates specific anomalous patterns for a chosen endpoint to demonstrate ML detection.
"""
import requests
import time
import random
from datetime import datetime

BASE_URL = "http://localhost:8000"

def inject_payment_anomaly():
    """
    Create PAYMENT endpoint anomalies:
    - High error rate (invalid amounts, failed transactions)
    - Rapid repeated attempts (bot-like)
    - Large payload sizes
    """
    print("\n💳 INJECTING PAYMENT ENDPOINT ANOMALIES...")
    print("="*60)
    
    print("1️⃣  Generating rapid payment attempts (bot behavior)...")
    for i in range(40):
        try:
            requests.post(f"{BASE_URL}/payment", json={
                "user_id": "attacker_bot",
                "amount": 0.01,  # Micro-transaction spam
                "currency": "USD",
                "card_number": "0000000000000000"
            }, timeout=2)
        except:
            pass
        time.sleep(0.03)  # Very fast - 33 requests/second
    
    print("2️⃣  Generating high error rate (invalid transactions)...")
    for i in range(25):
        try:
            requests.post(f"{BASE_URL}/payment", json={
                "user_id": "fraud_user",
                "amount": -random.uniform(100, 1000),  # Negative amounts
                "currency": "INVALID",
                "card_number": "1111"
            }, timeout=2)
        except:
            pass
        time.sleep(0.1)
    
    print("3️⃣  Generating large payload spam...")
    for i in range(15):
        try:
            requests.post(f"{BASE_URL}/payment", json={
                "user_id": "payload_attack_" + "X"*1000,  # Large user ID
                "amount": 999999.99,
                "currency": "USD" * 100,  # Repeated currency
                "card_number": "4" * 500  # Huge card number
            }, timeout=2)
        except:
            pass
        time.sleep(0.05)
    
    print("✅ Payment anomalies injected!")
    print(f"   - {40+25+15} = 80 anomalous requests generated")
    print(f"   - Expected: HIGH error rate, bot cluster detection")

def inject_login_anomaly():
    """
    Create LOGIN endpoint anomalies:
    - Credential stuffing attack (rapid attempts)
    - High failure rate
    - Repeated from same source
    """
    print("\n🔐 INJECTING LOGIN ENDPOINT ANOMALIES...")
    print("="*60)
    
    print("1️⃣  Simulating credential stuffing attack...")
    for i in range(50):
        try:
            requests.post(f"{BASE_URL}/login", json={
                "username": f"victim@email.com",
                "password": f"password{random.randint(1, 10000)}"
            }, timeout=2)
        except:
            pass
        time.sleep(0.02)  # 50 requests/second
    
    print("2️⃣  Simulating brute force with common passwords...")
    common_passwords = ["123456", "password", "admin", "12345678", "qwerty"]
    for pwd in common_passwords * 10:  # 50 attempts
        try:
            requests.post(f"{BASE_URL}/login", json={
                "username": "admin",
                "password": pwd
            }, timeout=2)
        except:
            pass
        time.sleep(0.04)
    
    print("✅ Login anomalies injected!")
    print(f"   - {50+50} = 100 anomalous requests generated")
    print(f"   - Expected: Bot-like behavior, HIGH risk score")

def inject_search_anomaly():
    """
    Create SEARCH endpoint anomalies:
    - SQL injection attempts
    - XSS payload attempts
    - Massive repeated searches
    """
    print("\n🔍 INJECTING SEARCH ENDPOINT ANOMALIES...")
    print("="*60)
    
    print("1️⃣  Simulating SQL injection attempts...")
    sql_payloads = [
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "' UNION SELECT * FROM passwords --",
        "admin'--",
        "' OR 1=1--"
    ]
    for payload in sql_payloads * 8:  # 40 attempts
        try:
            requests.get(f"{BASE_URL}/search", params={
                "query": payload,
                "limit": 100
            }, timeout=2)
        except:
            pass
        time.sleep(0.05)
    
    print("2️⃣  Simulating XSS payload attempts...")
    xss_payloads = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert(1)>",
        "javascript:alert('XSS')",
        "<svg/onload=alert('XSS')>"
    ]
    for payload in xss_payloads * 10:  # 40 attempts
        try:
            requests.get(f"{BASE_URL}/search", params={
                "query": payload,
                "limit": 50
            }, timeout=2)
        except:
            pass
        time.sleep(0.04)
    
    print("3️⃣  Simulating search spam (scraping)...")
    for i in range(30):
        try:
            requests.get(f"{BASE_URL}/search", params={
                "query": f"product_{i}",
                "limit": 100
            }, timeout=2)
        except:
            pass
        time.sleep(0.02)
    
    print("✅ Search anomalies injected!")
    print(f"   - {40+40+30} = 110 anomalous requests generated")
    print(f"   - Expected: Bot detection, high request rate")

def inject_mixed_endpoint_anomaly():
    """
    Create anomalies across ALL endpoints:
    - Simulates sophisticated attack
    - High volume across multiple endpoints
    - Patterns that trigger ensemble risk scoring
    """
    print("\n⚡ INJECTING MIXED ENDPOINT ANOMALIES...")
    print("="*60)
    
    print("Simulating distributed attack pattern...")
    endpoints = [
        ("POST", "/login", {"username": "attacker", "password": "test"}),
        ("POST", "/payment", {"user_id": "attacker", "amount": 0.01, "currency": "USD", "card_number": "0000"}),
        ("GET", "/search", {"query": "exploit", "limit": 10}),
    ]
    
    for cycle in range(25):  # 75 total requests
        for method, endpoint, data in endpoints:
            try:
                if method == "POST":
                    requests.post(f"{BASE_URL}{endpoint}", json=data, timeout=2)
                else:
                    requests.get(f"{BASE_URL}{endpoint}", params=data, timeout=2)
            except:
                pass
            time.sleep(0.02)
    
    print("✅ Mixed anomalies injected!")
    print(f"   - 75 anomalous requests across all endpoints")
    print(f"   - Expected: Multiple HIGH risk detections")

def show_menu():
    print("\n" + "="*60)
    print("  TARGETED ANOMALY INJECTION TOOL")
    print("  Choose an endpoint to inject anomalies")
    print("="*60)
    print("\n1. /payment - Inject payment fraud patterns")
    print("2. /login   - Inject credential stuffing attack")
    print("3. /search  - Inject injection/scraping attempts")
    print("4. ALL      - Mixed attack across all endpoints")
    print("5. Exit")
    print()

def main():
    try:
        # Test connection
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code != 200:
            print("❌ Backend not running! Start it first.")
            return
        print(f"✅ Connected to API at {BASE_URL}")
        
        while True:
            show_menu()
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == "1":
                inject_payment_anomaly()
            elif choice == "2":
                inject_login_anomaly()
            elif choice == "3":
                inject_search_anomaly()
            elif choice == "4":
                inject_mixed_endpoint_anomaly()
            elif choice == "5":
                print("\n👋 Exiting...")
                break
            else:
                print("❌ Invalid choice! Please enter 1-5")
                continue
            
            print("\n" + "="*60)
            print("⏳ WAIT 60 SECONDS for ML analysis to run...")
            print("="*60)
            print("\nThen check results:")
            print("  • Dashboard: http://localhost:3000")
            print("  • API: http://localhost:8000/api/anomalies")
            print()
            
            again = input("Inject more anomalies? (y/n): ").strip().lower()
            if again != 'y':
                break
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to backend!")
        print("Start backend with: python app.py")
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
