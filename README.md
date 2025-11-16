# Google Maps Scraper

A powerful web application for scraping business data from Google Maps without using API keys. Built with Flask, Python, Playwright, and a modern web frontend.

## Features

- 🌐 **Web Interface** - Easy-to-use browser-based interface
- 🗺️ **Live Interactive Map** - Real-time visualization with MapLibre GL JS (WebGL-powered)
- 📁 **Flexible Input** - Upload CSV/Excel files or enter queries manually
- 🔄 **Smart Proxy Rotation** - Automatic rotation after 14 requests or on failure
- 👁️ **Visible Browser** - Watch the scraping process in real-time
- 📊 **Real-time Progress** - Live status updates and progress tracking
- 💾 **Multiple Export Formats** - Download results as CSV or JSON
- 🛡️ **Error Handling** - Automatic retry with CAPTCHA detection
- 🔧 **Modular Design** - Easy to maintain and extend
- ⚡ **Optimized Performance** - 2x faster scraping with reduced timeouts

## Architecture

The application consists of three layers:

1. **Frontend** (HTML/CSS/JS + MapLibre GL JS) - Modern UI with live map visualization
2. **Backend** (Flask) - API server with state management and coordination
3. **Scraper** (Playwright) - Browser automation with proxy rotation

### Technology Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript, MapLibre GL JS 3.6.2
- **Backend**: Python 3.9+, Flask 2.x
- **Browser Automation**: Playwright (Chromium)
- **Data Processing**: pandas, openpyxl
- **Mapping**: MapLibre GL JS (WebGL-powered, hardware-accelerated)

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Install Playwright Browsers

```bash
playwright install chromium
```

### Step 3: Configure Proxies

Add your proxies to `proxies.txt` in the following format (one per line):

```
IP:PORT:USERNAME:PASSWORD
```

Example:
```
72.46.139.137:6697:myuser:mypass
45.196.40.119:6197:myuser:mypass
```

**Important:** You need at least 1 proxy, but 10 proxies are recommended for optimal rotation.

## Usage

### Starting the Application

1. Run the Flask server:

```bash
python app.py
```

2. Open your browser and navigate to:

```
http://127.0.0.1:5000
```

### Input Methods

#### Option 1: File Upload

1. Prepare a CSV or Excel file with the following columns:
   - `keyword` (required) - Search term (e.g., "restaurants")
   - `zip_code` (required) - Zip code to search in (e.g., "10001")
   - `url` (optional) - Custom URL (leave empty if not needed)

2. Click "Choose File" and select your file
3. Click "Upload & Start" to begin scraping

**Sample files provided:**
- `sample_queries.csv` - Example CSV file
- `sample_queries.xlsx` - Example Excel file

#### Option 2: Manual Entry

1. Fill in the keyword and zip code fields
2. Click "Add Row" to add more queries
3. Click "Start Scraping" to begin

### Monitoring Progress

The interface displays:
- **Status** - Current scraping state (Idle, Running, Completed, Stopped)
- **Current Query** - The query being processed
- **Current Proxy** - Active proxy IP and port
- **Processed** - Number of queries completed
- **Successful** - Number of successful queries
- **Failed** - Number of failed queries
- **Progress Bar** - Visual progress indicator

### Downloading Results

Once scraping is complete:
1. The "Results" section will appear
2. Click "Download CSV" or "Download JSON" to export data

### Stopping Scraping

Click the "Stop Scraping" button to halt the process at any time.

## Proxy Rotation Logic

The scraper uses intelligent proxy rotation to avoid detection:

- **Sequential Rotation** - Cycles through all proxies in order
- **Threshold-Based** - Rotates after every 14 requests
- **Failure-Triggered** - Immediately switches on CAPTCHA or timeout
- **Automatic Recovery** - Retries failed queries with next proxy (up to 3 attempts)

## Extracted Data Fields

For each business, the scraper collects:

- `name` - Business name
- `address` - Full address
- `phone` - Phone number
- `website` - Website URL
- `rating` - Star rating (0-5)
- `review_count` - Number of reviews
- `category` - Business category
- `keyword` - Original search keyword
- `zip_code` - Original search zip code

## Configuration

Edit `config.py` to customize settings:

