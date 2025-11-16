"""
Proxy Manager Module
Handles proxy rotation logic with sequential rotation after 14 requests or on failure.
"""

import logging
from typing import List, Dict, Optional


class ProxyManager:
    """Manages proxy rotation for the scraper."""
    
    def __init__(self, proxy_file: str, rotation_threshold: int = 14):
        """
        Initialize the ProxyManager.
        
        Args:
            proxy_file: Path to the proxy file (IP:PORT:USER:PASS format)
            rotation_threshold: Number of requests before rotating (default: 14)
        """
        self.proxy_file = proxy_file
        self.rotation_threshold = rotation_threshold
        self.proxies: List[Dict] = []
        self.current_index = 0
        self.request_counter = 0
        self.logger = logging.getLogger(__name__)
        
        # Load proxies on initialization
        self.load_proxies()
    
    def load_proxies(self) -> List[Dict]:
        """
        Load proxies from the proxy file.
        Expected format: IP:PORT:USERNAME:PASSWORD (one per line)
        
        Returns:
            List of proxy dictionaries
        """
        self.proxies = []
        
        try:
            with open(self.proxy_file, 'r') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split(':')
                if len(parts) == 4:
                    ip, port, username, password = parts
                    proxy = {
                        'server': f'http://{ip}:{port}',
                        'username': username,
                        'password': password,
                        'ip': ip,
                        'port': port
                    }
                    self.proxies.append(proxy)
                else:
                    self.logger.warning(f"Invalid proxy format: {line}")
            
            self.logger.info(f"Loaded {len(self.proxies)} proxies from {self.proxy_file}")
            
            if not self.proxies:
                self.logger.error("No valid proxies loaded!")
            
            return self.proxies
            
        except FileNotFoundError:
            self.logger.error(f"Proxy file not found: {self.proxy_file}")
            return []
        except Exception as e:
            self.logger.error(f"Error loading proxies: {e}")
            return []
    
    def get_next_proxy(self) -> Optional[Dict]:
        """
        Get the next proxy in the rotation cycle.
        
        Returns:
            Proxy dictionary or None if no proxies available
        """
        if not self.proxies:
            self.logger.error("No proxies available")
            return None
        
        proxy = self.proxies[self.current_index]
        self.logger.info(f"Using proxy: {proxy['ip']}:{proxy['port']}")
        
        return proxy
    
    def should_rotate(self) -> bool:
        """
        Check if proxy should be rotated based on request counter.
        
        Returns:
            True if rotation threshold reached, False otherwise
        """
        return self.request_counter >= self.rotation_threshold
    
    def mark_failure(self, proxy: Optional[Dict] = None) -> None:
        """
        Mark a proxy as failed and immediately rotate to the next one.
        
        Args:
            proxy: The proxy that failed (optional, uses current if not provided)
        """
        if proxy:
            self.logger.warning(f"Proxy failed: {proxy['ip']}:{proxy['port']}")
        else:
            current_proxy = self.proxies[self.current_index] if self.proxies else None
            if current_proxy:
                self.logger.warning(f"Current proxy failed: {current_proxy['ip']}:{current_proxy['port']}")
        
        # Rotate to next proxy immediately
        self._rotate()
    
    def increment_counter(self) -> None:
        """
        Increment the request counter and rotate if threshold is reached.
        """
        self.request_counter += 1
        self.logger.debug(f"Request counter: {self.request_counter}/{self.rotation_threshold}")
        
        if self.should_rotate():
            self.logger.info(f"Rotation threshold ({self.rotation_threshold}) reached")
            self._rotate()
    
    def _rotate(self) -> None:
        """
        Internal method to rotate to the next proxy in the list.
        Cycles back to the first proxy after reaching the end.
        """
        if not self.proxies:
            return
        
        old_index = self.current_index
        self.current_index = (self.current_index + 1) % len(self.proxies)
        self.reset_counter()
        
        old_proxy = self.proxies[old_index]
        new_proxy = self.proxies[self.current_index]
        
        self.logger.info(
            f"Rotated proxy: {old_proxy['ip']}:{old_proxy['port']} -> "
            f"{new_proxy['ip']}:{new_proxy['port']}"
        )
    
    def reset_counter(self) -> None:
        """
        Reset the request counter to 0.
        Called after proxy rotation.
        """
        self.request_counter = 0
        self.logger.debug("Request counter reset")
    
    def get_current_proxy_info(self) -> str:
        """
        Get a string representation of the current proxy.
        
        Returns:
            String like "IP:PORT" or "No proxy" if none available
        """
        if not self.proxies:
            return "No proxy"
        
        proxy = self.proxies[self.current_index]
        return f"{proxy['ip']}:{proxy['port']}"
    
    def get_proxy_count(self) -> int:
        """
        Get the total number of proxies loaded.
        
        Returns:
            Number of proxies
        """
        return len(self.proxies)
