import requests
import time

print("Testing email extraction with plumbers...")

requests.post("http://127.0.0.1:5000/start", json={
    "queries": [{"keyword": "plumber", "zip_code": "10001", "url": ""}]
})

for i in range(50):
    time.sleep(3)
    status = requests.get("http://127.0.0.1:5000/status").json()
    
    if status['results']:
        print(f"\n[{i+1}] Results: {len(status['results'])}")
        for b in status['results']:
            email_icon = "✓" if b['email'] != 'Not given' else "✗"
            print(f"  {b['name']}: {b['email']} {email_icon}")
    
    if status['status'] == 'completed':
        print("\n✓ COMPLETED!")
        emails_found = sum(1 for b in status['results'] if b['email'] != 'Not given')
        print(f"Emails found: {emails_found}/{len(status['results'])}")
        break
