# Project Structure

This document provides an overview of the Google Maps Scraper project structure.

## Directory Layout

```
google-maps-scraper/
├── app.py                          # Main Flask application
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── runtime.txt                     # Python version for deployment
├── Procfile                        # Deployment process file
├── render.yaml                     # Render deployment configuration
├── proxies.txt                     # Proxy list (not in git)
├── .gitignore                      # Git ignore rules
│
├── README.md                       # Main documentation
├── QUICK_START.md                  # Quick start guide
├── CHANGELOG.md                    # Version history
├── DEPLOYMENT_CHECKLIST.md         # Pre-deployment checklist
│
├── modules/                        # Core application modules
│   ├── __init__.py
│   ├── scraper.py                 # Playwright scraper logic
│   ├── proxy_manager.py           # Proxy rotation management
│   ├── file_parser.py             # CSV/Excel file parsing
│   ├── data_extractor.py          # Data extraction utilities
│   └── utils.py                   # Helper functions
│
├── templates/                      # HTML templates
│   ├── index.html                 # Main web interface
│   └── dashboard.html             # Proxy health dashboard
│
├── static/                         # Static assets
│   ├── css/
│   │   └── style.css              # Application styles
│   └── js/
│       └── app.js                 # Frontend JavaScript (MapLibre)
│
├── docs/                           # Documentation
│   ├── API_DOCUMENTATION.md       # REST API reference
│   ├── BULK_UPLOAD_GUIDE.md       # File upload guide
│   ├── PROXY_SETUP_GUIDE.md       # Proxy configuration
│   ├── RENDER_DEPLOYMENT.md       # Deployment instructions
│   └── TROUBLESHOOTING.md         # Common issues
│
├── tests/                          # Test files
│   ├── test_integration.py        # Integration tests
│   ├── test_parallel_scraper.py   # Parallel scraping tests
│   └── run_performance_test.py    # Performance benchmarks
│
├── samples/                        # Sample files
│   └── sample_queries.csv         # Example CSV file
│
├── output/                         # Scraped results (CSV/JSON)
│   └── .gitkeep
│
└── uploads/                        # Temporary file uploads
    └── .gitkeep
```

## Core Files

### Application Entry Point
- **app.py**: Main Flask application with routes and scraping logic

### Configuration
- **config.py**: Centralized configuration (timeouts, proxy settings, etc.)
- **proxies.txt**: List of proxies in format `IP:PORT:USERNAME:PASSWORD`

### Deployment
- **Procfile**: Tells deployment platform how to run the app
- **runtime.txt**: Specifies Python version
- **render.yaml**: Render-specific deployment configuration
- **requirements.txt**: Python package dependencies

## Modules

### scraper.py
- Playwright-based browser automation
- Business data extraction from Google Maps
- CAPTCHA detection and handling
- Retry logic with proxy rotation

### proxy_manager.py
- Sequential proxy rotation
- Threshold-based rotation (every N requests)
- Failure-triggered rotation
- Proxy health tracking

### file_parser.py
- CSV and Excel file parsing
- Support for keyword+location and URL modes
- Input validation and error handling

### data_extractor.py
- Extract business information from page elements
- Parse addresses, phone numbers, ratings
- Handle missing or malformed data

### utils.py
- Data deduplication
- Email extraction from websites
- Notification management
- Proxy health monitoring

## Templates

### index.html
- Main web interface
- Three input modes: keyword search, URL input, file upload
- Real-time status updates
- Interactive map with MapLibre GL JS
- Results table and download options

### dashboard.html
- Proxy health monitoring dashboard
- Success rates and performance metrics
- Visual charts and statistics

## Static Assets

### style.css
- Modern, responsive design
- Gradient backgrounds and animations
- Card-based layout
- Mobile-friendly

### app.js
- MapLibre GL JS integration
- Real-time map updates
- Status polling (every 1.5 seconds)
- Marker animations and popups
- File upload handling

## Documentation

### User Guides
- **README.md**: Complete project overview
- **QUICK_START.md**: Get started in 5 minutes
- **BULK_UPLOAD_GUIDE.md**: File upload instructions

