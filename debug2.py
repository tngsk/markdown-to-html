import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('http://localhost:8000/poll.html')

        # Take a screenshot specifically of the first poll
        poll = page.locator('mono-poll').first
        await poll.screenshot(path='poll_element.png')

        await browser.close()

asyncio.run(main())
