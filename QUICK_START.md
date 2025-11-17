# 🚀 Quick Start Guide - Improved Features

## What's New?

I've just added several powerful improvements to your Google Maps scraper:

### ✅ Implemented Features

1. **Smart Deduplication** - Automatically removes duplicate businesses
2. **Proxy Health Dashboard** - Monitor proxy performance at `/dashboard`
3. **Improved Email Extraction** - Faster, more accurate, configurable
4. **Notification System** - Get alerts when scraping completes
5. **Better Configuration** - More control over scraper behavior
6. **Startup Validation** - Checks proxies before starting

## How to Use New Features

### 1. Configure Your Settings

Edit `config.py` to customize behavior:

```python
# Deduplication
DEDUPLICATE_RESULTS = True  # Remove duplicates
DEDUP_METHOD = 'cid'  # Options: 'cid', 'name_address', 'none'

# Email Extraction
EXTRACT_EMAILS_FROM_WEBSITES = True  # Enable/disable
EMAIL_EXTRACTION_TIMEOUT = 3  # Max seconds per website

# Performance
PARALLEL_TABS = 5  # Scrape 5 businesses at once
DELAY_BETWEEN_QUERIES = 2  # Seconds between queries

# Validation
MIN_PROXY_COUNT = 1  # Minimum proxies required

# Notifications (optional)
ENABLE_NOTIFICATIONS = False
NOTIFICATION_WEBHOOK = 'https://hooks.slack.com/...'  # Slack webhook
```

### 2. View Proxy Health Dashboard

1. Start your scraper: `python app.py`
2. Open browser to: `http://127.0.0.1:5000/dashboard`
3. See real-time proxy statistics:
   - Success rates
   - Failed requests
   - Best performing proxy
   - Color-coded health status

### 3. Enable Notifications

To get notified when scraping completes:

```python
# In config.py
ENABLE_NOTIFICATIONS = True
NOTIFICATION_WEBHOOK = 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
```

**Slack Webhook Setup:**
1. Go to https://api.slack.com/messaging/webhooks
2. Create a new webhook
3. Copy the URL to `config.py`
4. You'll get messages like:
   ```
   Scraping Completed Successfully!
   
   Statistics:
   - Total Queries: 5
   - Successful: 5
   - Failed: 0
   - Businesses Found: 87
   - Unique Businesses: 82
   ```

### 4. Faster Email Extraction

The email extractor is now:
- **3x faster** (3 second timeout instead of 10)
- **More accurate** (better filtering)
- **Configurable** (can be disabled)

To disable email extraction entirely:
```python
EXTRACT_EMAILS_FROM_WEBSITES = False
```

### 5. Deduplication

Results are automatically deduplicated using Google's CID (business ID).

To change deduplication method:
```python
DEDUP_METHOD = 'name_address'  # Use name+address instead of CID
# or
DEDUP_METHOD = 'none'  # Disable deduplication
```

## Testing the Improvements

### Test 1: Deduplication
```bash
# Run a scrape that might have duplicates
# Check the logs for:
# "Deduplication: 100 -> 95 businesses"
```

### Test 2: Proxy Health
```bash
# Start scraping
# Visit http://127.0.0.1:5000/dashboard
# Watch proxy statistics update in real-time
```

### Test 3: Faster Scraping
```bash
# With PARALLEL_TABS = 5, you should see:
# - 5 businesses scraped simultaneously
# - Faster completion times
# - More efficient proxy usage
```

## What to Do Next

### Immediate (5 minutes)
1. ✅ Update `config.py` with your preferences
2. ✅ Test the proxy dashboard
3. ✅ Run a test scrape to see deduplication in action

### Short Term (1 hour)
1. 📦 Add database storage (see `IMPROVEMENTS.md`)
2. 🔒 Add rate limiting with Flask-Limiter
3. 🐳 Create Docker container for easy deployment

### Long Term (1 day)
1. 📅 Add scheduled scraping with APScheduler
2. 📊 Export to Google Sheets
3. 🤖 Add CAPTCHA solving integration

