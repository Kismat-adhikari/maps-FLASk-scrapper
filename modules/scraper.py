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
    """Scrapes business data from Google Maps using Playwright."""
    
    def __init__(self, proxy_manager: ProxyManager, headless: bool = False):
        """
        Initialize the Google Maps scraper.
        
        Args:
            proxy_manager: ProxyManager instance for proxy rotation
            headless: Whether to run browser in headless mode (default: False for visible)
        """
        self.proxy_manager = proxy_manager
        self.headless = headless
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.logger = logging.getLogger(__name__)
        
        # Timeouts
        self.request_timeout = 30000  # 30 seconds
        self.page_load_timeout = 60000  # 60 seconds
    
    async def initialize_browser(self, proxy: Dict) -> bool:
        """
        Initialize Playwright browser with proxy configuration.
        
        Args:
            proxy: Proxy dictionary with server, username, password
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.playwright:
                self.playwright = await async_playwright().start()
            
            # Close existing browser if any
            if self.browser:
                await self.close_browser()
            
            self.logger.info(f"Launching browser with proxy: {proxy.get('ip', 'unknown')}")
            
            # Launch browser with proxy
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                proxy={
                    'server': proxy['server'],
                    'username': proxy['username'],
                    'password': proxy['password']
                }
            )
            
            # Create new page with viewport settings
            self.page = await self.browser.new_page(
                viewport={'width': 1920, 'height': 1080}
            )
            
            # Set default timeout
            self.page.set_default_timeout(self.page_load_timeout)
            
            self.logger.info("Browser initialized successfully")
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
            
            # Navigate to Google Maps
            try:
                await self.page.goto('https://www.google.com/maps', timeout=self.page_load_timeout)
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
            
            # Wait for results to load
            await asyncio.sleep(3)  # Give time for results to populate
            
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
            # Wait for results to load
            await asyncio.sleep(3)
            
            # Scroll to load more results
            await self._scroll_results()
            
            # Find all business links in the results
            # Google Maps shows results as clickable links
            result_links = await self.page.locator('a[href*="/maps/place/"]').all()
            
            self.logger.info(f"Found {len(result_links)} business results")
            
            # Limit to 40 results
            max_results = 40
            result_links = result_links[:max_results]
            
            # Store the results page URL to return to
            results_url = self.page.url
            
            # Extract data from each business
            for idx, link in enumerate(result_links, start=1):
                try:
                    self.logger.info(f"Extracting business {idx}/{len(result_links)}...")
                    
                    # Get the href before clicking
                    business_url = await link.get_attribute('href')
                    
                    # Navigate to business page (avoid about:blank)
                    if business_url and business_url.startswith('http'):
                        await self.page.goto(business_url, timeout=self.page_load_timeout, wait_until='domcontentloaded')
                        await asyncio.sleep(2)  # Wait for details to load
                    else:
                        # Fallback to clicking
                        await link.click()
                        await asyncio.sleep(2)
                    
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
                        
                        # Save incrementally if callback provided
                        if csv_callback:
                            try:
                                csv_callback(business_info)
                            except Exception as e:
                                self.logger.warning(f"Error in CSV callback: {e}")
                    
                    # Navigate back to results page (avoid about:blank)
                    if results_url and results_url.startswith('http'):
                        await self.page.goto(results_url, timeout=self.page_load_timeout, wait_until='domcontentloaded')
                        await asyncio.sleep(1)
                    
                    # Re-find the links after navigation
                    result_links = await self.page.locator('a[href*="/maps/place/"]').all()
                    result_links = result_links[:max_results]
                    
                except Exception as e:
                    self.logger.warning(f"Error extracting business {idx}: {e}")
                    # Try to go back to results page
                    try:
                        if results_url and results_url.startswith('http'):
                            await self.page.goto(results_url, timeout=self.page_load_timeout, wait_until='domcontentloaded')
                            await asyncio.sleep(1)
                        # Re-find the links
                        result_links = await self.page.locator('a[href*="/maps/place/"]').all()
                        result_links = result_links[:max_results]
                    except:
                        pass
                    continue
            
            # Stay on results page at the end (don't navigate to about:blank)
            try:
                if results_url and results_url.startswith('http'):
                    await self.page.goto(results_url, timeout=self.page_load_timeout, wait_until='domcontentloaded')
            except:
                pass
            
            self.logger.info(f"Successfully extracted {len(businesses)} businesses")
            
        except Exception as e:
            self.logger.error(f"Error extracting business data: {e}")
        
        return businesses
    
    async def _scroll_results(self):
        """Scroll the results panel to load more businesses."""
        try:
            # Find the scrollable results container
            results_panel = self.page.locator('[role="feed"]').first
            
            # Scroll down multiple times to load more results
            for _ in range(3):
                await results_panel.evaluate('el => el.scrollTop = el.scrollHeight')
                await asyncio.sleep(1)
                
        except Exception as e:
            self.logger.debug(f"Could not scroll results: {e}")
    
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
    
    async def scrape_query(self, query: Dict, csv_callback=None, retry_count: int = 0, max_retries: int = 3) -> List[Dict]:
        """
        Main entry point to scrape a single query with retry logic.
        Coordinates the entire scraping flow.
        
        Args:
            query: Dictionary with 'keyword', 'zip_code', and optional 'url'
            csv_callback: Optional callback to save each business incrementally
            retry_count: Current retry attempt (internal use)
            max_retries: Maximum number of retries
            
        Returns:
            List of business dictionaries
        """
        keyword = query.get('keyword', '')
        zip_code = query.get('zip_code', '')
        
        if not keyword or not zip_code:
            self.logger.error("Missing keyword or zip_code in query")
            return []
        
        self.logger.info(f"Starting scrape for: {keyword} in {zip_code} (attempt {retry_count + 1}/{max_retries + 1})")
        
        # Get current proxy
        proxy = self.proxy_manager.get_next_proxy()
        if not proxy:
            self.logger.error("No proxy available")
            return []
        
        try:
            # Initialize browser with proxy
            success = await self.initialize_browser(proxy)
            if not success:
                self.logger.error("Failed to initialize browser")
                self.proxy_manager.mark_failure(proxy)
                
                # Retry with next proxy if retries available
                if retry_count < max_retries:
                    self.logger.info(f"Retrying with next proxy...")
                    return await self.scrape_query(query, csv_callback, retry_count + 1, max_retries)
                return []
            
            # Increment request counter
            self.proxy_manager.increment_counter()
            
            # Perform search
            search_success = await self.search_google_maps(keyword, zip_code)
            if not search_success:
                self.logger.error("Search failed - CAPTCHA or network error")
                self.proxy_manager.mark_failure(proxy)
                
                # Retry with next proxy if retries available
                if retry_count < max_retries:
                    self.logger.info(f"Retrying with next proxy...")
                    await self.close_browser()
                    return await self.scrape_query(query, csv_callback, retry_count + 1, max_retries)
                return []
            
            # Extract business data with incremental saving
            businesses = await self.extract_business_data(csv_callback)
            
            # Add query context to each business
            for business in businesses:
                business['keyword'] = keyword
                business['zip_code'] = zip_code
            
            self.logger.info(f"Scrape completed: {len(businesses)} businesses found")
            
            return businesses
            
        except Exception as e:
            self.logger.error(f"Unexpected error during scrape: {e}")
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
