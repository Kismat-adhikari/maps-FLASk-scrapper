# Bulk Upload Guide

## File Upload Feature

You can now upload CSV or Excel files to scrape multiple queries at once. The file supports **three modes**:

### Mode 1: Keyword + Location (Traditional)
Upload a file with `keyword` and `zip_code` (or `location`) columns.

**Example:**
```csv
keyword,zip_code
restaurants,10001
coffee shops,90210
plumbers,Miami
dentists,33101
```

### Mode 2: URL Only
Upload a file with just a `url` column containing Google Maps URLs.

**Example:**
```csv
url
https://www.google.com/maps/search/restaurants+new+york
https://www.google.com/maps/search/coffee+miami
https://www.google.com/maps/place/Business+Name/@40.7308,-73.9973,17z
```

### Mode 3: Mixed (Keyword + URL)
Upload a file with both types - some rows with keywords, some with URLs.

**Example:**
```csv
keyword,zip_code,url
restaurants,10001,
coffee shops,90210,
,,https://www.google.com/maps/search/gyms+new+york
plumbers,Miami,
,,https://www.google.com/maps/place/Business+Name/@40.7308,-73.9973,17z
```

## Column Names

The parser supports flexible column names:
- **keyword**: The search keyword (e.g., "restaurants", "plumbers")
- **zip_code** OR **location**: The location (zip code, city, or address)
- **url**: Google Maps URL (search URL or business URL)

## File Formats

- **CSV**: `.csv` files
- **Excel**: `.xlsx` or `.xls` files

## How to Use

1. Go to the web interface at http://127.0.0.1:5000
2. Click the **"File Upload"** tab
3. Click **"Choose file"** or drag and drop your file
4. Click **"Start Scraping"**
5. The scraper will process all rows in your file

## Download Template

Click the **"📥 Download Template"** link in the File Upload tab to get a sample CSV file with all three modes.

## Validation Rules

Each row must have:
- **Either** `keyword` + `zip_code` (or `location`)
- **OR** a valid Google Maps `url`
- Empty rows are skipped

## Examples

### Example 1: Pure Keyword Search
```csv
keyword,location
restaurants,New York
coffee shops,Los Angeles
plumbers,Miami
dentists,Chicago
```

### Example 2: Pure URL Search
```csv
url
https://www.google.com/maps/search/restaurants+10001
https://www.google.com/maps/search/coffee+90210
https://www.google.com/maps/search/plumbers+miami
```

### Example 3: Mixed Mode
```csv
keyword,zip_code,url
restaurants,10001,
,,https://www.google.com/maps/search/coffee+90210
plumbers,Miami,
,,https://www.google.com/maps/place/Specific+Business/@40.7308,-73.9973,17z
dentists,Chicago,
```

## Tips

- Use **search URLs** to scrape up to 60 businesses per URL
- Use **business URLs** to scrape specific businesses (1 per URL)
- Mix both types in one file for maximum flexibility
- The scraper processes rows sequentially
- Results are saved incrementally to CSV as they're scraped
