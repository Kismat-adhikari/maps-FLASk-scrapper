# Requirements Document

## Introduction

This document defines the requirements for a Google Maps scraping web application. The system enables users to extract business information from Google Maps without using an API key. The application uses Flask for the backend, Playwright for browser automation, and a web frontend for user interaction. The system implements intelligent proxy rotation to avoid detection and CAPTCHAs.

## Glossary

- **Scraper System**: The complete Google Maps scraping web application including frontend, backend, and scraper module
- **Proxy Pool**: A collection of 10 proxy servers used for rotating IP addresses
- **Rotation Cycle**: The process of switching to the next proxy after 14 requests or upon proxy failure
- **Search Query**: A combination of keyword, zip code, and optional URL used to search Google Maps
- **Business Record**: Extracted information including name, address, phone, website, rating, and review count
- **Flask Server**: The Python web server that handles HTTP requests and coordinates scraping operations
- **Playwright Browser**: The automated browser instance used to interact with Google Maps
- **Input Source**: Either a CSV/Excel file upload or manual form entry containing search queries

## Requirements

### Requirement 1

**User Story:** As a user, I want to input search queries through multiple methods, so that I can flexibly provide data based on my workflow

#### Acceptance Criteria

1. THE Scraper System SHALL accept CSV file uploads containing keyword, zip code, and URL columns
2. THE Scraper System SHALL accept Excel file uploads containing keyword, zip code, and URL columns
3. THE Scraper System SHALL provide a web form for manual entry of keyword, zip code, and URL data
4. WHEN a user uploads a file, THE Scraper System SHALL parse and validate the file contents before processing
5. THE Scraper System SHALL display validation errors when uploaded files contain invalid data formats

### Requirement 2

**User Story:** As a user, I want to see real-time scraping progress, so that I can monitor the operation and know when it completes

#### Acceptance Criteria

1. WHILE scraping is active, THE Scraper System SHALL display the current progress percentage
2. WHILE scraping is active, THE Scraper System SHALL show which Search Query is currently being processed
3. WHILE scraping is active, THE Scraper System SHALL display the currently active proxy from the Proxy Pool
4. THE Scraper System SHALL update the success count in real-time as Business Records are collected
5. THE Scraper System SHALL update the failure count in real-time when requests fail

### Requirement 3

**User Story:** As a user, I want to download scraped results, so that I can use the data in my business workflows

#### Acceptance Criteria

1. WHEN scraping completes, THE Scraper System SHALL provide a download button for results
2. THE Scraper System SHALL export results in CSV format
3. THE Scraper System SHALL export results in JSON format
4. THE Scraper System SHALL include all collected Business Record fields in the exported file
5. WHEN no results are collected, THE Scraper System SHALL display a message indicating no data is available

### Requirement 4

**User Story:** As a user, I want the system to rotate proxies intelligently, so that I can avoid CAPTCHAs and IP bans while scraping

#### Acceptance Criteria

1. THE Scraper System SHALL maintain a Proxy Pool of exactly 10 proxy servers
2. THE Scraper System SHALL rotate to the next proxy after every 14th request attempt
3. IF a proxy fails during a request, THEN THE Scraper System SHALL immediately switch to the next proxy in the Proxy Pool
4. THE Scraper System SHALL continue the Rotation Cycle sequentially through all proxies in the Proxy Pool
5. WHEN a proxy triggers a CAPTCHA, THE Scraper System SHALL treat it as a failure and rotate to the next proxy

### Requirement 5

**User Story:** As a user, I want to scrape Google Maps in a visible browser, so that I can watch the automation process in real-time

#### Acceptance Criteria

1. WHEN scraping starts, THE Scraper System SHALL launch a visible Playwright Browser window
2. THE Scraper System SHALL navigate the Playwright Browser to Google Maps for each Search Query
3. THE Scraper System SHALL perform search operations using the keyword and zip code from the Search Query
4. THE Scraper System SHALL extract Business Record fields including name, address, phone, website, rating, and review count
5. THE Scraper System SHALL keep the Playwright Browser visible throughout the scraping session

### Requirement 6

**User Story:** As a user, I want to access the scraper through a web interface, so that I can easily control it from any browser on my local network

#### Acceptance Criteria

1. WHEN the Flask Server starts, THE Scraper System SHALL bind to address 127.0.0.1 on port 5000
2. THE Scraper System SHALL serve a web interface accessible via HTTP
3. THE Scraper System SHALL provide a start button to initiate scraping operations
4. THE Scraper System SHALL provide a stop button to halt scraping operations
5. THE Scraper System SHALL display the Flask Server URL to the user upon startup

### Requirement 7

**User Story:** As a user, I want the system to handle errors gracefully, so that scraping continues even when individual requests fail

#### Acceptance Criteria

1. IF a proxy times out, THEN THE Scraper System SHALL log the failure and rotate to the next proxy
2. IF a Search Query fails after trying all proxies, THEN THE Scraper System SHALL record the failure and continue with the next query
3. WHEN the Playwright Browser crashes, THE Scraper System SHALL restart the browser and resume scraping
4. THE Scraper System SHALL log all errors with timestamps and proxy information
5. THE Scraper System SHALL continue processing remaining Search Queries when individual queries fail

### Requirement 8

**User Story:** As a user, I want the system to be modular and maintainable, so that I can easily migrate to other platforms like Apify in the future

#### Acceptance Criteria

1. THE Scraper System SHALL separate scraping logic into an independent module
2. THE Scraper System SHALL separate proxy management into an independent module
3. THE Scraper System SHALL separate Flask Server routes from business logic
4. THE Scraper System SHALL use configuration files for proxy lists and scraping parameters
5. THE Scraper System SHALL provide clear interfaces between frontend, backend, and scraper components
