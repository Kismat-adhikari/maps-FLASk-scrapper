"""
Google Maps Scraper Module
Handles browser automation and scraping using Playwright.
"""

import asyncio
import logging
from typing import Dict, List, Optional
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeout

from modules.proxy_manager import ProxyManager
from modules.data_extractor import DataExtractor


class GoogleMapsScraper:
    """Scrapes business data from Google Maps using Playwright - OPTIMIZED FOR APIFY."""
    
    def __init__(self, proxy_manager: ProxyManager = None, headless: bool = True, 
                 use_apify_proxy: bool = False, apify_proxy_config: Dict = None):
        """
        Initialize the Google Maps scraper.
        
        Args:
            proxy_manager: ProxyManager instance for proxy rotation (optional if using Apify proxy)
            headless: Whether to run browser in headless mode (default: True for Apify)
            use_apify_proxy: Whether to use Apify's proxy service
            apify_proxy_config: Apify proxy configuration dict
        """
        self.proxy_manager = proxy_manager
        self.headless = headless
        self.use_apify_proxy = use_apify_proxy
        self.apify_proxy_config = apify_proxy_config or {}
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.logger = logging.getLogger(__name__)
        
        # Timeouts (OPTIMIZED for Apify - fast but stable)
        self.request_timeout = 10000  # 10 seconds for element waits
        self.page_load_timeout = 15000  # 15 seconds for page loads
        
        # Resource blocking for speed
        self.blocked_resources = [
            'image', 'media', 'font', 'stylesheet',
            'analytics', 'beacon', 'ads', 'tracking'
        ]
    
    async def _block_resources(self, route):
        """Block heavy resources to speed up page loads."""
        request = route.request
        resource_type = request.resource_type
        url = request.url
        
        # Block images, fonts, media, stylesheets
        if resource_type in ['image', 'media', 'font', 'stylesheet']:
            await route.abort()
            return
        
        # Block analytics, ads, tracking
        blocked_domains = [
            'google-analytics.com', 'googletagmanager.com', 'doubleclick.net',
            'facebook.com', 'twitter.com', 'analytics', 'tracking', 'ads',
            'googlesyndication.com', 'adservice.google', 'googleadservices.com'
        ]
        
        if any(domain in url for domain in blocked_domains):
            await route.abort()
            return
        
        # Continue with other requests
        await route.continue_()
    
    async def initialize_browser(self, proxy: Dict = None) -> bool:
        """
        Initialize Playwright browser with proxy configuration.
        
        Args:
            proxy: Proxy dictionary with server, username, password (optional for Apify proxy)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.playwright:
                self.playwright = await async_playwright().start()
            
            # Close existing browser if any
            if self.browser:
                await self.close_browser()
            
            # Prepare launch options
            launch_options = {
                'headless': self.headless
            }
            
            # Add proxy configuration
            if self.use_apify_proxy:
                # Use Apify proxy
                self.logger.info("Launching browser with Apify proxy")
                # Get Apify proxy URL from config
                proxy_groups = self.apify_proxy_config.get('apifyProxyGroups', ['RESIDENTIAL'])
                proxy_country = self.apify_proxy_config.get('apifyProxyCountry', '')
                
                # Build Apify proxy URL
                import os
                apify_proxy_password = os.getenv('APIFY_PROXY_PASSWORD', '')
                if apify_proxy_password:
                    # Format: http://groups-{GROUPS},country-{COUNTRY}:{PASSWORD}@proxy.apify.com:8000
                    groups_str = '+'.join(proxy_groups)
                    proxy_url = f"http://groups-{groups_str}"
                    if proxy_country:
                        proxy_url += f",country-{proxy_country}"
                    proxy_url += f":{apify_proxy_password}@proxy.apify.com:8000"
                    
                    launch_options['proxy'] = {'server': proxy_url}
                    self.logger.info(f"Configured Apify proxy with groups: {groups_str}")
                else:
                    self.logger.warning("APIFY_PROXY_PASSWORD not found, proxy may not work")
            elif proxy:
                # Use custom proxy
                self.logger.info(f"Launching browser with custom proxy: {proxy.get('ip', 'unknown')}")
                launch_options['proxy'] = {
                    'server': proxy['server'],
                    'username': proxy['username'],
                    'password': proxy['password']
                }
            else:
                self.logger.info("Launching browser without proxy")
            
            # Launch browser
            self.browser = await self.playwright.chromium.launch(**launch_options)
            
            # Create new page with viewport settings
            self.page = await self.browser.new_page(
                viewport={'width': 1920, 'height': 1080}
            )
            
            # Set default timeout
            self.page.set_default_timeout(self.page_load_timeout)
            
            # Block heavy resources for speed (images, fonts, media, ads, analytics)
            await self.page.route("**/*", self._block_resources)
            
            self.logger.info("Browser initialized successfully with resource blocking")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize browser: {e}")
            return False
    
    async def search_google_maps(self, keyword: str, zip_code: str) -> bool:
        """
        Navigate to Google Maps and perform a search.
        
        Args:
            keyword: Search keyword (e.g., "restaurants")
            zip_code: Zip code to search in
            
        Returns:
            True if search successful, False otherwise
        """
        if not self.page:
            self.logger.error("Browser not initialized")
            return False
        
        try:
            search_query = f"{keyword} {zip_code}"
            self.logger.info(f"Searching Google Maps for: {search_query}")
            
            # Navigate to Google Maps with English language
            try:
                await self.page.goto('https://www.google.com/maps?hl=en', timeout=self.page_load_timeout)
            except PlaywrightTimeout:
                self.logger.error("Timeout loading Google Maps - possible network issue")
                raise
            except Exception as e:
                self.logger.error(f"Network error loading Google Maps: {e}")
                raise
            
            # Check for CAPTCHA
            if await self._detect_captcha():
                self.logger.warning("CAPTCHA detected - marking proxy as failed")
                return False
            
            # Wait for search box to be visible
            search_box = self.page.locator('input[id="searchboxinput"]')
            await search_box.wait_for(state='visible', timeout=self.request_timeout)
            
            # Enter search query
            await search_box.fill(search_query)
            
            # Click search button
            search_button = self.page.locator('button[id="searchbox-searchbutton"]')
            await search_button.click()
            
            # Wait for results to load (optimized)
            await asyncio.sleep(1.5)  # Reduced from 3 seconds
            
            # Check for CAPTCHA again after search
            if await self._detect_captcha():
                self.logger.warning("CAPTCHA detected after search - marking proxy as failed")
                return False
            
            # Wait for results container
            try:
                await self.page.wait_for_selector('[role="feed"]', timeout=self.request_timeout)
                self.logger.info("Search results loaded")
                return True
            except PlaywrightTimeout:
                self.logger.warning("Results container not found, but continuing")
                return True
            
        except PlaywrightTimeout as e:
            self.logger.error(f"Timeout during search: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error during search: {e}")
            return False
    
    async def _detect_captcha(self) -> bool:
        """
        Detect if a CAPTCHA is present on the page.
        
        Returns:
            True if CAPTCHA detected, False otherwise
        """
        try:
            # Check for common CAPTCHA indicators
            captcha_selectors = [
                'iframe[src*="recaptcha"]',
                'iframe[src*="captcha"]',
                '[id*="captcha"]',
                '[class*="captcha"]'
            ]
            
            for selector in captcha_selectors:
                captcha_element = await self.page.query_selector(selector)
                if captcha_element:
                    self.logger.warning(f"CAPTCHA detected with selector: {selector}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.debug(f"Error detecting CAPTCHA: {e}")
            return False
    
    async def extract_business_data(self, csv_callback=None) -> List[Dict]:
        """
        Extract business data from the current Google Maps results page.
        Extracts up to 20 businesses with comprehensive details.
        
        Args:
            csv_callback: Optional callback function to save each business incrementally
        
        Returns:
            List of business information dictionaries
        """
        if not self.page:
            self.logger.error("Browser not initialized")
            return []
        
        businesses = []
        
        try:
            # Wait for results to load (optimized)
            await asyncio.sleep(1.5)  # Reduced from 3 seconds
            
            # Scroll to load more results
            await self._scroll_results()
            
            # Find all business links in the results
            # Google Maps shows results as clickable links
            result_links = await self.page.locator('a[href*="/maps/place/"]').all()
            
            self.logger.info(f"Found {len(result_links)} business results")
            
            # Limit to 100 results (increased for broader coverage)
            max_results = 100
            result_links = result_links[:max_results]
            
            # Extract URLs first to avoid stale references
            business_urls = []
            for link in result_links:
                try:
                    href = await link.get_attribute('href')
                    if href and href.startswith('http'):
                        business_urls.append(href)
                except:
                    continue
            
            self.logger.info(f"Collected {len(business_urls)} business URLs to scrape")
            
            # Store the results page URL to return to
            results_url = self.page.url
            
            # Extract data from each business URL
            for idx, business_url in enumerate(business_urls, start=1):
                try:
                    self.logger.info(f"Extracting business {idx}/{len(business_urls)}...")
                    
                    # Navigate to business page with English language
                    if '?' in business_url:
                        business_url += '&hl=en'
                    else:
                        business_url += '?hl=en'
                    await self.page.goto(business_url, timeout=self.page_load_timeout, wait_until='domcontentloaded')
                    # No sleep - let Playwright handle it
                    
                    # Extract comprehensive business info
                    business_info = await DataExtractor.extract_detailed_business_info(self.page)
                    
                    if business_info.get('name'):
                        # Try to extract email from website if not found on Maps
                        if business_info.get('email') == 'Not given' and business_info.get('website') != 'Not given':
                            try:
                                email = await DataExtractor.extract_email_from_website(self.page, business_info['website'])
                                if email:
                                    business_info['email'] = email
                            except Exception as e:
                                self.logger.debug(f"Could not extract email from website: {e}")
                        
                        businesses.append(business_info)
                        self.logger.info(f"Extracted: {business_info.get('name')}")
                        
                        # Call callback immediately for real-time updates
                        if csv_callback:
                            try:
                                csv_callback(business_info)
                            except Exception as e:
                                self.logger.warning(f"Error in callback: {e}")
                    
                    # Navigate back to results page
                    await self.page.goto(results_url, timeout=self.page_load_timeout, wait_until='domcontentloaded')
                    await asyncio.sleep(0.5)  # Optimized from 1 second
                    
                except Exception as e:
                    self.logger.warning(f"Error extracting business {idx}: {e}")
                    # Try to go back to results page
                    try:
                        await self.page.goto(results_url, timeout=self.page_load_timeout, wait_until='domcontentloaded')
                        await asyncio.sleep(0.5)  # Optimized from 1 second
                    except:
                        pass
                    continue
            
            self.logger.info(f"Successfully extracted {len(businesses)} businesses")
            
        except Exception as e:
            self.logger.error(f"Error extracting business data: {e}")
        
        return businesses
    
    async def _scroll_results(self):
        """Scroll the results panel to load more businesses - SMART SCROLLING."""
        try:
            # Find the scrollable results container
            results_panel = self.page.locator('[role="feed"]').first
            
            # Smart scrolling - keep scrolling until no new results load
            previous_count = 0
            no_change_count = 0
            max_scrolls = 50  # Safety limit
            
            for i in range(max_scrolls):
                # Count current results
                current_count = await self.page.locator('a[href*="/maps/place/"]').count()
                
                # Check if we got new results
                if current_count == previous_count:
                    no_change_count += 1
                    # If no new results for 3 scrolls, we've reached the end
                    if no_change_count >= 3:
                        self.logger.info(f"Reached end of results at {current_count} businesses after {i+1} scrolls")
                        break
                else:
                    no_change_count = 0  # Reset counter
                    self.logger.debug(f"Scroll {i+1}: Found {current_count} results (+{current_count - previous_count})")
                
                previous_count = current_count
                
                # Scroll down
                await results_panel.evaluate('el => el.scrollTop = el.scrollHeight')
                await asyncio.sleep(0.2)  # Minimal wait for new results
                
        except Exception as e:
            self.logger.debug(f"Could not scroll results: {e}")
    
    async def _scrape_single_business(self, business_url: str, index: int, total: int) -> Optional[Dict]:
        """
        Scrape a single business in a new tab/page - OPTIMIZED for speed and reliability.
        
        Args:
            business_url: URL of the business to scrape
            index: Current business index
            total: Total number of businesses
            
        Returns:
            Business info dictionary or None if failed
        """
        page = None
        try:
            self.logger.info(f"[Tab {index}/{total}] Opening tab...")
            
            # Create new page (tab) in the same browser
            page = await self.browser.new_page(viewport={'width': 1920, 'height': 1080})
            page.set_default_timeout(10000)  # 10s for element waits (ultra-fast)
            
            # Block heavy resources on this tab too
            await page.route("**/*", self._block_resources)
            
            # Add English language parameter to URL
            if '?' in business_url:
                business_url += '&hl=en'
            else:
                business_url += '?hl=en'
            
            # Navigate to business page - fast load
            await page.goto(business_url, timeout=60000, wait_until='domcontentloaded')
            
            # Quick wait for critical content to render
            await asyncio.sleep(1.5)
            
            # Quick wait for business name
            try:
                await page.wait_for_selector('h1.DUwDvf, h1.fontHeadlineLarge, h1', timeout=5000, state='visible')
            except:
                # If name not found quickly, skip the wait
                pass
            
            # Extract business info (NO email extraction here - done in parallel later!)
            business_info = await DataExtractor.extract_detailed_business_info(page)
            
            # Validate we got actual data
            if business_info.get('name') and business_info.get('name') != 'Not given':
                self.logger.info(f"[Tab {index}/{total}] ✓ {business_info.get('name')}")
                return business_info
            else:
                self.logger.warning(f"[Tab {index}/{total}] ✗ No name extracted from {business_url}")
                # Log page title for debugging
                try:
                    title = await page.title()
                    self.logger.debug(f"[Tab {index}/{total}] Page title: {title}")
                except:
                    pass
                return None
                
        except Exception as e:
            self.logger.warning(f"[Tab {index}/{total}] ✗ {str(e)[:50]}")
            return None
        finally:
            # Always close the tab quickly
            if page:
                try:
                    await page.close()
                except:
                    pass
    
    async def extract_business_data_parallel(self, csv_callback=None, max_concurrent=3, max_results=60) -> List[Dict]:
        """
        Extract business data using parallel tabs for faster scraping.
        NOW WITH FAST PARALLEL EMAIL EXTRACTION!
        
        Args:
            csv_callback: Optional callback function to save each business incrementally
            max_concurrent: Maximum number of tabs to open simultaneously
        
        Returns:
            List of business information dictionaries
        """
        if not self.page:
            self.logger.error("Browser not initialized")
            return []
        
        businesses = []
        
        try:
            # No wait - let Playwright handle it
            
            # Scroll to load more results (optimized)
            await self._scroll_results()
            
            # Find all business links
            result_links = await self.page.locator('a[href*="/maps/place/"]').all()
            self.logger.info(f"Found {len(result_links)} business results")
            
            # Extract URLs
            business_urls = []
            for link in result_links:
                try:
                    href = await link.get_attribute('href')
                    if href and href.startswith('http'):
                        business_urls.append(href)
                        # Stop when we reach max_results
                        if len(business_urls) >= max_results:
                            break
                except:
                    continue
            
            self.logger.info(f"Collected {len(business_urls)} business URLs (limited to {max_results})")
            self.logger.info(f"🚀 PARALLEL scraping: {max_concurrent} tabs at once (optimized for Apify)")
            
            # Process businesses in batches
            for i in range(0, len(business_urls), max_concurrent):
                batch = business_urls[i:i + max_concurrent]
                batch_num = (i // max_concurrent) + 1
                total_batches = (len(business_urls) + max_concurrent - 1) // max_concurrent
                
                self.logger.info(f"📦 Batch {batch_num}/{total_batches} ({len(batch)} tabs)")
                
                # Create tasks for parallel scraping (NO STAGGER - maximum speed)
                tasks = []
                for idx, url in enumerate(batch):
                    tasks.append(self._scrape_single_business(url, i + idx + 1, len(business_urls)))
                
                # Run all tasks in parallel
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results immediately
                for result in results:
                    if isinstance(result, dict) and result.get('name'):
                        businesses.append(result)
            
            self.logger.info(f"✅ Google Maps scraping complete! Extracted {len(businesses)} businesses")
            
            # NOW: Extract emails in parallel using FAST HTTP requests (not Playwright!)
            from config import Config
            if Config.EXTRACT_EMAILS_FROM_WEBSITES and businesses:
                self.logger.info(f"🚀 Starting parallel email extraction (ORIGINAL PROVEN SETTINGS)...")
                
                # Get websites that need email extraction
                websites_to_check = []
                business_indices = []
                for idx, business in enumerate(businesses):
                    if business.get('email') == 'Not given' and business.get('website') != 'Not given':
                        websites_to_check.append(business['website'])
                        business_indices.append(idx)
                
                if websites_to_check:
                    self.logger.info(f"Checking {len(websites_to_check)} websites for emails...")
                    
                    # Use ORIGINAL PROVEN SETTINGS for email extraction
                    from modules.email_extractor import ParallelEmailExtractor, FastEmailExtractor
                    from config import Config
                    max_concurrent = getattr(Config, 'EMAIL_MAX_CONCURRENT', 5)
                    timeout = getattr(Config, 'EMAIL_EXTRACTION_TIMEOUT', 6)
                    max_html_size = getattr(Config, 'EMAIL_MAX_HTML_SIZE', 500 * 1024)
                    
                    # Configure extractor with HTML size limit
                    email_extractor = ParallelEmailExtractor(max_concurrent=max_concurrent, timeout=timeout)
                    email_extractor.extractor.max_html_size = max_html_size
                    emails = await email_extractor.extract_emails_parallel(websites_to_check)
                    
                    # Update businesses with found emails
                    for idx, email in zip(business_indices, emails):
                        if email:
                            businesses[idx]['email'] = email
                    
                    emails_found = sum(1 for e in emails if e)
                    self.logger.info(f"✅ Email extraction complete: {emails_found}/{len(websites_to_check)} found")
            
            # Call callback for all businesses (after email extraction)
            if csv_callback:
                for business in businesses:
                    try:
                        csv_callback(business)
                    except Exception as e:
                        self.logger.warning(f"Error in callback: {e}")
            
        except Exception as e:
            self.logger.error(f"Error in parallel scraping: {e}")
        
        return businesses
    
    async def close_browser(self) -> None:
        """Close the browser and cleanup resources."""
        try:
            if self.page:
                # Don't navigate anywhere, just close
                try:
                    await self.page.close()
                except:
                    pass
                self.page = None
            
            if self.browser:
                try:
                    await self.browser.close()
                except:
                    pass
                self.browser = None
            
            self.logger.info("Browser closed")
            
        except Exception as e:
            self.logger.error(f"Error closing browser: {e}")
    
    async def scrape_query(self, query: Dict, csv_callback=None, retry_count: int = 0, max_retries: int = 3, max_results: int = 60) -> List[Dict]:
        """
        Main entry point to scrape a single query with retry logic.
        Coordinates the entire scraping flow.
        
        Args:
            query: Dictionary with 'keyword', 'zip_code', and optional 'url'
            csv_callback: Optional callback to save each business incrementally
            retry_count: Current retry attempt (internal use)
            max_retries: Maximum number of retries
            max_results: Maximum number of businesses to scrape (default: 60)
            
        Returns:
            List of business dictionaries
        """
        keyword = query.get('keyword', '')
        zip_code = query.get('zip_code', '')
        url = query.get('url', '')
        
        # Check if URL mode
        if url:
            return await self.scrape_url(url, csv_callback, retry_count, max_retries)
        
        if not keyword or not zip_code:
            self.logger.error("Missing keyword or zip_code in query")
            return []
        
        self.logger.info(f"Starting scrape for: {keyword} in {zip_code} (attempt {retry_count + 1}/{max_retries + 1})")
        
        # Get current proxy (if using custom proxies)
        proxy = None
        if self.proxy_manager:
            proxy = self.proxy_manager.get_next_proxy()
            if not proxy:
                self.logger.error("No proxy available")
                return []
        
        try:
            # Initialize browser ONLY if not already initialized (reuse browser)
            if not self.browser or not self.page:
                self.logger.info("Initializing browser for first time...")
                success = await self.initialize_browser(proxy)
                if not success:
                    self.logger.error("Failed to initialize browser")
                    if self.proxy_manager and proxy:
                        self.proxy_manager.mark_failure(proxy)
                    
                    # Retry with next proxy if retries available
                    if retry_count < max_retries:
                        self.logger.info(f"Retrying with next proxy...")
                        return await self.scrape_query(query, csv_callback, retry_count + 1, max_retries, max_results)
                    return []
            else:
                self.logger.info("Reusing existing browser instance")
            
            # Increment request counter (if using custom proxies)
            if self.proxy_manager:
                self.proxy_manager.increment_counter()
            
            # Perform search
            search_success = await self.search_google_maps(keyword, zip_code)
            if not search_success:
                self.logger.error("Search failed - CAPTCHA or network error")
                if self.proxy_manager and proxy:
                    self.proxy_manager.mark_failure(proxy)
                
                # Retry with next proxy if retries available
                if retry_count < max_retries:
                    self.logger.info(f"Retrying with next proxy...")
                    await self.close_browser()
                    return await self.scrape_query(query, csv_callback, retry_count + 1, max_retries, max_results)
                return []
            
            # Extract business data with incremental saving (PARALLEL MODE)
            from config import Config
            max_concurrent = getattr(Config, 'PARALLEL_TABS', 5)
            businesses = await self.extract_business_data_parallel(csv_callback, max_concurrent, max_results)
            
            # Add query context to each business
            for business in businesses:
                business['keyword'] = keyword
                business['zip_code'] = zip_code
            
            self.logger.info(f"Scrape completed: {len(businesses)} businesses found")
            
            return businesses
            
        except Exception as e:
            self.logger.error(f"Unexpected error during scrape: {e}")
            if self.proxy_manager and proxy:
                self.proxy_manager.mark_failure(proxy)
            
            # Attempt to restart browser on crash
            try:
                await self.close_browser()
            except:
                pass
            
            # Retry if retries available
            if retry_count < max_retries:
                self.logger.info(f"Retrying after error...")
                return await self.scrape_query(query, csv_callback, retry_count + 1, max_retries)
            
            return []
    
    async def scrape_url(self, url: str, csv_callback=None, retry_count: int = 0, max_retries: int = 3) -> List[Dict]:
        """
        Scrape from a Google Maps URL (search URL or business URL).
        
        Args:
            url: Google Maps URL
            csv_callback: Optional callback to save each business incrementally
            retry_count: Current retry attempt
            max_retries: Maximum number of retries
            
        Returns:
            List of business dictionaries
        """
        self.logger.info(f"Starting scrape from URL: {url} (attempt {retry_count + 1}/{max_retries + 1})")
        
        # Get current proxy (if using custom proxies)
        proxy = None
        if self.proxy_manager:
            proxy = self.proxy_manager.get_next_proxy()
            if not proxy:
                self.logger.error("No proxy available")
                return []
        
        try:
            # Initialize browser with proxy (or Apify proxy)
            success = await self.initialize_browser(proxy)
            if not success:
                self.logger.error("Failed to initialize browser")
                if self.proxy_manager and proxy:
                    self.proxy_manager.mark_failure(proxy)
                
                if retry_count < max_retries:
                    self.logger.info(f"Retrying with next proxy...")
                    return await self.scrape_url(url, csv_callback, retry_count + 1, max_retries)
                return []
            
            # Increment request counter (if using custom proxies)
            if self.proxy_manager:
                self.proxy_manager.increment_counter()
            
            # Navigate to URL with English language
            try:
                if '?' in url:
                    url += '&hl=en'
                else:
                    url += '?hl=en'
                await self.page.goto(url, timeout=self.page_load_timeout)
                await asyncio.sleep(1.5)  # Optimized from 3 seconds
            except Exception as e:
                self.logger.error(f"Failed to load URL: {e}")
                if self.proxy_manager and proxy:
                    self.proxy_manager.mark_failure(proxy)
                
                if retry_count < max_retries:
                    self.logger.info(f"Retrying with next proxy...")
                    await self.close_browser()
                    return await self.scrape_url(url, csv_callback, retry_count + 1, max_retries)
                return []
            
            # Check for CAPTCHA
            if await self._detect_captcha():
                self.logger.warning("CAPTCHA detected - marking proxy as failed")
                if self.proxy_manager and proxy:
                    self.proxy_manager.mark_failure(proxy)
                
                if retry_count < max_retries:
                    self.logger.info(f"Retrying with next proxy...")
                    await self.close_browser()
                    return await self.scrape_url(url, csv_callback, retry_count + 1, max_retries)
                return []
            
            # Determine if it's a search URL or business URL
            if '/maps/place/' in url:
                # Single business URL
                self.logger.info("Detected business URL - extracting single business")
                business_info = await DataExtractor.extract_detailed_business_info(self.page)
                
                if business_info.get('name'):
                    # Try to extract email from website
                    if business_info.get('email') == 'Not given' and business_info.get('website') != 'Not given':
                        try:
                            email = await DataExtractor.extract_email_from_website(self.page, business_info['website'])
                            if email:
                                business_info['email'] = email
                        except Exception as e:
                            self.logger.debug(f"Could not extract email from website: {e}")
                    
                    # Save incrementally if callback provided
                    if csv_callback:
                        try:
                            csv_callback(business_info)
                        except Exception as e:
                            self.logger.warning(f"Error in CSV callback: {e}")
                    
                    self.logger.info(f"Scrape completed: 1 business found")
                    return [business_info]
                else:
                    self.logger.warning("Could not extract business information")
                    return []
            else:
                # Search URL - extract multiple businesses
                self.logger.info("Detected search URL - extracting multiple businesses")
                businesses = await self.extract_business_data(csv_callback)
                self.logger.info(f"Scrape completed: {len(businesses)} businesses found")
                return businesses
            
        except Exception as e:
            self.logger.error(f"Unexpected error during URL scrape: {e}")
            if self.proxy_manager and proxy:
                self.proxy_manager.mark_failure(proxy)
            
            try:
                await self.close_browser()
            except:
                pass
            
            if retry_count < max_retries:
                self.logger.info(f"Retrying after error...")
                return await self.scrape_url(url, csv_callback, retry_count + 1, max_retries)
            
            return []
    
    async def cleanup(self) -> None:
        """Cleanup all resources."""
        try:
            await self.close_browser()
        except:
            pass
        
        try:
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
        except:
            pass
