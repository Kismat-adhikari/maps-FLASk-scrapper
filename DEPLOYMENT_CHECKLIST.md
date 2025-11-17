# Deployment Checklist

Use this checklist before deploying to production.

## Pre-Deployment

### Code Quality
- [ ] All tests passing (`python tests/test_integration.py`)
- [ ] No syntax errors or warnings
- [ ] Code reviewed and cleaned up
- [ ] Unused files removed
- [ ] Documentation up to date

### Configuration
- [ ] `HEADLESS = True` in `config.py` (for production)
- [ ] `SECRET_KEY` set to secure random value
- [ ] `DEBUG = False` in Flask app
- [ ] Proxy file (`proxies.txt`) configured with valid proxies
- [ ] Environment variables configured (if using)

### Security
- [ ] Sensitive data not in git (check `.gitignore`)
- [ ] API keys/secrets in environment variables
- [ ] CORS configured properly (if needed)
- [ ] Rate limiting configured
- [ ] Input validation in place

### Dependencies
- [ ] `requirements.txt` up to date
- [ ] Python version specified in `runtime.txt`
- [ ] All dependencies compatible with deployment platform

### Files & Directories
- [ ] `output/` directory exists
- [ ] `uploads/` directory exists
- [ ] Static files optimized (CSS/JS minified if needed)
- [ ] No unnecessary files in repository

## Deployment Platform

### Render (Recommended)
- [ ] `render.yaml` configured
- [ ] `Procfile` present
- [ ] Environment variables set in Render dashboard
- [ ] Playwright browsers will install automatically
- [ ] Health check endpoint configured

### Heroku
- [ ] `Procfile` configured
- [ ] Buildpacks added (Python + Playwright)
- [ ] Environment variables set
- [ ] Dyno type selected

### VPS/Cloud
- [ ] Server provisioned
- [ ] Python 3.9+ installed
- [ ] Playwright browsers installed
- [ ] Reverse proxy configured (nginx/Apache)
- [ ] SSL certificate configured
- [ ] Firewall rules set

## Post-Deployment

### Verification
- [ ] Application starts without errors
- [ ] Web interface loads correctly
- [ ] Map displays properly (MapLibre GL JS)
- [ ] File upload works
- [ ] Scraping works with test query
- [ ] Results download works (CSV/JSON)
- [ ] Proxy rotation working
- [ ] Logs being written correctly

### Monitoring
- [ ] Application logs accessible
- [ ] Error tracking configured (optional)
- [ ] Uptime monitoring configured (optional)
- [ ] Performance metrics tracked (optional)

### Documentation
- [ ] Deployment URL documented
- [ ] Access credentials secured
- [ ] Team notified of deployment
- [ ] User guide updated with production URL

## Rollback Plan

If deployment fails:
1. Check application logs for errors
2. Verify environment variables
3. Test locally with production config
4. Rollback to previous version if needed
5. Document issues for future reference

## Production Testing

After deployment, test these features:
- [ ] Homepage loads
- [ ] Keyword search works
- [ ] URL input works
- [ ] File upload works
- [ ] Map displays markers
- [ ] Results table populates
- [ ] CSV download works
- [ ] JSON download works
- [ ] Proxy rotation works
- [ ] Error handling works

## Performance

- [ ] Response times acceptable (<2s for page load)
- [ ] Scraping speed acceptable (10-15s per query)
- [ ] Memory usage stable
- [ ] No memory leaks during long sessions
- [ ] Browser instances cleaned up properly

## Maintenance

- [ ] Backup strategy in place
- [ ] Update schedule planned
- [ ] Monitoring alerts configured
- [ ] Support contact information available

---

**Deployment Date**: _______________  
**Deployed By**: _______________  
**Platform**: _______________  
**URL**: _______________  
**Status**: ☐ Success ☐ Failed  
**Notes**: _______________
