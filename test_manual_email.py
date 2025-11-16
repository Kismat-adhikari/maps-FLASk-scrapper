"""Manually test email extraction from a website"""
import asyncio
import re
from playwright.async_api import async_playwright

async def test_email_extraction():
    website_url = "http://www.deathave.com/"
    
    print(f"Testing email extraction from: {website_url}")
    
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            print("Loading homepage...")
            await page.goto(website_url, timeout=10000)
            await page.wait_for_timeout(2000)
            
            content = await page.content()
            print(f"Page content length: {len(content)}")
            
            # Find emails
            emails = re.findall(email_pattern, content, re.IGNORECASE)
            print(f"Emails found: {emails}")
            
            # Try /contact page
            try:
                contact_url = website_url.rstrip('/') + '/contact'
                print(f"\nTrying contact page: {contact_url}")
                await page.goto(contact_url, timeout=10000)
                await page.wait_for_timeout(2000)
                
                content = await page.content()
                emails = re.findall(email_pattern, content, re.IGNORECASE)
                print(f"Emails found on contact: {emails}")
            except Exception as e:
                print(f"Contact page error: {e}")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_email_extraction())
