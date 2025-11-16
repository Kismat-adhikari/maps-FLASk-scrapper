"""Test with a single business to see detailed logs"""
import requests
import time

BASE_URL = "http://127.0.0.1:5000"

print("Testing with dentists (single query)...")

response = requests.post(f"{BASE_URL}/start", json={
    "queries": [{
        "keyword": "dentist",
        "zip_code": "10001",
        "url": ""
    }]
})

print(f"Started: {response.json()}")

# Wait for completion
for i in range(60):
    time.sleep(3)
    status = requests.get(f"{BASE_URL}/status").json()
    print(f"[{i+1}] Status: {status['status']} | Results: {len(status['results'])}")
    
    if status['status'] in ['completed', 'stopped']:
        print("\nResults:")
        for business in status['results']:
            print(f"  - {business['name']}")
            print(f"    Website: {business['website']}")
            print(f"    Email: {business['email']}")
        break
