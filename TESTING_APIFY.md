# Testing the Apify Actor

There are 3 ways to test your Apify Actor:

## Option 1: Test on Apify Platform (Easiest & Recommended)

1. **Create Apify Account**
   - Go to https://apify.com
   - Sign up for free account
   - Get $5 free credit

2. **Push to Apify**
   ```bash
   # Login to Apify CLI
   apify login
   
   # Push the actor
   apify push
   ```

3. **Test in Apify Console**
   - Go to your actor page
   - Click "Try it"
   - Fill in the input form
   - Click "Start"
   - Watch it run!

## Option 2: Test with Apify CLI Locally

```bash
# Make sure you're on apify-actor branch
git checkout apify-actor

# Install Apify CLI (if not already installed)
npm install -g apify-cli

# Login
apify login

# Run locally (simulates Apify environment)
apify run --purge
```

**Note**: This requires Docker to be installed and running.

## Option 3: Test the Flask Version Instead

The easiest way to test the scraping logic is to use the Flask version on the `main` branch:

```bash
# Switch to main branch
git checkout main

# Run the Flask app
python app.py

# Open browser
http://127.0.0.1:5000

# Test scraping through the web interface
```

This tests the same scraping logic without Apify complexity.

## What's Different Between Branches?

### Main Branch (Flask)
- Web interface
- Real-time updates
- File uploads
- Interactive map
- **Easy to test locally**

### Apify-Actor Branch
- No web interface
- JSON input
- Apify Dataset output
- Designed for Apify platform
- **Requires Apify environment to test properly**

## Recommended Testing Flow

1. **Test scraping logic** on `main` branch (Flask app)
2. **Once working**, switch to `apify-actor` branch
3. **Push to Apify** and test there
4. **Publish** when ready

## Quick Test on Apify Platform

1. Go to https://console.apify.com
2. Click "Actors" → "Create new"
3. Choose "Import from GitHub"
4. Enter your repo URL and select `apify-actor` branch
5. Click "Build"
6. Once built, click "Try it"
7. Test with this input:

```json
{
  "mode": "keyword",
  "keywords": ["coffee shops"],
  "locations": ["Miami"],
  "maxResultsPerQuery": 10,
  "useApifyProxy": true,
  "headless": true,
  "extractEmails": false,
  "deduplicate": true
}
```

## Troubleshooting

### "Actor run ID not found"
- This means you're trying to run Apify code outside Apify environment
- Solution: Test on Apify platform or use Flask version

### "No proxy available"
- Make sure you have proxies in `proxies.txt` or enable Apify proxy
- For Apify proxy, set `useApifyProxy: true`

### Browser won't start
- Set `headless: true` in input
- Make sure Playwright is installed: `playwright install chromium`

## Cost Estimate for Testing

- **Free tier**: $5 credit (enough for ~6,000 businesses)
- **Test run**: 10 businesses = ~$0.01
- **Small test**: 100 businesses = ~$0.08
- **Full test**: 1,000 businesses = ~$0.75

## Next Steps

1. Test on Apify platform (recommended)
2. Adjust settings based on results
3. Set pricing for your actor
4. Publish to Apify Store
5. Start selling! 💰
