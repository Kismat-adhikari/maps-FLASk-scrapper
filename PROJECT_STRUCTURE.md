# Google Maps Scraper - Apify Actor Structure

Clean, production-ready Apify Actor for scraping Google Maps.

## Directory Structure

```
google-maps-scraper-apify/
│
├── 📄 Apify Configuration
│   ├── main.py                      # Actor entry point
│   ├── INPUT_SCHEMA.json            # Input form definition
│   ├── .actor/
│   │   └── actor.json               # Actor metadata
│   ├── Dockerfile                   # Container configuration
│   └── requirements.txt             # Python dependencies
│
├── 🔧 Core Modules
│   └── modules/
│       ├── __init__.py              # Package initialization
│       ├── scraper.py               # Main scraping logic
│       ├── proxy_manager.py         # Proxy rotation
│       ├── data_extractor.py        # Data extraction
│       ├── file_parser.py           # File parsing utilities
│       └── utils.py                 # Helper functions
│
├── ⚙️ Configuration
│   ├── config.py                    # App configuration
│   ├── .gitignore                   # Git ignore rules
│   ├── .dockerignore                # Docker ignore rules
│   └── .actorignore                 # Apify ignore rules
│
├── 📚 Documentation
│   ├── README.md                    # Main documentation (Apify marketplace)
│   ├── CHANGELOG.md                 # Version history
│   ├── APIFY_DEPLOYMENT_GUIDE.md    # Deployment instructions
│   ├── APIFY_READY_SUMMARY.md       # Complete overview
│   ├── TESTING_APIFY.md             # Testing guide
│   ├── PROXY_SETUP_GUIDE.md         # Proxy configuration
│   └── TROUBLESHOOTING.md           # Common issues
│
└── 🔐 Sensitive (not in git)
    └── proxies.txt                  # Proxy list (user-provided)
```

## File Descriptions

### Apify Configuration Files

**main.py**
- Entry point for Apify Actor
- Reads input from Apify
- Coordinates scraping process
- Outputs to Apify Dataset

**INPUT_SCHEMA.json**
- Defines input form in Apify Console
- Specifies all configuration options
- Provides validation rules

**.actor/actor.json**
- Actor metadata (name, version, etc.)
- Storage configuration
- Dataset view definitions

**Dockerfile**
- Container build instructions
- Based on Apify's Python+Playwright image
- Installs dependencies and browsers

**requirements.txt**
- Python package dependencies
- Apify SDK, Playwright, pandas, etc.

### Core Modules

**modules/scraper.py**
- Main scraping logic using Playwright
- Handles browser automation
- Supports both Apify and custom proxies
- Parallel scraping with multiple tabs
- CAPTCHA detection and retry logic

**modules/proxy_manager.py**
- Proxy rotation management
- Sequential rotation with threshold
- Failure tracking and recovery
- Health monitoring

**modules/data_extractor.py**
- Extracts business data from pages
- Parses addresses, phones, ratings
- Email extraction from websites
- Handles missing/malformed data

**modules/file_parser.py**
- CSV/Excel file parsing (if needed)
- Input validation
- Error handling

**modules/utils.py**
- Data deduplication
- Email extraction helpers
- Notification management
- Proxy health monitoring

### Configuration

**config.py**
- Centralized configuration
- Timeouts, thresholds, settings
- Can be overridden by Apify input

**.gitignore**
- Excludes sensitive files from git
- Python cache, logs, proxies

**.dockerignore**
- Excludes unnecessary files from Docker build
- Speeds up container builds

**.actorignore**
- Excludes files from Apify upload
- Reduces actor size

### Documentation

**README.md**
- Main documentation for Apify marketplace
- Features, usage, examples
- Pricing information
- What users see when browsing actors

**APIFY_DEPLOYMENT_GUIDE.md**
- Step-by-step deployment instructions
- Account setup, import, testing
- Publishing to store
- Marketing strategies

