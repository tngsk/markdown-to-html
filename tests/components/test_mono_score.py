import os
import pytest
from playwright.sync_api import sync_playwright

def test_mono_score_rendering():
    """
    Test that the mono-score component successfully renders SVG for both
    legacy space-separated notes and EasyScore multi-voice inputs without errors.
    """
    with open('src/templates/core/mono-base-element.js', 'r') as f:
        base_script_content = f.read()

    with open('src/components/mono-score/script.js', 'r') as f:
        script_content = f.read()

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/vexflow@4.2.2/build/cjs/vexflow.js"></script>
        <script>
            {base_script_content}
        </script>
        <script>
            document.write('<template id="mono-score-template"><div class="score-container"></div></template>');
        </script>
        <script>
            {script_content}
        </script>
    </head>
    <body>
        <mono-score id="score1" notes="C4 D4 E4 F4 G4 A4 B4 C5"></mono-score>
        <mono-score id="score2" voices='["C#5/q, B4", "C#4/h"]'></mono-score>
    </body>
    </html>
    """

    test_file = "test_score_render.html"
    with open(test_file, 'w') as f:
        f.write(html_content)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto('file://' + os.path.abspath(test_file))

            page.wait_for_selector('#score1 svg')
            page.wait_for_selector('#score2 svg')

            svg1 = page.evaluate("document.querySelector('#score1 svg') !== null")
            svg2 = page.evaluate("document.querySelector('#score2 svg') !== null")

            assert svg1, "Score 1 SVG not found"
            assert svg2, "Score 2 SVG not found"

            width1 = float(page.evaluate("document.querySelector('#score1 svg').getAttribute('width')"))
            width2 = float(page.evaluate("document.querySelector('#score2 svg').getAttribute('width')"))

            assert width1 > 100, f"Score 1 width too small: {width1}"
            assert width2 > 100, f"Score 2 width too small: {width2}"

            browser.close()
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)
