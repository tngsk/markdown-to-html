import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('http://localhost:8000/poll.html')

        # Check why padding is 0 on :host
        padding_info = await page.evaluate('''() => {
            const poll = document.querySelector('mono-poll');
            const style = window.getComputedStyle(poll);
            return style.getPropertyValue('padding');
        }''')
        print(f"Padding on :host: {padding_info}")

        await browser.close()

asyncio.run(main())
