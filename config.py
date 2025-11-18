import os


class Config:
    """
    Application configuration settings.
    
    For production deployment:
    - Set HEADLESS = True
    - Set SECRET_KEY via environment variable
    - Adjust timeouts based on your needs
    - Configure proxy settings
    """
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max file upload
    
    # Scraper settings
    PROXY_FILE = 'proxies.txt'
    ROTATION_THRESHOLD = 14  # Rotate proxy after N requests
    REQUEST_TIMEOUT = 30  # Seconds to wait for page elements
    PAGE_LOAD_TIMEOUT = 60  # Seconds to wait for page load
    HEADLESS = False  # Set to True for production (no visible browser)
    MIN_PROXY_COUNT = 1  # Minimum proxies required to start
    
    # Parallel scraping settings
    PARALLEL_TABS = 3  # Number of tabs to open simultaneously (3 for speed, 2 for stability)
    MAX_CONCURRENT_BUSINESSES = 3  # Max businesses to scrape at once
    
    # Browser settings
    VIEWPORT_WIDTH = 1920
    VIEWPORT_HEIGHT = 1080
    
    # Deduplication settings
    DEDUPLICATE_RESULTS = True  # Remove duplicate businesses
    DEDUP_METHOD = 'cid'  # Options: 'cid', 'name_address', 'none'
    
    # Email extraction settings
    EXTRACT_EMAILS_FROM_WEBSITES = True  # Extract emails from business websites
    EMAIL_EXTRACTION_TIMEOUT = 2  # Max seconds to spend on each website (reduced for speed)
    
    # Rate limiting
    DELAY_BETWEEN_QUERIES = 2  # Seconds to wait between queries
    
    # Notifications (optional)
    ENABLE_NOTIFICATIONS = False
    NOTIFICATION_EMAIL = os.environ.get('NOTIFICATION_EMAIL')
    NOTIFICATION_WEBHOOK = os.environ.get('NOTIFICATION_WEBHOOK')
    
    # Logging
    LOG_FILE = 'scraper.log'
    LOG_LEVEL = 'INFO'
