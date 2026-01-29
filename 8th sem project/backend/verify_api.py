"""
Simple test to verify API returns root_cause_analysis
"""
import urllib.request
import json

try:
    # Fetch anomalies from API
    url = 'http://localhost:8000/api/anomalies?limit=2'
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
    
    print(f"✅ Fetched {len(data)} anomalies from API")
    print("="*80)
    
    if len(data) > 0:
        anomaly = data[0]
        print(f"\n📋 Anomaly #1:")
        print(f"   ID: {anomaly.get('id')}")
        print(f"   Endpoint: {anomaly.get('endpoint')}")
        print(f"   Error Rate: {anomaly.get('error_rate', 0)*100:.1f}%")
        print(f"   Avg Response: {anomaly.get('avg_response_time', 0):.0f}ms")
        
        if 'root_cause_analysis' in anomaly:
            rca = anomaly['root_cause_analysis']
            print(f"\n   ✅ ROOT CAUSE ANALYSIS FOUND!")
            print(f"   Root Cause: {rca.get('root_cause')}")
            print(f"   Confidence: {rca.get('confidence', 0)*100:.0f}%")
            
            suggestions = rca.get('resolution_suggestions', [])
            print(f"\n   💡 RESOLUTION SUGGESTIONS ({len(suggestions)}):")
            for i, sug in enumerate(suggestions, 1):
                print(f"      {i}. [{sug.get('priority')}] {sug.get('category')}: {sug.get('action')}")
        else:
            print(f"\n   ❌ NO root_cause_analysis field in response!")
            print(f"   Available fields: {list(anomaly.keys())}")
    
    print("\n" + "="*80)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
