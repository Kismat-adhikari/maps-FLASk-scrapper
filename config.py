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
    REQUEST_TIMEOUT = 20  # Seconds to wait for page elements (reduced for Apify)
    PAGE_LOAD_TIMEOUT = 30  # Seconds to wait for page load (reduced for Apify)
    HEADLESS = True  # Set to True for production (no visible browser)
    MIN_PROXY_COUNT = 1  # Minimum proxies required to start
    
    # Parallel scraping settings (OPTIMIZED FOR APIFY)
    PARALLEL_TABS = 10  # Number of tabs to open simultaneously (increased for Apify)
    MAX_CONCURRENT_BUSINESSES = 10  # Max businesses to scrape at once
    
    # Browser settings
    VIEWPORT_WIDTH = 1920
    VIEWPORT_HEIGHT = 1080
    
    # Deduplication settings
    DEDUPLICATE_RESULTS = True  # Remove duplicate businesses
    DEDUP_METHOD = 'cid'  # Options: 'cid', 'name_address', 'none'
    
    # Email extraction settings (ORIGINAL SETTINGS - 42% email success proven)
    EXTRACT_EMAILS_FROM_WEBSITES = True  # Website scraping enabled to find emails
    EMAIL_EXTRACTION_TIMEOUT = 6  # 6 seconds (proven to work)
    EMAIL_MAX_CONCURRENT = 5  # 5 concurrent requests (proven to work)
    EMAIL_MAX_HTML_SIZE = 500 * 1024  # 500KB HTML limit (proven to work)
    
    # Rate limiting
    DELAY_BETWEEN_QUERIES = 2  # Seconds to wait between queries
    
    # Notifications (optional)
    ENABLE_NOTIFICATIONS = False
    NOTIFICATION_EMAIL = os.environ.get('NOTIFICATION_EMAIL')
    NOTIFICATION_WEBHOOK = os.environ.get('NOTIFICATION_WEBHOOK')
    
    # Logging
    LOG_FILE = 'scraper.log'
    LOG_LEVEL = 'INFO'
