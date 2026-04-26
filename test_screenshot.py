from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("file:///tmp/poll_fixed2.html")
    page.wait_for_timeout(1000)
    page.screenshot(path="poll_fixed_screenshot.png", full_page=True)
    browser.close()
