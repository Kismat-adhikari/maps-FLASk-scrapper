# API Documentation

This document describes the REST API endpoints provided by the Google Maps Scraper Flask backend.

## Base URL

```
http://127.0.0.1:5000
```

## Endpoints

### 1. GET /

**Description:** Serve the main web interface

**Response:**
- HTML page with the scraper interface

**Example:**
```bash
curl http://127.0.0.1:5000
```

---

### 2. POST /upload

**Description:** Upload and parse a CSV or Excel file containing search queries

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: Form data with file field named `file`

**Accepted File Formats:**
- `.csv` - CSV file
- `.xlsx` - Excel file
- `.xls` - Excel file (legacy)

**Expected File Structure:**
```csv
keyword,zip_code,url
restaurants,10001,
coffee shops,90210,
```

**Response (Success):**
```json
{
  "message": "Scraping started",
  "query_count": 3
}
```

**Response (Error):**
```json
{
  "error": "Invalid file format. Please upload CSV or Excel file."
}
```

**Status Codes:**
- `200` - Success
- `400` - Bad request (invalid file, missing fields, validation error)
- `500` - Server error

**Example:**
```bash
curl -X POST -F "file=@sample_queries.csv" http://127.0.0.1:5000/upload
```

---

### 3. POST /start

**Description:** Start scraping with manually entered queries

**Request:**
- Method: `POST`
- Content-Type: `application/json`
- Body: JSON object with queries array

**Request Body:**
```json
{
  "queries": [
    {
      "keyword": "restaurants",
      "zip_code": "10001",
      "url": ""
    },
    {
      "keyword": "coffee shops",
      "zip_code": "90210",
      "url": ""
    }
  ]
}
```

**Response (Success):**
```json
{
  "message": "Scraping started",
  "query_count": 2
}
```

**Response (Error):**
```json
{
  "error": "Row 1: Missing or empty 'keyword' field"
}
```

**Status Codes:**
- `200` - Success
- `400` - Bad request (no queries, validation error)
- `500` - Server error

**Example:**
```bash
curl -X POST http://127.0.0.1:5000/start \
  -H "Content-Type: application/json" \
  -d '{"queries":[{"keyword":"restaurants","zip_code":"10001","url":""}]}'
```

---

### 4. GET /status

**Description:** Get current scraping status (polled by frontend every 2 seconds)

**Request:**
- Method: `GET`

**Response:**
```json
{
  "status": "running",
  "total_queries": 5,
  "processed": 2,
  "success_count": 2,
  "failure_count": 0,
  "current_query": "restaurants - 10001",
  "current_proxy": "72.46.139.137:6697",
  "results": [
    {
      "name": "Joe's Pizza",
      "address": "123 Main St, New York, NY 10001",
      "phone": "(212) 555-1234",
      "website": "https://joespizza.com",
      "rating": 4.5,
      "review_count": 1234,
      "category": "Pizza Restaurant",
      "keyword": "restaurants",
      "zip_code": "10001"
    }
  ]
}
```

**Status Values:**
- `idle` - No scraping in progress
- `running` - Scraping is active
- `completed` - Scraping finished successfully
- `stopped` - Scraping was stopped by user

**Status Codes:**
- `200` - Success

**Example:**
```bash
curl http://127.0.0.1:5000/status
```

---

### 5. POST /stop

**Description:** Stop the current scraping operation

**Request:**
- Method: `POST`

**Response:**
```json
{
  "message": "Scraping stopped"
}
```

**Status Codes:**
- `200` - Success

**Example:**
```bash
curl -X POST http://127.0.0.1:5000/stop
```

---

### 6. GET /download/csv

**Description:** Download scraping results as CSV file

**Request:**
- Method: `GET`

**Response:**
- Content-Type: `text/csv`
- File download with name: `google_maps_results_YYYYMMDD_HHMMSS.csv`

**Response (Error):**
```json
{
  "error": "No results available"
}
```

**Status Codes:**
- `200` - Success (file download)
- `404` - No results available

**Example:**
```bash
curl http://127.0.0.1:5000/download/csv -o results.csv
```

---

### 7. GET /download/json

**Description:** Download scraping results as JSON file

**Request:**
- Method: `GET`

**Response:**
- Content-Type: `application/json`
- File download with name: `google_maps_results_YYYYMMDD_HHMMSS.json`

**Response (Error):**
```json
{
  "error": "No results available"
}
```

**Status Codes:**
- `200` - Success (file download)
- `404` - No results available

**Example:**
```bash
curl http://127.0.0.1:5000/download/json -o results.json
```

---

## Data Models

### Query Object

```json
{
  "keyword": "string (required)",
  "zip_code": "string (required)",
  "url": "string (optional)"
}
```

### Business Object

```json
{
  "name": "string",
  "address": "string",
  "phone": "string or null",
  "website": "string or null",
  "rating": "float or null",
  "review_count": "integer or null",
  "category": "string or null",
  "keyword": "string",
  "zip_code": "string"
}
```

### Application State Object

```json
{
  "status": "idle | running | completed | stopped",
  "total_queries": "integer",
  "processed": "integer",
  "success_count": "integer",
  "failure_count": "integer",
  "current_query": "string",
  "current_proxy": "string",
  "results": "array of Business objects"
}
```

---

## Error Handling

All endpoints return JSON error responses in the following format:

```json
{
  "error": "Error message description"
}
```

Common error scenarios:

1. **File Upload Errors**
   - No file provided
   - Invalid file format
   - File parsing error
   - Validation error (missing required fields)

2. **Scraping Errors**
   - No proxies available
   - All proxies failed
   - Browser initialization failed
   - Network errors

3. **Download Errors**
   - No results available
   - Invalid format specified

---

## Rate Limiting

Currently, there is no rate limiting on the API endpoints. However, the scraper implements natural rate limiting through:

- Proxy rotation (every 14 requests)
- Delays between queries (2 seconds)
- Browser initialization overhead (~2 seconds per proxy rotation)

---

## Authentication

The current version does not implement authentication. If deploying beyond localhost, consider adding:

- API key authentication
- Session-based authentication
- OAuth 2.0

---

## CORS

CORS is not configured by default since the application is designed for localhost use. If you need to access the API from a different origin, add Flask-CORS:

```python
from flask_cors import CORS
CORS(app)
```

---

## WebSocket Support

The current implementation uses HTTP polling (every 2 seconds) for status updates. For real-time updates, consider implementing WebSocket support with Flask-SocketIO.

---

## Example Workflow

1. **Start scraping with file upload:**
```bash
# Upload file
curl -X POST -F "file=@queries.csv" http://127.0.0.1:5000/upload

# Poll status
curl http://127.0.0.1:5000/status

# Download results
curl http://127.0.0.1:5000/download/csv -o results.csv
```

2. **Start scraping with manual queries:**
```bash
# Start scraping
curl -X POST http://127.0.0.1:5000/start \
  -H "Content-Type: application/json" \
  -d '{"queries":[{"keyword":"restaurants","zip_code":"10001","url":""}]}'

# Poll status
curl http://127.0.0.1:5000/status

# Stop if needed
curl -X POST http://127.0.0.1:5000/stop

# Download results
curl http://127.0.0.1:5000/download/json -o results.json
```

---

## Notes

- The scraper runs in a background thread, so API responses are immediate
- Status polling is required to track progress
- Results are stored in memory and cleared on new scraping session
- File uploads are temporarily stored in the `uploads/` directory
- Maximum file upload size is 5MB (configurable in `config.py`)
