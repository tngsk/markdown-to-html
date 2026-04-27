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

def test_parse_bracket_content():
    parser = BaseComponentParser()

    # 1. Label and args
    label, args = parser.parse_bracket_content('"My Label", id: "123", placeholder: "test"')
    assert label == "My Label"
    assert args == {"id": "123", "placeholder": "test"}

    # 2. Label without quotes and args
    label, args = parser.parse_bracket_content('My Label, id: "123"')
    assert label == "My Label"
    assert args == {"id": "123"}

    # 3. Only args
    label, args = parser.parse_bracket_content('id: "123", placeholder: "test"')
    assert label == ""
    assert args == {"id": "123", "placeholder": "test"}

    # 4. Only label
    label, args = parser.parse_bracket_content('"Only Label"')
    assert label == "Only Label"
    assert args == {}

    # 5. Label with deprecated equal syntax
    label, args = parser.parse_bracket_content('"My Label", id="123"')
    assert label == "My Label"
    assert args == {"id": "123"}

    # 6. Empty content
    label, args = parser.parse_bracket_content('')
    assert label == ""
    assert args == {}
