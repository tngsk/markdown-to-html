import pytest
import importlib.util

# Load the parser dynamically because of the hyphenated path
spec = importlib.util.spec_from_file_location("countdown_parser", "src/components/mono-countdown/parser.py")
countdown_parser_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(countdown_parser_module)

Parser = countdown_parser_module.Parser

@pytest.fixture
def parser():
    return Parser()

def test_countdown_basic(parser):
    markdown = "Here is a timer: @[countdown](time: \"5m\", color: \"blue\")"
    html = parser.process(markdown)
    assert '<mono-countdown time="5m" color="blue"></mono-countdown>' in html

def test_countdown_no_color(parser):
    markdown = "@[countdown](time: \"30s\")"
    html = parser.process(markdown)
    assert '<mono-countdown time="30s"></mono-countdown>' in html

def test_countdown_no_args(parser):
    markdown = "@[countdown]"
    html = parser.process(markdown)
    assert '<mono-countdown></mono-countdown>' in html

def test_countdown_with_spaces(parser):
    markdown = "@[countdown]( time: \"1h\",  color :  \"red\" )"
    html = parser.process(markdown)
    assert '<mono-countdown time="1h" color="red"></mono-countdown>' in html

def test_countdown_with_multiple_instances(parser):
    markdown = "@[countdown](time: \"1m\") and @[countdown](time: \"2m\", color: \"green\")"
    html = parser.process(markdown)
    assert '<mono-countdown time="1m"></mono-countdown>' in html
    assert '<mono-countdown time="2m" color="green"></mono-countdown>' in html
