"""
Google Maps Scraper - Flask Application
Main entry point for the web application.
"""

import os
import asyncio
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import pandas as pd
import json
from datetime import datetime
from threading import Thread

from config import Config
from modules.proxy_manager import ProxyManager
from modules.file_parser import FileParser
from modules.scraper import GoogleMapsScraper
from modules.utils import DataUtils, NotificationManager, ProxyHealthMonitor


# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    handlers=[
        RotatingFileHandler(Config.LOG_FILE, maxBytes=10*1024*1024, backupCount=3),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Global application state
app_state = {
    'status': 'idle',  # idle, running, completed, stopped
    'total_queries': 0,
    'processed': 0,
    'success_count': 0,
    'failure_count': 0,
    'current_query': '',
    'current_proxy': '',
    'results': []
}

# Global instances
proxy_manager = None
scraper = None
notification_manager = None
proxy_health_monitor = None


def initialize_components():
    """Initialize proxy manager and scraper."""
    global proxy_manager, scraper, notification_manager, proxy_health_monitor
    
    try:
        proxy_manager = ProxyManager(
            proxy_file=Config.PROXY_FILE,
            rotation_threshold=Config.ROTATION_THRESHOLD
        )
        proxy_count = proxy_manager.get_proxy_count()
        logger.info(f"Initialized ProxyManager with {proxy_count} proxies")
        
        # Validate minimum proxy count
        if proxy_count < Config.MIN_PROXY_COUNT:
            logger.error(f"Insufficient proxies! Found {proxy_count}, need at least {Config.MIN_PROXY_COUNT}")
            logger.error(f"Add proxies to {Config.PROXY_FILE} in format: IP:PORT:USERNAME:PASSWORD")
            return False
        
        scraper = GoogleMapsScraper(
            proxy_manager=proxy_manager,
            headless=Config.HEADLESS
        )
        logger.info("Initialized GoogleMapsScraper")
        
        # Initialize notification manager if enabled
        if Config.ENABLE_NOTIFICATIONS:
            notification_manager = NotificationManager(
                email=Config.NOTIFICATION_EMAIL,
                webhook=Config.NOTIFICATION_WEBHOOK
            )
            logger.info("Initialized NotificationManager")
        
        # Initialize proxy health monitor
        proxy_health_monitor = ProxyHealthMonitor()
        logger.info("Initialized ProxyHealthMonitor")
        
        return True
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        return False


def reset_state():
    """Reset application state to initial values."""
    global app_state
    app_state = {
        'status': 'idle',
        'total_queries': 0,
        'processed': 0,
        'success_count': 0,
        'failure_count': 0,
        'current_query': '',
        'current_proxy': '',
        'results': []
    }


