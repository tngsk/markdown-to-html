import pytest
import importlib.util
from pathlib import Path
from src.processors.base_parser import BaseComponentParser

def load_parser():
    parser_path = Path("src/components/mono-flipcard/parser.py")
    spec = importlib.util.spec_from_file_location("mono_flipcard_parser", parser_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Parser()

def test_mono_flipcard_basic():
    parser = load_parser()
    text = '@[flipcard: "Front"](a: "Back")'
    result = parser.process(text)
    assert '<mono-flipcard front="Front" back="Back"></mono-flipcard>' in result

def test_mono_flipcard_different_keys():
    parser = load_parser()

    keys = ["A", "ans", "answer"]
    for key in keys:
        text = f'@[flipcard: "Front"]({key}: "Back")'
        result = parser.process(text)
        assert '<mono-flipcard front="Front" back="Back"></mono-flipcard>' in result

def test_mono_flipcard_quotes():
    parser = load_parser()
    # Testing quotes handling in the front text and back text
    text = "@[flipcard: 'Front text'](a: 'Back text')"
    result = parser.process(text)
    assert '<mono-flipcard front="Front text" back="Back text"></mono-flipcard>' in result

def test_mono_flipcard_no_back():
    parser = load_parser()
    text = '@[flipcard: "Front"]()'
    result = parser.process(text)
    assert '<mono-flipcard front="Front" back=""></mono-flipcard>' in result

def test_mono_flipcard_no_args():
    parser = load_parser()
    text = '@[flipcard: "Front"]'
    result = parser.process(text)
    assert '<mono-flipcard front="Front" back=""></mono-flipcard>' in result

def test_mono_flipcard_html_escaping():
    parser = load_parser()
    text = '@[flipcard: "Front <br>"](a: "Back & forth")'
    result = parser.process(text)
    assert '<mono-flipcard front="Front &lt;br&gt;" back="Back &amp; forth"></mono-flipcard>' in result
