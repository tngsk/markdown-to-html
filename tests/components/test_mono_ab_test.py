import pytest
import importlib.util
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Load the parser module dynamically
spec = importlib.util.spec_from_file_location("mono_ab_test_parser", "src/components/mono-ab-test/parser.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
Parser = module.Parser

@pytest.fixture
def parser():
    return Parser()

def test_mono_ab_test_basic(parser):
    markdown = '@[ab-test: "A/B Title"](src-a: "a.html", src-b: "b.html")'
    html = parser.process(markdown)
    assert '<mono-ab-test' in html
