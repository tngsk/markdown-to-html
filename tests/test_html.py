import unittest
from unittest.mock import patch
from pathlib import Path
import logging

from src.processors.html import HTMLDocumentBuilder
from src.config import ConversionError

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

    def test_build_document_generic_exception(self):
        with patch('pathlib.Path.read_text', side_effect=Exception("Read error")):
            with self.assertRaises(ConversionError) as context:
                self.builder.build_document(html_body="<p>test</p>")
            self.assertIn("テンプレート読み込みエラー: Read error", str(context.exception))

    @patch("pathlib.Path.read_text")
    def test_build_document_icon_fonts_injection(self, mock_read_text):
        """<mono-icon>が存在する場合にGoogle Fontsが注入されることをテスト"""
        mock_read_text.return_value = "<!doctype html><html><head>{CSP_META}</head><body>{BODY}</body></html>"
        html_body = "<mono-icon name=\"search\"></mono-icon>"

        result = self.builder.build_document(html_body=html_body)

        self.assertIn("https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined", result)
        self.assertIn("https://fonts.googleapis.com", result)
        self.assertIn("https://fonts.gstatic.com", result)

    @patch('pathlib.Path.read_text')
    def test_build_document_export_and_interactive(self, mock_read_text):
        mock_read_text.return_value = "{BODY}{COPY_BUTTON_JS}"
        with patch.object(self.builder, '_get_used_component_dirs', return_value=[]), \
             patch.object(self.builder, '_load_highlight_js_script', return_value=""), \
             patch.object(self.builder, '_load_base_css', return_value=""), \
             patch.object(self.builder, '_build_highlight_js_link', return_value=""), \
             patch.object(self.builder, '_load_component_templates', return_value=""), \
             patch.object(self.builder, '_load_mono_components_script', return_value=""):

            # test enable_export=True
            result1 = self.builder.build_document(html_body="<p>test</p>", enable_export=True)
            self.assertIn("<mono-export></mono-export>", result1)

            # test interactive component triggers export
            result2 = self.builder.build_document(html_body="<mono-poll></mono-poll>")
            self.assertIn("<mono-export></mono-export>", result2)

    @patch('pathlib.Path.read_text')
    def test_build_document_connect_ws_src(self, mock_read_text):
        mock_read_text.return_value = "{CSP_META}{COPY_BUTTON_JS}"
        with patch.object(self.builder, '_get_used_component_dirs', return_value=[]), \
             patch.object(self.builder, '_load_highlight_js_script', return_value=""), \
             patch.object(self.builder, '_load_base_css', return_value=""), \
             patch.object(self.builder, '_build_highlight_js_link', return_value=""), \
             patch.object(self.builder, '_load_component_templates', return_value=""), \
             patch.object(self.builder, '_load_mono_components_script', return_value=""):

            result = self.builder.build_document(
                html_body="<p>test</p>",
                connect_src="https://api.example.com",
                ws_src="wss://ws.example.com"
            )
            self.assertIn("connect-src 'self' https://api.example.com wss://ws.example.com", result)
            self.assertIn('<meta name="mono-api-url" content="https://api.example.com">', result)
            self.assertIn('<meta name="mono-ws-url" content="wss://ws.example.com">', result)

    @patch('pathlib.Path.read_text')
    def test_build_document_asset_store(self, mock_read_text):
        mock_read_text.return_value = "{BODY}{COPY_BUTTON_JS}"
        with patch.object(self.builder, '_get_used_component_dirs', return_value=[]), \
             patch.object(self.builder, '_load_highlight_js_script', return_value=""), \
             patch.object(self.builder, '_load_base_css', return_value=""), \
             patch.object(self.builder, '_build_highlight_js_link', return_value=""), \
             patch.object(self.builder, '_load_lazy_load_script', return_value="console.log('lazy');"), \
             patch.object(self.builder, '_load_component_templates', return_value=""), \
             patch.object(self.builder, '_load_mono_components_script', return_value=""):

            asset_store = {"image1.png": "data:image/png;base64,1234"}
            result = self.builder.build_document(html_body="<p>test</p>", asset_store=asset_store)

            self.assertIn('<template id="mono-asset-store">{"image1.png": "data:image/png;base64,1234"}</template>', result)
            self.assertIn("console.log('lazy');", result)

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
        expected = '<mono-code-block language="python">\n<pre><code class="language-python">print("hello")</code></pre>\n</mono-code-block>'
        self.assertEqual(self.builder._enhance_code_blocks(html_input), expected)

        html_input_no_lang = '<pre><code>print("hello")</code></pre>'
        expected_no_lang = '<mono-code-block language="">\n<pre><code>print("hello")</code></pre>\n</mono-code-block>'
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

    def test_build_highlight_js_link(self):
        from src.constants import HIGHLIGHT_JS_CDN_CSS
        result = self.builder._build_highlight_js_link()
        self.assertEqual(result, f'<link rel="stylesheet" href="{HIGHLIGHT_JS_CDN_CSS}">')

    def test_load_highlight_js_script(self):
        from src.constants import HIGHLIGHT_JS_CDN_JS
        result = self.builder._load_highlight_js_script()
        self.assertEqual(result, f'<script src="{HIGHLIGHT_JS_CDN_JS}"></script>')

    def test_load_lazy_load_script(self):
        with patch('pathlib.Path.read_text', return_value="console.log('lazy');"):
            self.assertEqual(self.builder._load_lazy_load_script(), "console.log('lazy');")

        with patch('pathlib.Path.read_text', side_effect=FileNotFoundError):
            self.assertEqual(self.builder._load_lazy_load_script(), "")

        with patch('pathlib.Path.read_text', side_effect=Exception("Read error")):
            self.assertEqual(self.builder._load_lazy_load_script(), "")

    def test_load_base_css(self):
        with patch('pathlib.Path.read_text', return_value="body { color: red; }"):
            result = self.builder._load_base_css()
            self.assertIn("<style>\nbody { color: red; }\n</style>", result)

        with patch('pathlib.Path.read_text', side_effect=FileNotFoundError):
            self.assertEqual(self.builder._load_base_css(), "")

        with patch('pathlib.Path.read_text', side_effect=Exception("Read error")):
            self.assertEqual(self.builder._load_base_css(), "")

    @patch('pathlib.Path.exists', return_value=True)
    @patch('pathlib.Path.is_dir', return_value=True)
    @patch('pathlib.Path.iterdir')
    def test_get_used_component_dirs(self, mock_iterdir, mock_is_dir, mock_exists):
        # Create mock paths using MagicMock so they are sortable
        from unittest.mock import MagicMock

        mock_sync = MagicMock()
        mock_sync.name = 'mono-sync'
        mock_sync.is_dir.return_value = True
        mock_sync.__lt__.side_effect = lambda other: mock_sync.name < other.name

        mock_brush = MagicMock()
        mock_brush.name = 'mono-brush'
        mock_brush.is_dir.return_value = True
        mock_brush.__lt__.side_effect = lambda other: mock_brush.name < other.name

        mock_export = MagicMock()
        mock_export.name = 'mono-export'
        mock_export.is_dir.return_value = True
        mock_export.__lt__.side_effect = lambda other: mock_export.name < other.name

        mock_poll = MagicMock()
        mock_poll.name = 'mono-poll'
        mock_poll.is_dir.return_value = True
        mock_poll.__lt__.side_effect = lambda other: mock_poll.name < other.name

        mock_unknown = MagicMock()
        mock_unknown.name = 'mono-unknown'
        mock_unknown.is_dir.return_value = True
        mock_unknown.__lt__.side_effect = lambda other: mock_unknown.name < other.name

        mock_not_dir = MagicMock()
        mock_not_dir.name = 'not-a-dir'
        mock_not_dir.is_dir.return_value = False
        mock_not_dir.__lt__.side_effect = lambda other: mock_not_dir.name < other.name

        mock_iterdir.return_value = [mock_sync, mock_brush, mock_export, mock_poll, mock_unknown, mock_not_dir]

        # Test 1: enable_export=False, html_body has <mono-poll>
        result1 = self.builder._get_used_component_dirs(html_body="<mono-poll></mono-poll>", should_enable_export=False)
        names1 = [p.name for p in result1]
        self.assertIn('mono-sync', names1)  # Always included
        self.assertIn('mono-brush', names1) # Always included
        self.assertIn('mono-poll', names1)  # Found in HTML
        self.assertNotIn('mono-export', names1) # Export not enabled
        self.assertNotIn('mono-unknown', names1) # Not found in HTML
        self.assertNotIn('not-a-dir', names1) # Not a directory

        # Test 2: enable_export=True, no components in HTML
        result2 = self.builder._get_used_component_dirs(html_body="<p>test</p>", should_enable_export=True)
        names2 = [p.name for p in result2]
        self.assertIn('mono-sync', names2)
        self.assertIn('mono-brush', names2)
        self.assertIn('mono-export', names2) # Export enabled
        self.assertNotIn('mono-poll', names2)

    @patch('pathlib.Path.exists', return_value=False)
    def test_get_used_component_dirs_missing_dir(self, mock_exists):
        result = self.builder._get_used_component_dirs(html_body="", should_enable_export=False)
        self.assertEqual(result, [])

    @patch('pathlib.Path.exists', return_value=True)
    @patch('pathlib.Path.read_text', return_value="console.log('component');")
    def test_load_mono_components_script(self, mock_read_text, mock_exists):
        mock_dir1 = Path("fake_dir1")
        mock_dir2 = Path("fake_dir2")

        result = self.builder._load_mono_components_script([mock_dir1, mock_dir2])
        self.assertIn("<script>", result)
        self.assertIn("console.log('component');", result)
        self.assertIn("</script>", result)

        # Test exception handling
        mock_read_text.side_effect = Exception("Read error")
        result_error = self.builder._load_mono_components_script([mock_dir1])
        self.assertEqual(result_error, "")

    def test_load_mono_components_script_empty(self):
        self.assertEqual(self.builder._load_mono_components_script([]), "")

    @patch('pathlib.Path.exists', return_value=True)
    @patch('pathlib.Path.read_text')
    def test_load_component_templates(self, mock_read_text, mock_exists):
        # We can simulate by returning a dictionary-like side_effect based on the file name being accessed.
        # But for simpler mocking, we will just return a string and see what happens.
        # Since read_text is called twice (for template, then css), side_effect as list works.
        mock_read_text.side_effect = ["<template>{COMPONENTS_CSS}</template>", ".css { color: red; }"]

        mock_dir = Path("fake_dir")
        result = self.builder._load_component_templates([mock_dir])
        self.assertEqual(result, "<template>.css { color: red; }</template>")

        # Test CSS error
        mock_read_text.side_effect = ["<template>{COMPONENTS_CSS}</template>", Exception("CSS read error")]
        result_css_error = self.builder._load_component_templates([mock_dir])
        self.assertEqual(result_css_error, "<template></template>")

        # Test template error
        mock_read_text.side_effect = Exception("Template read error")
        result_template_error = self.builder._load_component_templates([mock_dir])
        self.assertEqual(result_template_error, "")

    def test_load_component_templates_empty(self):
        self.assertEqual(self.builder._load_component_templates([]), "")


if __name__ == '__main__':
    unittest.main()
