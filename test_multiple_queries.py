"""
Test scraper with multiple keywords and locations
"""
import asyncio
import logging
import csv
import time
from modules.scraper import GoogleMapsScraper
from modules.proxy_manager import ProxyManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

async def test_multiple_queries():
    """Test with multiple keywords and locations"""
    start_time = time.time()
    
    # Configuration
    with open('temp_proxies.txt', 'w') as f:
        f.write("72.46.139.137:6697:tnfqnyqb:bsjia1uasdxr\n")
    
    proxy_manager = ProxyManager('temp_proxies.txt', rotation_threshold=14)
    
    # Define queries
    keywords = ["Cafe", "Coffee Shop", "Bakery"]
    locations = ["New York", "Miami", "Austin"]
    
    all_businesses = []
    
    # Create scraper
    scraper = GoogleMapsScraper(
        proxy_manager=proxy_manager,
        headless=True,
        use_apify_proxy=False
    )
    
    try:
        # Initialize browser once
        await scraper.initialize_browser()
        
        print(f"\n{'='*70}")
        print(f"MULTI-QUERY TEST: {len(keywords)} keywords × {len(locations)} locations = {len(keywords) * len(locations)} queries")
        print(f"{'='*70}\n")
        
        # Loop through all combinations
        for location in locations:
            for keyword in keywords:
                print(f"\n🔍 Searching: {keyword} in {location}")
                print(f"-" * 50)
                
                query_start = time.time()
                
                # Search
                success = await scraper.search_google_maps(keyword, location)
                
                if success:
                    # Extract businesses (limit to 50 per query for speed)
                    businesses = await scraper.extract_business_data_parallel(
                        max_concurrent=5, 
                        max_results=50
                    )
                    
                    # Add query info to each business
                    for business in businesses:
                        business['search_keyword'] = keyword
                        business['search_location'] = location
                    
                    all_businesses.extend(businesses)
                    
                    query_time = time.time() - query_start
                    print(f"✅ Found {len(businesses)} businesses in {query_time:.1f}s")
                else:
                    print(f"❌ Search failed")
                
                # Small delay between queries
                await asyncio.sleep(2)
        
        # Calculate totals
        elapsed = time.time() - start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        
        # Remove duplicates based on name + address
        unique_businesses = []
        seen = set()
        for business in all_businesses:
            key = f"{business.get('name', '')}_{business.get('address', '')}"
            if key not in seen:
                seen.add(key)
                unique_businesses.append(business)
        
        # Save to CSV
        if unique_businesses:
            with open('multi_query_results.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=unique_businesses[0].keys())
                writer.writeheader()
                writer.writerows(unique_businesses)
        
        # Print summary
        print(f"\n{'='*70}")
        print(f"FINAL RESULTS")
        print(f"{'='*70}")
        print(f"Total businesses scraped: {len(all_businesses)}")
        print(f"Unique businesses: {len(unique_businesses)}")
        print(f"Duplicates removed: {len(all_businesses) - len(unique_businesses)}")
        print(f"Total time: {minutes}m {seconds}s")
        print(f"Average per business: {elapsed/len(all_businesses):.1f}s")
        print(f"Results saved to: multi_query_results.csv")
        print(f"{'='*70}\n")
        
        return unique_businesses
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        await scraper.close_browser()

if __name__ == "__main__":
    results = asyncio.run(test_multiple_queries())
    print(f"\nTest complete: {len(results)} unique businesses scraped")
