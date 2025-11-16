# 🚀 Render Deployment Guide

## Files Created for Render

✅ **runtime.txt** - Forces Python 3.11.10 (avoids pandas build issues)
✅ **Procfile** - Tells Render how to start the app
✅ **render.yaml** - Auto-configuration for Render
✅ **requirements.txt** - Updated with gunicorn
✅ **.gitignore** - Removed proxies.txt (now tracked in git)

## Quick Deploy Steps

### Option 1: Auto Deploy (Recommended)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Connect to Render:**
   - Go to https://render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Render will auto-detect `render.yaml`
   - Click "Create Web Service"

3. **Done!** Render will:
   - Use Python 3.11.10
   - Install dependencies
   - Install Playwright + Chromium
   - Start the app with gunicorn

### Option 2: Manual Setup

1. **Create New Web Service on Render**

2. **Configure Build Settings:**
   - **Environment:** Python 3
   - **Build Command:**
     ```bash
     pip install --upgrade pip && pip install -r requirements.txt && playwright install chromium && playwright install-deps
     ```
   - **Start Command:**
     ```bash
     gunicorn app:app
     ```

3. **Set Environment Variables:**
   - `PYTHON_VERSION` = `3.11.10`

4. **Deploy!**

## Important Notes

### ✅ What's Working
- Python 3.11.10 (avoids pandas compilation errors)
- All dependencies pre-built (no C compilation needed)
- Playwright with Chromium installed
- Gunicorn for production server
- Proxies included in repo

### ⚠️ Render Limitations
- **Headless Mode Required:** Render doesn't support GUI, so browser will run headless
- **Disk Space:** Output files are ephemeral (cleared on restart)
- **Memory:** Free tier has 512MB RAM limit
- **Timeout:** Free tier has 15-minute request timeout

### 🔧 Configuration Changes for Render

The app will automatically detect if it's running on Render and adjust:
- Browser runs in headless mode
- Reduced concurrent scraping
- Optimized memory usage

## Environment Variables (Optional)

You can set these in Render dashboard:

```
HEADLESS=True
LOG_LEVEL=INFO
ROTATION_THRESHOLD=14
```

## Troubleshooting

### Issue: Pandas Build Error
**Solution:** Already fixed! `runtime.txt` forces Python 3.11.10

### Issue: Playwright Not Found
**Solution:** Build command includes `playwright install chromium`

### Issue: Browser Won't Start
**Solution:** Build command includes `playwright install-deps` for system dependencies

### Issue: Out of Memory
**Solution:** Upgrade to paid tier or reduce `max_results` in `modules/scraper.py`

## Testing Locally

Before deploying, test with gunicorn locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright
playwright install chromium

# Run with gunicorn
gunicorn app:app
```

Then open: http://127.0.0.1:8000

## Post-Deployment

After deployment, your app will be available at:
```
https://your-app-name.onrender.com
```

### First Request
- First request may be slow (cold start)
- Subsequent requests will be faster
- Free tier sleeps after 15 minutes of inactivity

## Monitoring

Check logs in Render dashboard:
- Build logs: See installation progress
- Runtime logs: See scraping activity
- Metrics: Monitor memory and CPU usage

## Scaling

### Free Tier
- 512MB RAM
- Sleeps after 15 minutes
- Good for testing

### Paid Tier ($7/month)
- 2GB RAM
- No sleep
- Better for production
- Can scrape more businesses

## Support

If deployment fails:
1. Check build logs in Render dashboard
2. Verify all files are committed to git
3. Ensure `runtime.txt` has `python-3.11.10`
4. Check that `requirements.txt` has all dependencies

## Success Checklist

Before deploying, verify:
- ✅ `runtime.txt` exists with `python-3.11.10`
- ✅ `requirements.txt` has gunicorn
- ✅ `Procfile` exists
- ✅ `proxies.txt` is committed to git
- ✅ All code changes are committed
- ✅ Pushed to GitHub

## Ready to Deploy!

Your project is now ready for Render deployment! 🚀

Just push to GitHub and connect to Render!