## Troubleshooting

### "Insufficient proxies" Error
```
ERROR: Insufficient proxies! Found 0, need at least 1
```
**Solution:** Add proxies to `proxies.txt` in format:
```
IP:PORT:USERNAME:PASSWORD
```

### Deduplication Not Working
**Check:** `Config.DEDUPLICATE_RESULTS = True` in `config.py`
**Check:** Logs show "Deduplication: X -> Y businesses"

### Dashboard Shows No Data
**Reason:** No scraping has been done yet
**Solution:** Run a scrape first, then check dashboard

### Email Extraction Too Slow
**Solution:** Reduce timeout in `config.py`:
```python
EMAIL_EXTRACTION_TIMEOUT = 2  # Reduce from 3 to 2 seconds
```
Or disable entirely:
```python
EXTRACT_EMAILS_FROM_WEBSITES = False
```

## Performance Tips

### For Maximum Speed
```python
PARALLEL_TABS = 5  # Max recommended
EXTRACT_EMAILS_FROM_WEBSITES = False  # Skip email extraction
EMAIL_EXTRACTION_TIMEOUT = 2  # If you need emails
DELAY_BETWEEN_QUERIES = 1  # Reduce delay (risky)
```

### For Maximum Data Quality
```python
PARALLEL_TABS = 3  # More stable
EXTRACT_EMAILS_FROM_WEBSITES = True  # Get all emails
EMAIL_EXTRACTION_TIMEOUT = 5  # More time per site
DEDUPLICATE_RESULTS = True  # Remove duplicates
DEDUP_METHOD = 'cid'  # Most accurate
```

### For Maximum Reliability
```python
PARALLEL_TABS = 3  # Fewer tabs = more stable
MIN_PROXY_COUNT = 5  # Require more proxies
ROTATION_THRESHOLD = 10  # Rotate proxies more often
DELAY_BETWEEN_QUERIES = 3  # More delay = less detection
```

## API Endpoints

### New Endpoints

**GET /dashboard**
- Visual proxy health dashboard
- Real-time statistics
- Color-coded health indicators

**GET /proxy-health**
- JSON API for proxy statistics
- Returns success rates, failure counts
- Identifies best performing proxy

Example response:
```json
{
  "proxy_stats": {
    "192.168.1.1:8080": {
      "success": 45,
      "failure": 5,
      "total": 50,
      "success_rate": 90.0
    }
  },
  "best_proxy": "192.168.1.1:8080",
  "total_proxies": 10
}
```

## Configuration Reference

### All New Config Options

```python
# Proxy Settings
MIN_PROXY_COUNT = 1  # Minimum proxies required to start

# Deduplication
DEDUPLICATE_RESULTS = True  # Enable deduplication
DEDUP_METHOD = 'cid'  # Method: 'cid', 'name_address', 'none'

# Email Extraction
EXTRACT_EMAILS_FROM_WEBSITES = True  # Enable email extraction
EMAIL_EXTRACTION_TIMEOUT = 3  # Max seconds per website

# Rate Limiting
DELAY_BETWEEN_QUERIES = 2  # Seconds between queries

# Notifications
ENABLE_NOTIFICATIONS = False  # Enable notifications
NOTIFICATION_EMAIL = None  # Email for notifications (future)
NOTIFICATION_WEBHOOK = None  # Webhook URL (Slack, Discord, etc.)

# Performance
PARALLEL_TABS = 5  # Number of simultaneous tabs
```

## Next Steps

Read `IMPROVEMENTS.md` for:
- 📦 Database storage implementation
- 🔒 Security enhancements
- 📅 Scheduled scraping
- 📊 Google Sheets export
- 🤖 CAPTCHA solving
- 🐳 Docker deployment
- And 20+ more improvements!

---

**Questions?** Check the logs in `scraper.log` for detailed information.

**Need help?** All improvements are documented in `IMPROVEMENTS.md`.

**Ready to deploy?** See the Docker section in `IMPROVEMENTS.md`.

Happy scraping! 🚀
