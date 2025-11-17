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
    
    # Create scraper
    scraper = GoogleMapsScraper(
        proxy_manager=proxy_manager,
        headless=True,
        use_apify_proxy=False
    )
    
    try:
        # Initialize browser
        await scraper.initialize_browser()
        
        # Search for businesses
        keyword = "coffee shops"
        location = "Miami"
        print(f"\nSearching for: {keyword} in {location}")
        
        success = await scraper.search_google_maps(keyword, location)
        
        if success:
            print("Search successful, extracting businesses...")
            
            # Extract business data (limit to 10 for quick test)
            businesses = await scraper.extract_business_data_parallel(max_concurrent=3)
            
            print(f"\nResults: {len(businesses)} businesses extracted")
            
            # Show first few results
            for i, business in enumerate(businesses[:5], 1):
                print(f"\n{i}. {business.get('name', 'N/A')}")
                print(f"   Address: {business.get('full_address', 'N/A')}")
                print(f"   Phone: {business.get('phone', 'N/A')}")
                print(f"   Website: {business.get('website', 'N/A')}")
            
            if len(businesses) > 5:
                print(f"\n... and {len(businesses) - 5} more")
            
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
