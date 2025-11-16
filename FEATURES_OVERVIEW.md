# Google Maps Scraper - Complete Features Overview

## What This Application Does

This is a professional web-based Google Maps scraper that extracts business information from Google Maps without requiring any API keys. It's designed to be fast, reliable, and user-friendly with a modern interface that shows real-time progress.

---

## Core Functionality

### Business Data Extraction

The scraper collects comprehensive information about businesses from Google Maps:

- **Basic Information**: Business name, full address, phone number
- **Location Data**: GPS coordinates (latitude/longitude), plus codes
- **Online Presence**: Website URLs, email addresses (extracted from websites)
- **Ratings & Reviews**: Star ratings, review counts
- **Business Details**: Categories, opening hours, descriptions
- **Direct Links**: Google Maps URLs for each business

### Smart Email Discovery

One of the standout features is intelligent email extraction:

- First checks if email is available directly on Google Maps
- If not found, automatically visits the business website
- Searches the homepage for email addresses
- If still not found, checks the contact page
- Filters out fake emails (like example@domain.com)
- Returns to Google Maps to continue scraping

This happens automatically for every business, giving you the most complete contact information possible.

---

## Three Ways to Search

### 1. Keyword + Location Search

The simplest method - just like searching on Google Maps:

- Enter a keyword (e.g., "restaurants", "gyms", "dentists")
- Enter a location (city name, zip code, or address)
- Click "Start Scraping"
- The scraper finds up to 60 businesses matching your search

**Perfect for**: Finding all businesses of a certain type in a specific area.

### 2. URL Input

Paste Google Maps URLs directly:

**Option A - Search URL**: Paste a Google Maps search URL to scrape all results from that search. Great for complex searches you've already refined on Google Maps.

**Option B - Business URLs (Bulk)**: Paste multiple specific business URLs (one per line) to scrape exact businesses you've already identified.

**Perfect for**: Scraping specific businesses or using pre-made Google Maps searches.

### 3. File Upload (Bulk Processing)

Upload a CSV or Excel file with multiple searches:

- Can contain keyword + location pairs
- Can contain Google Maps URLs
- Can mix both types in one file
- Process dozens or hundreds of searches automatically

**Perfect for**: Large-scale data collection across multiple locations or categories.

---

## Live Scraping Dashboard

### Real-Time Progress Tracking

Watch your scraping happen in real-time with multiple visual indicators:

**Currently Scraping Banner**: Shows which business is being processed right now with an orange highlight.

**Progress Bar**: Visual percentage bar showing overall completion (e.g., "Processing 3 of 10 queries").

**Statistics Cards**: Three live counters showing:
- Active proxy being used (IP masked for security)
- Number of businesses successfully scraped (green)
- Number of failed attempts (red)

**Live Activity Log**: Scrolling console-style log showing every action:
- When scraping starts
- Which proxy is being used
- Each business as it's found
- Success and error messages
- Color-coded entries (green for success, red for errors, blue for info)

### Interactive Live Map

The crown jewel of the interface - a real-time map showing exactly where businesses are located:

**Powered by MapLibre GL JS** (upgraded from Leaflet for better performance):
- Modern WebGL-powered rendering for smooth animations
- Hardware-accelerated graphics
- Better performance with many markers
- Future-ready for vector tiles and 3D features

**Visual Design**:
- Clean, modern OpenStreetMap tiles
- Professional pin-style markers (teardrop shape like Google Maps)
- Gradient colors for visual depth
- Smooth shadows and animations

**Pin Colors & Status**:
- **Green pins**: Successfully scraped businesses
- **Yellow pins**: Currently being scraped (pulsing animation)
- **Red pins**: Failed to scrape
- **Grey pins**: Waiting to be scraped

**Animations**:
- Pins drop from the sky when added (smooth fall animation)
- Yellow pins pulse to show active scraping
- Map smoothly flies to show all markers
- Hover effects on all interactive elements

**Interactivity**:
- **Hover over pins**: Dark tooltip shows business name
- **Click pins**: Beautiful popup card appears with:
  - Business name in gradient header
  - Full address with location icon
  - Phone number with phone icon
  - Rating and review count with star icon
  - "View on Google Maps" link (opens in new tab)
- **Zoom & Pan**: Standard map controls, scroll to zoom, drag to pan
- **Auto-centering**: Map automatically adjusts to show all businesses

