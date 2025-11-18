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
    
    # Configuration - write proxies to file
    with open('temp_proxies.txt', 'w') as f:
        f.write("72.46.139.137:6697:tnfqnyqb:bsjia1uasdxr\n")
    
    proxy_manager = ProxyManager('temp_proxies.txt', rotation_threshold=14)
    
    # Create scraper with headless mode
    scraper = GoogleMapsScraper(
        proxy_manager=proxy_manager,
        headless=True,  # Headless mode for testing
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
            
            # Extract business data - limit to 10 for quick test
            businesses = await scraper.extract_business_data_parallel(max_concurrent=4, max_results=10)
            
            print(f"\nResults: {len(businesses)} businesses extracted")
            
            # Count how many have emails
            emails_found = sum(1 for b in businesses if b.get('email') and b.get('email') != 'Not given')
            print(f"Emails found: {emails_found}/{len(businesses)}")
            
            # Save to CSV
            import csv
            with open('test_results.csv', 'w', newline='', encoding='utf-8') as f:
                if businesses:
                    writer = csv.DictWriter(f, fieldnames=businesses[0].keys())
                    writer.writeheader()
                    writer.writerows(businesses)
            
            print(f"\n✓ Results saved to test_results.csv")
            
            # Show summary
            for i, business in enumerate(businesses, 1):
                email = business.get('email', 'Not given')
                email_status = "OK" if email != 'Not given' else "NO"
                print(f"{i}. {business.get('name', 'N/A')[:40]} - Email: {email_status}")
            
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