async def scrape_queries_async(queries):
    """
    Asynchronously scrape all queries with comprehensive error handling.
    Saves results incrementally to CSV.
    
    Args:
        queries: List of query dictionaries
    """
    global app_state, scraper, proxy_manager
    
    try:
        app_state['status'] = 'running'
        app_state['total_queries'] = len(queries)
        app_state['processed'] = 0
        app_state['success_count'] = 0
        app_state['failure_count'] = 0
        app_state['results'] = []
        
        logger.info(f"Starting scraping for {len(queries)} queries")
    except Exception as e:
        logger.error(f"Error initializing scrape: {e}", exc_info=True)
        app_state['status'] = 'completed'
        return
    
    # Setup incremental CSV saving
    location = queries[0].get('zip_code', 'results') if queries else 'results'
    location = location.lower().replace(' ', '-')
    timestamp = datetime.now().strftime('%Y-%m-%d')
    csv_filename = f'{location}-{timestamp}.csv'
    csv_filepath = os.path.join('output', csv_filename)
    
    # Create CSV file with headers
    csv_headers_written = False
    
    def save_to_csv(business_info):
        """Callback to save each business to CSV incrementally AND update app_state for real-time map."""
        nonlocal csv_headers_written
        
        try:
            # Add to app_state results immediately for real-time map updates
            app_state['results'].append(business_info)
            logger.debug(f"Added business to app_state for real-time map: {business_info.get('name')}")
            
            df = pd.DataFrame([business_info])
            
            # Write headers only once
            if not csv_headers_written:
                df.to_csv(csv_filepath, mode='w', index=False, header=True)
                csv_headers_written = True
                logger.info(f"Created CSV file: {csv_filepath}")
            else:
                df.to_csv(csv_filepath, mode='a', index=False, header=False)
            
            logger.debug(f"Saved business to CSV: {business_info.get('name')}")
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
    
    for idx, query in enumerate(queries, start=1):
        # Check if stopped
        if app_state['status'] == 'stopped':
            logger.info("Scraping stopped by user")
            break
        
        keyword = query.get('keyword', '')
        zip_code = query.get('zip_code', '')
        
        app_state['current_query'] = f"{keyword} - {zip_code}"
        app_state['current_proxy'] = proxy_manager.get_current_proxy_info()
        
        logger.info(f"Processing query {idx}/{len(queries)}: {keyword} in {zip_code}")
        logger.info(f"Using proxy: {app_state['current_proxy']}")
        
        try:
            # Scrape the query with incremental CSV saving (businesses are added to app_state in real-time via callback)
            businesses = await scraper.scrape_query(query, csv_callback=save_to_csv)
            
            if businesses:
                # Don't extend results here - already added via callback for real-time updates
                app_state['success_count'] += 1
                logger.info(f"Query successful: {len(businesses)} businesses found")
            else:
                app_state['failure_count'] += 1
                logger.warning(f"Query failed or returned no results after retries")
            
        except Exception as e:
            logger.error(f"Unexpected error scraping query: {e}", exc_info=True)
            app_state['failure_count'] += 1
            
            # Try to recover by marking proxy as failed
            try:
                proxy_manager.mark_failure()
            except Exception as pm_error:
                logger.error(f"Error marking proxy failure: {pm_error}")
        
        app_state['processed'] += 1
        
        # Configurable delay between queries to avoid rate limiting
        await asyncio.sleep(Config.DELAY_BETWEEN_QUERIES)
    
    # Cleanup
    try:
        await scraper.cleanup()
        logger.info("Scraper cleanup completed")
    except Exception as e:
        logger.error(f"Error during scraper cleanup: {e}")
    
    # Deduplicate results if enabled
    original_count = len(app_state['results'])
    if Config.DEDUPLICATE_RESULTS and app_state['results']:
        app_state['results'] = DataUtils.deduplicate_businesses(
            app_state['results'],
            method=Config.DEDUP_METHOD
        )
        unique_count = len(app_state['results'])
        logger.info(f"Deduplication: {original_count} -> {unique_count} businesses")
    
    # Update final status
    if app_state['status'] != 'stopped':
        app_state['status'] = 'completed'
    
    app_state['current_query'] = ''
    
    logger.info(f"Scraping finished: {app_state['success_count']} successful, {app_state['failure_count']} failed")
    logger.info(f"Total businesses collected: {len(app_state['results'])}")
    logger.info(f"Results saved to: {csv_filepath}")
    
    # Send completion notification if enabled
    if notification_manager and Config.ENABLE_NOTIFICATIONS:
        try:
            notification_manager.send_completion_notification({
                'total_queries': len(queries),
                'success_count': app_state['success_count'],
                'failure_count': app_state['failure_count'],
                'total_businesses': original_count,
                'unique_businesses': len(app_state['results'])
            })
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")


def run_scraping_thread(queries):
    """
    Run scraping in a separate thread with asyncio.
    
    Args:
        queries: List of query dictionaries
    """
    try:
        logger.info("Scraping thread started")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(scrape_queries_async(queries))
        loop.close()
        logger.info("Scraping thread completed")
    except Exception as e:
        logger.error(f"Error in scraping thread: {e}", exc_info=True)
        app_state['status'] = 'completed'
        app_state['failure_count'] += 1


