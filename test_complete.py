"""Test complete scraping flow"""
import requests
import time

BASE_URL = "http://127.0.0.1:5000"

print("=" * 60)
print("TESTING GOOGLE MAPS SCRAPER")
print("=" * 60)

# Start scraping
print("\n1. Starting scrape...")
response = requests.post(f"{BASE_URL}/start", json={
    "queries": [{
        "keyword": "coffee",
        "zip_code": "10001",
        "url": ""
    }]
})

print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")

# Poll status
print("\n2. Monitoring progress...")
for i in range(60):
    time.sleep(2)
    status_response = requests.get(f"{BASE_URL}/status")
    status = status_response.json()
    
    print(f"   [{i+1}] Status: {status['status']} | Processed: {status['processed']}/{status['total_queries']} | Results: {len(status['results'])}")
    
    if status['status'] in ['completed', 'stopped']:
        print("\n3. Scraping finished!")
        print(f"   Total results: {len(status['results'])}")
        print(f"   Success: {status['success_count']}, Failed: {status['failure_count']}")
        
        if status['results']:
            print("\n4. Sample results:")
            for idx, business in enumerate(status['results'][:3], 1):
                print(f"   {idx}. {business['name']}")
                print(f"      Phone: {business['phone']}")
                print(f"      Rating: {business['rating']}")
                print(f"      Website: {business['website']}")
        
        print("\n" + "=" * 60)
        print("TEST COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        break
else:
    print("\n✗ Test timed out")
