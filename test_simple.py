import requests

response = requests.post("http://127.0.0.1:5000/start", json={
    "queries": [{
        "keyword": "pizza",
        "zip_code": "10001",
        "url": ""
    }]
})

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