@app.route('/')
def index():
    """Serve the main web interface."""
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """Serve the proxy health dashboard."""
    return render_template('dashboard.html')


@app.route('/download-template')
def download_template():
    """Download a sample CSV template."""
    import io
    from flask import send_file
    
    # Create sample CSV content
    csv_content = """keyword,zip_code,url
restaurants,10001,
coffee shops,90210,
plumbers,33101,
,,https://www.google.com/maps/search/dentists+miami
,,https://www.google.com/maps/place/Business+Name/@40.7308,-73.9973,17z"""
    
    # Create a BytesIO object
    buffer = io.BytesIO()
    buffer.write(csv_content.encode('utf-8'))
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='text/csv',
        as_attachment=True,
        download_name='google_maps_scraper_template.csv'
    )


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handle file upload (CSV or Excel).
    Parse and validate the file, then start scraping.
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file extension
        if not file.filename.lower().endswith(('.csv', '.xlsx', '.xls')):
            return jsonify({'error': 'Invalid file format. Please upload CSV or Excel file.'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        logger.info(f"File uploaded: {filename}")
        
        # Parse file
        queries, error = FileParser.parse_file(filepath)
        
        if error:
            return jsonify({'error': error}), 400
        
        if not queries:
            return jsonify({'error': 'No valid queries found in file'}), 400
        
        # Reset state
        reset_state()
        
        # Start scraping in background thread
        thread = Thread(target=run_scraping_thread, args=(queries,))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'message': 'Scraping started',
            'query_count': len(queries)
        }), 200
        
    except Exception as e:
        logger.error(f"Error in upload: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/start', methods=['POST'])
def start_scraping():
    """
    Start scraping with manually entered queries or URLs.
    Supports three modes:
    - keyword: keyword + location search
    - search_url: Google Maps search URL
    - business_urls: Multiple business URLs
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        mode = data.get('mode', 'keyword')
        queries = []
        
        if mode == 'keyword':
            # Traditional keyword + location mode
            keyword = data.get('keyword', '').strip()
            location = data.get('location', '').strip()
            
            if not keyword or not location:
                return jsonify({'error': 'Keyword and location are required'}), 400
            
            queries = [{
                'keyword': keyword,
                'zip_code': location,
                'url': ''
            }]
            
        elif mode == 'search_url':
            # Google Maps search URL mode
            url = data.get('url', '').strip()
            
            if not url:
                return jsonify({'error': 'Search URL is required'}), 400
            
            if 'google.com/maps' not in url:
                return jsonify({'error': 'Invalid Google Maps URL'}), 400
            
            queries = [{
                'keyword': '',
                'zip_code': '',
                'url': url
            }]
            
        elif mode == 'business_urls':
            # Multiple business URLs mode
            urls = data.get('urls', [])
            
            if not urls or len(urls) == 0:
                return jsonify({'error': 'At least one business URL is required'}), 400
            
            # Validate URLs
            for url in urls:
                if 'google.com/maps' not in url:
                    return jsonify({'error': f'Invalid Google Maps URL: {url}'}), 400
            
            # Create a query for each URL
            queries = [{
                'keyword': '',
                'zip_code': '',
                'url': url
            } for url in urls]
            
        else:
            return jsonify({'error': 'Invalid mode'}), 400
        
        # Reset state
        reset_state()
        
        # Start scraping in background thread
        logger.info(f"Creating scraping thread for {len(queries)} queries (mode: {mode})")
        thread = Thread(target=run_scraping_thread, args=(queries,))
        thread.daemon = True
        thread.start()
        logger.info("Scraping thread started successfully")
        
        return jsonify({
            'message': 'Scraping started',
            'query_count': len(queries)
        }), 200
        
    except Exception as e:
        logger.error(f"Error in start: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/status')
def get_status():
    """
    Get current scraping status.
    Returns JSON with current state.
    """
    return jsonify(app_state)


@app.route('/stop', methods=['POST'])
def stop_scraping():
    """Stop the current scraping operation."""
    global app_state
    
    if app_state['status'] == 'running':
        app_state['status'] = 'stopped'
        logger.info("Scraping stop requested")
        return jsonify({'message': 'Scraping stopped'}), 200
    else:
        return jsonify({'message': 'No scraping in progress'}), 200


@app.route('/proxy-health')
def get_proxy_health():
    """
    Get proxy health statistics.
    Returns success rates and performance metrics for all proxies.
    """
    if not proxy_health_monitor:
        return jsonify({'error': 'Proxy health monitor not initialized'}), 500
    
    stats = proxy_health_monitor.get_proxy_stats()
    best_proxy = proxy_health_monitor.get_best_proxy()
    
    return jsonify({
        'proxy_stats': stats,
        'best_proxy': best_proxy,
        'total_proxies': proxy_manager.get_proxy_count() if proxy_manager else 0
    })


@app.route('/download/<format>')
def download_results(format):
    """
    Download results in specified format (csv or json).
    Also saves a copy in the output/ folder.
    
    Args:
        format: 'csv' or 'json'
    """
    try:
        if not app_state['results']:
            return jsonify({'error': 'No results available'}), 404
        
        # Get location from first result for filename
        location = 'results'
        if app_state['results']:
            first_result = app_state['results'][0]
            zip_code = first_result.get('zip_code', '')
            if zip_code:
                location = zip_code.lower().replace(' ', '-')
        
        timestamp = datetime.now().strftime('%Y-%m-%d')
        
        if format == 'csv':
            # Create DataFrame and save as CSV
            df = pd.DataFrame(app_state['results'])
            
            # Reorder columns to match requirements
            column_order = [
                'name', 'full_address', 'latitude', 'longitude', 'phone', 
                'website', 'email', 'rating', 'review_count', 'category', 
                'opening_hours', 'plus_code', 'cid', 'url', 'description',
                'keyword', 'zip_code'
            ]
            
            # Only include columns that exist
            existing_columns = [col for col in column_order if col in df.columns]
            df = df[existing_columns]
            
            # Save to output folder
            output_filename = f'{location}-{timestamp}.csv'
            output_filepath = os.path.join('output', output_filename)
            df.to_csv(output_filepath, index=False)
            logger.info(f"Saved results to {output_filepath}")
            
            # Also save to uploads for download
            download_filename = f'google_maps_{location}_{timestamp}.csv'
            download_filepath = os.path.join(app.config['UPLOAD_FOLDER'], download_filename)
            df.to_csv(download_filepath, index=False)
            
            return send_file(
                download_filepath,
                mimetype='text/csv',
                as_attachment=True,
                download_name=download_filename
            )
        
        elif format == 'json':
            # Save as JSON
            output_filename = f'{location}-{timestamp}.json'
            output_filepath = os.path.join('output', output_filename)
            
            with open(output_filepath, 'w') as f:
                json.dump(app_state['results'], f, indent=2)
            logger.info(f"Saved results to {output_filepath}")
            
            # Also save to uploads for download
            download_filename = f'google_maps_{location}_{timestamp}.json'
            download_filepath = os.path.join(app.config['UPLOAD_FOLDER'], download_filename)
            
            with open(download_filepath, 'w') as f:
                json.dump(app_state['results'], f, indent=2)
            
            return send_file(
                download_filepath,
                mimetype='application/json',
                as_attachment=True,
                download_name=download_filename
            )
        
        else:
            return jsonify({'error': 'Invalid format. Use csv or json'}), 400
    
    except Exception as e:
        logger.error(f"Error in download: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    logger.info("Starting Google Maps Scraper application")
    
    # Initialize components
    if initialize_components():
        logger.info("All components initialized successfully")
        logger.info(f"Server starting at http://127.0.0.1:5000")
        app.run(host='127.0.0.1', port=5000, debug=False)
    else:
        logger.error("Failed to initialize components. Exiting.")
