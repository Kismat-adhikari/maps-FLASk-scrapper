import os


class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    
    # Scraper settings
    PROXY_FILE = 'proxies.txt'
    ROTATION_THRESHOLD = 14
    REQUEST_TIMEOUT = 30
    PAGE_LOAD_TIMEOUT = 60
    HEADLESS = False  # Set to False to see browser
    MIN_PROXY_COUNT = 1  # Minimum proxies required to start
    
    # Parallel scraping settings
    PARALLEL_TABS = 5  # Number of tabs to open simultaneously (3-5 recommended for stability)
    MAX_CONCURRENT_BUSINESSES = 5  # Max businesses to scrape at once
    
    # Browser settings
    VIEWPORT_WIDTH = 1920
    VIEWPORT_HEIGHT = 1080
    
    # Deduplication settings
    DEDUPLICATE_RESULTS = True  # Remove duplicate businesses
    DEDUP_METHOD = 'cid'  # Options: 'cid', 'name_address', 'none'
    
    # Email extraction settings
    EXTRACT_EMAILS_FROM_WEBSITES = True  # Extract emails from business websites
    EMAIL_EXTRACTION_TIMEOUT = 3  # Max seconds to spend on each website
    
    # Rate limiting
    DELAY_BETWEEN_QUERIES = 2  # Seconds to wait between queries
    
    # Notifications (optional)
    ENABLE_NOTIFICATIONS = False
    NOTIFICATION_EMAIL = os.environ.get('NOTIFICATION_EMAIL')
    NOTIFICATION_WEBHOOK = os.environ.get('NOTIFICATION_WEBHOOK')
    
    # Logging
    LOG_FILE = 'scraper.log'
    LOG_LEVEL = 'INFO'
