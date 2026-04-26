import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('http://localhost:8000/poll.html')

        # Check shadow root content
        shadow_html = await page.evaluate('''() => {
            const poll = document.querySelector('mono-poll');
            return poll.shadowRoot.innerHTML;
        }''')
        print(f"Shadow root HTML: {shadow_html[:500]}...")

        await browser.close()

asyncio.run(main())
