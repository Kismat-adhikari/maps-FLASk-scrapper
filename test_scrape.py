"""
Test script to scrape 10 cafes in Miami
"""

import asyncio
import logging
from modules.proxy_manager import ProxyManager
from modules.scraper import GoogleMapsScraper
from modules.data_extractor import DataExtractor
from config import Config
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
)

logger = logging.getLogger(__name__)


async def test_scrape():
    """Test scraping 10 cafes in Miami."""
    
    logger.info("=" * 60)
    logger.info("TEST: Scraping 10 Cafes in Miami")
    logger.info("=" * 60)
    
    # Initialize components
    proxy_manager = ProxyManager(Config.PROXY_FILE, Config.ROTATION_THRESHOLD)
    logger.info(f"Loaded {proxy_manager.get_proxy_count()} proxies")
    
    scraper = GoogleMapsScraper(proxy_manager, headless=False)
    logger.info("Scraper initialized (visible browser)")
    
    # Test query
    query = {
        'keyword': 'cafe',
        'zip_code': 'Miami',
        'url': ''
    }
    
    logger.info(f"Query: {query['keyword']} in {query['zip_code']}")
    logger.info("Starting scrape...")
    
    try:
        # Scrape
        results = await scraper.scrape_query(query)
        
        logger.info("=" * 60)
        logger.info(f"RESULTS: Found {len(results)} businesses")
        logger.info("=" * 60)
        
        if results:
            # Show first result details
            logger.info("\nFirst Result:")
            for key, value in results[0].items():
                logger.info(f"  {key}: {value}")
            
            # Save to CSV
            df = pd.DataFrame(results)
            output_file = 'output/test-miami-cafes.csv'
            df.to_csv(output_file, index=False)
            logger.info(f"\n✓ Saved {len(results)} results to {output_file}")
            
            # Show summary
            logger.info("\nSummary:")
            logger.info(f"  Total businesses: {len(results)}")
            logger.info(f"  With phone: {sum(1 for r in results if r.get('phone'))}")
            logger.info(f"  With website: {sum(1 for r in results if r.get('website'))}")
            logger.info(f"  With rating: {sum(1 for r in results if r.get('rating'))}")
            
        else:
            logger.error("❌ No results found!")
            logger.error("This might be due to:")
            logger.error("  1. Google Maps selectors changed")
            logger.error("  2. Proxy issues")
            logger.error("  3. CAPTCHA blocking")
            
    except Exception as e:
        logger.error(f"❌ Error during scraping: {e}", exc_info=True)
    
    finally:
        # Cleanup
        await scraper.cleanup()
        logger.info("\nCleanup completed")


if __name__ == '__main__':
    asyncio.run(test_scrape())
