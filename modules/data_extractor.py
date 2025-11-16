"""
Data Extractor Module
Handles extraction and cleaning of business data from Google Maps.
"""

import re
import logging
from typing import Dict, Optional


class DataExtractor:
    """Extracts and cleans business information from Google Maps."""
    
    @staticmethod
    async def extract_detailed_business_info(page) -> Dict:
        """
        Extract comprehensive business information from Google Maps detail page.
        
        Args:
            page: Playwright page object on business detail page
            
        Returns:
            Dictionary with comprehensive business information
        """
        logger = logging.getLogger(__name__)
        
        business_info = {
            'name': 'Not given',
            'full_address': 'Not given',
            'latitude': 'Not given',
            'longitude': 'Not given',
            'phone': 'Not given',
            'website': 'Not given',
            'email': 'Not given',
            'rating': 'Not given',
            'review_count': 'Not given',
            'category': 'Not given',
            'opening_hours': 'Not given',
            'plus_code': 'Not given',
            'cid': 'Not given',
            'url': 'Not given',
            'description': 'Not given'
        }
        
        try:
            # Get current URL for CID and URL
            current_url = page.url
            business_info['url'] = current_url
            
            # Extract CID from URL
            try:
                if '!1s' in current_url:
                    cid_match = current_url.split('!1s')[1].split('!')[0]
                    business_info['cid'] = cid_match
            except:
                pass
            
            # Extract coordinates from URL
            try:
                if '@' in current_url:
                    coords = current_url.split('@')[1].split(',')
                    if len(coords) >= 2:
                        business_info['latitude'] = coords[0]
                        business_info['longitude'] = coords[1]
            except:
                pass
            
            # Extract business name
            try:
                # Try multiple selectors for the business name
                name_selectors = [
                    'h1.DUwDvf',  # Main heading
                    'h1[class*="fontHeadline"]',
                    'h1',
                    'div[role="main"] h1'
                ]
                
                for selector in name_selectors:
                    try:
                        name_elem = await page.locator(selector).first.text_content(timeout=3000)
                        if name_elem and name_elem.strip() and name_elem.strip() != 'Results':
                            business_info['name'] = name_elem.strip()
                            break
                    except:
                        continue
            except:
                pass
            
            # Extract category
            try:
                category_elem = await page.locator('button[jsaction*="category"]').first.text_content(timeout=3000)
                if category_elem:
                    business_info['category'] = category_elem.strip()
            except:
                pass
            
            # Extract rating and reviews - FIXED
            try:
                # Look for the rating in the main info section
                # Google Maps shows rating like "4.5" followed by review count
                rating_text = await page.locator('div.F7nice').first.text_content(timeout=3000)
                
                if rating_text:
                    # Extract rating (first number)
                    rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                    if rating_match:
                        rating_value = float(rating_match.group(1))
                        if 0 <= rating_value <= 5:
                            business_info['rating'] = rating_value
                            logger.debug(f"Extracted rating: {rating_value}")
                    
                    # Extract review count
                    review_match = re.search(r'\(?([\d,]+)\)?', rating_text)
                    if review_match:
                        review_str = review_match.group(1).replace(',', '')
                        business_info['review_count'] = int(review_str)
                        logger.debug(f"Extracted reviews: {review_str}")
            except Exception as e:
                logger.debug(f"Could not extract rating: {e}")
                # Try alternative method
                try:
                    # Sometimes rating is in aria-label
                    rating_elem = await page.locator('span[role="img"][aria-label*="star"]').first.get_attribute('aria-label', timeout=2000)
                    if rating_elem:
                        rating = DataExtractor.clean_rating(rating_elem)
                        if rating:
                            business_info['rating'] = rating
                        review_count = DataExtractor.extract_review_count(rating_elem)
                        if review_count:
                            business_info['review_count'] = review_count
                except:
                    pass
            
            # Extract address
            try:
                address_button = await page.locator('button[data-item-id="address"]').first.text_content(timeout=3000)
                if address_button:
                    business_info['full_address'] = address_button.strip()
            except:
                pass
            
            # Extract phone
            try:
                phone_button = await page.locator('button[data-item-id*="phone"]').first.text_content(timeout=3000)
                if phone_button:
                    business_info['phone'] = DataExtractor.clean_phone_number(phone_button)
            except:
                pass
            
            # Extract website
            try:
                website_link = await page.locator('a[data-item-id="authority"]').first.get_attribute('href', timeout=3000)
                if website_link:
                    business_info['website'] = website_link.strip()
                    
                    # Try to extract email from the website
                    try:
                        email = await DataExtractor.extract_email_from_website(page, website_link)
                        if email:
                            business_info['email'] = email
                            logger.debug(f"Extracted email: {email}")
                    except Exception as e:
                        logger.debug(f"Could not extract email from website: {e}")
            except:
                pass
            
            # Extract plus code
            try:
                plus_code_button = await page.locator('button[data-item-id="oloc"]').first.text_content(timeout=3000)
                if plus_code_button:
                    business_info['plus_code'] = plus_code_button.strip()
            except:
                pass
            
            # Extract opening hours
            try:
                hours_selectors = [
                    'button[data-item-id*="hours"]',
                    'div[aria-label*="Hours"]',
                    'button[aria-label*="Hours"]'
                ]
                
                for selector in hours_selectors:
                    try:
                        hours_elem = await page.locator(selector).first.get_attribute('aria-label', timeout=2000)
                        if not hours_elem:
                            hours_elem = await page.locator(selector).first.text_content(timeout=2000)
                        
                        if hours_elem and len(hours_elem) > 5:
                            business_info['opening_hours'] = hours_elem.strip()
                            break
                    except:
                        continue
            except:
                pass
            
            # Extract description/about
            try:
                # Look for description in various possible locations
                desc_selectors = [
                    'div[class*="description"]',
                    'div[jsaction*="description"]',
                    'div[aria-label*="About"]'
                ]
                for selector in desc_selectors:
                    try:
                        desc_elem = await page.locator(selector).first.text_content(timeout=2000)
                        if desc_elem and len(desc_elem) > 10:
                            business_info['description'] = desc_elem.strip()
                            break
                    except:
                        continue
            except:
                pass
            
        except Exception as e:
            logger.error(f"Error extracting detailed business info: {e}")
        
        return business_info
    
    @staticmethod
    async def extract_business_info(page, element) -> Dict:
        """
        Extract business information from a Google Maps result element.
        
        Args:
            page: Playwright page object
            element: The business card element
            
        Returns:
            Dictionary with business information
        """
        logger = logging.getLogger(__name__)
        
        business_info = {
            'name': '',
            'address': '',
            'phone': '',
            'website': '',
            'rating': None,
            'review_count': None,
            'category': ''
        }
        
        try:
            # Extract name
            try:
                name_elem = await element.query_selector('[class*="fontHeadlineSmall"]')
                if name_elem:
                    business_info['name'] = (await name_elem.inner_text()).strip()
            except Exception as e:
                logger.debug(f"Could not extract name: {e}")
            
            # Extract rating and review count
            try:
                rating_elem = await element.query_selector('[role="img"][aria-label*="star"]')
                if rating_elem:
                    aria_label = await rating_elem.get_attribute('aria-label')
                    if aria_label:
                        rating = DataExtractor.clean_rating(aria_label)
                        business_info['rating'] = rating
                        review_count = DataExtractor.extract_review_count(aria_label)
                        business_info['review_count'] = review_count
            except Exception as e:
                logger.debug(f"Could not extract rating: {e}")
            
            # Extract category
            try:
                category_elem = await element.query_selector('[class*="fontBodyMedium"] > span:first-child')
                if category_elem:
                    business_info['category'] = (await category_elem.inner_text()).strip()
            except Exception as e:
                logger.debug(f"Could not extract category: {e}")
            
            # Extract address
            try:
                address_elems = await element.query_selector_all('[class*="fontBodyMedium"] > span')
                for addr_elem in address_elems:
                    text = (await addr_elem.inner_text()).strip()
                    # Address usually contains numbers and commas
                    if text and (',' in text or any(char.isdigit() for char in text)):
                        business_info['address'] = text
                        break
            except Exception as e:
                logger.debug(f"Could not extract address: {e}")
            
        except Exception as e:
            logger.error(f"Error extracting business info: {e}")
        
        return business_info
    
    @staticmethod
    def clean_phone_number(phone: str) -> str:
        """
        Clean and format phone number.
        
        Args:
            phone: Raw phone number string
            
        Returns:
            Cleaned phone number
        """
        if not phone:
            return ''
        
        # Remove common phone number formatting characters
        cleaned = re.sub(r'[^\d+\-() ]', '', phone)
        return cleaned.strip()
    
    @staticmethod
    def clean_rating(rating_text: str) -> Optional[float]:
        """
        Extract and convert rating from text to float.
        
        Args:
            rating_text: Text containing rating (e.g., "4.5 stars")
            
        Returns:
            Rating as float or None if not found
        """
        if not rating_text:
            return None
        
        try:
            # Look for decimal number pattern (e.g., "4.5" or "4")
            match = re.search(r'(\d+\.?\d*)', rating_text)
            if match:
                rating = float(match.group(1))
                # Validate rating is in reasonable range
                if 0 <= rating <= 5:
                    return rating
        except (ValueError, AttributeError):
            pass
        
        return None
    
    @staticmethod
    async def extract_email_from_website(page, website_url: str) -> Optional[str]:
        """
        Extract email from business website.
        
        Args:
            page: Playwright page object
            website_url: URL of the business website
            
        Returns:
            Email address or None
        """
        logger = logging.getLogger(__name__)
        
        try:
            # Open website in new tab
            new_page = await page.context.new_page()
            
            try:
                await new_page.goto(website_url, timeout=10000, wait_until='domcontentloaded')
                await new_page.wait_for_timeout(2000)
                
                # Get page content
                content = await new_page.content()
                
                # Look for email patterns
                email_patterns = [
                    r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                    r'mailto:([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
                ]
                
                for pattern in email_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        # Filter out common non-business emails
                        for email in matches:
                            email_lower = email.lower()
                            if not any(x in email_lower for x in ['example.com', 'domain.com', 'email.com', 'test.com', 'wix.com', 'wordpress.com']):
                                logger.info(f"Found email: {email}")
                                await new_page.close()
                                return email
                
                await new_page.close()
            except:
                await new_page.close()
        except Exception as e:
            logger.debug(f"Error extracting email: {e}")
        
        return None
    
    @staticmethod
    def extract_review_count(text: str) -> Optional[int]:
        """
        Extract review count from text.
        
        Args:
            text: Text containing review count (e.g., "4.5 stars 123 reviews")
            
        Returns:
            Review count as integer or None if not found
        """
        if not text:
            return None
        
        try:
            # Look for patterns like "123 reviews" or "(123)"
            # Try to find number followed by "review"
            match = re.search(r'(\d+(?:,\d+)*)\s*(?:review|rating)', text, re.IGNORECASE)
            if match:
                count_str = match.group(1).replace(',', '')
                return int(count_str)
            
            # Try to find number in parentheses
            match = re.search(r'\((\d+(?:,\d+)*)\)', text)
            if match:
                count_str = match.group(1).replace(',', '')
                return int(count_str)
        except (ValueError, AttributeError):
            pass
        
        return None
    
    @staticmethod
    async def extract_email_from_website(page, website_url: str) -> Optional[str]:
        """
        Extract email from business website by visiting it.
        
        Args:
            page: Playwright page object
            website_url: URL of the business website
            
        Returns:
            Email address if found, None otherwise
        """
        logger = logging.getLogger(__name__)
        
        try:
            # Open website in new tab
            new_page = await page.context.new_page()
            
            try:
                # Navigate to website with short timeout
                await new_page.goto(website_url, timeout=10000, wait_until='domcontentloaded')
                
                # Get page content
                content = await new_page.content()
                
                # Look for email patterns
                email_patterns = [
                    r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                    r'mailto:([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
                ]
                
                for pattern in email_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        # Filter out common non-business emails
                        for email in matches:
                            email = email.lower()
                            if not any(x in email for x in ['example.com', 'test.com', 'domain.com', 'email.com', 'wix.com', 'squarespace.com']):
                                await new_page.close()
                                return email
                
                # Try to find contact page
                try:
                    contact_link = await new_page.locator('a[href*="contact"]').first.get_attribute('href', timeout=2000)
                    if contact_link:
                        if not contact_link.startswith('http'):
                            from urllib.parse import urljoin
                            contact_link = urljoin(website_url, contact_link)
                        
                        await new_page.goto(contact_link, timeout=10000, wait_until='domcontentloaded')
                        content = await new_page.content()
                        
                        for pattern in email_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            if matches:
                                for email in matches:
                                    email = email.lower()
                                    if not any(x in email for x in ['example.com', 'test.com', 'domain.com']):
                                        await new_page.close()
                                        return email
                except:
                    pass
                
            finally:
                await new_page.close()
                
        except Exception as e:
            logger.debug(f"Error extracting email from website: {e}")
        
        return None
    
    @staticmethod
    def extract_from_detail_page(page) -> Dict:
        """
        Extract additional business information from the detail page.
        This is called when clicking into a business listing.
        
        Args:
            page: Playwright page object on business detail page
            
        Returns:
            Dictionary with additional business information
        """
        logger = logging.getLogger(__name__)
        
        detail_info = {
            'phone': '',
            'website': ''
        }
        
        try:
            # Extract phone number
            try:
                phone_button = page.locator('[data-item-id*="phone"]').first
                if phone_button:
                    phone_text = phone_button.inner_text()
                    detail_info['phone'] = DataExtractor.clean_phone_number(phone_text)
            except Exception as e:
                logger.debug(f"Could not extract phone from detail page: {e}")
            
            # Extract website
            try:
                website_link = page.locator('[data-item-id*="authority"]').first
                if website_link:
                    website_url = website_link.get_attribute('href')
                    if website_url:
                        detail_info['website'] = website_url.strip()
            except Exception as e:
                logger.debug(f"Could not extract website from detail page: {e}")
        
        except Exception as e:
            logger.error(f"Error extracting from detail page: {e}")
        
        return detail_info
