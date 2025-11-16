# Proxy Setup Guide

This guide explains how to configure proxies for the Google Maps Scraper.

## Why Proxies Are Needed

Google Maps may block or rate-limit requests from a single IP address. Using proxies helps:

- **Avoid IP bans** - Distribute requests across multiple IPs
- **Bypass rate limits** - Each proxy has its own rate limit
- **Prevent CAPTCHAs** - Reduce the chance of triggering CAPTCHA challenges
- **Increase reliability** - Continue scraping even if some proxies fail

## Proxy Format

Add your proxies to `proxies.txt` in the following format:

```
IP:PORT:USERNAME:PASSWORD
```

### Example

```
72.46.139.137:6697:myusername:mypassword
45.196.40.119:6197:myusername:mypassword
156.238.179.127:6695:myusername:mypassword
```

## Requirements

- **Minimum:** 1 proxy (not recommended)
- **Recommended:** 10 proxies for optimal rotation
- **Protocol:** HTTP/HTTPS proxies with authentication

## Proxy Types

### Residential Proxies (Recommended)
- **Pros:** Less likely to be detected, higher success rate
- **Cons:** More expensive
- **Use case:** Best for Google Maps scraping

### Datacenter Proxies
- **Pros:** Cheaper, faster
- **Cons:** More likely to be detected and blocked
- **Use case:** Can work but may trigger more CAPTCHAs

### Mobile Proxies
- **Pros:** Highest success rate, rarely blocked
- **Cons:** Most expensive
- **Use case:** Best for high-volume scraping

## Proxy Providers

Popular proxy providers (not affiliated):

1. **Bright Data** (formerly Luminati)
   - High-quality residential proxies
   - Good for Google Maps

2. **Smartproxy**
   - Affordable residential proxies
   - Easy to use

3. **Oxylabs**
   - Enterprise-grade proxies
   - Excellent reliability

4. **IPRoyal**
   - Budget-friendly option
   - Decent quality

5. **Webshare**
   - Free tier available
   - Good for testing

## Configuration Steps

### Step 1: Obtain Proxies

1. Sign up with a proxy provider
2. Purchase a proxy plan (residential recommended)
3. Get your proxy credentials (IP, port, username, password)

### Step 2: Create proxies.txt

1. Create a file named `proxies.txt` in the project root
2. Add your proxies in the format: `IP:PORT:USERNAME:PASSWORD`
3. One proxy per line

Example:
```bash
# Windows
notepad proxies.txt

# Linux/Mac
nano proxies.txt
```

### Step 3: Verify Format

Ensure each line follows the exact format:
```
72.46.139.137:6697:myuser:mypass
```

**Common mistakes to avoid:**
- ❌ Missing colons
- ❌ Extra spaces
- ❌ Wrong order (must be IP:PORT:USER:PASS)
- ❌ Empty lines between proxies

### Step 4: Test Proxies

Run the integration test to verify proxies are loaded:

```bash
python test_integration.py
```

Expected output:
```
✓ Loaded 10 proxies from proxies.txt
✓ Got proxy: 72.46.139.137:6697
```

## Rotation Logic

The scraper uses intelligent proxy rotation:

### Sequential Rotation
- Proxies are used in the order they appear in `proxies.txt`
- After the last proxy, it cycles back to the first

### Threshold-Based Rotation
- Default: Rotate after **14 requests**
- Configurable in `config.py`:
  ```python
  ROTATION_THRESHOLD = 14
  ```

### Failure-Triggered Rotation
- Immediately switches to next proxy on:
  - CAPTCHA detection
  - Connection timeout
  - Authentication failure
  - Network errors

### Example Rotation Flow

With 3 proxies and threshold of 14:

```
Request 1-14:   Proxy 1 (72.46.139.137)
Request 15-28:  Proxy 2 (45.196.40.119)
Request 29-42:  Proxy 3 (156.238.179.127)
Request 43-56:  Proxy 1 (72.46.139.137) [cycle repeats]
```

