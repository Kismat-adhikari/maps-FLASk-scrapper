"""
Performance Test Script
Tests scraping 2 queries (gym + restaurant in Miami) and measures time
"""

import asyncio
import time
import logging
from datetime import datetime
from modules.proxy_manager import ProxyManager
from modules.scraper import GoogleMapsScraper
from modules.file_parser import FileParser

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

async def run_test():
    """Run performance test"""
    
    # Parse test file
    logger.info("=" * 60)
    logger.info("PERFORMANCE TEST STARTING")
    logger.info("=" * 60)
    
    queries, error = FileParser.parse_file('performance_test.csv')
    
    if error:
        logger.error(f"Failed to parse file: {error}")
        return
    
    logger.info(f"Loaded {len(queries)} queries:")
    for idx, q in enumerate(queries, 1):
        logger.info(f"  {idx}. {q['keyword']} in {q['zip_code']}")
    
    # Initialize components
    proxy_manager = ProxyManager('proxies.txt')
    scraper = GoogleMapsScraper(proxy_manager, headless=False)
    
    # Track results
    all_businesses = []
    start_time = time.time()
    
    logger.info("\n" + "=" * 60)
    logger.info("STARTING SCRAPE")
    logger.info("=" * 60 + "\n")
    
    # Scrape each query
    for idx, query in enumerate(queries, 1):
        query_start = time.time()
        
        keyword = query['keyword']
        location = query['zip_code']
        
        logger.info(f"\n>>> Query {idx}/{len(queries)}: {keyword} in {location}")
        logger.info(f">>> Expected: Up to 60 businesses")
        
        businesses = await scraper.scrape_query(query)
        
        query_time = time.time() - query_start
        
        logger.info(f">>> Scraped: {len(businesses)} businesses")
        logger.info(f">>> Time: {query_time:.2f} seconds ({query_time/60:.2f} minutes)")
        
        all_businesses.extend(businesses)
        
        # Small delay between queries
        if idx < len(queries):
            logger.info(">>> Waiting 2 seconds before next query...")
            await asyncio.sleep(2)
    
    # Cleanup
    await scraper.cleanup()
    
    # Calculate totals
    total_time = time.time() - start_time
    
    # Print report
    logger.info("\n" + "=" * 60)
    logger.info("PERFORMANCE TEST REPORT")
    logger.info("=" * 60)
    logger.info(f"Total Queries: {len(queries)}")
    logger.info(f"Total Businesses Scraped: {len(all_businesses)}")
    logger.info(f"Total Time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
    logger.info(f"Average per Query: {total_time/len(queries):.2f} seconds")
    logger.info(f"Average per Business: {total_time/len(all_businesses):.2f} seconds" if all_businesses else "N/A")
    logger.info("=" * 60)
    
    # Breakdown by query
    logger.info("\nBREAKDOWN:")
    logger.info(f"  Query 1 (gym in Miami): ~{len([b for b in all_businesses if 'gym' in str(b.get('keyword', '')).lower()])} businesses")
    logger.info(f"  Query 2 (restaurant in Miami): ~{len([b for b in all_businesses if 'restaurant' in str(b.get('keyword', '')).lower()])} businesses")
    
    # Save report
    report_file = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w') as f:
        f.write("=" * 60 + "\n")
        f.write("GOOGLE MAPS SCRAPER - PERFORMANCE TEST REPORT\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Queries Tested:\n")
        for idx, q in enumerate(queries, 1):
            f.write(f"  {idx}. {q['keyword']} in {q['zip_code']}\n")
        f.write(f"\nResults:\n")
        f.write(f"  Total Queries: {len(queries)}\n")
        f.write(f"  Total Businesses Scraped: {len(all_businesses)}\n")
        f.write(f"  Expected Maximum: {len(queries) * 60} businesses\n")
        f.write(f"  Success Rate: {(len(all_businesses) / (len(queries) * 60) * 100):.1f}%\n\n")
        f.write(f"Performance:\n")
        f.write(f"  Total Time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)\n")
        f.write(f"  Average per Query: {total_time/len(queries):.2f} seconds\n")
        f.write(f"  Average per Business: {total_time/len(all_businesses):.2f} seconds\n" if all_businesses else "  Average per Business: N/A\n")
        f.write("\n" + "=" * 60 + "\n")
    
    logger.info(f"\nReport saved to: {report_file}")

if __name__ == '__main__':
    asyncio.run(run_test())
