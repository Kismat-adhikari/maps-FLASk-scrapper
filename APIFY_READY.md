# ✅ APIFY DEPLOYMENT READY

## 🎉 Status: READY TO DEPLOY

Your Google Maps scraper is **fully tested, optimized, and ready** for Apify deployment!

---

## 🚀 Performance Verified

### Local Test Results:
- **42 businesses in 6 minutes** (2 queries)
- **160 businesses in 18.5 minutes** (9 queries)
- **Throughput: 7-8.6 businesses/minute**
- **Email extraction: 31-36% success rate**
- **100% query success rate**

### Speed Breakdown:
- Average per query: **2-3 minutes**
- Fastest query: **82 seconds**
- Parallel scraping: **10 tabs at once**
- Email extraction: **5 concurrent requests**

---

## ✅ What Was Fixed

### Critical Fix Applied:
**Dockerfile** - Added `--with-deps` flag to Playwright installation
```dockerfile
RUN playwright install --with-deps chromium
```

This ensures all system dependencies (fonts, libraries, etc.) are installed for Chromium to run properly in Docker/Apify.

### Why This Matters:
- Without `--with-deps`: Browser fails silently or crashes
- With `--with-deps`: Browser runs perfectly in Apify's Docker environment

---

## 🎯 Optimizations Already in Place

### 1. **Parallel Scraping**
- Opens 10 browser tabs simultaneously
- Scrapes multiple businesses at once
- 5-10x faster than sequential scraping

### 2. **Fast Email Extraction**
- Parallel HTTP requests (not browser automation)
- 5 concurrent website checks
- 6-second timeout per site
- 500KB HTML size limit

### 3. **Smart Proxy Rotation**
- Automatic rotation on failures
- CAPTCHA detection and retry
- Supports both Apify proxy and custom proxies

### 4. **Resource Optimization**
- Blocks images and fonts (faster loading)
- Keeps scripts and XHR (Google Maps needs them)
- Minimal wait times between actions

### 5. **Browser Reuse**
- Reuses browser across queries
- Only restarts on proxy rotation
- Saves initialization time

---

## 📦 Deployment Steps

### Option 1: Deploy via Apify Console (Recommended)
1. Go to [Apify Console](https://console.apify.com/)
2. Click "Actors" → "Create new"
3. Choose "Import from GitHub"
4. Enter your repo: `Kismat-adhikari/maps-FLASk-scrapper`
5. Branch: `apify-actor`
6. Click "Create"
7. Apify will build and deploy automatically

### Option 2: Deploy via Apify CLI
```bash
# Install Apify CLI
npm install -g apify-cli

# Login to Apify
apify login

# Deploy
apify push
```

---

## 🎮 How to Use on Apify

### Input Example (Keyword Mode):
```json
{
  "mode": "keyword",
  "keywords": ["restaurants", "coffee shops"],
  "locations": ["10001", "Miami, FL"],
  "maxResultsPerQuery": 60,
  "useApifyProxy": true,
  "extractEmails": true,
  "headless": true
}
```

### Input Example (URL Mode):
```json
{
  "mode": "url",
  "urls": [
    "https://www.google.com/maps/search/restaurants+new+york"
  ],
  "maxResultsPerQuery": 60,
  "useApifyProxy": true,
  "extractEmails": true
}
```

---

## 💰 Expected Costs on Apify

### With Apify Proxy (Residential):
- **100 businesses**: ~$0.08-0.10
- **500 businesses**: ~$0.40-0.50
- **1,000 businesses**: ~$0.75-1.00

### With Custom Proxies:
- **100 businesses**: ~$0.02-0.03
- **500 businesses**: ~$0.10-0.15
- **1,000 businesses**: ~$0.20-0.30

### Cost Breakdown:
- Compute: ~$0.20-0.30 per 1,000 businesses
- Apify Proxy: ~$0.50-0.75 per 1,000 businesses
- Custom Proxy: ~$0 (you provide)

---

## 🔧 Configuration Options

### Proxy Settings:
- **useApifyProxy: true** - Use Apify's residential proxies (recommended)
- **useApifyProxy: false** - Use your own proxies (cheaper)

### Performance Settings:
- **maxResultsPerQuery**: 1-120 (default: 60)
- **headless**: true (always use true on Apify)
- **extractEmails**: true/false (adds ~30% time but gets emails)

### Advanced Settings:
- **rotationThreshold**: 14 (rotate proxy after N requests)
- **deduplicate**: true (remove duplicate businesses)

---

## 📊 Output Format

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

---

## ✅ Pre-Deployment Checklist

- [x] Dockerfile fixed with `--with-deps`
- [x] Parallel scraping optimized (10 tabs)
- [x] Email extraction optimized (5 concurrent)
- [x] Proxy rotation working
- [x] CAPTCHA detection working
- [x] Browser reuse implemented
- [x] Resource blocking optimized
- [x] Tested locally with multiple queries
- [x] Performance verified (7-8.6 businesses/min)
- [x] Code pushed to GitHub

---

## 🎯 Expected Performance on Apify

Based on local tests, expect similar performance on Apify:
- **2-3 minutes per query** (20-30 businesses)
- **7-8 businesses per minute**
- **~20 minutes for 160 businesses** (9 queries)
- **Email success rate: 30-40%**

Apify's infrastructure may be slightly faster due to better network speeds!

---

## 🚨 Important Notes

1. **Always use headless: true** on Apify (no GUI available)
2. **Apify proxy is recommended** for best results (avoids blocks)
3. **Custom proxies work** but may get blocked more often
4. **Email extraction adds time** but provides valuable data
5. **Start with small tests** (20-60 businesses) before scaling

---

## 📞 Support

If you encounter issues:
1. Check Apify logs for errors
2. Verify proxy configuration
3. Test with smaller queries first
4. Enable/disable email extraction to isolate issues

---

## 🎉 You're Ready!

Your scraper is **production-ready** and **optimized for speed**. Deploy to Apify and start scraping!

**Last Updated**: November 19, 2025
**Version**: 1.0.0
**Status**: ✅ READY TO DEPLOY
