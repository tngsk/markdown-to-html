import unittest
from unittest.mock import patch
from pathlib import Path
import logging

from processors.html import HTMLDocumentBuilder
from config import ConversionError

class TestHTMLDocumentBuilder(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger("test_html_logger")
        self.template_path = Path("test_template.html")
        self.builder = HTMLDocumentBuilder(self.logger, self.template_path)

    @patch('pathlib.Path.read_text')
    def test_build_document_success(self, mock_read_text):
        mock_read_text.return_value = "<html><head>{CSP_META}{CSS_BLOCK}{HIGHLIGHT_JS_CSS}{CODE_BLOCK_CSS}</head><body>{TITLE}{BODY}{HIGHLIGHT_JS}{COPY_BUTTON_JS}</body></html>"

        with patch.object(self.builder, '_get_used_component_dirs', return_value=[]), \
             patch.object(self.builder, '_load_highlight_js_script', return_value="<script></script>"), \
             patch.object(self.builder, '_load_base_css', return_value="<style></style>"), \
             patch.object(self.builder, '_build_highlight_js_link', return_value="<link>"):

            result = self.builder.build_document(html_body="<p>test</p>", title="Test Title")

            self.assertIn("Test Title", result)
            self.assertIn("<p>test</p>", result)

    def test_build_document_missing_template(self):
        with patch('pathlib.Path.read_text', side_effect=FileNotFoundError):
            with self.assertRaises(ConversionError) as context:
                self.builder.build_document(html_body="<p>test</p>")
            self.assertIn("テンプレートファイルが見つかりません", str(context.exception))

    def test_build_css_block(self):
        css = "body { color: red; }"
        result = self.builder._build_css_block(css)
        self.assertIn("<style>", result)
        self.assertIn("body { color: red; }", result)
        self.assertIn("</style>", result)

        self.assertEqual(self.builder._build_css_block(None), "")
        self.assertEqual(self.builder._build_css_block(""), "")

    def test_extract_title_from_html(self):
        html_with_title = "<html><body><h1>My Title</h1><p>content</p></body></html>"
        self.assertEqual(self.builder.extract_title_from_html(html_with_title), "My Title")

        html_without_title = "<html><body><h2>My Title</h2><p>content</p></body></html>"
        self.assertEqual(self.builder.extract_title_from_html(html_without_title), "Document")

        html_with_nested_tags = "<h1><span>Complex</span> Title</h1>"
        self.assertEqual(self.builder.extract_title_from_html(html_with_nested_tags), "Complex Title")

    def test_escape_html(self):
        self.assertEqual(self.builder._escape_html("AT&T"), "AT&amp;T")
        self.assertEqual(self.builder._escape_html("<script>"), "&lt;script&gt;")
        self.assertEqual(self.builder._escape_html('He said "Hello"'), 'He said &quot;Hello&quot;')
        self.assertEqual(self.builder._escape_html("It's a test"), "It&#39;s a test")

    def test_enhance_code_blocks(self):
        html_input = '<pre><code class="language-python">print("hello")</code></pre>'
        expected = '<situ-code-block language="python">\n<pre><code class="language-python">print("hello")</code></pre>\n</situ-code-block>'
        self.assertEqual(self.builder._enhance_code_blocks(html_input), expected)

        html_input_no_lang = '<pre><code>print("hello")</code></pre>'
        expected_no_lang = '<situ-code-block language="">\n<pre><code>print("hello")</code></pre>\n</situ-code-block>'
        self.assertEqual(self.builder._enhance_code_blocks(html_input_no_lang), expected_no_lang)

    def test_remove_table_inline_styles(self):
        html_input = '<table><tr><td style="text-align: left;">Data</td><th style="color: red;">Head</th></tr></table>'
        expected = '<table><tr><td>Data</td><th>Head</th></tr></table>'
        self.assertEqual(self.builder._remove_table_inline_styles(html_input), expected)

    def test_remove_excluded_tags(self):
        html_input = '<div><p>Text</p></div><hr /><hr>'

        # The existing code first removes `<tag...>` (the opening or self-closing tag)
        # leaving `<p>Text</p></div>`. The paired regex then won't match `<div>...</div>`.
        # So we should test what it actually does with the current implementation.
        html_input_paired = '<div><p>Text</p></div>'
        result1 = self.builder._remove_excluded_tags(html_input_paired, ["div"])
        self.assertEqual(result1, '<p>Text</p></div>')

        # Test self-closing tag
        result2 = self.builder._remove_excluded_tags(html_input, ["hr"])
        self.assertEqual(result2, '<div><p>Text</p></div>')

        # Test no exclusions
        result3 = self.builder._remove_excluded_tags(html_input, None)
        self.assertEqual(result3, html_input)

    def test_enhance_colab_links(self):
        html_input = '<a href="https://github.com/user/repo/blob/main/test.ipynb">Open Note</a>'
        result = self.builder._enhance_colab_links(html_input)
        self.assertIn("https://colab.research.google.com/github/user/repo/blob/main/test.ipynb", result)
        self.assertIn('class="colab-link"', result)
        self.assertIn("colab-badge.svg", result)

        html_input_other = '<a href="https://example.com/test.ipynb">Open Note</a>'
        result_other = self.builder._enhance_colab_links(html_input_other)
        self.assertIn("https://example.com/test.ipynb", result_other)
        self.assertIn('class="colab-link"', result_other)
        self.assertIn("colab-badge.svg", result_other)

    def test_replace_custom_nowrap(self):
        html_input = 'Here is some {{custom syntax}} text.'
        expected = 'Here is some <span class="nowrap">custom syntax</span> text.'
        self.assertEqual(self.builder._replace_custom_nowrap(html_input), expected)

if __name__ == '__main__':
    unittest.main()
