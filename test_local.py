"""
Quick local test script to verify scraper works
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

async def test_scraper():
    """Test the scraper locally"""
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
    
    try:
        # Initialize browser
        await scraper.initialize_browser()
        
        # Search for businesses
        keyword = "Cafe"
        location = "New York"
        print(f"\nSearching for: {keyword} in {location}")
        
        success = await scraper.search_google_maps(keyword, location)
        
        if success:
            print("Search successful, extracting businesses...")
            
            # Extract business data - 100 businesses (will get ~80-90)
            businesses = await scraper.extract_business_data_parallel(max_concurrent=5, max_results=100)
            
            print(f"\nResults: {len(businesses)} businesses extracted")
            
            # Count how many have emails
            emails_found = sum(1 for b in businesses if b.get('email') and b.get('email') != 'Not given')
            print(f"Emails found: {emails_found}/{len(businesses)}")
            
            # Calculate time
            elapsed = time.time() - start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            
            # Save to CSV
            import csv
            with open('speed_test_100_businesses.csv', 'w', newline='', encoding='utf-8') as f:
                if businesses:
                    writer = csv.DictWriter(f, fieldnames=businesses[0].keys())
                    writer.writeheader()
                    writer.writerows(businesses)
            
            print(f"\n{'='*60}")
            print(f"SPEED TEST RESULTS")
            print(f"{'='*60}")
            print(f"Businesses scraped: {len(businesses)}")
            print(f"Time taken: {minutes}m {seconds}s")
            print(f"Average per business: {elapsed/len(businesses):.1f}s")
            print(f"Results saved to: speed_test_100_businesses.csv")
            print(f"{'='*60}\n")
            
            return businesses
        else:
            print("Search failed")
            return []
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        await scraper.close_browser()

if __name__ == "__main__":
    results = asyncio.run(test_scraper())
    print(f"\nTest complete: {len(results)} businesses scraped")
