# Troubleshooting Guide

## Issue: Scraper not working / Browser not opening

### Quick Fixes:

**1. Check if server is running:**
```bash
# Should see: Running on http://127.0.0.1:5000
```

**2. Hard refresh browser:**
- Press `Ctrl + Shift + R` (Windows/Linux)
- Press `Cmd + Shift + R` (Mac)

**3. Check browser console:**
- Press `F12` to open DevTools
- Look for errors in Console tab
- Look for failed network requests in Network tab

**4. Verify headless mode is OFF:**
- Open `config.py`
- Check: `HEADLESS = False`
- If True, change to False to see browser

**5. Test with simple query:**
- Keyword: `restaurant`
- Location: `Miami`
- Click "Start Scraping"
- Browser should open within 5-10 seconds

---

## Issue: Map not showing / Half loaded

### Fixes:

**1. Check internet connection:**
- Map needs to download tiles from OpenStreetMap
- Requires active internet connection

**2. Wait for scraping to start:**
- Map initializes when page loads
- Markers appear after businesses are scraped
- Give it 10-15 seconds after clicking "Start Scraping"

**3. Check browser console:**
```javascript
// Open console (F12) and type:
console.log(map);
// Should show Leaflet map object, not null
```

**4. Verify Leaflet loaded:**
```javascript
// In console:
console.log(typeof L);
// Should show "object", not "undefined"
```

**5. Check if map div exists:**
```javascript
// In console:
console.log(document.getElementById('scrapingMap'));
// Should show <div id="scrapingMap"></div>
```

---

## Issue: No markers on map

### Reasons:

**1. No businesses scraped yet:**
- Wait for scraping to complete
- Markers appear as businesses are found

**2. Businesses have no coordinates:**
- Some businesses don't have lat/lng on Google Maps
- Map only shows businesses with valid coordinates

**3. Coordinates are invalid:**
- Check if latitude/longitude are not 0 or NaN
- Map skips invalid coordinates

**4. Map not initialized:**
- Check console for "Map initialized successfully"
- If not there, map didn't load

---

## Issue: Scraping starts but no results

### Checks:

**1. Proxy issues:**
- Check if proxies are valid in `proxies.txt`
- Format: `ip:port:username:password`

**2. CAPTCHA detected:**
- Check logs for "CAPTCHA detected"
- Try different proxy
- Wait a few minutes and retry

**3. Network timeout:**
- Check logs for "Timeout" errors
- Increase timeouts in `config.py`

**4. No results found:**
- Google Maps might not have businesses for that search
- Try different keyword/location

---

## Testing Steps:

### 1. Test Server:
```bash
python app.py
# Should see: Running on http://127.0.0.1:5000
```

### 2. Test Frontend:
- Go to http://127.0.0.1:5000
- Should see form with tabs
- Should see empty map on right side

### 3. Test Scraping:
- Enter: Keyword = "gym", Location = "Miami"
- Click "Start Scraping"
- Browser should open (if HEADLESS = False)
- Should see Google Maps loading
- Wait 30-60 seconds
- Should see results appear

### 4. Test Map:
- After scraping starts, map should show markers
- Click marker to see popup
- Popup should show business details

---

## Common Errors:

### Error: "No proxy available"
**Fix:** Add valid proxies to `proxies.txt`

### Error: "CAPTCHA detected"
**Fix:** Use different proxy or wait before retrying

### Error: "Failed to initialize browser"
**Fix:** 
- Install Playwright: `playwright install chromium`
- Check if Chromium is installed

### Error: "Leaflet is not defined"
**Fix:**
- Check internet connection
- Leaflet CDN might be blocked
- Hard refresh browser

### Error: "Map container not found"
**Fix:**
- Map div might not be in DOM yet
- Check if status section is visible
- Map only shows when scraping starts

---

## Debug Mode:

### Enable verbose logging:

**1. Open browser console (F12)**

**2. Check for errors:**
- Red errors in Console tab
- Failed requests in Network tab

**3. Check map status:**
```javascript
console.log('Map:', map);
console.log('Markers:', markers);
console.log('Business Data:', businessData);
```

**4. Check if Leaflet loaded:**
```javascript
console.log('Leaflet version:', L.version);
```

---

## Still Not Working?

### Last Resort:

**1. Clear browser cache:**
- Settings → Privacy → Clear browsing data
- Check "Cached images and files"
- Clear data

**2. Try different browser:**
- Chrome
- Firefox
- Edge

**3. Restart everything:**
```bash
# Stop server (Ctrl+C)
# Restart
python app.py
```

**4. Check file versions:**
- Ensure all files are updated
- Check `?v=3` in HTML links

**5. Disable browser extensions:**
- Ad blockers might block OpenStreetMap
- Try incognito/private mode

---

## Contact Info:

If still having issues, check:
1. Server logs in terminal
2. Browser console errors
3. Network tab for failed requests

Provide these details when asking for help!