If Proxy 2 fails at request 20:
```
Request 1-14:   Proxy 1
Request 15-19:  Proxy 2
Request 20:     Proxy 2 fails → immediate rotation
Request 20-33:  Proxy 3
Request 34-47:  Proxy 1
```

## Troubleshooting

### Issue: "No proxies loaded"

**Cause:** `proxies.txt` file not found or empty

**Solution:**
1. Verify file exists in project root
2. Check file name is exactly `proxies.txt`
3. Ensure file contains at least one proxy

### Issue: "Proxy authentication failed"

**Cause:** Incorrect username or password

**Solution:**
1. Verify credentials with your proxy provider
2. Check for typos in `proxies.txt`
3. Ensure no extra spaces in credentials

### Issue: "Connection timeout"

**Cause:** Proxy is not responding or blocked

**Solution:**
1. Test proxy with curl:
   ```bash
   curl -x http://username:password@ip:port https://google.com
   ```
2. Contact your proxy provider
3. Remove non-working proxies from `proxies.txt`

### Issue: "Too many CAPTCHAs"

**Cause:** Proxies are being detected

**Solution:**
1. Use residential proxies instead of datacenter
2. Reduce rotation threshold (more frequent rotation)
3. Add more proxies to the pool
4. Increase delays between requests

## Testing Proxies

### Test with curl (Windows PowerShell)

```powershell
$proxy = "http://username:password@ip:port"
curl.exe -x $proxy https://api.ipify.org
```

### Test with curl (Linux/Mac)

```bash
curl -x http://username:password@ip:port https://api.ipify.org
```

Expected output: The proxy's IP address

### Test with Python

```python
import requests

proxy = {
    'http': 'http://username:password@ip:port',
    'https': 'http://username:password@ip:port'
}

response = requests.get('https://api.ipify.org', proxies=proxy)
print(f"Proxy IP: {response.text}")
```

## Best Practices

1. **Use Multiple Proxies**
   - Minimum 5 proxies for small projects
   - 10+ proxies for production use

2. **Monitor Proxy Health**
   - Check `scraper.log` for proxy failures
   - Remove consistently failing proxies

3. **Rotate Regularly**
   - Keep default threshold (14 requests)
   - Lower if experiencing issues

4. **Choose Quality Over Quantity**
   - 5 good proxies > 20 bad proxies
   - Invest in residential proxies

5. **Keep Credentials Secure**
   - Never commit `proxies.txt` to git
   - Use environment variables in production
   - Rotate credentials periodically

## Security Notes

⚠️ **Important Security Considerations:**

1. **Never commit proxies.txt**
   - Already in `.gitignore`
   - Contains sensitive credentials

2. **Protect proxy credentials**
   - Treat like passwords
   - Don't share publicly

3. **Use HTTPS proxies**
   - Encrypts traffic
   - More secure than HTTP

4. **Monitor usage**
   - Track proxy usage with provider
   - Watch for unusual activity

## Cost Optimization

### Tips to Reduce Proxy Costs

1. **Use rotation efficiently**
   - Don't rotate too frequently
   - Balance between detection and cost

2. **Cache results**
   - Avoid re-scraping same queries
   - Store results in database

3. **Filter queries**
   - Remove duplicates before scraping
   - Validate queries first

4. **Schedule scraping**
   - Run during off-peak hours
   - Batch queries together

## Advanced Configuration

### Custom Rotation Threshold

Edit `config.py`:

```python
ROTATION_THRESHOLD = 10  # Rotate every 10 requests
```

Lower values = more frequent rotation = less detection risk

### Proxy-Specific Settings

For advanced users, you can modify `modules/proxy_manager.py` to:

- Add proxy health checks
- Implement weighted rotation
- Track proxy performance
- Auto-remove failing proxies

## Support

If you have proxy-related issues:

1. Check this guide first
2. Review `scraper.log` for errors
3. Test proxies manually with curl
4. Contact your proxy provider
5. Run integration tests

---

**Remember:** Quality proxies are essential for successful scraping. Invest in good proxies for best results!
