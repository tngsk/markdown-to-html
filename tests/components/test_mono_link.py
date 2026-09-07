import sys
import os
import importlib.util

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

spec = importlib.util.spec_from_file_location("mono_link_parser", "src/components/mono-link/parser.py")
mono_link_parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mono_link_parser)
Parser = mono_link_parser.Parser

def test_link_parser():
    parser = Parser()
    result = parser.process("@[link: \"https://example.com\"]")
    assert "<mono-link url=\"https://example.com\"" in result

    # Test card style defaults
    assert 'card-style="full"' in result


def test_mono_link_no_options():
    parser = Parser()
    markdown = '@[link]()'
    html = parser.process(markdown)
    assert isinstance(html, str)

def test_mono_link_all_options():
    parser = Parser()
    markdown = '@[link: "Label"](url: "test", style: "test")'
    html = parser.process(markdown)
    assert isinstance(html, str)
    assert 'title="Label"' in html

def test_mono_link_label_priority_over_ogp():
    parser = Parser()
    from unittest.mock import patch
    with patch.object(parser, 'fetch_og_data', return_value={"title": "OG Title", "desc": "OG Desc", "image": ""}):
        # When explicit label is provided
        markdown = '@[link: "My Custom Title"](url: "https://example.com")'
        html = parser.process(markdown)
        assert 'title="My Custom Title"' in html

        # When no explicit label is provided
        markdown_no_label = '@[link](url: "https://example.com")'
        html_no_label = parser.process(markdown_no_label)
        assert 'title="OG Title"' in html_no_label

def test_mono_link_trailing_attributes():
    parser = Parser()
    markdown = '@[link: "Site"](url: "https://example.com"){.featured-card #link-site}'
    html = parser.process(markdown)
    assert 'class="featured-card"' in html
    assert 'id="link-site"' in html
    assert 'title="Site"' in html
    assert '{' not in html
    assert '}' not in html
