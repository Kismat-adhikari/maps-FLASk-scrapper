# MapLibre GL JS - Testing Checklist

## Pre-Deployment Testing

Use this checklist to verify the MapLibre GL JS upgrade is working correctly before deploying to production.

---

## 1. Basic Map Functionality

### Map Initialization
- [ ] Open http://127.0.0.1:5000 in browser
- [ ] Verify map loads without errors
- [ ] Check browser console for errors (should be none)
- [ ] Verify map shows OpenStreetMap tiles
- [ ] Verify map is centered on Miami (default location)

### Map Controls
- [ ] Zoom in button works
- [ ] Zoom out button works
- [ ] Scroll wheel zoom works
- [ ] Click and drag to pan works
- [ ] Double-click to zoom works

---

## 2. Marker Functionality

### Marker Appearance
- [ ] Start a test scrape (keyword: "restaurant", location: "Miami")
- [ ] Verify markers appear on map as businesses are scraped
- [ ] Verify markers have pin/teardrop shape
- [ ] Verify markers have correct colors:
  - Green for successfully scraped
  - Yellow for currently scraping (pulsing)
  - Red for failed
  - Grey for waiting

### Marker Animations
- [ ] Verify markers drop from sky when added (smooth animation)
- [ ] Verify yellow markers pulse while scraping
- [ ] Verify no lag or stuttering during marker addition

### Marker Interactions
- [ ] Hover over marker (should show cursor pointer)
- [ ] Click marker to open popup
- [ ] Verify popup shows business information:
  - Business name in header
  - Full address
  - Phone number
  - Rating and review count
  - "View on Google Maps" link
- [ ] Click "View on Google Maps" link (should open in new tab)
- [ ] Close popup by clicking X button
- [ ] Close popup by clicking elsewhere on map

---

## 3. Real-Time Updates

### Status Polling
- [ ] Start scraping with 5-10 businesses
- [ ] Verify map updates automatically every 1.5 seconds
- [ ] Verify new markers appear without page refresh
- [ ] Verify "Currently Scraping" banner updates
- [ ] Verify progress bar updates

### Auto-Fit Bounds
- [ ] Verify map automatically zooms to show all markers
- [ ] Verify smooth animation when auto-fitting
- [ ] Verify padding around markers (not cut off at edges)

---

## 4. Multiple Scraping Sessions

### Map Reset
- [ ] Complete a scraping session
- [ ] Start a new scraping session
- [ ] Verify old markers are removed
- [ ] Verify map resets to default position
- [ ] Verify new markers appear correctly

### Different Locations
- [ ] Scrape businesses in Miami
- [ ] Scrape businesses in New York
- [ ] Verify map centers on correct location
- [ ] Verify markers appear in correct geographic positions

---

## 5. Performance Testing

### Many Markers
- [ ] Scrape 50+ businesses
- [ ] Verify map remains responsive
- [ ] Verify no lag when panning/zooming
- [ ] Verify animations remain smooth (60 FPS)
- [ ] Check browser memory usage (should be reasonable)

### Long Scraping Session
- [ ] Start scraping with 100+ queries (file upload)
- [ ] Let it run for 10+ minutes
- [ ] Verify map continues updating correctly
- [ ] Verify no memory leaks
- [ ] Verify no performance degradation over time

---

## 6. Browser Compatibility

### Desktop Browsers
- [ ] Test in Chrome (latest)
- [ ] Test in Firefox (latest)
- [ ] Test in Safari (latest)
- [ ] Test in Edge (latest)

### Mobile Browsers
- [ ] Test on mobile Chrome
- [ ] Test on mobile Safari
- [ ] Verify touch gestures work (pinch zoom, pan)
- [ ] Verify responsive layout

---

## 7. Error Handling

### No Coordinates
- [ ] Scrape businesses without coordinates
- [ ] Verify map doesn't crash
- [ ] Verify markers only appear for businesses with valid coordinates

### Network Issues
- [ ] Disconnect internet briefly during scraping
- [ ] Verify map handles gracefully
- [ ] Verify map recovers when connection restored

---

## 8. Visual Quality

### Styling
- [ ] Verify marker colors match design (green, yellow, red, grey)
- [ ] Verify marker shadows look good
- [ ] Verify popup styling is clean and professional
- [ ] Verify map controls are styled correctly
- [ ] Verify legend is visible and clear

### Animations
- [ ] Verify marker drop animation is smooth
- [ ] Verify pulse animation is smooth (not choppy)
- [ ] Verify zoom/pan animations are fluid
- [ ] Verify popup open/close is smooth

---

## 9. Integration Testing

### With Other Features
- [ ] Verify map works with keyword search
- [ ] Verify map works with URL input
- [ ] Verify map works with file upload
- [ ] Verify map updates alongside results table
- [ ] Verify map updates alongside live log
- [ ] Verify download CSV includes coordinates

### State Management
- [ ] Verify map state persists during scraping
- [ ] Verify map resets on new scrape
- [ ] Verify map handles stop/resume correctly

---

## 10. Console Checks

### No Errors
- [ ] Open browser DevTools console
- [ ] Verify no JavaScript errors
- [ ] Verify no CSS warnings
- [ ] Verify no 404 errors for resources
- [ ] Verify MapLibre GL JS loads correctly

### Performance
- [ ] Check Network tab for resource loading
- [ ] Verify MapLibre GL JS loads (~200KB)
- [ ] Verify map tiles load efficiently
- [ ] Check Performance tab for frame rate
- [ ] Verify 60 FPS during animations

---

## 11. Accessibility

### Keyboard Navigation
- [ ] Tab through map controls
- [ ] Verify controls are keyboard accessible
- [ ] Verify focus indicators are visible

### Screen Reader
- [ ] Test with screen reader (if available)
- [ ] Verify map has appropriate ARIA labels
- [ ] Verify controls are announced correctly

---

## 12. Documentation

### Code Comments
- [ ] Verify JavaScript has clear comments
- [ ] Verify CSS has section comments
- [ ] Verify complex logic is explained

### User Documentation
- [ ] Verify README mentions MapLibre
- [ ] Verify FEATURES_OVERVIEW is updated
- [ ] Verify upgrade docs are complete

---

## Quick Test Script

For rapid testing, run this sequence:

1. **Start server**: `python app.py`
2. **Open browser**: http://127.0.0.1:5000
3. **Quick scrape**: 
   - Keyword: "restaurant"
   - Location: "Miami"
   - Click "Start Scraping"
4. **Verify**:
   - Map loads ✅
   - Markers appear ✅
   - Popups work ✅
   - No console errors ✅
5. **Done!** If all pass, upgrade is working.

---

## Known Issues

### None Currently
All features tested and working as expected.

---

## Reporting Issues

If you find any issues:

1. Note the browser and version
2. Check browser console for errors
3. Take screenshots if visual issue
4. Note steps to reproduce
5. Check if issue exists in Leaflet version (rollback test)

---

## Sign-Off

- [ ] All critical tests passed
- [ ] All browsers tested
- [ ] Performance is acceptable
- [ ] No console errors
- [ ] Documentation is complete
- [ ] Ready for production deployment

**Tested by**: _________________  
**Date**: _________________  
**Status**: ☐ Pass ☐ Fail  
**Notes**: _________________

---

**Last Updated**: November 16, 2025  
**Version**: MapLibre GL JS 3.6.2
