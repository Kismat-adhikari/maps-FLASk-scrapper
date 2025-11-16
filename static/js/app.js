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
const searchUrlInput = document.getElementById('searchUrl');
const businessUrlsInput = document.getElementById('businessUrls');
const fileUploadInput = document.getElementById('fileUpload');
const fileUploadText = document.getElementById('fileUploadText');
const statusSection = document.getElementById('statusSection');
const resultsSection = document.getElementById('resultsSection');
const completionMessage = document.getElementById('completionMessage');
const liveLog = document.getElementById('liveLog');
const clearLogBtn = document.getElementById('clearLogBtn');
const downloadBtn = document.getElementById('downloadBtn');

// Tab switching
let activeTab = 'keyword';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    startBtn.addEventListener('click', handleStartScraping);
    clearLogBtn.addEventListener('click', clearLog);
    downloadBtn.addEventListener('click', () => downloadResults('csv'));
    
    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });
    
    // File upload handling
    fileUploadInput.addEventListener('change', handleFileSelect);
    
    addLogEntry('System ready. Choose your input method and start scraping.', 'info');
});

// Handle file selection
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        fileUploadText.textContent = file.name;
        addLogEntry(`File selected: ${file.name}`, 'info');
    } else {
        fileUploadText.textContent = 'Choose file or drag here';
    }
}

// Switch between tabs
function switchTab(tab) {
    activeTab = tab;
    
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tab);
    });
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(tab + 'Tab').classList.add('active');
}

// Start Scraping
async function handleStartScraping() {
    let requestData = {};
    let isFileUpload = false;
    
    // Validate based on active tab
    if (activeTab === 'keyword') {
        const keyword = keywordInput.value.trim();
        const location = locationInput.value.trim();
        
        if (!keyword || !location) {
            addLogEntry('Error: Please enter both keyword and location', 'error');
            return;
        }
        
        requestData = {
            mode: 'keyword',
            keyword: keyword,
            location: location
        };
    } else if (activeTab === 'file') {
        const file = fileUploadInput.files[0];
        
        if (!file) {
            addLogEntry('Error: Please select a file to upload', 'error');
            return;
        }
        
        isFileUpload = true;
        
    } else if (activeTab === 'url') {
        const searchUrl = searchUrlInput.value.trim();
        const businessUrls = businessUrlsInput.value.trim();
        
        if (!searchUrl && !businessUrls) {
            addLogEntry('Error: Please enter either a search URL or business URLs', 'error');
            return;
        }
        
        if (searchUrl && businessUrls) {
            addLogEntry('Error: Please use either search URL OR business URLs, not both', 'error');
            return;
        }
        
        if (searchUrl) {
            requestData = {
                mode: 'search_url',
                url: searchUrl
            };
        } else {
            // Parse business URLs (one per line)
            const urls = businessUrls.split('\n')
                .map(url => url.trim())
                .filter(url => url.length > 0);
            
            if (urls.length === 0) {
                addLogEntry('Error: No valid URLs found', 'error');
                return;
            }
            
            requestData = {
                mode: 'business_urls',
                urls: urls
            };
        }
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
    
    // Log based on mode
    if (isFileUpload) {
        addLogEntry(`Uploading file...`, 'info');
    } else if (requestData.mode === 'keyword') {
        addLogEntry(`Starting scrape: "${requestData.keyword}" in "${requestData.location}"`, 'info');
    } else if (requestData.mode === 'search_url') {
        addLogEntry(`Starting scrape from search URL`, 'info');
    } else if (requestData.mode === 'business_urls') {
        addLogEntry(`Starting scrape for ${requestData.urls.length} business URLs`, 'info');
    }
    
    try {
        let response;
        
        if (isFileUpload) {
            // File upload uses FormData
            const formData = new FormData();
            formData.append('file', fileUploadInput.files[0]);
            
            response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
        } else {
            // Regular JSON request
            response = await fetch('/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
        }
        
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
        // Mask proxy IP (show only first two octets)
        let maskedProxy = '-';
        if (data.current_proxy) {
            const parts = data.current_proxy.split(':');
            if (parts.length === 2) {
                const ipParts = parts[0].split('.');
                if (ipParts.length === 4) {
                    maskedProxy = `${ipParts[0]}.${ipParts[1]}.xx.xx:xxxx`;
                } else {
                    maskedProxy = data.current_proxy;
                }
            } else {
                maskedProxy = data.current_proxy;
            }
        }
        document.getElementById('currentProxy').textContent = maskedProxy;
        
        // Show actual number of businesses scraped (not queries)
        document.getElementById('scrapedCount').textContent = data.results ? data.results.length : 0;
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
            
            data.results.forEach((business, index) => {
                // Use index as unique ID to show all results (including duplicates from Google Maps)
                const businessId = index;
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
