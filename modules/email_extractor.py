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
        Initialize the fast email extractor.
        
        Args:
            timeout: Maximum seconds to wait for website response
            max_html_size: Maximum HTML size to download (bytes)
        """
        self.timeout = timeout
        self.max_html_size = max_html_size
        self.logger = logging.getLogger(__name__)
        
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
        Extract email from website using fast HTTP requests.
        
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
        
        self.logger.info(f"Fast email check: {website_url}")
        
        # Create session if not provided
        close_session = False
        if session is None:
            session = aiohttp.ClientSession()
            close_session = True
        
        try:
            # Try homepage first
            email = await self._extract_from_url(website_url, session)
            if email:
                return email
            
            # Try common contact pages
            base_url = website_url.rstrip('/')
            for path in self.contact_paths:
                contact_url = base_url + path
                email = await self._extract_from_url(contact_url, session)
                if email:
                    return email
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Error extracting email from {website_url}: {e}")
            return None
        finally:
            if close_session:
                await session.close()
    
    async def _extract_from_url(self, url: str, session: aiohttp.ClientSession) -> Optional[str]:
        """
        Extract email from a single URL using fast HTTP request.
        
        Args:
            url: URL to check
            session: aiohttp session
            
        Returns:
            Email address or None
        """
        try:
            # Set headers to look like a real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            # Make fast HTTP request with timeout
            async with session.get(
                url,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                allow_redirects=True,
                max_redirects=3
            ) as response:
                
                # Check if response is HTML
                content_type = response.headers.get('Content-Type', '').lower()
                if 'text/html' not in content_type:
                    return None
                
                # Check for Cloudflare/CAPTCHA
                if response.status == 403 or response.status == 503:
                    self.logger.debug(f"Blocked/CAPTCHA detected: {url}")
                    return None
                
                if response.status != 200:
                    return None
                
                # Read only first chunk of HTML (fast!)
                html = await response.text()
                
                # Limit HTML size for speed
                if len(html) > self.max_html_size:
                    html = html[:self.max_html_size]
                
                # Quick check for Cloudflare challenge
                if 'cloudflare' in html.lower() and 'challenge' in html.lower():
                    self.logger.debug(f"Cloudflare challenge detected: {url}")
                    return None
                
                # Extract emails
                email = self._extract_email_from_html(html)
                if email:
                    self.logger.info(f"✓ Found email: {email} from {url}")
                    return email
                
                return None
                
        except asyncio.TimeoutError:
            self.logger.debug(f"Timeout: {url}")
            return None
        except aiohttp.ClientError as e:
            self.logger.debug(f"Request error for {url}: {e}")
            return None
        except Exception as e:
            self.logger.debug(f"Error checking {url}: {e}")
            return None
    
    def _extract_email_from_html(self, html: str) -> Optional[str]:
        """
        Extract email from HTML content using multiple methods.
        
        Args:
            html: HTML content
            
        Returns:
            Email address or None
        """
        emails_found: Set[str] = set()
        
        # Method 1: Find mailto: links (most reliable)
        mailto_pattern = r'mailto:([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})'
        mailto_emails = re.findall(mailto_pattern, html, re.IGNORECASE)
        emails_found.update(mailto_emails)
        
        # Method 2: Find emails in text
        text_emails = re.findall(self.email_pattern, html, re.IGNORECASE)
        emails_found.update(text_emails)
        
        # Method 3: Look in common sections (header, footer, contact)
        # Extract header/footer sections for focused search
        header_match = re.search(r'<header[^>]*>(.*?)</header>', html, re.IGNORECASE | re.DOTALL)
        if header_match:
            header_emails = re.findall(self.email_pattern, header_match.group(1), re.IGNORECASE)
            emails_found.update(header_emails)
        
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
    """Manages parallel email extraction for multiple websites."""
    
    def __init__(self, max_concurrent: int = 5, timeout: int = 6):
        """
        Initialize parallel email extractor.
        
        Args:
            max_concurrent: Maximum number of concurrent requests
            timeout: Timeout per website in seconds
        """
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.extractor = FastEmailExtractor(timeout=timeout)
        self.logger = logging.getLogger(__name__)
    
    async def extract_emails_parallel(self, websites: List[str]) -> List[Optional[str]]:
        """
        Extract emails from multiple websites in parallel.
        
        Args:
            websites: List of website URLs
            
        Returns:
            List of email addresses (None if not found)
        """
        if not websites:
            return []
        
        self.logger.info(f"🚀 Parallel email extraction: {len(websites)} websites, {self.max_concurrent} at once")
        
        # Create shared session for connection pooling
        connector = aiohttp.TCPConnector(limit=self.max_concurrent, limit_per_host=2)
        async with aiohttp.ClientSession(connector=connector) as session:
            
            # Create semaphore to limit concurrency
            semaphore = asyncio.Semaphore(self.max_concurrent)
            
            async def extract_with_limit(website: str) -> Optional[str]:
                async with semaphore:
                    return await self.extractor.extract_email_from_website(website, session)
            
            # Run all extractions in parallel
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
            self.logger.info(f"✅ Email extraction complete: {found_count}/{len(websites)} found")
            
            return emails
