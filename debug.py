import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('http://localhost:8000/poll.html')

        # get the padding of the first mono-poll
        padding = await page.evaluate('''() => {
            const poll = document.querySelector('mono-poll');
            return window.getComputedStyle(poll).padding;
        }''')
        print(f"mono-poll padding: {padding}")

        box_sizing = await page.evaluate('''() => {
            const poll = document.querySelector('mono-poll');
            return window.getComputedStyle(poll).boxSizing;
        }''')
        print(f"mono-poll box-sizing: {box_sizing}")

        await browser.close()

asyncio.run(main())
