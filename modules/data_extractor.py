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
            
            # Extract coordinates from URL (multiple methods)
            try:
                logger.debug(f"Current URL for coordinate extraction: {current_url}")
                
                # Method 1: Extract from @ symbol (e.g., @40.7128,-74.0060,17z)
                if '@' in current_url:
                    coords = current_url.split('@')[1].split(',')
                    if len(coords) >= 2:
                        business_info['latitude'] = coords[0]
                        business_info['longitude'] = coords[1]
                        logger.debug(f"Extracted coordinates from @: lat={coords[0]}, lng={coords[1]}")
                
                # Method 2: Extract from !3d and !4d parameters (e.g., !3d40.7128!4d-74.0060)
                if business_info['latitude'] == 'Not given' and '!3d' in current_url and '!4d' in current_url:
                    try:
                        lat_part = current_url.split('!3d')[1].split('!')[0]
                        lng_part = current_url.split('!4d')[1].split('!')[0]
                        business_info['latitude'] = lat_part
                        business_info['longitude'] = lng_part
                        logger.debug(f"Extracted coordinates from !3d/!4d: lat={lat_part}, lng={lng_part}")
                    except:
                        pass
                
                # Method 3: Extract from data attributes or meta tags
                if business_info['latitude'] == 'Not given':
                    try:
                        # Try to find coordinates in page metadata
                        lat_elem = await page.locator('[data-latitude]').first.get_attribute('data-latitude', timeout=1000)
                        lng_elem = await page.locator('[data-longitude]').first.get_attribute('data-longitude', timeout=1000)
                        if lat_elem and lng_elem:
                            business_info['latitude'] = lat_elem
                            business_info['longitude'] = lng_elem
                            logger.debug(f"Extracted coordinates from data attributes: lat={lat_elem}, lng={lng_elem}")
                    except:
                        pass
                
                if business_info['latitude'] == 'Not given':
                    logger.warning(f"Could not extract coordinates from URL: {current_url}")
                    
            except Exception as e:
                logger.error(f"Error extracting coordinates: {e}")
            
            # Extract business name
            try:
                # Try multiple selectors for the business name
                name_selectors = [
                    'h1.DUwDvf',  # Main heading
                    'h1[class*="fontHeadline"]',
                    'h1.fontHeadlineLarge',
                    'h1',
                    'div[role="main"] h1',
                    '[data-attrid="title"]',
                    'div.SPZz6b h1',
                    'div.tAiQdd h1'
                ]
                
                for selector in name_selectors:
                    try:
                        name_elem = await page.locator(selector).first.text_content(timeout=5000)
                        if name_elem and name_elem.strip() and name_elem.strip() != 'Results':
                            business_info['name'] = name_elem.strip()
                            logger.debug(f"Found name with selector '{selector}': {business_info['name']}")
                            break
                    except Exception as e:
                        logger.debug(f"Selector '{selector}' failed: {e}")
                        continue
                
                # If still no name, try getting page title as fallback
                if business_info['name'] == 'Not given':
                    try:
                        title = await page.title()
                        if title and ' - Google Maps' in title:
                            business_info['name'] = title.replace(' - Google Maps', '').strip()
                            logger.debug(f"Extracted name from page title: {business_info['name']}")
                    except:
                        pass
                
                # Log if we still couldn't find the name
                if business_info['name'] == 'Not given':
                    logger.warning(f"Could not extract business name from page: {page.url}")
                    # Log page content for debugging
                    try:
                        page_content = await page.content()
                        logger.debug(f"Page HTML length: {len(page_content)} chars")
                        # Check if page has any h1 tags
                        h1_count = page_content.count('<h1')
                        logger.debug(f"Number of h1 tags found: {h1_count}")
                    except:
                        pass
            except Exception as e:
                logger.error(f"Error extracting business name: {e}")
            
            # Extract category
            try:
                category_elem = await page.locator('button[jsaction*="category"]').first.text_content(timeout=3000)
                if category_elem:
                    business_info['category'] = category_elem.strip()
            except:
                pass
            
            # Extract rating and reviews - Multiple methods
            try:
                # Method 1: Try the main rating container
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
                logger.debug(f"Method 1 failed: {e}")
                
            # Method 2: Try aria-label if Method 1 failed
            if business_info['rating'] == 'Not given' or business_info['review_count'] == 'Not given':
                try:
                    rating_elem = await page.locator('span[role="img"][aria-label*="star"]').first.get_attribute('aria-label', timeout=2000)
                    if rating_elem:
                        rating = DataExtractor.clean_rating(rating_elem)
                        if rating and business_info['rating'] == 'Not given':
                            business_info['rating'] = rating
                            logger.debug(f"Extracted rating from aria-label: {rating}")
                        review_count = DataExtractor.extract_review_count(rating_elem)
                        if review_count and business_info['review_count'] == 'Not given':
                            business_info['review_count'] = review_count
                            logger.debug(f"Extracted review count from aria-label: {review_count}")
                except Exception as e:
                    logger.debug(f"Method 2 failed: {e}")
            
            # Method 3: Try button with reviews text
            if business_info['review_count'] == 'Not given':
                try:
                    review_button = await page.locator('button:has-text("reviews")').first.text_content(timeout=2000)
                    if review_button:
                        review_match = re.search(r'([\d,]+)\s*reviews?', review_button, re.IGNORECASE)
                        if review_match:
                            review_str = review_match.group(1).replace(',', '')
                            business_info['review_count'] = int(review_str)
                            logger.debug(f"Extracted review count from button: {review_str}")
                except Exception as e:
                    logger.debug(f"Method 3 failed: {e}")
            
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
            
            # Extract website (check main view first, then menu tab)
            try:
                # Try main view first
                website_link = await page.locator('a[data-item-id="authority"]').first.get_attribute('href', timeout=2000)
                if website_link:
                    business_info['website'] = website_link.strip()
                    logger.info(f"Found website: {website_link}")
            except:
                # If not found, try clicking "Menu" tab where website might be hidden
                try:
                    logger.debug("Website not in main view, checking menu tab...")
                    # Click on the menu/about tab
                    menu_button = page.locator('button[aria-label*="Menu"], button:has-text("Menu"), button[role="tab"]:has-text("About")')
                    await menu_button.first.click(timeout=2000)
                    await asyncio.sleep(0.5)
                    
                    # Try to find website again
                    website_link = await page.locator('a[data-item-id="authority"]').first.get_attribute('href', timeout=2000)
                    if website_link:
                        business_info['website'] = website_link.strip()
                        logger.info(f"Found website in menu tab: {website_link}")
                except Exception as e:
                    logger.debug(f"Could not find website in menu tab: {e}")
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
        Fast email extraction from business website.
        Only checks homepage and /contact page with short timeout.
        Uses the same browser session (reuses the existing page).
        
        Args:
            page: Playwright page object (same browser session)
            website_url: URL of the business website
            
        Returns:
            Email address or None
        """
        logger = logging.getLogger(__name__)
        
        # Skip if no website
        if not website_url or website_url == 'Not given':
            return None
        
        # Check if email extraction is enabled
        from config import Config
        if not Config.EXTRACT_EMAILS_FROM_WEBSITES:
            return None
        
        logger.info("No email from Maps, checking website...")
        
        # Email regex pattern (improved to avoid false positives)
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        # Common non-business email domains to filter out
        excluded_domains = [
            'example.com', 'domain.com', 'email.com', 'test.com',
            'wix.com', 'wordpress.com', 'sentry.io', 'sentry-next.wixpress.com', 'sentry.wixpress.com',
            'google.com', 'facebook.com', 'twitter.com', 'instagram.com', 
            'squarespace.com', 'linkedin.com', 'youtube.com', 'pinterest.com'
        ]
        
        # Image file extensions to exclude
        image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico', '.bmp')
        
        # Store current URL to return to it later
        original_url = page.url
        
        try:
            # Use the same page (don't create new one)
            logger.info(f"Visiting website for email extraction...")
            
            # Use configurable timeout
            timeout = Config.EMAIL_EXTRACTION_TIMEOUT * 1000  # Convert to milliseconds
            
            # Try homepage first
            try:
                logger.info(f"Visiting homepage: {website_url}")
                try:
                    await page.goto(website_url, timeout=timeout, wait_until='networkidle')
                except:
                    # If networkidle times out, try with domcontentloaded
                    await page.goto(website_url, timeout=timeout, wait_until='domcontentloaded')
                
                await page.wait_for_timeout(500)  # Quick wait for JavaScript
                logger.info("Page loaded, extracting visible text...")
                
                # Get VISIBLE rendered text (not raw HTML)
                try:
                    visible_text = await page.evaluate('() => document.body.innerText')
                    logger.info(f"Visible text extracted: {len(visible_text)} chars")
                except Exception as e:
                    logger.error(f"Error extracting visible text: {e}")
                    visible_text = ""
                
                # Also get HTML content for mailto links
                html_content = await page.content()
                logger.info(f"HTML content extracted: {len(html_content)} chars")
                
                # Combine both sources
                combined_content = visible_text + " " + html_content
                
                # Find all emails
                emails = re.findall(email_pattern, combined_content, re.IGNORECASE)
                logger.info(f"Found {len(emails)} potential emails on homepage: {emails[:3]}")
                
                # Filter and return first valid email
                for email in emails:
                    email_lower = email.lower()
                    # Exclude image files and other non-email patterns
                    if email_lower.endswith(image_extensions):
                        continue
                    # Exclude common non-business domains
                    if any(domain in email_lower for domain in excluded_domains):
                        continue
                    # Additional validation: must have @ and valid TLD
                    if '@' in email and '.' in email.split('@')[1]:
                        logger.info(f"Found valid email on homepage: {email}")
                        # Return to original page
                        try:
                            await page.goto(original_url, timeout=timeout)
                        except:
                            pass
                        return email
                
                logger.info("No valid emails on homepage, trying /contact and /about...")
                
                # Only check the 2 most common pages (balance of coverage and speed)
                contact_pages = ['/contact', '/about']
                
                for page_path in contact_pages:
                    try:
                        contact_url = website_url.rstrip('/') + page_path
                        logger.info(f"Trying page: {contact_url}")
                        try:
                            # Fast load - don't wait for everything
                            await page.goto(contact_url, timeout=timeout, wait_until='domcontentloaded')
                            await page.wait_for_timeout(300)  # Quick wait for critical content
                        except:
                            continue  # Skip this page if it doesn't exist
                        
                        # Get both visible text and HTML quickly
                        try:
                            visible_text = await page.evaluate('() => document.body.innerText')
                        except:
                            visible_text = ""
                        
                        html_content = await page.content()
                        combined_content = visible_text + " " + html_content
                        
                        emails = re.findall(email_pattern, combined_content, re.IGNORECASE)
                        
                        # Filter and return FIRST valid email found (stop searching)
                        for email in emails:
                            email_lower = email.lower()
                            if email_lower.endswith(image_extensions):
                                continue
                            if any(domain in email_lower for domain in excluded_domains):
                                continue
                            if '@' in email and '.' in email.split('@')[1]:
                                logger.info(f"✓ Found email on {page_path}: {email}")
                                try:
                                    await page.goto(original_url, timeout=timeout)
                                except:
                                    pass
                                return email  # STOP as soon as we find one
                    except Exception as e:
                        logger.debug(f"Could not access {page_path}: {e}")
                        continue
                
            except Exception as e:
                logger.debug(f"Could not extract email from {website_url}: {e}")
                
        except Exception as e:
            logger.error(f"Error in email extraction: {e}", exc_info=True)
        finally:
            # Return to original page
            try:
                logger.info(f"Returning to original page...")
                await page.goto(original_url, timeout=timeout)
            except Exception as e:
                logger.error(f"Error returning to original page: {e}")
        
        logger.info("No email found on website")
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
