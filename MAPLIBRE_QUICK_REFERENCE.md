# MapLibre GL JS - Quick Reference Guide

## Common Tasks

Quick reference for working with MapLibre GL JS in the Google Maps Scraper.

---

## Map Initialization

```javascript
map = new maplibregl.Map({
    container: 'scrapingMap',
    style: {
        version: 8,
        sources: {
            'osm': {
                type: 'raster',
                tiles: ['https://a.tile.openstreetmap.org/{z}/{x}/{y}.png'],
                tileSize: 256,
                attribution: '© OpenStreetMap contributors'
            }
        },
        layers: [{
            id: 'osm',
            type: 'raster',
            source: 'osm',
            minzoom: 0,
            maxzoom: 19
        }]
    },
    center: [-80.1918, 25.7617], // [lng, lat]
    zoom: 10,
    attributionControl: true
});
```

---

## Adding Markers

### Create Marker Element
```javascript
const el = document.createElement('div');
el.className = `map-marker marker-${color}`;
el.innerHTML = '<div class="marker-dot"></div>';
```

### Create Marker
```javascript
const marker = new maplibregl.Marker({
    element: el,
    anchor: 'bottom'
})
.setLngLat([lng, lat])
.addTo(map);
```

### Store Marker Reference
```javascript
markerElements[businessId] = marker;
```

---

## Creating Popups

### Create Popup
```javascript
const popup = new maplibregl.Popup({
    offset: 25,
    closeButton: true,
    closeOnClick: false,
    maxWidth: '300px'
}).setHTML(popupHTML);
```

### Attach to Marker
```javascript
marker.setPopup(popup);
```

### Popup HTML Template
```javascript
const popupHTML = `
    <div class="maplibre-popup">
        <div class="popup-header">
            <h3>${business.name}</h3>
            <span class="popup-badge badge-green">✓ Scraped</span>
        </div>
        <div class="popup-body">
            <div class="popup-row">
                <span class="popup-icon">📍</span>
                <span>${business.address}</span>
            </div>
        </div>
        <div class="popup-footer">
            <a href="${business.url}" target="_blank" class="popup-link">
                View on Google Maps →
            </a>
        </div>
    </div>
`;
```

---

## Map Controls

### Add Navigation Controls
```javascript
map.addControl(new maplibregl.NavigationControl(), 'top-right');
```

### Add Fullscreen Control
```javascript
map.addControl(new maplibregl.FullscreenControl());
```

### Add Scale Control
```javascript
map.addControl(new maplibregl.ScaleControl({
    maxWidth: 100,
    unit: 'imperial'
}));
```

---

## Map Navigation

### Fly To Location
```javascript
map.flyTo({
    center: [lng, lat],
    zoom: 12,
    duration: 1000
});
```

### Jump To Location (No Animation)
```javascript
map.jumpTo({
    center: [lng, lat],
    zoom: 12
});
```

### Fit Bounds
```javascript
const bounds = new maplibregl.LngLatBounds();
bounds.extend([lng1, lat1]);
bounds.extend([lng2, lat2]);

map.fitBounds(bounds, {
    padding: {top: 50, bottom: 50, left: 50, right: 50},
    maxZoom: 13,
    duration: 1500
});
```

---

## Marker Management

### Remove Single Marker
```javascript
marker.remove();
```

### Remove All Markers
```javascript
Object.values(markerElements).forEach(marker => marker.remove());
markerElements = {};
```

### Update Marker Position
```javascript
marker.setLngLat([newLng, newLat]);
```

### Toggle Marker Visibility
```javascript
marker.getElement().style.display = 'none'; // Hide
marker.getElement().style.display = 'block'; // Show
```

---

## Event Handling

### Map Click
```javascript
map.on('click', (e) => {
    console.log('Clicked at:', e.lngLat);
});
```

### Map Load
```javascript
map.on('load', () => {
    console.log('Map loaded');
});
```

### Marker Click
```javascript
marker.getElement().addEventListener('click', () => {
    console.log('Marker clicked');
});
```

---

## Coordinate Conversion

### Important: Coordinate Order
MapLibre uses **[longitude, latitude]** (opposite of Leaflet)

```javascript
// Correct
map.setCenter([-80.1918, 25.7617]); // [lng, lat]

// Wrong (Leaflet style)
map.setCenter([25.7617, -80.1918]); // [lat, lng] - DON'T DO THIS
```

### Extract from Google Maps URL
```javascript
// URL format: @lat,lng,zoom
const coords = url.split('@')[1].split(',');
const lat = parseFloat(coords[0]);
const lng = parseFloat(coords[1]);

// Use in MapLibre (swap order!)
marker.setLngLat([lng, lat]);
```

---

## Styling

