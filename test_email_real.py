"""Test email extraction with a website that definitely has an email"""
import asyncio
import re
from playwright.async_api import async_playwright

async def test_email_extraction():
    # Test with a law firm website (they usually have emails)
    test_urls = [
        "https://www.nycbar.org/",  # NY Bar Association
        "https://www.law.com/",  # Law.com
    ]
    
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        for website_url in test_urls:
            print(f"\n{'='*70}")
            print(f"Testing: {website_url}")
            print('='*70)
            
            try:
                print("Loading homepage...")
                await page.goto(website_url, timeout=10000)
                await page.wait_for_timeout(2000)
                
                content = await page.content()
                print(f"Page content length: {len(content)}")
                
                # Find emails
                emails = re.findall(email_pattern, content, re.IGNORECASE)
                print(f"Emails found: {emails[:5]}")  # Show first 5
                
                if emails:
                    print(f"✓ SUCCESS! Found {len(emails)} emails")
                    print(f"First email: {emails[0]}")
                else:
                    print("✗ No emails found")
                
            except Exception as e:
                print(f"Error: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_email_extraction())
