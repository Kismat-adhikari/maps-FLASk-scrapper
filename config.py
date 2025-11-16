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
    HEADLESS = False
    
    # Browser settings
    VIEWPORT_WIDTH = 1920
    VIEWPORT_HEIGHT = 1080
    
    # Logging
    LOG_FILE = 'scraper.log'
    LOG_LEVEL = 'INFO'
