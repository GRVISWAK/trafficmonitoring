import requests
import time

print("Triggering test requests to /payment endpoint...")
for i in range(15):
    try:
        response = requests.post(
            'http://localhost:8000/payment',
            json={'amount': 100, 'currency': 'USD'},
            headers={'Content-Type': 'application/json'}
        )
        print(f"Request {i+1}: Status {response.status_code}")
        time.sleep(0.1)
    except Exception as e:
        print(f"Request {i+1}: Error - {e}")

print("\nChecking anomalies...")
try:
    response = requests.get('http://localhost:8000/api/anomalies')
    anomalies = response.json()
    print(f"Total anomalies detected: {len(anomalies)}")
    if anomalies:
        print("\nFirst anomaly:")
        print(f"  Endpoint: {anomalies[0]['endpoint']}")
        print(f"  Root Cause: {anomalies[0].get('root_cause_analysis', {}).get('root_cause', 'N/A')}")
        print(f"  Suggestions: {len(anomalies[0].get('root_cause_analysis', {}).get('resolution_suggestions', []))}")
except Exception as e:
    print(f"Error checking anomalies: {e}")
