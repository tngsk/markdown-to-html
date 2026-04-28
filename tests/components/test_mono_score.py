import sys
import os
import pytest
import importlib.util
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

spec = importlib.util.spec_from_file_location("mono_score_parser", "src/components/mono-score/parser.py")
mono_score_parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mono_score_parser)
Parser = mono_score_parser.Parser

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
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
# Note: component folders have dashes, but in python they are normally imported via dynamic import.
# The component is at src/components/mono-score/parser.py
# We should probably use importlib to import it or just add the folder to sys.path
import importlib.util

spec = importlib.util.spec_from_file_location("mono_score_parser", "src/components/mono-score/parser.py")
mono_score_parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mono_score_parser)
Parser = mono_score_parser.Parser

def test_mono_score_parser_basic():
    parser = Parser()
    markdown = '@[score](notes: "C4/q, D4/q")'
    result = parser.process(markdown)
    assert '<mono-score notes="C4/q, D4/q"></mono-score>' in result

def test_mono_score_parser_with_clef_and_time():
    parser = Parser()
    markdown = '@[score](notes: "C4/q", clef: "bass", time: "3/4")'
    result = parser.process(markdown)
    assert '<mono-score notes="C4/q" clef="bass" time="3/4"></mono-score>' in result

def test_mono_score_parser_with_colon_syntax():
    parser = Parser()
    markdown = '@[score: "C4/q, E4/q"](clef: treble)'
    result = parser.process(markdown)
    assert '<mono-score notes="C4/q, E4/q" clef="treble"></mono-score>' in result

def test_mono_score_parser_with_voices():
    parser = Parser()
    markdown = '@[score](voices: \'["C#5/q, B4", "C#4/h"]\', clef: "treble")'
    result = parser.process(markdown)
    assert 'voices="[&quot;C#5/q, B4&quot;, &quot;C#4/h&quot;]"' in result
    assert 'clef="treble"' in result
