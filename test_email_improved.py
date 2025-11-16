"""Test improved email extraction with visible text"""
import requests
import time

print("=" * 70)
print("TESTING IMPROVED EMAIL EXTRACTION")
print("Now extracting from VISIBLE TEXT (not just HTML)")
print("=" * 70)

# Test with contractors (more likely to have emails)
response = requests.post("http://127.0.0.1:5000/start", json={
    "queries": [{
        "keyword": "contractor",
        "zip_code": "10001",
        "url": ""
    }]
})

print(f"\nStarted: {response.json()}")

emails_found = 0
for i in range(60):
    time.sleep(3)
    status = requests.get("http://127.0.0.1:5000/status").json()
    
    if status['results']:
        current_emails = sum(1 for b in status['results'] if b['email'] != 'Not given')
        if current_emails > emails_found:
            emails_found = current_emails
            print(f"\n[{i+1}] NEW EMAIL FOUND! Total: {emails_found}/{len(status['results'])}")
            for b in status['results']:
                if b['email'] != 'Not given':
                    print(f"  ✓ {b['name']}: {b['email']}")
    
    if status['status'] == 'completed':
        print("\n" + "=" * 70)
        print("SCRAPING COMPLETED!")
        print("=" * 70)
        print(f"Total businesses: {len(status['results'])}")
        print(f"Emails found: {emails_found}")
        print(f"Success rate: {100*emails_found//len(status['results']) if status['results'] else 0}%")
        
        print("\nAll results:")
        for idx, b in enumerate(status['results'], 1):
            email_icon = "✓" if b['email'] != 'Not given' else "✗"
            print(f"{idx}. {b['name']}")
            print(f"   Website: {b['website']}")
            print(f"   Email: {b['email']} {email_icon}")
        break
