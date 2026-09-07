import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import unittest
import importlib.util

# Load parser.py dynamically since we cannot import it directly due to hyphens in dir name
spec = importlib.util.spec_from_file_location("mono_badge_parser", "src/components/mono-badge/parser.py")
mono_badge_parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mono_badge_parser)

class TestMonoBadgeParser(unittest.TestCase):
    def setUp(self):
        self.parser = mono_badge_parser.Parser()

    def test_basic_badge(self):
        markdown = '@[badge: "New!"]()'
        html = self.parser.process(markdown)
        self.assertIn('<mono-badge>New!</mono-badge>', html)

    def test_badge_with_color(self):
        markdown = '@[badge: "Update"](color: "primary")'
        html = self.parser.process(markdown)
        self.assertIn('color="primary"', html)
        self.assertIn('Update', html)

    def test_badge_soft(self):
        markdown = '@[badge: "Soft"](color: "secondary", soft: "true")'
        html = self.parser.process(markdown)
        self.assertIn('color="secondary"', html)
        self.assertIn('soft=""', html)

    def test_badge_outline(self):
        markdown = '@[badge: "Outline"](color: "accent", outline: "true")'
        html = self.parser.process(markdown)
        self.assertIn('color="accent"', html)
        self.assertIn('outline=""', html)


    def test_mono_badge_no_options(self):
        markdown = '@[badge]()'
        html = self.parser.process(markdown)
        self.assertTrue(isinstance(html, str))

    def test_badge_trailing_attributes(self):
        markdown = '@[badge: "Important"]{.custom-class #badge-1}'
        html = self.parser.process(markdown)
        self.assertIn('class="custom-class"', html)
        self.assertIn('id="badge-1"', html)
        self.assertIn('Important', html)
        self.assertNotIn('{', html)
        self.assertNotIn('}', html)

if __name__ == '__main__':
    unittest.main()
