"""
Fast Email Extractor Module
Uses HTTP requests instead of Playwright for 10x faster email extraction.
"""

import re
import asyncio
import logging
from typing import Optional, List, Set
import aiohttp
from urllib.parse import urljoin, urlparse


class FastEmailExtractor:
    """Fast email extraction using HTTP requests instead of browser automation."""
    
    def __init__(self, timeout: int = 6, max_html_size: int = 500_000):
        """
        Initialize the email extractor with ORIGINAL PROVEN SETTINGS.
        
        Args:
            timeout: Maximum seconds to wait for website response (6s - proven)
            max_html_size: Maximum HTML size to download (500KB - proven)
        """
        self.timeout = timeout
        self.max_html_size = max_html_size
        self.logger = logging.getLogger(__name__)
        
        # Cache for previously scraped websites (reuse results)
        self.email_cache = {}
        
        # Email regex pattern
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        # Excluded domains (fake/spam emails)
        self.excluded_domains = {
            'example.com', 'domain.com', 'email.com', 'test.com',
            'wix.com', 'wordpress.com', 'sentry.io', 'sentry-next.wixpress.com',
            'google.com', 'facebook.com', 'twitter.com', 'instagram.com',
            'squarespace.com', 'linkedin.com', 'youtube.com', 'pinterest.com',
            'user@domain.com', 'admin@example.com', 'info@example.com'
        }
        
        # Image extensions to exclude
        self.image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico', '.bmp')
        
        # Common contact page paths
        self.contact_paths = ['/contact', '/contact-us', '/about', '/about-us']
    
    async def extract_email_from_website(self, website_url: str, session: aiohttp.ClientSession = None) -> Optional[str]:
        """
        Extract email from website using ULTRA-FAST HTTP requests with caching.
        
        Args:
            website_url: URL of the business website
            session: Optional aiohttp session (for connection pooling)
            
        Returns:
            Email address or None
        """
        if not website_url or website_url == 'Not given':
            return None
        
        # Check if email extraction is enabled
        from config import Config
        if not Config.EXTRACT_EMAILS_FROM_WEBSITES:
            return None
        
        # Check cache first (SPEED OPTIMIZATION)
        if website_url in self.email_cache:
            cached_email = self.email_cache[website_url]
            if cached_email:
                self.logger.debug(f"Cache hit: {website_url} → {cached_email}")
            return cached_email
        
        self.logger.debug(f"Fast check: {website_url}")
        
        # Create session if not provided
        close_session = False
        if session is None:
            session = aiohttp.ClientSession()
            close_session = True
        
        try:
            # Try homepage first
            email = await self._extract_from_url(website_url, session)
            if email:
                self.email_cache[website_url] = email  # Cache result
                return email
            
            # Try /contact and /about pages (ORIGINAL PROVEN APPROACH)
            base_url = website_url.rstrip('/')
            for path in ['/contact', '/about']:
                contact_url = base_url + path
                email = await self._extract_from_url(contact_url, session)
                if email:
                    self.email_cache[website_url] = email
                    return email
            
            # Cache result (even if None to avoid re-checking)
            self.email_cache[website_url] = email
            return email
            
        except Exception as e:
            self.logger.debug(f"Error: {website_url}: {e}")
            self.email_cache[website_url] = None  # Cache failure
            return None
        finally:
            if close_session:
                await session.close()
    
    async def _extract_from_url(self, url: str, session: aiohttp.ClientSession) -> Optional[str]:
        """
        Extract email from a single URL using ULTRA-FAST HTTP request.
        
        Args:
            url: URL to check
            session: aiohttp session
            
        Returns:
            Email address or None
        """
        try:
            # Minimal headers for speed
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html',
            }
            
            # ULTRA-FAST HTTP request with aggressive timeout
            async with session.get(
                url,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout, connect=2),  # 2s connect timeout
                allow_redirects=True,
                max_redirects=2  # Reduced from 3
            ) as response:
                
                # Quick status checks
                if response.status in (403, 503, 429):  # Blocked/rate limited
                    return None
                
                if response.status != 200:
                    return None
                
                # Check content type quickly
                content_type = response.headers.get('Content-Type', '')
                if 'text/html' not in content_type:
                    return None
                
                # Read HTML with size limit for accuracy
                html = await response.text()
                if len(html) > self.max_html_size:
                    html = html[:self.max_html_size]
                
                # Quick Cloudflare check (first 1000 chars only)
                html_start = html[:1000].lower()
                if 'cloudflare' in html_start and 'challenge' in html_start:
                    return None
                
                # Extract emails (optimized)
                email = self._extract_email_from_html(html)
                if email:
                    self.logger.info(f"✓ {email}")
                    return email
                
                return None
                
        except asyncio.TimeoutError:
            return None
        except aiohttp.ClientError:
            return None
        except Exception:
            return None
    
    def _extract_email_from_html(self, html: str) -> Optional[str]:
        """
        Extract email from HTML content using HIGH ACCURACY multiple methods.
        
        Args:
            html: HTML content (up to max_html_size)
            
        Returns:
            Email address or None
        """
        emails_found: Set[str] = set()
        
        # Method 1: Find mailto: links (FASTEST and most reliable)
        mailto_pattern = r'mailto:([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})'
        mailto_emails = re.findall(mailto_pattern, html, re.IGNORECASE)
        if mailto_emails:
            emails_found.update(mailto_emails)
            # If we found mailto, return immediately (SPEED OPTIMIZATION)
            valid_emails = self._filter_emails(list(emails_found))
            if valid_emails:
                return valid_emails[0]
        
        # Method 2: Find emails in full text (comprehensive)
        text_emails = re.findall(self.email_pattern, html, re.IGNORECASE)
        emails_found.update(text_emails)
        
        # Method 3: Quick header/footer check (only if no emails found yet)
        if not emails_found:
            # Quick regex for header/footer (no full parsing)
            header_match = re.search(r'<header[^>]*>(.*?)</header>', html, re.IGNORECASE | re.DOTALL)
            if header_match:
                header_emails = re.findall(self.email_pattern, header_match.group(1), re.IGNORECASE)
                emails_found.update(header_emails)
            
            if not emails_found:  # Still nothing? Try footer
                footer_match = re.search(r'<footer[^>]*>(.*?)</footer>', html, re.IGNORECASE | re.DOTALL)
                if footer_match:
                    footer_emails = re.findall(self.email_pattern, footer_match.group(1), re.IGNORECASE)
                    emails_found.update(footer_emails)
        
        # Filter and validate emails
        valid_emails = self._filter_emails(list(emails_found))
        
        # Return first valid email
        if valid_emails:
            return valid_emails[0]
        
        return None
    
    def _filter_emails(self, emails: List[str]) -> List[str]:
        """
        Filter out fake/spam emails and return valid ones.
        
        Args:
            emails: List of potential email addresses
            
        Returns:
            List of valid email addresses
        """
        valid_emails = []
        
        for email in emails:
            email_lower = email.lower()
            
            # Skip image files
            if email_lower.endswith(self.image_extensions):
                continue
            
            # Skip excluded domains
            if any(domain in email_lower for domain in self.excluded_domains):
                continue
            
            # Validate format
            if '@' not in email or '.' not in email.split('@')[1]:
                continue
            
            # Skip if domain is too short
            domain = email.split('@')[1]
            if len(domain) < 4:
                continue
            
            # Valid email found
            if email not in valid_emails:
                valid_emails.append(email)
        
        return valid_emails


