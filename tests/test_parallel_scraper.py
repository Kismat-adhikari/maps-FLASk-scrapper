"""
Quick test script to measure parallel scraping performance
"""
import asyncio
import time
from modules.proxy_manager import ProxyManager
from modules.scraper import GoogleMapsScraper

async def test_scraper():
    print("=" * 60)
    print("PARALLEL SCRAPING PERFORMANCE TEST")
    print("=" * 60)
    
    # Initialize
    proxy_manager = ProxyManager('proxies.txt')
    scraper = GoogleMapsScraper(proxy_manager, headless=False)
    
    # Test query
    query = {
        'keyword': 'restaurant',
        'zip_code': 'Miami'
    }
    
    print(f"\n🔍 Testing: {query['keyword']} in {query['zip_code']}")
    print(f"⏱️  Starting timer...\n")
    
    # Start timer
    start_time = time.time()
    
    # Run scraper
    try:
        results = await scraper.scrape_query(query)
        
        # End timer
        end_time = time.time()
        elapsed = end_time - start_time
        
        # Results
        print("\n" + "=" * 60)
        print("RESULTS")
        print("=" * 60)
        print(f"✅ Businesses scraped: {len(results)}")
        print(f"⏱️  Total time: {elapsed:.2f} seconds ({elapsed/60:.2f} minutes)")
        
        if len(results) > 0:
            print(f"⚡ Average per business: {elapsed/len(results):.2f} seconds")
            print(f"🚀 Speed: {len(results)/(elapsed/60):.2f} businesses/minute")
        
        print("\n📋 Sample businesses:")
        for i, business in enumerate(results[:5], 1):
            name = business.get('name', 'Not given')
            phone = business.get('phone', 'Not given')
            rating = business.get('rating', 'Not given')
            print(f"  {i}. {name} - {phone} - ⭐ {rating}")
        
        if len(results) > 5:
            print(f"  ... and {len(results) - 5} more")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        await scraper.cleanup()

if __name__ == "__main__":
    asyncio.run(test_scraper())
