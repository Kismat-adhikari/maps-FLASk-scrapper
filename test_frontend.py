"""Test the frontend scraping flow"""
import requests
import time
import json

BASE_URL = "http://127.0.0.1:5000"

def test_scrape():
    print("Testing scrape flow...")
    
    # Start scraping
    response = requests.post(f"{BASE_URL}/start", json={
        "queries": [{
            "keyword": "pizza",
            "zip_code": "10001",
            "url": ""
        }]
    })
    
    print(f"Start response: {response.status_code}")
    print(f"Response data: {response.json()}")
    
    # Poll status
    for i in range(30):
        time.sleep(2)
        status_response = requests.get(f"{BASE_URL}/status")
        status = status_response.json()
        
        print(f"\n[{i+1}] Status: {status['status']}")
        print(f"    Processed: {status['processed']}/{status['total_queries']}")
        print(f"    Success: {status['success_count']}, Failed: {status['failure_count']}")
        print(f"    Results count: {len(status['results'])}")
        print(f"    Current query: {status['current_query']}")
        
        if status['status'] in ['completed', 'stopped']:
            print("\n✓ Scraping finished!")
            print(f"Total results: {len(status['results'])}")
            if status['results']:
                print(f"First result: {status['results'][0]['name']}")
            break

if __name__ == "__main__":
    test_scrape()
