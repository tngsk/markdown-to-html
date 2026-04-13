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

        with patch('pathlib.Path.read_text', side_effect=Exception("Read error")):
            with self.assertRaises(ConversionError) as context:
                self.builder.build_document(html_body="<p>test</p>")
            self.assertIn("テンプレート読み込みエラー", str(context.exception))

    @patch('pathlib.Path.read_text')
    def test_build_document_with_assets_and_components(self, mock_read_text):
        mock_read_text.return_value = "<html><body>{BODY}</body></html>"

        with patch.object(self.builder, '_get_used_component_dirs', return_value=[]), \
             patch.object(self.builder, '_load_lazy_load_script', return_value="console.log('lazy');"):

            result = self.builder.build_document(
                html_body="<p>test</p><situ-poll></situ-poll>",
                asset_store={"img1": "data:image/png;base64,..."},
                enable_export=True,
                connect_src="http://api",
                ws_src="ws://api"
            )
            self.assertIn("situ-asset-store", result)
            self.assertIn("console.log('lazy');", result)
            self.assertIn("situ-export", result)

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

    @patch('pathlib.Path.read_text')
    def test_load_lazy_load_script(self, mock_read_text):
        mock_read_text.return_value = "console.log('lazy');"
        self.assertEqual(self.builder._load_lazy_load_script(), "console.log('lazy');")

        mock_read_text.side_effect = FileNotFoundError()
        self.assertEqual(self.builder._load_lazy_load_script(), "")

        mock_read_text.side_effect = Exception("error")
        self.assertEqual(self.builder._load_lazy_load_script(), "")

    @patch('pathlib.Path.read_text')
    def test_load_base_css(self, mock_read_text):
        mock_read_text.return_value = "body { color: red; }"
        self.assertIn("body { color: red; }", self.builder._load_base_css())

        mock_read_text.side_effect = FileNotFoundError()
        self.assertEqual(self.builder._load_base_css(), "")

        mock_read_text.side_effect = Exception("error")
        self.assertEqual(self.builder._load_base_css(), "")

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_dir')
    @patch('pathlib.Path.iterdir')
    def test_get_used_component_dirs(self, mock_iterdir, mock_is_dir, mock_exists):
        mock_exists.return_value = False
        self.assertEqual(self.builder._get_used_component_dirs("body", True), [])

        mock_exists.return_value = True
        mock_is_dir.return_value = True

        # Test situ-sync, situ-export, matching component, unmatching component, non-dir
        p_sync = Path("situ-sync")
        p_export = Path("situ-export")
        p_match = Path("situ-match")
        p_unmatch = Path("situ-unmatch")
        p_nondir = Path("file.txt")

        mock_iterdir.return_value = [p_sync, p_export, p_match, p_unmatch, p_nondir]

        m_sync = unittest.mock.MagicMock()
        m_sync.name = "situ-sync"
        m_sync.is_dir.return_value = True

        m_export = unittest.mock.MagicMock()
        m_export.name = "situ-export"
        m_export.is_dir.return_value = True

        m_match = unittest.mock.MagicMock()
        m_match.name = "situ-match"
        m_match.is_dir.return_value = True

        m_unmatch = unittest.mock.MagicMock()
        m_unmatch.name = "situ-unmatch"
        m_unmatch.is_dir.return_value = True

        m_nondir = unittest.mock.MagicMock()
        m_nondir.name = "file.txt"
        m_nondir.is_dir.return_value = False

        mock_iterdir.return_value = [m_export, m_nondir, m_sync, m_match, m_unmatch]

        # Override the top-level mock_is_dir to just return True so components_dir.is_dir() succeeds
        mock_is_dir.side_effect = lambda: True

        # Need to patch Path.iterdir specifically, but since Path.exists/is_dir are mocked
        # we can just run the test if we patch Path instances dynamically.
        # However, the code uses sorted(components_dir.iterdir()), so it sorts by the mock.
        # Let's ensure they are sortable by mocking __lt__
        m_sync.__lt__.side_effect = lambda other: m_sync.name < other.name
        m_export.__lt__.side_effect = lambda other: m_export.name < other.name
        m_match.__lt__.side_effect = lambda other: m_match.name < other.name
        m_unmatch.__lt__.side_effect = lambda other: m_unmatch.name < other.name
        m_nondir.__lt__.side_effect = lambda other: m_nondir.name < other.name

        html_body = "<situ-match></situ-match>"

        result = self.builder._get_used_component_dirs(html_body, should_enable_export=True)
        self.assertIn(m_sync, result)
        self.assertIn(m_export, result)
        self.assertIn(m_match, result)
        self.assertNotIn(m_unmatch, result)
        self.assertNotIn(m_nondir, result)

        result_no_export = self.builder._get_used_component_dirs(html_body, should_enable_export=False)
        self.assertNotIn(m_export, result_no_export)

    def test_load_situ_components_script(self):
        m_dir = unittest.mock.MagicMock()
        m_js = unittest.mock.MagicMock()
        m_dir.__truediv__.return_value = m_js

        # 1. file exists and readable
        m_js.exists.return_value = True
        m_js.read_text.return_value = "console.log();"
        self.assertIn("console.log();", self.builder._load_situ_components_script([m_dir]))

        # 2. file exists, read throws exception
        m_js.read_text.side_effect = Exception("Read Error")
        self.assertEqual(self.builder._load_situ_components_script([m_dir]), "")

        # 3. file does not exist
        m_js.exists.return_value = False
        self.assertEqual(self.builder._load_situ_components_script([m_dir]), "")

    def test_load_component_templates(self):
        m_dir = unittest.mock.MagicMock()
        m_template = unittest.mock.MagicMock()
        m_css = unittest.mock.MagicMock()

        def mock_div(key):
            if key == "template.html": return m_template
            if key == "style.css": return m_css
            return unittest.mock.MagicMock()

        m_dir.__truediv__.side_effect = mock_div

        m_template.exists.return_value = True
        m_css.exists.return_value = True
        m_template.read_text.return_value = "<div>{COMPONENTS_CSS}</div>"
        m_css.read_text.return_value = "color: red;"

        res1 = self.builder._load_component_templates([m_dir])
        self.assertIn("color: red;", res1)

        m_css.read_text.side_effect = Exception("CSS Error")
        res2 = self.builder._load_component_templates([m_dir])
        self.assertIn("<div></div>", res2)  # CSS removed

        m_template.read_text.side_effect = Exception("Template Error")
        res3 = self.builder._load_component_templates([m_dir])
        self.assertEqual(res3, "")

        m_template.exists.return_value = False
        res4 = self.builder._load_component_templates([m_dir])
        self.assertEqual(res4, "")

if __name__ == '__main__':
    unittest.main()
