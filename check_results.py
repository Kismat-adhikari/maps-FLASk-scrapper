import requests

status = requests.get('http://127.0.0.1:5000/status').json()

print(f"Status: {status['status']}")
print(f"Total results: {len(status['results'])}")
print(f"\nBusinesses with emails:")

for b in status['results']:
    if b['email'] != 'Not given':
        print(f"  ✓ {b['name']}: {b['email']}")
    else:
        print(f"  ✗ {b['name']}: No email")