**Real-Time Updates**:
- Map updates every 1.5 seconds as new businesses are found
- Pins appear instantly when businesses are scraped
- No page refresh needed
- Smooth, lag-free performance even with 50+ pins

---

## Proxy Management

### Automatic Proxy Rotation

The scraper uses residential proxies to avoid detection and rate limiting:

**How It Works**:
- Loads proxies from a text file (one per line)
- Automatically rotates through proxies
- Switches proxy after every 14 requests
- Marks failed proxies and skips them
- Shows current proxy in dashboard (IP masked for privacy)

**Benefits**:
- Avoids IP bans from Google
- Bypasses rate limits
- Enables large-scale scraping
- Automatic failover if proxy fails

### CAPTCHA Detection

Smart CAPTCHA handling:
- Automatically detects if Google shows a CAPTCHA
- Marks that proxy as failed
- Switches to next proxy automatically
- Retries the search with new proxy
- Up to 3 retry attempts per query

---

## Performance Optimizations

### Speed Enhancements

The scraper has been optimized for maximum speed while maintaining data quality:

**Reduced Wait Times**:
- Page loads: 30 seconds (down from 60)
- Between actions: 1 second (down from 2-3)
- Website visits: 5 seconds (down from 10)

**Smart Email Extraction**:
- Skips website if email found on Google Maps
- Stops searching once email is found
- Doesn't check contact page if homepage has email

**Headless Mode Option**:
- Can run browser in background (no visible window)
- Faster rendering without GUI
- Toggle in config file

**Result**: Scraping is now 2x faster - approximately 20-25 seconds per business instead of 47 seconds.

### Incremental Saving

Data is saved as it's collected:
- Each business is written to CSV immediately after scraping
- If scraper crashes, you don't lose data
- Can stop scraping anytime and keep what's been collected
- Results file is created at the start with timestamp

---

## Data Export

### CSV Output

All scraped data is automatically saved to CSV files:

**File Location**: `output/` folder
**File Naming**: `{keyword}-{date}.csv` (e.g., `restaurants-2025-11-16.csv`)

**Columns Included**:
- Business Name
- Full Address
- Latitude & Longitude
- Phone Number
- Email Address
- Website URL
- Rating (stars)
- Review Count
- Category
- Opening Hours
- Plus Code
- CID (Google Maps ID)
- Google Maps URL
- Description
- Keyword (what you searched for)
- Zip Code/Location (where you searched)

**Download Options**:
- Click "Download CSV" button in results section
- File downloads immediately to your browser
- Can also access files directly from output folder

---

## User Interface Design

### Modern, Professional Look

The interface is designed to be both beautiful and functional:

**Color Scheme**:
- Purple/blue gradient headers
- Green for success indicators
- Red for errors/failures
- Orange for active/in-progress items
- Clean white backgrounds with subtle shadows

**Layout**:
- Responsive design (works on desktop and mobile)
- Card-based interface with rounded corners
- Smooth animations and transitions
- Clear visual hierarchy
- Intuitive tab navigation

**Typography**:
- System fonts for fast loading
- Clear, readable sizes
- Proper contrast for accessibility
- Bold weights for emphasis

### Three-Tab Input System

Clean organization of input methods:

**Tab 1 - Keyword Search**: Simple form with two fields
**Tab 2 - URL Input**: Two options (search URL or bulk business URLs)
**Tab 3 - File Upload**: Drag-and-drop file upload with format guide

Tabs have:
- Active state highlighting
- Smooth transitions
- Clear labels
- Helpful hints and examples

### Results Display

**Results Table**:
- Clean, striped rows for readability
- Hover effects on rows
- Status badges (green "Scraped" indicator)
- Clickable business names (open Google Maps)
- Sortable columns
- Smooth animations when rows appear

**Completion Message**:
- Large green checkmark
- "Scraping Completed!" message
- Appears when all queries finish
- Celebratory feel

---

## Technical Architecture

### Frontend (What You See)

**Technologies**:
- HTML5 for structure
- CSS3 for styling and animations
- Vanilla JavaScript for interactivity
- MapLibre GL JS 3.6.2 for mapping (WebGL-powered)
- OpenStreetMap for map tiles

**Features**:
- Real-time polling (checks for updates every 1.5 seconds)
- Dynamic DOM updates (no page refreshes)
- Smooth animations and transitions
- Responsive design
- Browser-based (no installation needed)

### Backend (What Powers It)

