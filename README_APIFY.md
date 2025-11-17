# Google Maps Scraper - Apify Actor

Scrape business data from Google Maps **without API keys**. Extract names, addresses, phones, emails, ratings, reviews, and more.

## 🚀 Features

- ✅ **No API Key Required** - Scrape Google Maps without Google API
- ✅ **Multiple Input Modes** - Keywords + locations or direct URLs
- ✅ **Email Extraction** - Extract emails from business websites
- ✅ **Smart Proxy Rotation** - Automatic rotation to avoid blocks
- ✅ **Fast & Reliable** - Parallel scraping with Playwright
- ✅ **Rich Data** - Names, addresses, phones, websites, ratings, reviews, coordinates
- ✅ **Apify Integration** - Results saved to Apify Dataset

## 📊 Output

Each business includes:

```json
{
  "name": "Business Name",
  "full_address": "123 Main St, New York, NY 10001",
  "latitude": 40.7308,
  "longitude": -73.9973,
  "phone": "(212) 555-1234",
  "website": "https://example.com",
  "email": "contact@example.com",
  "rating": 4.5,
  "review_count": 234,
  "category": "Restaurant",
  "opening_hours": "Mon-Fri: 9AM-5PM",
  "plus_code": "8Q7X+2G New York",
  "cid": "1234567890",
  "url": "https://www.google.com/maps/place/...",
  "description": "Business description...",
  "keyword": "restaurants",
  "zip_code": "10001"
}
```

## 🎯 Use Cases

- **Lead Generation** - Find potential customers
- **Market Research** - Analyze competitors
- **Data Enrichment** - Add business details to your database
- **Local SEO** - Track local business listings
- **Sales Prospecting** - Build targeted contact lists

## 📝 Input

### Mode 1: Keyword + Location

Search by keywords and locations:

```json
{
  "mode": "keyword",
  "keywords": ["restaurants", "coffee shops"],
  "locations": ["10001", "New York", "Miami"],
  "maxResultsPerQuery": 60
}
```

This will scrape:
- Restaurants in 10001
- Restaurants in New York
- Restaurants in Miami
- Coffee shops in 10001
- Coffee shops in New York
- Coffee shops in Miami

### Mode 2: Google Maps URLs

Provide direct Google Maps URLs:

```json
{
  "mode": "url",
  "urls": [
    "https://www.google.com/maps/search/restaurants+new+york",
    "https://www.google.com/maps/place/Business+Name/@40.7308,-73.9973,17z"
  ]
}
```

## ⚙️ Configuration

### Proxy Options

**Option 1: Apify Proxy (Recommended)**
- Automatic proxy management
- Residential IPs for best results
- Additional cost applies
- Set `useApifyProxy: true`

**Option 2: Custom Proxies**
- Bring your own proxies
- Format: `IP:PORT:USERNAME:PASSWORD`
- Set `useApifyProxy: false`
- Provide `customProxies` array

### Advanced Settings

- **maxResultsPerQuery** (1-120): Businesses per query
- **headless** (true/false): Run browser in headless mode
- **extractEmails** (true/false): Extract emails from websites
- **deduplicate** (true/false): Remove duplicate businesses
- **rotationThreshold** (1-100): Rotate proxy after N requests

## 💰 Cost Estimate

### Apify Platform Costs
- **Compute**: ~$0.25 per 1,000 businesses
- **Proxy** (if using Apify): ~$0.50 per 1,000 businesses
- **Total**: ~$0.75 per 1,000 businesses

### Example Runs
- 100 businesses: ~$0.08
- 1,000 businesses: ~$0.75
- 10,000 businesses: ~$7.50

*Costs vary based on proxy usage and scraping speed*

## 🔧 Tips for Best Results

### 1. Use Specific Keywords
❌ Bad: "business"
✅ Good: "italian restaurants", "plumbers near me"

### 2. Use Precise Locations
❌ Bad: "USA"
✅ Good: "10001", "Miami, FL", "Brooklyn, NY"

### 3. Optimize Max Results
- Start with 20-60 results per query
- Increase if you need more data
- Higher numbers = longer runtime

### 4. Use Apify Proxy
- More reliable than custom proxies
- Residential IPs avoid blocks
- Worth the extra cost

### 5. Enable Email Extraction
- Adds valuable contact data
- Slightly slower but worth it
- Great for lead generation

## 📈 Performance

- **Speed**: 10-15 seconds per query
- **Throughput**: 4-6 queries per minute
- **Results**: Up to 120 businesses per query
- **Success Rate**: 95%+ with Apify proxy

## 🛡️ Anti-Detection Features

- Smart proxy rotation
- Random delays between requests
- Browser fingerprint randomization
- CAPTCHA detection and handling
- Automatic retry on failures

## 🚨 Limitations

- Google Maps rate limits apply
- Some businesses may have incomplete data
- Email extraction requires visiting websites (slower)
- Maximum 120 results per query (Google Maps limit)

## 📞 Support

Need help? Contact us:
- Email: support@yourdomain.com
- Documentation: Full docs in GitHub repo
- Issues: Report bugs on GitHub

## 🔐 Privacy & Legal

- This actor scrapes publicly available data
- Respect robots.txt and terms of service
- Use responsibly and ethically
- Don't scrape personal data without consent

## 🎓 Examples

### Example 1: Local Restaurants
```json
{
  "mode": "keyword",
  "keywords": ["restaurants"],
  "locations": ["New York, NY"],
  "maxResultsPerQuery": 60,
  "useApifyProxy": true,
  "extractEmails": true
}
```

### Example 2: Multiple Cities
```json
{
  "mode": "keyword",
  "keywords": ["coffee shops", "cafes"],
  "locations": ["10001", "90210", "33101"],
  "maxResultsPerQuery": 40,
  "useApifyProxy": true
}
```

### Example 3: Specific URLs
```json
{
  "mode": "url",
  "urls": [
    "https://www.google.com/maps/search/plumbers+miami",
    "https://www.google.com/maps/search/dentists+chicago"
  ],
  "maxResultsPerQuery": 60,
  "useApifyProxy": true
}
```

## 🔄 Updates

- **v1.0.0** - Initial release
- Regular updates for Google Maps changes
- New features based on user feedback

## ⭐ Rate This Actor

If you find this actor useful, please rate it 5 stars! Your feedback helps us improve.

---

**Built with ❤️ using Playwright and Apify SDK**
