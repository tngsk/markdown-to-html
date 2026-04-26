import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('http://localhost:8000/poll.html')

        # Get styles
        host_style = await page.evaluate('''() => {
            const poll = document.querySelector('mono-poll');
            const style = window.getComputedStyle(poll);
            return {
                padding: style.padding,
                display: style.display,
                border: style.border
            };
        }''')
        print(f"Host style: {host_style}")

        # Check shadow root
        wrapper_style = await page.evaluate('''() => {
            const poll = document.querySelector('mono-poll');
            const wrapper = poll.shadowRoot.querySelector('.poll-wrapper');
            const style = window.getComputedStyle(wrapper);
            return {
                padding: style.padding,
                display: style.display,
                margin: style.margin
            };
        }''')
        print(f"Wrapper style: {wrapper_style}")

        await browser.close()

asyncio.run(main())
