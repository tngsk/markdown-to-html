import pytest
import importlib.util
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Load the parser module dynamically
spec = importlib.util.spec_from_file_location("mono_session_join_parser", "src/components/mono-session-join/parser.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
Parser = module.Parser

@pytest.fixture
def parser():
    return Parser()

def test_mono_session_join_basic(parser):
    markdown = '@[session-join: "Room 1"]()'
    html = parser.process(markdown)
    assert '<mono-session-join' in html
