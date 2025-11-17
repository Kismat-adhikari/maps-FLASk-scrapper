"""
Simple test without Apify SDK - just test the scraping logic
"""

import asyncio
import json
from modules.proxy_manager import ProxyManager
from modules.scraper import GoogleMapsScraper

async def test_scraper():
    print("=" * 60)
    print("TESTING SCRAPER LOGIC")
    print("=" * 60)
    
    # Load test input
    with open('test_input.json', 'r') as f:
        test_input = json.load(f)
    
    print(f"\nTest Input:")
    print(f"  Mode: {test_input['mode']}")
    print(f"  Keywords: {test_input['keywords']}")
    print(f"  Locations: {test_input['locations']}")
    print(f"  Max Results: {test_input['maxResultsPerQuery']}")
    print(f"  Headless: {test_input['headless']}")
    
    # Create queries
    queries = []
    for keyword in test_input['keywords']:
        for location in test_input['locations']:
            queries.append({
                'keyword': keyword,
                'zip_code': location,
                'url': ''
            })
    
    print(f"\nGenerated {len(queries)} queries")
    
    # Initialize proxy manager
    custom_proxies = test_input['customProxies']
    with open('temp_proxies.txt', 'w') as f:
        for proxy in custom_proxies:
            f.write(f"{proxy}\n")
    
    proxy_manager = ProxyManager(
        proxy_file='temp_proxies.txt',
        rotation_threshold=test_input['rotationThreshold']
    )
    
    print(f"Proxy manager initialized with {proxy_manager.get_proxy_count()} proxies")
    
    # Initialize scraper
    scraper = GoogleMapsScraper(
        proxy_manager=proxy_manager,
        headless=test_input['headless']
    )
    
    print("\nScraper initialized")
    print("\nStarting scraping...\n")
    
    # Process queries
    all_businesses = []
    for idx, query in enumerate(queries, start=1):
        keyword = query['keyword']
        location = query['zip_code']
        
        print(f"\n[{idx}/{len(queries)}] Scraping: {keyword} in {location}")
        print("-" * 60)
        
        try:
            businesses = await scraper.scrape_query(
                query, 
                max_results=test_input['maxResultsPerQuery']
            )
            
            if businesses:
                print(f"✓ Found {len(businesses)} businesses")
                all_businesses.extend(businesses)
                
                # Show first business as example
                if businesses:
                    first = businesses[0]
                    print(f"\nExample business:")
                    print(f"  Name: {first.get('name', 'N/A')}")
                    print(f"  Address: {first.get('full_address', 'N/A')}")
                    print(f"  Phone: {first.get('phone', 'N/A')}")
                    print(f"  Rating: {first.get('rating', 'N/A')}")
            else:
                print("✗ No businesses found")
        
        except Exception as e:
            print(f"✗ Error: {e}")
    
    # Cleanup
    await scraper.cleanup()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print(f"Total businesses scraped: {len(all_businesses)}")
    
    # Save results
    if all_businesses:
        with open('test_results.json', 'w') as f:
            json.dump(all_businesses, f, indent=2)
        print(f"Results saved to: test_results.json")

if __name__ == '__main__':
    asyncio.run(test_scraper())
