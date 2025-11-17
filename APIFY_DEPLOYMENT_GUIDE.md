# Apify Actor Deployment Guide

Complete guide to deploy your Google Maps Scraper to Apify platform.

## Prerequisites

- GitHub account with your code pushed
- Apify account (sign up at https://apify.com - free $5 credit)

## Step-by-Step Deployment

### 1. Create Apify Account

1. Go to https://apify.com
2. Click "Sign up" (free)
3. Verify your email
4. You'll get $5 free credit (~6,000 businesses worth)

### 2. Import from GitHub

1. Go to https://console.apify.com
2. Click "Actors" in left sidebar
3. Click "Create new" button
4. Select "Import from GitHub"
5. Fill in the form:
   - **GitHub URL**: `https://github.com/Kismat-adhikari/maps-FLASk-scrapper`
   - **Branch**: `apify-actor`
   - **Actor name**: `google-maps-scraper` (or your choice)
   - **Title**: "Google Maps Scraper - No API Key"
   - **Description**: Copy from README_APIFY.md

6. Click "Create"

### 3. Build the Actor

1. Apify will automatically start building
2. Wait 2-5 minutes for build to complete
3. Check "Builds" tab for progress
4. Look for green checkmark ✓

### 4. Test the Actor

1. Once built, click "Try it" button
2. Use this test input:

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

3. Click "Start"
4. Watch it run!
5. Check "Dataset" tab for results

### 5. Configure Actor Settings

#### Basic Settings
- **Title**: Google Maps Scraper - No API Key Required
- **Description**: Professional description from README_APIFY.md
- **Categories**: Data extraction, Web scraping, Business intelligence
- **README**: Use README_APIFY.md content

#### Pricing (if publishing to store)
Choose one of these models:

**Option 1: Pay-per-result**
- $0.01 per business scraped
- Minimum $1 purchase
- Best for: Occasional users

**Option 2: Subscription Tiers**
- **Starter**: $19/month - 2,000 businesses
- **Professional**: $49/month - 10,000 businesses
- **Business**: $99/month - 50,000 businesses
- Best for: Regular users

**Option 3: Freemium**
- Free: 100 businesses/month
- Pro: $29/month - 5,000 businesses
- Enterprise: Custom pricing
- Best for: Growing user base

#### Advanced Settings
- **Memory**: 2048 MB (recommended)
- **Timeout**: 3600 seconds (1 hour)
- **Build tag**: latest
- **Restart on error**: Yes

### 6. Publish to Apify Store (Optional)

1. Go to actor settings
2. Click "Publish to Store"
3. Fill in:
   - **SEO title**: "Google Maps Scraper - No API Key | Extract Business Data"
   - **SEO description**: "Scrape business data from Google Maps without API keys. Get names, addresses, phones, emails, ratings. Fast, reliable, easy to use."
   - **Categories**: Select relevant ones
   - **Tags**: google-maps, scraper, business-data, lead-generation, no-api-key

4. Add screenshots:
   - Input form screenshot
   - Results dataset screenshot
   - Example output

5. Set pricing (see options above)
6. Click "Submit for review"
7. Wait for Apify approval (1-3 days)

## Testing Checklist

Before publishing, test these scenarios:

### Basic Tests
- [ ] Keyword + location search (10 results)
- [ ] Multiple keywords and locations
- [ ] URL-based search
- [ ] With Apify proxy
- [ ] With custom proxies
- [ ] Email extraction on/off
- [ ] Different maxResultsPerQuery values

### Edge Cases
- [ ] Invalid input (should fail gracefully)
- [ ] Empty results (should return empty dataset)
- [ ] CAPTCHA handling (should retry)
- [ ] Network errors (should retry)
- [ ] Very long queries (should timeout properly)

### Performance Tests
- [ ] 100 businesses (check cost)
- [ ] 1,000 businesses (check time)
- [ ] Multiple concurrent runs

## Monitoring & Maintenance

### Check Actor Health
1. Go to actor dashboard
2. Monitor:
   - Success rate (should be >95%)
   - Average runtime
   - Error logs
   - User feedback

### Update Actor
When you need to update:

```bash
# Make changes on apify-actor branch
git checkout apify-actor

# Make your changes
# ...

# Commit and push
git add -A
git commit -m "Update: description of changes"
git push origin apify-actor
```

Apify will automatically rebuild on push!

### Handle Issues
- Check "Runs" tab for failed runs
- Review error logs
- Test locally first
- Update and redeploy

## Marketing Your Actor

### Apify Store Optimization
- Use clear, benefit-focused title
- Add detailed description with examples
- Include screenshots and demo video
- Respond to user reviews quickly
- Update regularly with new features

### External Marketing
- Share on Twitter/LinkedIn
- Post on Reddit (r/webscraping, r/entrepreneur)
- Write blog post about use cases
- Create YouTube tutorial
- Add to your portfolio

### Pricing Strategy
Start with competitive pricing:
- Research similar actors
- Offer free tier to build user base
- Gradually increase prices as you add features
- Offer volume discounts

## Support & Documentation

### Provide Good Support
- Respond to questions within 24 hours
- Create FAQ based on common questions
- Update README with troubleshooting tips
- Offer email support for paid users

### Documentation
- Keep README_APIFY.md updated
- Add example inputs for common use cases
- Document all input parameters
- Show expected output format

## Revenue Optimization

### Track Metrics
- Monthly active users
- Revenue per user
- Churn rate
- Support tickets

### Improve Conversion
- Offer free trial
- Show example results
- Add testimonials
- Optimize pricing

### Upsell Opportunities
- Premium features (faster scraping, more results)
- Priority support
- Custom integrations
- White-label version

## Troubleshooting

### Build Fails
- Check Dockerfile syntax
- Verify requirements.txt
- Check for missing files
- Review build logs

### Actor Fails to Run
- Test input format
- Check proxy configuration
- Review error logs
- Test locally first

### Poor Performance
- Increase memory allocation
- Optimize scraping logic
- Use better proxies
- Reduce concurrent requests

### Low Sales
- Improve description
- Add more screenshots
- Lower initial price
- Offer free tier
- Market more actively

## Next Steps

1. ✅ Deploy to Apify
2. ✅ Test thoroughly
3. ✅ Publish to store
4. 📈 Market your actor
5. 💰 Start earning!

## Resources

- **Apify Documentation**: https://docs.apify.com
- **Actor Examples**: https://apify.com/store
- **Support**: https://discord.gg/jyEM2PRvMU (Apify Discord)
- **Your Actor**: https://console.apify.com/actors

---

**Ready to deploy? Let's make some money! 💰**
