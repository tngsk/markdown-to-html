import pytest
import importlib.util
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Load the parser module dynamically
spec = importlib.util.spec_from_file_location("mono_clock_parser", "src/components/mono-clock/parser.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
Parser = module.Parser

@pytest.fixture
def parser():
    return Parser()

def test_mono_clock_basic(parser):
    markdown = '@[clock](format: "HH:mm")'
    html = parser.process(markdown)
    assert '<mono-clock format="HH:mm">' in html