### Marker Colors
```css
.marker-green .marker-dot {
    background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
}

.marker-yellow .marker-dot {
    background: linear-gradient(135deg, #f6ad55 0%, #ed8936 100%);
}

.marker-red .marker-dot {
    background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
}

.marker-grey .marker-dot {
    background: linear-gradient(135deg, #a0aec0 0%, #718096 100%);
}
```

### Popup Styling
```css
.maplibregl-popup-content {
    padding: 0 !important;
    border-radius: 12px !important;
    box-shadow: 0 10px 40px rgba(0,0,0,0.2) !important;
}
```

---

## Common Patterns

### Add Multiple Markers
```javascript
businesses.forEach((business, index) => {
    const lat = parseFloat(business.latitude);
    const lng = parseFloat(business.longitude);
    
    if (isNaN(lat) || isNaN(lng)) return;
    
    const el = document.createElement('div');
    el.className = 'map-marker marker-green';
    el.innerHTML = '<div class="marker-dot"></div>';
    
    const marker = new maplibregl.Marker({element: el, anchor: 'bottom'})
        .setLngLat([lng, lat])
        .addTo(map);
    
    markerElements[index] = marker;
});
```

### Update Marker Color
```javascript
function updateMarkerColor(markerId, newColor) {
    const marker = markerElements[markerId];
    const el = marker.getElement();
    
    // Remove old color classes
    el.classList.remove('marker-green', 'marker-yellow', 'marker-red', 'marker-grey');
    
    // Add new color class
    el.classList.add(`marker-${newColor}`);
}
```

### Auto-Fit to Markers
```javascript
function fitMapToMarkers() {
    const bounds = new maplibregl.LngLatBounds();
    let hasMarkers = false;
    
    Object.values(markerElements).forEach(marker => {
        bounds.extend(marker.getLngLat());
        hasMarkers = true;
    });
    
    if (hasMarkers) {
        map.fitBounds(bounds, {
            padding: 50,
            maxZoom: 13,
            duration: 1500
        });
    }
}
```

---

## Debugging

### Check Map Status
```javascript
console.log('Map loaded:', map.loaded());
console.log('Map center:', map.getCenter());
console.log('Map zoom:', map.getZoom());
```

### Check Marker Count
```javascript
console.log('Total markers:', Object.keys(markerElements).length);
```

### Verify Coordinates
```javascript
function isValidCoordinate(lat, lng) {
    return !isNaN(lat) && !isNaN(lng) && 
           lat >= -90 && lat <= 90 && 
           lng >= -180 && lng <= 180;
}
```

---

## Performance Tips

### Batch Marker Updates
```javascript
// Good: Add all markers at once
const markers = businesses.map(b => createMarker(b));
markers.forEach(m => m.addTo(map));

// Bad: Add markers one by one with delays
businesses.forEach(b => {
    setTimeout(() => createMarker(b).addTo(map), 100);
});
```

### Remove Unused Markers
```javascript
// Clean up markers that are no longer needed
Object.entries(markerElements).forEach(([id, marker]) => {
    if (!isBusinessActive(id)) {
        marker.remove();
        delete markerElements[id];
    }
});
```

### Limit Popup Content
```javascript
// Keep popup HTML simple and lightweight
// Avoid large images or complex layouts
```

---

## Migration from Leaflet

### Key Differences

| Leaflet | MapLibre GL JS |
|---------|----------------|
| `L.map('id')` | `new maplibregl.Map({container: 'id'})` |
| `[lat, lng]` | `[lng, lat]` |
| `L.marker([lat, lng])` | `new maplibregl.Marker().setLngLat([lng, lat])` |
| `marker.bindPopup()` | `marker.setPopup()` |
| `L.tileLayer()` | Style object with sources/layers |

### Quick Migration Checklist
- [ ] Swap coordinate order (lat,lng → lng,lat)
- [ ] Update map initialization
- [ ] Update marker creation
- [ ] Update popup creation
- [ ] Update CSS selectors
- [ ] Test all functionality

---

## Resources

- **Official Docs**: https://maplibre.org/maplibre-gl-js-docs/
- **Examples**: https://maplibre.org/maplibre-gl-js-docs/example/
- **API Reference**: https://maplibre.org/maplibre-gl-js-docs/api/
- **GitHub**: https://github.com/maplibre/maplibre-gl-js

---

## Getting Help

### Check Console First
```javascript
// Enable debug mode
map.showTileBoundaries = true;
map.showCollisionBoxes = true;
```

### Common Issues

**Markers not appearing?**
- Check coordinate order (lng, lat)
- Verify coordinates are valid numbers
- Check if marker element has correct CSS

**Map not loading?**
- Check browser console for errors
- Verify MapLibre GL JS is loaded
- Check if container element exists

**Popups not working?**
- Verify popup HTML is valid
- Check CSS for `.maplibregl-popup-content`
- Ensure popup is attached to marker

---

**Last Updated**: November 16, 2025  
**Version**: MapLibre GL JS 3.6.2
