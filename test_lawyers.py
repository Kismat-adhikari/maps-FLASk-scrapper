"""Test email extraction with lawyers (more likely to have emails)"""
import requests
import time

BASE_URL = "http://127.0.0.1:5000"

print("=" * 70)
print("TESTING EMAIL EXTRACTION WITH LAWYERS")
print("(Lawyers are more likely to display emails on their websites)")
print("=" * 70)

# Start scraping
print("\n1. Starting scrape for lawyers in 10001...")
response = requests.post(f"{BASE_URL}/start", json={
    "queries": [{
        "keyword": "lawyers",
        "zip_code": "10001",
        "url": ""
    }]
})

print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")

# Poll status
print("\n2. Monitoring progress...")
emails_found = 0
last_count = 0

for i in range(120):  # 4 minutes max
    time.sleep(3)
    status_response = requests.get(f"{BASE_URL}/status")
    status = status_response.json()
    
    # Count emails
    current_emails = sum(1 for r in status['results'] if r.get('email') != 'Not given')
    
    # Show update when new results or emails
    if len(status['results']) > last_count or current_emails > emails_found:
        last_count = len(status['results'])
        emails_found = current_emails
        print(f"   [{i+1}] Results: {len(status['results'])} | Emails: {emails_found}")
        
        # Show latest business
        if status['results']:
            latest = status['results'][-1]
            email_icon = "✓" if latest['email'] != 'Not given' else "✗"
            print(f"        Latest: {latest['name']} - Email: {latest['email']} {email_icon}")
    
    if status['status'] in ['completed', 'stopped']:
        print("\n3. Scraping finished!")
        print(f"   Total results: {len(status['results'])}")
        print(f"   Emails found: {emails_found}/{len(status['results'])}")
        
        if emails_found > 0:
            print(f"   ✓ SUCCESS! Email extraction is working!")
            print(f"   Success rate: {100*emails_found//len(status['results'])}%")
        else:
            print(f"   Note: No emails found (lawyers may use contact forms)")
        
        print("\n4. All results:")
        for idx, business in enumerate(status['results'], 1):
            email_icon = "✓" if business['email'] != 'Not given' else "✗"
            print(f"   {idx}. {business['name']}")
            print(f"      Website: {business['website']}")
            print(f"      Email: {business['email']} {email_icon}")
        
        print("\n" + "=" * 70)
        print("TEST COMPLETED!")
        print("=" * 70)
        break
else:
    print("\n✗ Test timed out")
