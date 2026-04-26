import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('http://localhost:8000/poll.html')

        # apply fix to see if it works
        await page.evaluate('''() => {
            const style = document.createElement('style');
            style.textContent = `
                mono-poll {
                    height: 100%;
                }
            `;
            document.head.appendChild(style);

            document.querySelectorAll('mono-poll').forEach(poll => {
                const sheet = new CSSStyleSheet();
                sheet.replaceSync(`
                    :host {
                        padding: 0 !important;
                    }
                    .poll-wrapper {
                        padding: 1.5rem;
                        height: 100%;
                        display: flex;
                        flex-direction: column;
                        box-sizing: border-box;
                    }
                    .submit-container {
                        margin-top: auto;
                    }
                `);
                poll.shadowRoot.adoptedStyleSheets = [...poll.shadowRoot.adoptedStyleSheets, sheet];
            });
        }''')

        await page.screenshot(path='fixed_poll.png', full_page=True)
        await browser.close()

asyncio.run(main())
