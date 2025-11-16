"""Test with just one business to see detailed logs"""
import requests
import time

print("Testing with accountants (likely to have emails)...")

requests.post("http://127.0.0.1:5000/start", json={
    "queries": [{"keyword": "accountant", "zip_code": "10001", "url": ""}]
})

for i in range(60):
    time.sleep(3)
    status = requests.get("http://127.0.0.1:5000/status").json()
    
    if status['results']:
        print(f"[{i+1}] Results: {len(status['results'])}")
        for b in status['results']:
            email_icon = "✓" if b['email'] != 'Not given' else "✗"
            print(f"  {b['name']}: {b['email']} {email_icon}")
    
    if status['status'] == 'completed':
        print("\nDONE!")
        break
