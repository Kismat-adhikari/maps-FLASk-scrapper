# Apify Actor Conversion Guide

Use this prompt when converting any scraper (YouTube, Reddit, Twitter, etc.) to Apify Actor.

---

## PROMPT FOR AI ASSISTANT:

I have a working [YouTube/Reddit/Twitter/etc.] scraper that works locally. I need to convert it to an Apify Actor that's production-ready and stable.

### CRITICAL REQUIREMENTS:

1. **Use Apify SDK properly**
   - `Actor.get_input()` for reading input
   - `Actor.push_data()` for saving results
   - `Actor.set_status_message()` for progress updates

2. **Support both Apify proxy AND custom proxies**
   - Apify proxy: Build proper URL with groups and password
   - Custom proxies: Support array of proxies with rotation
   - Make it easy to switch between them

3. **Implement proper proxy rotation**
   - Configurable threshold (default: 10-14 requests)
   - Rotate even if proxy is working (avoid patterns)
   - Handle proxy failures gracefully

4. **Use conservative parallel processing**
   - Start with 2-3 concurrent operations
   - Don't use 5+ parallel tabs/requests (causes freezing in Apify)
   - Add staggered delays between starting operations (2s)

5. **Set generous timeouts**
   - 90 seconds for page loads (Apify proxy is slow)
   - 20 seconds for element waits
   - 60 seconds for business page navigation
   - Don't use 30s timeouts (too short for residential proxies)

6. **Add proper error handling and retry logic**
   - 3-4 retry attempts for failed operations
   - Log errors clearly
   - Continue on single failures, don't crash entire run

7. **Create INPUT_SCHEMA.json**
   - All configuration options
   - Clear descriptions
   - Sensible defaults
   - Validation rules

8. **Test locally first**
   - Verify scraper works with test data
   - Then optimize for Apify's containerized environment
   - Test with small dataset (5-10 items) before scaling

9. **Add delays to avoid rate limiting**
   - 2-3 seconds between batches
   - 2 seconds between starting parallel operations
   - 3 seconds after page load for JavaScript to settle

10. **Implement proper cleanup**
    - Close browsers
    - Close connections
    - Clean up temporary files

### PERFORMANCE OPTIMIZATION:

- **Start conservative** (2 parallel), then increase if stable
- **Custom proxies** are often faster than Apify's residential proxies
- **Staggered delays** between starting parallel operations
- Use **'load'** wait_until for critical pages, **'domcontentloaded'** for speed
- **Email extraction** doubles scraping time - make it optional

### COMMON PITFALLS TO AVOID:

❌ **Don't use 5+ parallel operations** on Apify (causes freezing)
❌ **Don't use 30s timeouts** (too short for Apify proxy)
❌ **Don't forget to configure Apify proxy URL** properly with groups and password
❌ **Don't skip proxy rotation** (even if working, rotate every 10-14 requests)
❌ **Don't test with large datasets first** (always start with 5-10 items)
❌ **Don't use Apify's free residential proxy** for heavy scraping (too slow, times out)
❌ **Don't forget delays** between operations (Google/sites will block you)

### APIFY PROXY CONFIGURATION:

```python
# Correct way to configure Apify proxy
import os

proxy_groups = ['RESIDENTIAL']  # or ['SHADER'] for datacenter
apify_proxy_password = os.getenv('APIFY_PROXY_PASSWORD', '')

if apify_proxy_password:
    groups_str = '+'.join(proxy_groups)
    proxy_url = f"http://groups-{groups_str}:{apify_proxy_password}@proxy.apify.com:8000"
    launch_options['proxy'] = {'server': proxy_url}
```

### DOCKERFILE TEMPLATE:

```dockerfile
FROM apify/actor-python-playwright:3.11

COPY . ./
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium

CMD ["python", "main.py"]
```

### TESTING CHECKLIST:

- [ ] Works locally with test input
- [ ] Works on Apify with 5 items
- [ ] Works on Apify with 20 items
- [ ] Handles proxy failures gracefully
- [ ] Completes without timeouts
- [ ] Extracts all required data fields
- [ ] Saves data to Apify Dataset correctly
- [ ] Respects maxResults limit
- [ ] Rotates proxies properly

---

## LESSONS LEARNED FROM GOOGLE MAPS SCRAPER:

1. **Apify's residential proxy is VERY slow** - Custom proxies worked much better
2. **5 parallel tabs caused freezing** - Reduced to 2-3 for stability
3. **30s timeout was too short** - Increased to 90s for page loads
4. **Email extraction doubles time** - Made it optional
5. **Proxy rotation is critical** - Even working proxies should rotate
6. **Small delays prevent blocking** - 2-3s between operations
7. **Test with 5 items first** - Don't waste time on large failed runs
8. **maxResultsPerQuery wasn't working** - Had to implement limit properly

---

**Use this guide to convert any scraper to Apify and avoid 4+ hours of debugging!**