class ParallelEmailExtractor:
    """Manages parallel email extraction with ORIGINAL PROVEN SETTINGS."""
    
    def __init__(self, max_concurrent: int = 5, timeout: int = 6):
        """
        Initialize parallel email extractor with ORIGINAL PROVEN SETTINGS.
        
        Args:
            max_concurrent: Maximum number of concurrent requests (5 - proven)
            timeout: Timeout per website in seconds (6s - proven)
        """
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.extractor = FastEmailExtractor(timeout=timeout)
        self.logger = logging.getLogger(__name__)
    
    async def extract_emails_parallel(self, websites: List[str]) -> List[Optional[str]]:
        """
        Extract emails from multiple websites in ULTRA-FAST parallel mode.
        
        Args:
            websites: List of website URLs
            
        Returns:
            List of email addresses (None if not found)
        """
        if not websites:
            return []
        
        self.logger.info(f"⚡ Email extraction (ORIGINAL SETTINGS): {len(websites)} sites, {self.max_concurrent} at once")
        
        # Aggressive connection pooling for maximum speed
        connector = aiohttp.TCPConnector(
            limit=self.max_concurrent * 2,  # Higher limit
            limit_per_host=3,  # Allow more per host
            ttl_dns_cache=300  # Cache DNS for 5 minutes
        )
        
        async with aiohttp.ClientSession(connector=connector) as session:
            
            # Create semaphore to limit concurrency
            semaphore = asyncio.Semaphore(self.max_concurrent)
            
            async def extract_with_limit(website: str) -> Optional[str]:
                async with semaphore:
                    return await self.extractor.extract_email_from_website(website, session)
            
            # Run all extractions in parallel (NO STAGGER - maximum speed)
            tasks = [extract_with_limit(website) for website in websites]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Convert exceptions to None
            emails = []
            for result in results:
                if isinstance(result, Exception):
                    emails.append(None)
                else:
                    emails.append(result)
            
            found_count = sum(1 for email in emails if email)
            self.logger.info(f"✅ Complete: {found_count}/{len(websites)} found")
            
            return emails
