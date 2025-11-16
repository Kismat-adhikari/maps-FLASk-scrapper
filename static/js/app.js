// Google Maps Scraper - Frontend JavaScript

// Global state
let statusPollingInterval = null;
let isScrapingActive = false;

// DOM Elements
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const addRowBtn = document.getElementById('addRowBtn');
const startManualBtn = document.getElementById('startManualBtn');
const stopBtn = document.getElementById('stopBtn');
const downloadCsvBtn = document.getElementById('downloadCsvBtn');
const downloadJsonBtn = document.getElementById('downloadJsonBtn');
const manualEntryBody = document.getElementById('manualEntryBody');
const resultsSection = document.getElementById('resultsSection');
const messageContainer = document.getElementById('messageContainer');

// Status elements
const statusValue = document.getElementById('statusValue');
const currentQuery = document.getElementById('currentQuery');
const currentProxy = document.getElementById('currentProxy');
const processedCount = document.getElementById('processedCount');
const successCount = document.getElementById('successCount');
const failureCount = document.getElementById('failureCount');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const totalResults = document.getElementById('totalResults');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    console.log('Google Maps Scraper initialized');
});

// Setup event listeners
function setupEventListeners() {
    uploadBtn.addEventListener('click', handleFileUpload);
    addRowBtn.addEventListener('click', addManualEntryRow);
    startManualBtn.addEventListener('click', handleManualStart);
    stopBtn.addEventListener('click', handleStop);
    downloadCsvBtn.addEventListener('click', () => downloadResults('csv'));
    downloadJsonBtn.addEventListener('click', () => downloadResults('json'));
}

// File Upload Handler
async function handleFileUpload() {
    const file = fileInput.files[0];
    
    if (!file) {
        showMessage('Please select a file', 'error');
        return;
    }
    
    // Validate file type
    const validExtensions = ['.csv', '.xlsx', '.xls'];
    const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    
    if (!validExtensions.includes(fileExtension)) {
        showMessage('Invalid file format. Please upload CSV or Excel file.', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        uploadBtn.disabled = true;
        uploadBtn.textContent = 'Uploading...';
        
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(`Scraping started with ${data.query_count} queries`, 'success');
            startStatusPolling();
            updateUIForScraping(true);
        } else {
            showMessage(data.error || 'Upload failed', 'error');
        }
    } catch (error) {
        showMessage('Error uploading file: ' + error.message, 'error');
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.textContent = 'Upload & Start';
    }
}

// Add manual entry row
function addManualEntryRow() {
    const row = document.createElement('tr');
    row.className = 'entry-row';
    row.innerHTML = `
        <td><input type="text" class="keyword-input" placeholder="e.g., restaurants" /></td>
        <td><input type="text" class="zipcode-input" placeholder="e.g., New York or 10001" /></td>
        <td><input type="text" class="url-input" placeholder="Optional" /></td>
        <td><button class="btn-remove" onclick="removeRow(this)">Remove</button></td>
    `;
    manualEntryBody.appendChild(row);
}

// Remove row function (global scope for onclick)
function removeRow(button) {
    const row = button.closest('tr');
    // Keep at least one row
    if (manualEntryBody.children.length > 1) {
        row.remove();
    } else {
        showMessage('At least one row is required', 'error');
    }
}

// Handle manual start
async function handleManualStart() {
    const queries = [];
    const rows = manualEntryBody.querySelectorAll('.entry-row');
    
    // Collect data from rows
    rows.forEach((row, index) => {
        const keyword = row.querySelector('.keyword-input').value.trim();
        const zipCode = row.querySelector('.zipcode-input').value.trim();
        const url = row.querySelector('.url-input').value.trim();
        
        if (keyword && zipCode) {
            queries.push({
                keyword: keyword,
                zip_code: zipCode,
                url: url || ''
            });
        }
    });
    
    if (queries.length === 0) {
        showMessage('Please enter at least one valid query (keyword and location required)', 'error');
        return;
    }
    
    try {
        startManualBtn.disabled = true;
        startManualBtn.textContent = 'Starting...';
        
        const response = await fetch('/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ queries: queries })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(`Scraping started with ${data.query_count} queries`, 'success');
            startStatusPolling();
            updateUIForScraping(true);
        } else {
            showMessage(data.error || 'Failed to start scraping', 'error');
        }
    } catch (error) {
        showMessage('Error starting scraping: ' + error.message, 'error');
    } finally {
        startManualBtn.disabled = false;
        startManualBtn.textContent = 'Start Scraping';
    }
}

