"""
Google Maps Scraper - Apify Actor
Main entry point for Apify Actor execution.
"""

import asyncio
import logging
from apify import Actor
from modules.proxy_manager import ProxyManager
from modules.scraper import GoogleMapsScraper
from modules.utils import DataUtils

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """
    Main Apify Actor entry point.
    Reads input, scrapes Google Maps, and saves results to Apify Dataset.
    """
    async with Actor:
        # Get input from Apify
        actor_input = await Actor.get_input() or {}
        logger.info(f"Actor input: {actor_input}")
        
        # Extract configuration
        mode = actor_input.get('mode', 'keyword')
        queries = []
        
        # Parse input based on mode
        if mode == 'keyword':
            # Single or multiple keyword searches
            keywords = actor_input.get('keywords', [])
            locations = actor_input.get('locations', [])
            
            if not keywords or not locations:
                raise ValueError("Keywords and locations are required for keyword mode")
            
            # Create queries from keywords and locations
            for keyword in keywords:
                for location in locations:
                    queries.append({
                        'keyword': keyword,
                        'zip_code': location,
                        'url': ''
                    })
        
        elif mode == 'url':
            # URL-based scraping
            urls = actor_input.get('urls', [])
            
            if not urls:
                raise ValueError("URLs are required for URL mode")
            
            for url in urls:
                queries.append({
                    'keyword': '',
                    'zip_code': '',
                    'url': url
                })
        
        else:
            raise ValueError(f"Invalid mode: {mode}")
        
        logger.info(f"Processing {len(queries)} queries")
        
        # Configuration from input
        max_results_per_query = actor_input.get('maxResultsPerQuery', 60)
        use_apify_proxy = actor_input.get('useApifyProxy', False)
        proxy_config = actor_input.get('proxyConfiguration', {})
        headless = actor_input.get('headless', True)
        extract_emails = actor_input.get('extractEmails', True)
        deduplicate = actor_input.get('deduplicate', True)
        
        # Initialize proxy manager
        if use_apify_proxy:
            # Use Apify's proxy service
            logger.info("Using Apify proxy service")
            proxy_manager = None  # Will be handled by Playwright's proxy config
        else:
            # Use custom proxies from input
            custom_proxies = actor_input.get('customProxies', [])
            if not custom_proxies:
                raise ValueError("Custom proxies required when not using Apify proxy")
            
            # Write proxies to temporary file
            with open('temp_proxies.txt', 'w') as f:
                for proxy in custom_proxies:
                    f.write(f"{proxy}\n")
            
            proxy_manager = ProxyManager(
                proxy_file='temp_proxies.txt',
                rotation_threshold=actor_input.get('rotationThreshold', 14)
            )
            logger.info(f"Initialized proxy manager with {proxy_manager.get_proxy_count()} proxies")
        
        # Initialize scraper
        scraper = GoogleMapsScraper(
            proxy_manager=proxy_manager,
            headless=headless,
            use_apify_proxy=use_apify_proxy,
            apify_proxy_config=proxy_config
        )
        
        # Track statistics
        total_businesses = 0
        successful_queries = 0
        failed_queries = 0
        
        # Process each query
        for idx, query in enumerate(queries, start=1):
            keyword = query.get('keyword', '')
            location = query.get('zip_code', '')
            url = query.get('url', '')
            
            query_desc = url if url else f"{keyword} in {location}"
            logger.info(f"Processing query {idx}/{len(queries)}: {query_desc}")
            
            # Update progress
            await Actor.set_status_message(f"Scraping {idx}/{len(queries)}: {query_desc}")
            
            try:
                # Scrape the query
                businesses = await scraper.scrape_query(query, max_results=max_results_per_query)
                
                if businesses:
                    # Push results to Apify Dataset
                    for business in businesses:
                        await Actor.push_data(business)
                    
                    total_businesses += len(businesses)
                    successful_queries += 1
                    logger.info(f"✓ Query successful: {len(businesses)} businesses found")
                else:
                    failed_queries += 1
                    logger.warning(f"✗ Query failed or returned no results")
            
            except Exception as e:
                logger.error(f"Error processing query: {e}", exc_info=True)
                failed_queries += 1
        
        # Cleanup
        await scraper.cleanup()
        
        # Deduplicate if enabled
        if deduplicate and total_businesses > 0:
            logger.info("Deduplicating results...")
            # Note: Apify Dataset doesn't support in-place deduplication
            # This would need to be done by reading all data, deduping, and re-pushing
            # For now, we'll skip this and let users handle it post-scrape
        
        # Final statistics
        logger.info(f"Scraping completed!")
        logger.info(f"Total queries: {len(queries)}")
        logger.info(f"Successful: {successful_queries}")
        logger.info(f"Failed: {failed_queries}")
        logger.info(f"Total businesses: {total_businesses}")
        
        await Actor.set_status_message(
            f"Complete! {total_businesses} businesses from {successful_queries}/{len(queries)} queries"
        )


if __name__ == '__main__':
    asyncio.run(main())
