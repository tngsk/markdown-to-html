import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import unittest
import importlib.util
from pathlib import Path

def load_parser():
    parser_path = Path("src/components/mono-theme/parser.py")
    spec = importlib.util.spec_from_file_location("theme_parser", parser_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Parser()

class TestThemeParser(unittest.TestCase):
    def setUp(self):
        self.parser = load_parser()

    def test_parse_theme(self):
        markdown = "Some text @[theme: dark]() more text"
        html = self.parser.process(markdown)
        self.assertIn('<mono-theme theme="dark" show-ui="false" config=""></mono-theme>', html)

    def test_parse_theme_with_ui(self):
        markdown = "Some text @[theme: corporate](show_ui: true) more text"
        html = self.parser.process(markdown)
        self.assertIn('<mono-theme theme="corporate" show-ui="true" config=""></mono-theme>', html)

if __name__ == '__main__':
    unittest.main()
