from src.processors.base_parser import BaseComponentParser
import logging

def test_parse_key_value_args_colon():
    parser = BaseComponentParser()
    result = parser.parse_key_value_args('key: "value"')
    assert result == {"key": "value"}

def test_parse_key_value_args_equal_with_colon_in_value(caplog):
    parser = BaseComponentParser()
    with caplog.at_level(logging.WARNING, logger="markdown_converter"):
        result = parser.parse_key_value_args('url="https://example.com"')

    assert result == {"url": "https://example.com"}
    assert "Deprecated syntax: Use ':' instead of '=' for component options." in caplog.text

def test_parse_key_value_args_colon_with_colon_in_value():
    parser = BaseComponentParser()
    result = parser.parse_key_value_args('url: "https://example.com"')
    assert result == {"url": "https://example.com"}

def test_parse_key_value_args_mixed_separators(caplog):
    parser = BaseComponentParser()
    with caplog.at_level(logging.WARNING, logger="markdown_converter"):
        result = parser.parse_key_value_args('class: "gap-md", url="https://example.com"')

    assert result == {"class": "gap-md", "url": "https://example.com"}
    assert "Deprecated syntax: Use ':' instead of '=' for component options. Found in: 'url=\"https://example.com\"'" in caplog.text
