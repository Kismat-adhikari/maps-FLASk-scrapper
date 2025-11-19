"""
Test script with multiple keywords and locations
"""
import asyncio
import logging
from modules.scraper import GoogleMapsScraper
from modules.proxy_manager import ProxyManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

async def test_multiple_queries():
    """Test the scraper with multiple keywords and locations"""
    import time
    start_time = time.time()
    
    # Configuration - write proxies to file
    with open('temp_proxies.txt', 'w') as f:
        f.write("72.46.139.137:6697:tnfqnyqb:bsjia1uasdxr\n")
    
    proxy_manager = ProxyManager('temp_proxies.txt', rotation_threshold=14)
    
    # Create scraper in headless mode
    scraper = GoogleMapsScraper(
        proxy_manager=proxy_manager,
        headless=True,  # Headless - no browser window
        use_apify_proxy=False
    )
    
    # Multiple keywords and locations
    keywords = ["Cafe", "Restaurant"]
    locations = ["Manhattan NY", "Brooklyn NY"]
    
    all_businesses = []
    
    try:
        # Initialize browser once
        await scraper.initialize_browser()
        
        # Run each keyword-location combination
        for keyword in keywords:
            for location in locations:
                print(f"\n{'='*60}")
                print(f"Searching for: {keyword} in {location}")
                print(f"{'='*60}")
                
                success = await scraper.search_google_maps(keyword, location)
                
                if success:
                    print("Search successful, extracting businesses...")
                    
                    # Extract business data - 100 max per query
                    businesses = await scraper.extract_business_data_parallel(max_concurrent=5, max_results=100)
                    
                    # Add query context
                    for business in businesses:
                        business['search_keyword'] = keyword
                        business['search_location'] = location
                    
                    all_businesses.extend(businesses)
                    
                    print(f"✓ Extracted {len(businesses)} businesses from this query")
                    print(f"Total so far: {len(all_businesses)} businesses")
                else:
                    print(f"✗ Search failed for {keyword} in {location}")
                
                # Small delay between queries
                await asyncio.sleep(2)
        
        # Deduplicate by CID (Google's unique ID)
        print(f"\n{'='*60}")
        print("Deduplicating results...")
        print(f"{'='*60}")
        
        seen_cids = set()
        unique_businesses = []
        for business in all_businesses:
            cid = business.get('cid', '')
            if cid and cid not in seen_cids:
                seen_cids.add(cid)
                unique_businesses.append(business)
        
        print(f"Before deduplication: {len(all_businesses)} businesses")
        print(f"After deduplication: {len(unique_businesses)} businesses")
        
        # Count how many have emails
        emails_found = sum(1 for b in unique_businesses if b.get('email') and b.get('email') != 'Not given')
        
        # Calculate time
        elapsed = time.time() - start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        
        # Save to CSV
        import csv
        with open('multi_query_test_results.csv', 'w', newline='', encoding='utf-8') as f:
            if unique_businesses:
                writer = csv.DictWriter(f, fieldnames=unique_businesses[0].keys())
                writer.writeheader()
                writer.writerows(unique_businesses)
        
        print(f"\n{'='*60}")
        print(f"MULTI-QUERY TEST RESULTS")
        print(f"{'='*60}")
        print(f"Keywords tested: {', '.join(keywords)}")
        print(f"Locations tested: {', '.join(locations)}")
        print(f"Total queries: {len(keywords) * len(locations)}")
        print(f"Businesses scraped: {len(unique_businesses)} (after deduplication)")
        print(f"Emails found: {emails_found}/{len(unique_businesses)}")
        print(f"Time taken: {minutes}m {seconds}s")
        print(f"Average per business: {elapsed/len(unique_businesses):.1f}s")
        print(f"Results saved to: multi_query_test_results.csv")
        print(f"{'='*60}\n")
        
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