**Technologies**:
- Python 3.8+ for core logic
- Flask for web server
- Playwright for browser automation
- Pandas for data processing

**Architecture**:
- Modular design (separate files for scraping, data extraction, proxies)
- Async/await for concurrent operations
- Thread-based scraping (doesn't block web interface)
- State management for real-time updates

**No Backend Changes for Map**:
- Map uses existing latitude/longitude data
- No new API endpoints needed
- No changes to scraping logic
- Pure frontend enhancement

---

## Use Cases

### Business Development

- Find potential clients in specific industries
- Build targeted outreach lists
- Research competitors in different markets
- Identify business opportunities in new areas

### Marketing & Sales

- Create email marketing lists
- Build cold calling databases
- Research local businesses for partnerships
- Analyze market density by location

### Data Analysis

- Study business distribution patterns
- Analyze rating trends by area
- Compare business density across cities
- Research market saturation

### Lead Generation

- Collect contact information at scale
- Build industry-specific databases
- Create geo-targeted lead lists
- Export data for CRM systems

---

## Key Advantages

### No API Keys Required

Unlike official Google Maps API:
- No registration needed
- No credit card required
- No usage limits
- No per-request costs
- Completely free to use

### Comprehensive Data

Collects more information than many paid services:
- Email addresses (extracted from websites)
- Full contact details
- GPS coordinates
- Direct Google Maps links
- Business descriptions

### Visual Progress Tracking

See exactly what's happening:
- Live map shows business locations
- Real-time log shows each action
- Progress bar shows completion
- Statistics show success rate

### Flexible Input Methods

Three ways to search:
- Simple keyword search
- Direct URL input
- Bulk file upload

### Fast & Efficient

Optimized for speed:
- 2x faster than original version
- Parallel processing where possible
- Smart caching and skipping
- Incremental saving

### Professional Output

Clean, usable data:
- Standard CSV format
- All fields labeled clearly
- Ready for import to Excel, CRM, etc.
- Timestamped files for organization

---

## Limitations & Considerations

### Ethical Use

This tool should be used responsibly:
- Respect robots.txt and terms of service
- Don't overload Google's servers
- Use for legitimate business purposes
- Comply with data protection laws (GDPR, etc.)

### Technical Limitations

- Scrapes up to 60 businesses per search (Google Maps limit)
- Requires valid proxies to avoid rate limiting
- Some businesses may not have complete information
- Email extraction depends on website structure
- Speed depends on proxy quality and internet connection

### Data Accuracy

- Data is as accurate as Google Maps
- Some fields may be "Not given" if unavailable
- Email addresses may not always be found
- Coordinates may be approximate for some businesses

---

## Future Enhancement Possibilities

### Potential Features

- Export to multiple formats (JSON, Excel, SQL)
- Scheduled scraping (run automatically at set times)
- Duplicate detection and removal
- Data enrichment (add social media links, etc.)
- Advanced filtering (by rating, review count, etc.)
- Comparison mode (compare multiple locations)
- Historical tracking (track changes over time)
- API endpoint (integrate with other tools)

### Map Enhancements

With MapLibre GL JS, we can now add:
- Vector tiles for crisper, faster maps
- 3D building extrusions
- Clustering (group nearby pins when zoomed out)
- Heatmap mode (show business density)
- Filter pins by status
- Search within map results
- Export map as image
- Custom pin icons by category
- Custom map themes and branding
- Offline map support

---

## Getting Started

### Quick Start

1. Ensure Python 3.8+ is installed
2. Install dependencies: `pip install -r requirements.txt`
3. Install Playwright browser: `playwright install chromium`
4. Add proxies to `proxies.txt` file
5. Run: `python app.py`
6. Open browser to `http://127.0.0.1:5000`
7. Enter search and click "Start Scraping"

### First Scrape

Try a simple test:
- Keyword: `restaurant`
- Location: `Miami`
- Click "Start Scraping"
- Watch the map populate with pins
- Check results table for data
- Download CSV when complete

---

## Summary

This Google Maps scraper is a complete, professional solution for extracting business data at scale. It combines powerful scraping capabilities with a beautiful, intuitive interface that makes the process transparent and engaging. The live map feature transforms what could be a boring data collection task into a visual, interactive experience where you can literally watch your data being collected in real-time.

Whether you're building a lead list, researching a market, or analyzing business patterns, this tool provides everything you need in one clean, efficient package - and it's completely free to use.
