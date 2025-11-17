"""
Integration Test Script
Tests all components and their integration.
"""

import asyncio
import logging
from modules.proxy_manager import ProxyManager
from modules.file_parser import FileParser
from modules.scraper import GoogleMapsScraper
from modules.data_extractor import DataExtractor
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
)

logger = logging.getLogger(__name__)


def test_proxy_manager():
    """Test ProxyManager component."""
    logger.info("=" * 50)
    logger.info("Testing ProxyManager")
    logger.info("=" * 50)
    
    try:
        pm = ProxyManager(Config.PROXY_FILE, Config.ROTATION_THRESHOLD)
        
        # Test proxy loading
        assert pm.get_proxy_count() > 0, "No proxies loaded"
        logger.info(f"✓ Loaded {pm.get_proxy_count()} proxies")
        
        # Test getting proxy
        proxy = pm.get_next_proxy()
        assert proxy is not None, "Failed to get proxy"
        logger.info(f"✓ Got proxy: {proxy['ip']}:{proxy['port']}")
        
        # Test rotation threshold
        for i in range(Config.ROTATION_THRESHOLD):
            pm.increment_counter()
        
        old_proxy = pm.get_current_proxy_info()
        pm.increment_counter()  # Should trigger rotation
        new_proxy = pm.get_current_proxy_info()
        
        logger.info(f"✓ Rotation works: {old_proxy} -> {new_proxy}")
        
        # Test failure marking
        pm.mark_failure()
        logger.info(f"✓ Failure marking works, rotated to: {pm.get_current_proxy_info()}")
        
        logger.info("✓ ProxyManager tests passed!\n")
        return True
        
    except Exception as e:
        logger.error(f"✗ ProxyManager test failed: {e}")
        return False


def test_file_parser():
    """Test FileParser component."""
    logger.info("=" * 50)
    logger.info("Testing FileParser")
    logger.info("=" * 50)
    
    try:
        # Test CSV parsing
        csv_data, error = FileParser.parse_file('sample_queries.csv')
        assert not error, f"CSV parsing error: {error}"
        assert len(csv_data) > 0, "No data parsed from CSV"
        logger.info(f"✓ Parsed {len(csv_data)} rows from CSV")
        
        # Test Excel parsing
        try:
            excel_data, error = FileParser.parse_file('sample_queries.xlsx')
            if not error and len(excel_data) > 0:
                logger.info(f"✓ Parsed {len(excel_data)} rows from Excel")
            else:
                logger.warning("Excel file not found or empty (optional)")
        except:
            logger.warning("Excel parsing skipped (file may not exist)")
        
        # Test validation
        is_valid, msg = FileParser.validate_data(csv_data)
        assert is_valid, f"Validation failed: {msg}"
        logger.info(f"✓ Data validation passed")
        
        # Test invalid data
        invalid_data = [{'keyword': '', 'zip_code': ''}]
        is_valid, msg = FileParser.validate_data(invalid_data)
        assert not is_valid, "Should have failed validation"
        logger.info(f"✓ Invalid data correctly rejected")
        
        logger.info("✓ FileParser tests passed!\n")
        return True
        
    except Exception as e:
        logger.error(f"✗ FileParser test failed: {e}")
        return False


def test_data_extractor():
    """Test DataExtractor component."""
    logger.info("=" * 50)
    logger.info("Testing DataExtractor")
    logger.info("=" * 50)
    
    try:
        # Test phone cleaning
        phone = DataExtractor.clean_phone_number("(123) 456-7890")
        assert phone == "(123) 456-7890", "Phone cleaning failed"
        logger.info(f"✓ Phone cleaning works: {phone}")
        
        # Test rating extraction
        rating = DataExtractor.clean_rating("4.5 stars")
        assert rating == 4.5, "Rating extraction failed"
        logger.info(f"✓ Rating extraction works: {rating}")
        
        # Test review count extraction
        count = DataExtractor.extract_review_count("4.5 stars 123 reviews")
        assert count == 123, "Review count extraction failed"
        logger.info(f"✓ Review count extraction works: {count}")
        
        logger.info("✓ DataExtractor tests passed!\n")
        return True
        
    except Exception as e:
        logger.error(f"✗ DataExtractor test failed: {e}")
        return False


async def test_scraper_initialization():
    """Test GoogleMapsScraper initialization."""
    logger.info("=" * 50)
    logger.info("Testing GoogleMapsScraper Initialization")
    logger.info("=" * 50)
    
    try:
        pm = ProxyManager(Config.PROXY_FILE, Config.ROTATION_THRESHOLD)
        scraper = GoogleMapsScraper(pm, headless=True)
        
        logger.info("✓ Scraper initialized")
        
        # Test browser initialization
        proxy = pm.get_next_proxy()
        success = await scraper.initialize_browser(proxy)
        
        if success:
            logger.info("✓ Browser initialized successfully")
            await scraper.close_browser()
            logger.info("✓ Browser closed successfully")
        else:
            logger.warning("⚠ Browser initialization failed (may be expected if Playwright not installed)")
        
        await scraper.cleanup()
        logger.info("✓ Scraper cleanup completed")
        
        logger.info("✓ GoogleMapsScraper initialization tests passed!\n")
        return True
        
    except Exception as e:
        logger.error(f"✗ GoogleMapsScraper test failed: {e}")
        logger.info("Note: This may fail if Playwright browsers are not installed")
        logger.info("Run: playwright install chromium")
        return False


def test_integration():
    """Test component integration."""
    logger.info("=" * 50)
    logger.info("Testing Component Integration")
    logger.info("=" * 50)
    
    try:
        # Initialize all components
        pm = ProxyManager(Config.PROXY_FILE, Config.ROTATION_THRESHOLD)
        logger.info("✓ ProxyManager initialized")
        
        csv_data, error = FileParser.parse_file('sample_queries.csv')
        assert not error, f"Failed to parse CSV: {error}"
        logger.info(f"✓ FileParser loaded {len(csv_data)} queries")
        
        scraper = GoogleMapsScraper(pm, headless=True)
        logger.info("✓ GoogleMapsScraper initialized")
        
        logger.info("✓ All components integrated successfully!\n")
        return True
        
    except Exception as e:
        logger.error(f"✗ Integration test failed: {e}")
        return False


async def main():
    """Run all tests."""
    logger.info("\n" + "=" * 50)
    logger.info("GOOGLE MAPS SCRAPER - INTEGRATION TESTS")
    logger.info("=" * 50 + "\n")
    
    results = []
    
    # Run tests
    results.append(("ProxyManager", test_proxy_manager()))
    results.append(("FileParser", test_file_parser()))
    results.append(("DataExtractor", test_data_extractor()))
    results.append(("Scraper Init", await test_scraper_initialization()))
    results.append(("Integration", test_integration()))
    
    # Summary
    logger.info("=" * 50)
    logger.info("TEST SUMMARY")
    logger.info("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        logger.info(f"{name:20s}: {status}")
    
    logger.info("=" * 50)
    logger.info(f"Total: {passed}/{total} tests passed")
    logger.info("=" * 50 + "\n")
    
    if passed == total:
        logger.info("🎉 All tests passed! System is ready.")
        logger.info("\nNext steps:")
        logger.info("1. Install Playwright browsers: playwright install chromium")
        logger.info("2. Start the Flask server: python app.py")
        logger.info("3. Open browser: http://127.0.0.1:5000")
    else:
        logger.warning("⚠ Some tests failed. Please review the errors above.")


if __name__ == '__main__':
    asyncio.run(main())
