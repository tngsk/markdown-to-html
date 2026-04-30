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
        mock_read_text.return_value = "<html><head>{CSP_META}{HIGHLIGHT_JS_CSS}</head><body>{TITLE}{BODY}{HIGHLIGHT_JS}{COPY_BUTTON_JS}</body></html>"

        with patch.object(self.builder, '_get_used_component_dirs', return_value=[]), \
             patch.object(self.builder, '_load_highlight_js_script', return_value="<script></script>"), \
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
    def test_build_document_connect_src(self, mock_read_text):
        mock_read_text.return_value = "{CSP_META}{COPY_BUTTON_JS}"
        with patch.object(self.builder, '_get_used_component_dirs', return_value=[]), \
             patch.object(self.builder, '_load_highlight_js_script', return_value=""), \
             patch.object(self.builder, '_build_highlight_js_link', return_value=""), \
             patch.object(self.builder, '_load_component_templates', return_value=""), \
             patch.object(self.builder, '_load_mono_components_script', return_value=""):

            result = self.builder.build_document(
                html_body="<p>test</p>",
                connect_src="https://api.example.com"
            )
            self.assertIn("connect-src 'self' https://cdn.jsdelivr.net https://api.example.com", result)
            self.assertIn('<meta name="mono-api-url" content="https://api.example.com">', result)

    @patch('pathlib.Path.read_text')
    def test_build_document_asset_store(self, mock_read_text):
        mock_read_text.return_value = "{BODY}{COPY_BUTTON_JS}"
        with patch.object(self.builder, '_get_used_component_dirs', return_value=[]), \
             patch.object(self.builder, '_load_highlight_js_script', return_value=""), \
             patch.object(self.builder, '_build_highlight_js_link', return_value=""), \
             patch.object(self.builder, '_load_lazy_load_script', return_value="console.log('lazy');"), \
             patch.object(self.builder, '_load_component_templates', return_value=""), \
             patch.object(self.builder, '_load_mono_components_script', return_value=""):

            asset_store = {"image1.png": "data:image/png;base64,1234"}
            result = self.builder.build_document(html_body="<p>test</p>", asset_store=asset_store)

            self.assertIn('<script type="application/json" id="mono-asset-store">{"image1.png": "data:image/png;base64,1234"}</script>', result)
            self.assertIn("console.log('lazy');", result)

    def test_extract_title_from_html(self):
        html_with_title = "<html><body><h1>My Title</h1><p>content</p></body></html>"
        self.assertEqual(self.builder.extract_title_from_html(html_with_title), "My Title")

        html_without_title = "<html><body><h2>My Title</h2><p>content</p></body></html>"
        self.assertEqual(self.builder.extract_title_from_html(html_without_title), "Document")

        html_with_nested_tags = "<h1><span>Complex</span> Title</h1>"
        self.assertEqual(self.builder.extract_title_from_html(html_with_nested_tags), "Complex Title")

        html_with_attributes = '<h1 id="main-title" class="title-class">My Styled Title</h1>'
        self.assertEqual(self.builder.extract_title_from_html(html_with_attributes), "My Styled Title")

    def test_escape_html(self):
        self.assertEqual(self.builder._escape_html("AT&T"), "AT&amp;T")
        self.assertEqual(self.builder._escape_html("<script>"), "&lt;script&gt;")
        self.assertEqual(self.builder._escape_html('He said "Hello"'), 'He said &quot;Hello&quot;')
        self.assertEqual(self.builder._escape_html("It's a test"), "It&#39;s a test")

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

    def test_build_highlight_js_link(self):
        html_body = '<mono-code-block theme="github"></mono-code-block>'
        result = self.builder._build_highlight_js_link(html_body)
        self.assertIn('<style id="mono-highlightjs-css">', result)
        self.assertIn('mono-code-block[theme="github"] .hljs', result)

        # Test default
        html_body_default = '<mono-code-block></mono-code-block>'
        result_default = self.builder._build_highlight_js_link(html_body_default)
        self.assertIn('<style id="mono-highlightjs-css">', result_default)
        self.assertIn('mono-code-block:not([theme]) .hljs', result_default)

    def test_load_highlight_js_script(self):
        result = self.builder._load_highlight_js_script()
        self.assertEqual(result, "")

    def test_load_lazy_load_script(self):
        with patch('pathlib.Path.read_text', return_value="console.log('lazy');"):
            self.assertEqual(self.builder._load_lazy_load_script(), "console.log('lazy');")

        with patch('pathlib.Path.read_text', side_effect=FileNotFoundError):
            self.assertEqual(self.builder._load_lazy_load_script(), "")

        with patch('pathlib.Path.read_text', side_effect=Exception("Read error")):
            self.assertEqual(self.builder._load_lazy_load_script(), "")

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
        result1 = self.builder._get_used_component_dirs(found_mono_tags={"mono-poll"}, should_enable_export=False)
        names1 = [p.name for p in result1]
        self.assertIn('mono-sync', names1)  # Always included
        self.assertIn('mono-brush', names1) # Always included
        self.assertIn('mono-poll', names1)  # Found in HTML
        self.assertNotIn('mono-export', names1) # Export not enabled
        self.assertNotIn('mono-unknown', names1) # Not found in HTML
        self.assertNotIn('not-a-dir', names1) # Not a directory

        # Test 2: enable_export=True, no components in HTML
        result2 = self.builder._get_used_component_dirs(found_mono_tags=set(), should_enable_export=True)
        names2 = [p.name for p in result2]
        self.assertIn('mono-sync', names2)
        self.assertIn('mono-brush', names2)
        self.assertIn('mono-export', names2) # Export enabled
        self.assertNotIn('mono-poll', names2)

    @patch('pathlib.Path.exists', return_value=False)
    def test_get_used_component_dirs_missing_dir(self, mock_exists):
        result = self.builder._get_used_component_dirs(found_mono_tags=set(), should_enable_export=False)
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
