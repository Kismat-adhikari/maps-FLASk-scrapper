import requests
import json

response = requests.get("http://127.0.0.1:5000/status")
status = response.json()

print(json.dumps(status, indent=2))
print(f"\nResults count: {len(status['results'])}")
if status['results']:
    print("\nFirst result:")
    print(json.dumps(status['results'][0], indent=2))
