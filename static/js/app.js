// Modern Google Maps Scraper - Frontend Logic

let statusPollingInterval = null;
let isScrapingActive = false;
let lastProcessedCount = 0;
let scrapedBusinesses = new Set();

// DOM Elements
const startBtn = document.getElementById('startBtn');
const btnText = document.querySelector('.btn-text');
const btnLoader = document.querySelector('.btn-loader');
const keywordInput = document.getElementById('keyword');
const locationInput = document.getElementById('location');
const statusSection = document.getElementById('statusSection');
const resultsSection = document.getElementById('resultsSection');
const completionMessage = document.getElementById('completionMessage');
const liveLog = document.getElementById('liveLog');
const clearLogBtn = document.getElementById('clearLogBtn');
const downloadBtn = document.getElementById('downloadBtn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    startBtn.addEventListener('click', handleStartScraping);
    clearLogBtn.addEventListener('click', clearLog);
    downloadBtn.addEventListener('click', () => downloadResults('csv'));
    
    addLogEntry('System ready. Enter keyword and location to start scraping.', 'info');
});

// Start Scraping
async function handleStartScraping() {
    const keyword = keywordInput.value.trim();
    const location = locationInput.value.trim();
    
    if (!keyword || !location) {
        addLogEntry('Error: Please enter both keyword and location', 'error');
        return;
    }
    
    // Disable button and show loader
    startBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'flex';
    
    // Show status section
    statusSection.style.display = 'block';
    
    // Reset state
    lastProcessedCount = 0;
    scrapedBusinesses.clear();
    document.getElementById('resultsBody').innerHTML = '';
    completionMessage.style.display = 'none';
    
    addLogEntry(`Starting scrape: "${keyword}" in "${location}"`, 'info');
    
    try {
        const response = await fetch('/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                queries: [{
                    keyword: keyword,
                    zip_code: location,
                    url: ''
                }]
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            addLogEntry(`✓ Scraping initiated with ${data.query_count} query`, 'success');
            startStatusPolling();
            isScrapingActive = true;
        } else {
            addLogEntry(`✗ Error: ${data.error}`, 'error');
            resetButton();
        }
    } catch (error) {
        addLogEntry(`✗ Network error: ${error.message}`, 'error');
        resetButton();
    }
}

// Status Polling
function startStatusPolling() {
    if (statusPollingInterval) {
        clearInterval(statusPollingInterval);
    }
    
    statusPollingInterval = setInterval(updateStatus, 1500);
    updateStatus(); // Immediate first call
}

function stopStatusPolling() {
    if (statusPollingInterval) {
        clearInterval(statusPollingInterval);
        statusPollingInterval = null;
    }
}

// Update Status
async function updateStatus() {
    try {
        const response = await fetch('/status');
        const data = await response.json();
        
        // Update progress bar
        const percentage = data.total_queries > 0 
            ? Math.round((data.processed / data.total_queries) * 100) 
            : 0;
        document.getElementById('progressFill').style.width = percentage + '%';
        document.getElementById('progressText').textContent = percentage + '%';
        document.getElementById('progressCount').textContent = `${data.processed} / ${data.total_queries}`;
        
        // Update stats
        document.getElementById('currentProxy').textContent = data.current_proxy || '-';
        document.getElementById('scrapedCount').textContent = data.success_count;
        document.getElementById('failedCount').textContent = data.failure_count;
        
        // Log current query
        if (data.current_query && data.status === 'running') {
            if (data.processed > lastProcessedCount) {
                addLogEntry(`Processing: ${data.current_query} via ${data.current_proxy}`, 'info');
                lastProcessedCount = data.processed;
            }
        }
        
        // Update results table with new businesses
        if (data.results && data.results.length > 0) {
            // Show results section first
            resultsSection.style.display = 'block';
            document.getElementById('totalResults').textContent = `${data.results.length} businesses found`;
            
            data.results.forEach(business => {
                const businessId = business.name + business.phone;
                if (!scrapedBusinesses.has(businessId)) {
                    scrapedBusinesses.add(businessId);
                    addBusinessToTable(business);
                    addLogEntry(`Scraped: ${business.name} - Rating: ${business.rating} - Phone: ${business.phone}`, 'success');
                }
            });
        }
        
        // Check if completed
        if (data.status === 'completed' || data.status === 'stopped') {
            stopStatusPolling();
            handleCompletion(data);
        }
        
    } catch (error) {
        console.error('Error fetching status:', error);
    }
}

// Handle Completion
function handleCompletion(data) {
    isScrapingActive = false;
    resetButton();
    
    if (data.status === 'completed') {
        addLogEntry(`Scraping completed! Total: ${data.success_count} successful, ${data.failure_count} failed`, 'success');
        
        // Only show completion message if we have results
        if (data.results && data.results.length > 0) {
            completionMessage.style.display = 'block';
            
            // Scroll to completion message
            setTimeout(() => {
                completionMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }, 500);
        }
    } else {
        addLogEntry('Scraping stopped by user', 'info');
    }
}

// Add Business to Table
function addBusinessToTable(business) {
    const tbody = document.getElementById('resultsBody');
    const row = document.createElement('tr');
    
    const statusBadge = '<span class="status-badge status-success">✓ Scraped</span>';
    
    // Make business name clickable with Google Maps link
    const businessName = business.url && business.url !== 'Not given'
        ? `<a href="${business.url}" target="_blank" class="business-name-link">${business.name}</a>`
        : `<strong>${business.name}</strong>`;
    
    const rating = business.rating !== 'Not given' ? `<span class="rating-stars">⭐ ${business.rating}</span>` : 'Not given';
    const website = business.website !== 'Not given' 
        ? `<a href="${business.website}" target="_blank" class="website-link">Visit</a>` 
        : 'Not given';
    
    row.innerHTML = `
        <td>${statusBadge}</td>
        <td>${businessName}</td>
        <td>${business.phone}</td>
        <td>${business.email}</td>
        <td>${rating}</td>
        <td>${website}</td>
    `;
    
    tbody.appendChild(row);
}

// Add Log Entry
function addLogEntry(message, type = 'info') {
    const now = new Date();
    const time = now.toLocaleTimeString('en-US', { hour12: false });
    
    const entry = document.createElement('div');
    entry.className = 'log-entry';
    
    let className = 'log-info';
    let icon = '';
    if (type === 'success') {
        className = 'log-success';
        icon = '✓ ';
    }
    if (type === 'error') {
        className = 'log-error';
        icon = '✗ ';
    }
    
    entry.innerHTML = `<span class="log-time">[${time}]</span> <span class="${className}">${icon}${message}</span>`;
    
    liveLog.appendChild(entry);
    
    // Auto-scroll to bottom
    liveLog.scrollTop = liveLog.scrollHeight;
}

// Clear Log
function clearLog() {
    liveLog.innerHTML = '';
    addLogEntry('Log cleared', 'info');
}

// Reset Button
function resetButton() {
    startBtn.disabled = false;
    btnText.style.display = 'block';
    btnLoader.style.display = 'none';
}

// Download Results
function downloadResults(format) {
    window.location.href = `/download/${format}`;
    addLogEntry(`Downloading results as ${format.toUpperCase()}...`, 'success');
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    stopStatusPolling();
});