```python
# Proxy settings
PROXY_FILE = 'proxies.txt'
ROTATION_THRESHOLD = 14  # Rotate after N requests

# Timeout settings
REQUEST_TIMEOUT = 30  # seconds
PAGE_LOAD_TIMEOUT = 60  # seconds

# Browser settings
HEADLESS = False  # Set to True for headless mode
VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 1080
```

## API Endpoints

The Flask backend provides the following REST API:

- `GET /` - Serve main web interface
- `POST /upload` - Upload and parse CSV/Excel file
- `POST /start` - Start scraping with manual queries
- `GET /status` - Get current scraping status (polled every 2 seconds)
- `POST /stop` - Stop scraping operation
- `GET /download/csv` - Download results as CSV
- `GET /download/json` - Download results as JSON

## Project Structure

```
google-maps-scraper/
├── app.py                      # Flask application entry point
├── config.py                   # Configuration settings
├── proxies.txt                 # Proxy list (not in git)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── sample_queries.csv          # Example CSV file
├── sample_queries.xlsx         # Example Excel file
├── test_integration.py         # Integration tests
├── static/
│   ├── css/
│   │   └── style.css          # Frontend styles
│   └── js/
│       └── app.js             # Frontend logic
├── templates/
│   └── index.html             # Main web interface
├── modules/
│   ├── __init__.py
│   ├── proxy_manager.py       # Proxy rotation logic
│   ├── scraper.py             # Playwright scraper
│   ├── file_parser.py         # CSV/Excel parser
│   └── data_extractor.py      # Data extraction utilities
└── uploads/                    # Temporary file storage
```

## Testing

Run the integration tests to verify all components:

```bash
python test_integration.py
```

Expected output:
```
✓ ProxyManager tests passed!
✓ FileParser tests passed!
✓ DataExtractor tests passed!
✓ GoogleMapsScraper initialization tests passed!
✓ All components integrated successfully!
Total: 5/5 tests passed
```

## Troubleshooting

### Issue: "No proxies loaded"
**Solution:** Ensure `proxies.txt` exists and contains valid proxies in the correct format.

### Issue: "Playwright browsers not installed"
**Solution:** Run `playwright install chromium`

### Issue: "CAPTCHA detected"
**Solution:** The system automatically rotates proxies on CAPTCHA. If it persists:
- Add more proxies to your pool
- Reduce the rotation threshold in `config.py`
- Increase delays between requests

### Issue: "Browser fails to initialize"
**Solution:** 
- Check proxy credentials are correct
- Verify proxies are working (test with curl or browser)
- Try running in headless mode: set `HEADLESS = True` in `config.py`

### Issue: "No results found"
**Solution:**
- Verify the keyword and zip code are valid
- Check if Google Maps has results for that query
- Review logs in `scraper.log` for details

## Logging

Logs are written to `scraper.log` with rotation (max 10MB per file, 3 backups).

View logs:
```bash
# Windows
type scraper.log

# Linux/Mac
tail -f scraper.log
```

## Performance

- **Average time per query:** 10-15 seconds
- **Proxy rotation overhead:** ~2 seconds (browser restart)
- **Expected throughput:** 4-6 queries per minute
- **Results per query:** Up to 20 businesses

## Security Considerations

- ⚠️ **Never commit `proxies.txt`** - It's in `.gitignore` by default
- 🔒 Use environment variables for sensitive configuration in production
- 🛡️ File uploads are limited to 5MB
- ✅ All user inputs are validated before processing

## Future Enhancements

- [ ] Parallel scraping with multiple browsers
- [ ] Export to Apify actor format
- [ ] Advanced proxy health monitoring
- [ ] Result caching to avoid re-scraping
- [ ] Scheduled scraping with cron-like functionality
- [ ] RESTful API mode for programmatic access
- [ ] Database storage for results history

## License

This project is for educational purposes. Please respect Google's Terms of Service and use responsibly.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs in `scraper.log`
3. Run integration tests: `python test_integration.py`

## Credits

Built with:
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Playwright](https://playwright.dev/) - Browser automation
- [pandas](https://pandas.pydata.org/) - Data processing
- [openpyxl](https://openpyxl.readthedocs.io/) - Excel file handling

---

**Happy Scraping! 🚀**
