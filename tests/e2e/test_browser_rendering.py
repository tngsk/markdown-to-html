import pytest
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

from src.converter import MarkdownToHTMLConverter
from src.config import ConversionConfig
from src.logger import configure_logging

@pytest.fixture
def temp_markdown_file(tmp_path):
    md_file = tmp_path / "test.md"
    # Provide a local dummy image
    image_path = tmp_path / "dummy.png"
    import base64
    # transparent pixel
    image_path.write_bytes(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="))

    md_file.write_text(f"""
# Test Image Lazy Load
![placeholder](dummy.png)
    """)
    return md_file

def test_rendering_no_console_errors(temp_markdown_file, tmp_path):
    output_html_path = tmp_path / "output.html"
    config = ConversionConfig(input_file=Path(temp_markdown_file), output_file=output_html_path, css_files=[])
    logger = configure_logging(verbose=True)
    converter = MarkdownToHTMLConverter(config, logger)

    converter.convert()

    assert output_html_path.exists()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        errors = []
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda exc: errors.append(str(exc)))

        page.goto(f"file://{output_html_path.absolute()}")

        # Wait for lazy loading to happen by waiting for the data-lazy-src attribute to be removed
        # If there are images, wait for them to finish updating
        images = page.locator("img")
        if images.count() > 0:
            for i in range(images.count()):
                page.locator(f"img >> nth={i}").wait_for(state="attached")
                page.wait_for_function(f"document.querySelectorAll('img')[{i}].getAttribute('data-lazy-src') === null")

        browser.close()

        # There should be no console errors or exceptions
        filtered_errors = [e for e in errors if "net::ERR_CONNECTION_REFUSED" not in e and "net::ERR_FAILED" not in e and "favicon.ico" not in e and "Failed to load resource" not in e and "/api/sync/stream" not in e and "CORS policy" not in e]
        assert len(filtered_errors) == 0, f"Found errors in browser console: {filtered_errors}"

def test_lazy_loaded_image_rendered(temp_markdown_file, tmp_path):
    output_html_path = tmp_path / "output.html"
    config = ConversionConfig(input_file=Path(temp_markdown_file), output_file=output_html_path, css_files=[])
    logger = configure_logging(verbose=True)
    converter = MarkdownToHTMLConverter(config, logger)

    converter.convert()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        page.goto(f"file://{output_html_path.absolute()}")

        # Wait for lazy loading to happen
        images = page.locator("img")
        if images.count() > 0:
            for i in range(images.count()):
                page.locator(f"img >> nth={i}").wait_for(state="attached")
                page.wait_for_function(f"document.querySelectorAll('img')[{i}].getAttribute('data-lazy-src') === null")

        images = page.locator("img").all()
        assert len(images) > 0

        for img in images:
            src = img.get_attribute("src")
            assert src is not None
            assert not src.startswith("data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs="), "Image src was not replaced by lazy load script"

        browser.close()
