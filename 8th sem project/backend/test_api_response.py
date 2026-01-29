import requests
import json

# Test the API
resp = requests.get('http://localhost:8000/api/anomalies?limit=3')
data = resp.json()

print(f'Total anomalies fetched: {len(data)}')
print('='*80)

for i, anomaly in enumerate(data[:3], 1):
    print(f'\nAnomaly #{i}:')
    print(f'  ID: {anomaly.get("id")}')
    print(f'  Endpoint: {anomaly.get("endpoint")}')
    print(f'  Has root_cause_analysis: {"root_cause_analysis" in anomaly}')
    
    if 'root_cause_analysis' in anomaly:
        rca = anomaly['root_cause_analysis']
        print(f'  Root Cause: {rca.get("root_cause")}')
        print(f'  Confidence: {rca.get("confidence")}')
        print(f'  Suggestions: {len(rca.get("resolution_suggestions", []))}')
        
        for j, suggestion in enumerate(rca.get('resolution_suggestions', [])[:2], 1):
            print(f'    {j}. [{suggestion["priority"]}] {suggestion["action"]}')
    else:
        print('  ❌ No root_cause_analysis found!')

print('\n' + '='*80)
print(f'\nFirst anomaly keys: {list(data[0].keys()) if data else "No data"}')
