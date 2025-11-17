"""
Utility Module
Helper functions for deduplication, notifications, and data processing.
"""

import hashlib
import logging
import smtplib
import requests
from typing import List, Dict, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class DataUtils:
    """Utilities for data processing and deduplication."""
    
    @staticmethod
    def deduplicate_businesses(businesses: List[Dict], method: str = 'cid') -> List[Dict]:
        """
        Remove duplicate businesses from results.
        
        Args:
            businesses: List of business dictionaries
            method: Deduplication method ('cid', 'name_address', 'none')
            
        Returns:
            List of unique businesses
        """
        logger = logging.getLogger(__name__)
        
        if method == 'none' or not businesses:
            return businesses
        
        original_count = len(businesses)
        seen = set()
        unique_businesses = []
        
        for business in businesses:
            # Generate unique identifier based on method
            if method == 'cid':
                # Use Google's CID (most reliable)
                identifier = business.get('cid', '')
                # Fallback to name+address if no CID
                if not identifier or identifier == 'Not given':
                    identifier = DataUtils._generate_name_address_hash(business)
            elif method == 'name_address':
                identifier = DataUtils._generate_name_address_hash(business)
            else:
                identifier = str(hash(str(business)))
            
            if identifier and identifier not in seen:
                seen.add(identifier)
                unique_businesses.append(business)
        
        removed_count = original_count - len(unique_businesses)
        if removed_count > 0:
            logger.info(f"Removed {removed_count} duplicate businesses ({method} method)")
        
        return unique_businesses
    
    @staticmethod
    def _generate_name_address_hash(business: Dict) -> str:
        """Generate a hash from business name and address."""
        name = business.get('name', '').lower().strip()
        address = business.get('full_address', '').lower().strip()
        
        if not name:
            return ''
        
        # Create a unique string and hash it
        unique_str = f"{name}|{address}"
        return hashlib.md5(unique_str.encode()).hexdigest()
    
    @staticmethod
    def validate_coordinates(lat: float, lng: float, 
                           center_lat: float = None, center_lng: float = None,
                           max_distance_km: float = 50) -> bool:
        """
        Validate that coordinates are reasonable and within expected range.
        
        Args:
            lat: Latitude to validate
            lng: Longitude to validate
            center_lat: Expected center latitude (optional)
            center_lng: Expected center longitude (optional)
            max_distance_km: Maximum distance from center in km (optional)
            
        Returns:
            True if coordinates are valid
        """
        # Basic validation
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            return False
        
        # If center coordinates provided, check distance
        if center_lat is not None and center_lng is not None:
            distance = DataUtils._haversine_distance(lat, lng, center_lat, center_lng)
            return distance <= max_distance_km
        
        return True
    
    @staticmethod
    def _haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two coordinates in kilometers."""
        import math
        
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c


class NotificationManager:
    """Manages notifications via email and webhooks."""
    
    def __init__(self, email: Optional[str] = None, webhook: Optional[str] = None):
        """
        Initialize notification manager.
        
        Args:
            email: Email address to send notifications to
            webhook: Webhook URL to POST notifications to
        """
        self.email = email
        self.webhook = webhook
        self.logger = logging.getLogger(__name__)
    
    def send_completion_notification(self, stats: Dict) -> None:
        """
        Send notification when scraping completes.
        
        Args:
            stats: Dictionary with scraping statistics
        """
        message = self._format_completion_message(stats)
        
        if self.email:
            self._send_email(
                subject="Google Maps Scraper - Completed",
                body=message
            )
        
        if self.webhook:
            self._send_webhook({
                'event': 'scraping_completed',
                'stats': stats,
                'message': message
            })
    
    def send_error_notification(self, error: str) -> None:
        """
        Send notification when an error occurs.
        
        Args:
            error: Error message
        """
        if self.email:
            self._send_email(
                subject="Google Maps Scraper - Error",
                body=f"An error occurred during scraping:\n\n{error}"
            )
        
        if self.webhook:
            self._send_webhook({
                'event': 'scraping_error',
                'error': error
            })
    
    def _format_completion_message(self, stats: Dict) -> str:
        """Format completion statistics into a readable message."""
        return f"""
Scraping Completed Successfully!

Statistics:
- Total Queries: {stats.get('total_queries', 0)}
- Successful: {stats.get('success_count', 0)}
- Failed: {stats.get('failure_count', 0)}
- Businesses Found: {stats.get('total_businesses', 0)}
- Unique Businesses: {stats.get('unique_businesses', 0)}

Results are ready for download.
        """.strip()
    
    def _send_email(self, subject: str, body: str) -> None:
        """Send email notification (requires SMTP configuration)."""
        try:
            # This is a placeholder - configure with your SMTP settings
            self.logger.info(f"Email notification: {subject}")
            # Actual implementation would use smtplib
            # msg = MIMEText(body)
            # msg['Subject'] = subject
            # msg['From'] = 'scraper@example.com'
            # msg['To'] = self.email
            # smtp.send_message(msg)
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
    
    def _send_webhook(self, data: Dict) -> None:
        """Send webhook notification."""
        try:
            response = requests.post(
                self.webhook,
                json=data,
                timeout=10
            )
            if response.status_code == 200:
                self.logger.info("Webhook notification sent successfully")
            else:
                self.logger.warning(f"Webhook returned status {response.status_code}")
        except Exception as e:
            self.logger.error(f"Failed to send webhook: {e}")


class ProxyHealthMonitor:
    """Monitor proxy health and performance."""
    
    def __init__(self):
        """Initialize proxy health monitor."""
        self.proxy_stats = {}
        self.logger = logging.getLogger(__name__)
    
    def record_success(self, proxy_id: str) -> None:
        """Record a successful request for a proxy."""
        if proxy_id not in self.proxy_stats:
            self.proxy_stats[proxy_id] = {
                'success': 0,
                'failure': 0,
                'total': 0,
                'success_rate': 0.0
            }
        
        self.proxy_stats[proxy_id]['success'] += 1
        self.proxy_stats[proxy_id]['total'] += 1
        self._update_success_rate(proxy_id)
    
    def record_failure(self, proxy_id: str) -> None:
        """Record a failed request for a proxy."""
        if proxy_id not in self.proxy_stats:
            self.proxy_stats[proxy_id] = {
                'success': 0,
                'failure': 0,
                'total': 0,
                'success_rate': 0.0
            }
        
        self.proxy_stats[proxy_id]['failure'] += 1
        self.proxy_stats[proxy_id]['total'] += 1
        self._update_success_rate(proxy_id)
    
    def _update_success_rate(self, proxy_id: str) -> None:
        """Update success rate for a proxy."""
        stats = self.proxy_stats[proxy_id]
        if stats['total'] > 0:
            stats['success_rate'] = (stats['success'] / stats['total']) * 100
    
    def get_proxy_stats(self) -> Dict:
        """Get statistics for all proxies."""
        return self.proxy_stats
    
    def get_best_proxy(self) -> Optional[str]:
        """Get the proxy with the highest success rate."""
        if not self.proxy_stats:
            return None
        
        best_proxy = max(
            self.proxy_stats.items(),
            key=lambda x: (x[1]['success_rate'], x[1]['total'])
        )
        
        return best_proxy[0]
