"""Test email extraction from websites"""
import requests
import time
import json

BASE_URL = "http://127.0.0.1:5000"

print("=" * 70)
print("TESTING EMAIL EXTRACTION FROM WEBSITES")
print("=" * 70)

# Start scraping
print("\n1. Starting scrape for restaurants in 10001...")
response = requests.post(f"{BASE_URL}/start", json={
    "queries": [{
        "keyword": "restaurants",
        "zip_code": "10001",
        "url": ""
    }]
})

print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")

# Poll status and track email extraction
print("\n2. Monitoring progress and email extraction...")
emails_found = 0
for i in range(120):  # 4 minutes max
    time.sleep(2)
    status_response = requests.get(f"{BASE_URL}/status")
    status = status_response.json()
    
    # Count emails found
    current_emails = sum(1 for r in status['results'] if r.get('email') != 'Not given')
    if current_emails > emails_found:
        emails_found = current_emails
        print(f"   [{i+1}] Emails found: {emails_found}/{len(status['results'])}")
    
    print(f"   [{i+1}] Status: {status['status']} | Results: {len(status['results'])} | Emails: {emails_found}")
    
    if status['status'] in ['completed', 'stopped']:
        print("\n3. Scraping finished!")
        print(f"   Total results: {len(status['results'])}")
        print(f"   Emails extracted: {emails_found}")
        print(f"   Success rate: {emails_found}/{len(status['results'])} ({100*emails_found//len(status['results']) if status['results'] else 0}%)")
        
        if status['results']:
            print("\n4. Sample results with emails:")
            for idx, business in enumerate(status['results'][:5], 1):
                email_status = "✓" if business['email'] != 'Not given' else "✗"
                print(f"   {idx}. {business['name']}")
                print(f"      Phone: {business['phone']}")
                print(f"      Website: {business['website']}")
                print(f"      Email: {business['email']} {email_status}")
                print()
        
        print("=" * 70)
        print("TEST COMPLETED!")
        print("=" * 70)
        break
else:
    print("\n✗ Test timed out")