### Technical Docs
- **API_DOCUMENTATION.md**: REST API endpoints
- **PROXY_SETUP_GUIDE.md**: Proxy configuration
- **TROUBLESHOOTING.md**: Common issues and solutions

### Deployment
- **RENDER_DEPLOYMENT.md**: Deploy to Render
- **DEPLOYMENT_CHECKLIST.md**: Pre-deployment checklist

## Tests

### Integration Tests
- **test_integration.py**: Verify all components work together
- Tests proxy manager, file parser, data extractor, scraper

### Performance Tests
- **test_parallel_scraper.py**: Test parallel scraping
- **run_performance_test.py**: Benchmark scraping speed

## Data Flow

1. **User Input** → Web interface (index.html)
2. **Request** → Flask routes (app.py)
3. **File Upload** → FileParser (file_parser.py)
4. **Scraping** → GoogleMapsScraper (scraper.py)
5. **Proxy Rotation** → ProxyManager (proxy_manager.py)
6. **Data Extraction** → DataExtractor (data_extractor.py)
7. **Results** → CSV/JSON files in output/
8. **Real-time Updates** → Status polling (app.js)
9. **Map Visualization** → MapLibre GL JS (app.js)

## Key Features

### Frontend
- Modern, responsive UI
- Real-time progress tracking
- Interactive map with markers
- Multiple input modes
- CSV/JSON download

### Backend
- Flask REST API
- Playwright browser automation
- Smart proxy rotation
- Incremental CSV saving
- Error handling and retry logic

### Scraping
- Visible or headless browser
- CAPTCHA detection
- Automatic proxy rotation
- Parallel scraping support
- Email extraction from websites

## Configuration Options

See `config.py` for all available settings:
- Proxy rotation threshold
- Request/page load timeouts
- Headless mode (on/off)
- Parallel scraping settings
- Deduplication options
- Email extraction settings
- Notification settings

## Output Files

### Scraped Results
- Location: `output/`
- Format: `{location}-{date}.csv` or `.json`
- Columns: name, address, phone, website, rating, etc.

### Logs
- Location: `scraper.log` (root directory)
- Rotation: 10MB max, 3 backups
- Level: INFO (configurable)

## Environment Variables

Optional environment variables:
- `SECRET_KEY`: Flask secret key (required for production)
- `NOTIFICATION_EMAIL`: Email for completion notifications
- `NOTIFICATION_WEBHOOK`: Webhook URL for notifications

## Git Ignored Files

The following are not tracked in git:
- `__pycache__/` - Python bytecode
- `output/` - Scraped results
- `uploads/` - Temporary uploads
- `*.log` - Log files
- `proxies.txt` - Proxy list (sensitive)
- `.env` - Environment variables
- `.vscode/`, `.idea/` - IDE settings

## Dependencies

### Python Packages
- Flask 3.0.0 - Web framework
- Playwright 1.40.0 - Browser automation
- pandas 2.1.4 - Data processing
- openpyxl 3.1.2 - Excel file handling
- gunicorn 21.2.0 - Production server

### Frontend Libraries
- MapLibre GL JS 3.6.2 - Interactive maps
- Vanilla JavaScript - No framework dependencies

## Browser Requirements

- Chromium (installed via Playwright)
- Supports headless and visible modes
- Requires ~200MB disk space for browser

## System Requirements

- Python 3.9 or higher
- 2GB RAM minimum (4GB recommended)
- 500MB disk space (for browser + dependencies)
- Internet connection (for scraping)

## Deployment Platforms

Tested and working on:
- Render (recommended)
- Heroku
- VPS/Cloud servers
- Local development

## Security Considerations

- Proxy credentials not in git
- Secret key via environment variable
- Input validation on all endpoints
- File upload size limits (5MB)
- CORS configured properly

## Performance

- Average: 10-15 seconds per query
- Throughput: 4-6 queries per minute
- Results: Up to 60 businesses per search
- Parallel: 3-5 tabs simultaneously

## Maintenance

- Logs rotated automatically
- Browser cache cleared between sessions
- Proxy health monitored
- Results deduplicated
- Memory managed efficiently

---

**Last Updated**: November 17, 2025  
**Version**: 2.0.0
