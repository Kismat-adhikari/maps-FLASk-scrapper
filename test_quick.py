import requests
import time

requests.post("http://127.0.0.1:5000/start", json={
    "queries": [{"keyword": "plumber", "zip_code": "10001", "url": ""}]
})

for i in range(40):
    time.sleep(3)
    status = requests.get("http://127.0.0.1:5000/status").json()
    if status['results']:
        print(f"Results: {len(status['results'])}")
        for b in status['results']:
            print(f"  {b['name']}: {b['email']}")
    if status['status'] == 'completed':
        break