**APIFY_READY_SUMMARY.md**
- Complete project overview
- Revenue potential
- Competitive advantages
- Success metrics

**TESTING_APIFY.md**
- How to test the actor
- Local vs platform testing
- Test scenarios

**PROXY_SETUP_GUIDE.md**
- How to configure proxies
- Apify proxy vs custom proxies
- Proxy format and requirements

**TROUBLESHOOTING.md**
- Common issues and solutions
- Error messages explained
- Performance optimization

**CHANGELOG.md**
- Version history
- Feature additions
- Bug fixes

## Data Flow

```
User Input (Apify Console)
    ↓
INPUT_SCHEMA.json (validation)
    ↓
main.py (Actor entry point)
    ↓
modules/scraper.py (browser automation)
    ↓
modules/proxy_manager.py (proxy rotation)
    ↓
modules/data_extractor.py (data extraction)
    ↓
Apify Dataset (output)
    ↓
User Downloads Results
```

## Key Features

### Input Modes
1. **Keyword + Location** - Search by keywords and locations
2. **URL Mode** - Scrape from Google Maps URLs

### Proxy Support
1. **Apify Proxy** - Use Apify's residential proxies (recommended)
2. **Custom Proxies** - Bring your own proxies (cheaper)

### Output
- Apify Dataset (JSON)
- Downloadable as CSV, JSON, Excel
- 15+ fields per business

### Advanced Features
- Parallel scraping (5 tabs simultaneously)
- Email extraction from websites
- Smart proxy rotation
- CAPTCHA detection and retry
- Deduplication
- Real-time progress tracking

## Dependencies

### Python Packages
- `apify>=3.0.0` - Apify SDK
- `playwright>=1.40.0` - Browser automation
- `pandas>=2.1.0` - Data processing
- `requests>=2.31.0` - HTTP requests
- `beautifulsoup4>=4.12.0` - HTML parsing
- `lxml>=4.9.0` - XML/HTML parser

### System Requirements
- Python 3.9+
- Chromium browser (installed via Playwright)
- 2GB RAM minimum
- Internet connection

## Environment Variables

Optional environment variables:
- `APIFY_TOKEN` - Apify API token (auto-set by platform)
- `APIFY_PROXY_PASSWORD` - Apify proxy password (auto-set)

## Storage

### Apify Dataset
- Stores scraped business data
- Accessible via Apify API
- Downloadable in multiple formats

### Key-Value Store
- Stores actor input
- Temporary data storage
- Managed by Apify platform

## Performance

- **Speed**: 10-15 seconds per query
- **Throughput**: 4-6 queries per minute
- **Parallel**: 5 tabs simultaneously
- **Results**: Up to 120 businesses per query

## Cost Optimization

### Reduce Costs
- Use custom proxies instead of Apify proxy (save 60%)
- Disable email extraction (faster = cheaper)
- Lower maxResultsPerQuery (20-40 instead of 60)
- Run during off-peak hours

### Typical Costs
- **With Apify proxy**: ~$0.75-1.00 per 1,000 businesses
- **With custom proxy**: ~$0.20-0.30 per 1,000 businesses

## Security

- Proxy credentials not in git
- Environment variables for sensitive data
- Input validation on all parameters
- Rate limiting to prevent abuse

## Maintenance

### Regular Updates
- Monitor Google Maps changes
- Update selectors if needed
- Optimize performance
- Fix bugs promptly

### User Support
- Respond to issues quickly
- Update documentation
- Add requested features
- Maintain high rating

## Deployment

### To Apify Platform
1. Push code to GitHub
2. Import to Apify from GitHub
3. Build actor
4. Test with sample input
5. Publish to store

### Updates
- Push changes to GitHub
- Apify auto-rebuilds
- Test before publishing
- Update version number

---

**Status**: ✅ Production Ready  
**Version**: 1.0.0  
**Last Updated**: November 17, 2025