// Handle stop
async function handleStop() {
    try {
        stopBtn.disabled = true;
        
        const response = await fetch('/stop', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(data.message, 'info');
        }
    } catch (error) {
        showMessage('Error stopping scraping: ' + error.message, 'error');
    } finally {
        stopBtn.disabled = false;
    }
}

// Start status polling
function startStatusPolling() {
    if (statusPollingInterval) {
        clearInterval(statusPollingInterval);
    }
    
    // Poll every 2 seconds
    statusPollingInterval = setInterval(updateStatus, 2000);
    
    // Update immediately
    updateStatus();
}

// Stop status polling
function stopStatusPolling() {
    if (statusPollingInterval) {
        clearInterval(statusPollingInterval);
        statusPollingInterval = null;
    }
}

// Update status from server
async function updateStatus() {
    try {
        const response = await fetch('/status');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Update status display
        statusValue.textContent = capitalizeFirst(data.status);
        currentQuery.textContent = data.current_query || '-';
        currentProxy.textContent = data.current_proxy || '-';
        processedCount.textContent = `${data.processed} / ${data.total_queries}`;
        successCount.textContent = data.success_count;
        failureCount.textContent = data.failure_count;
        
        // Update progress bar
        const percentage = data.total_queries > 0 
            ? Math.round((data.processed / data.total_queries) * 100) 
            : 0;
        progressFill.style.width = percentage + '%';
        progressText.textContent = percentage + '%';
        
        // Check if scraping is complete or stopped
        if (data.status === 'completed' || data.status === 'stopped') {
            stopStatusPolling();
            updateUIForScraping(false);
            
            if (data.results && data.results.length > 0) {
                showResultsSection(data.results.length);
                showMessage(`Scraping completed! Found ${data.results.length} businesses.`, 'success');
            } else {
                showMessage('Scraping completed but no results found. Try different keywords or check logs.', 'info');
            }
            
            // Show summary
            if (data.failure_count > 0) {
                showMessage(`${data.failure_count} queries failed. Check proxy configuration or try again.`, 'error');
            }
        } else if (data.status === 'running') {
            isScrapingActive = true;
        }
        
    } catch (error) {
        console.error('Error fetching status:', error);
        // Don't show error message for every poll failure, just log it
    }
}

// Update UI for scraping state
function updateUIForScraping(isActive) {
    isScrapingActive = isActive;
    
    // Disable/enable inputs
    uploadBtn.disabled = isActive;
    startManualBtn.disabled = isActive;
    addRowBtn.disabled = isActive;
    stopBtn.disabled = !isActive;
    fileInput.disabled = isActive;
    
    // Disable/enable manual entry inputs
    const inputs = manualEntryBody.querySelectorAll('input');
    inputs.forEach(input => input.disabled = isActive);
    
    const removeButtons = manualEntryBody.querySelectorAll('.btn-remove');
    removeButtons.forEach(btn => btn.disabled = isActive);
}

// Show results section
function showResultsSection(count) {
    totalResults.textContent = count;
    resultsSection.style.display = 'block';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Download results
function downloadResults(format) {
    window.location.href = `/download/${format}`;
    showMessage(`Downloading results as ${format.toUpperCase()}...`, 'success');
}

// Show message
function showMessage(text, type = 'info') {
    const message = document.createElement('div');
    message.className = `message ${type}`;
    message.textContent = text;
    
    messageContainer.appendChild(message);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        message.style.opacity = '0';
        setTimeout(() => message.remove(), 300);
    }, 5000);
}

// Utility: Capitalize first letter
function capitalizeFirst(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    stopStatusPolling();
});
