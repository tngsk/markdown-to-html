import unittest
from unittest.mock import MagicMock, patch
import sys

# Mocking missing dependencies before they are imported by converter.py
mock_markdown = MagicMock()
mock_pil = MagicMock()
mock_requests = MagicMock()
mock_fastapi = MagicMock()
mock_uvicorn = MagicMock()
mock_websockets = MagicMock()

sys.modules['markdown'] = mock_markdown
sys.modules['PIL'] = mock_pil
sys.modules['PIL.Image'] = mock_pil.Image
sys.modules['requests'] = mock_requests
sys.modules['fastapi'] = mock_fastapi
sys.modules['uvicorn'] = mock_uvicorn
sys.modules['websockets'] = mock_websockets

from pathlib import Path
import logging

from converter import MarkdownToHTMLConverter
from config import ConversionConfig, ConversionError

class TestMarkdownToHTMLConverter(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger("test_logger")
        # Ensure we don't actually read config.toml if it exists
        with patch('tomllib.load', return_value={}):
            self.config = ConversionConfig(
                input_file=Path("test.md"),
                output_file=Path("test.html"),
                css_files=None,
                template_path=None
            )
        self.converter = MarkdownToHTMLConverter(self.config, self.logger)

        # Mock dependencies on the instance
        self.converter.file_handler = MagicMock()
        self.converter.media_embedder = MagicMock()
        self.converter.css_embedder = MagicMock()
        self.converter.markdown_processor = MagicMock()
        self.converter.html_document_builder = MagicMock()

    def test_convert_success(self):
        # Setup mocks
        self.converter.file_handler.read_text.return_value = "# Test Markdown"
        self.converter.markdown_processor.convert_markdown_to_html.return_value = "<h1>Test HTML</h1>"
        self.converter.media_embedder.embed_media_in_html.return_value = ("<h1>Test HTML</h1>", 0, {})
        self.converter.html_document_builder.extract_title_from_html.return_value = "Test Title"
        self.converter.html_document_builder.build_document.return_value = "<html><body><h1>Test HTML</h1></body></html>"

        result = self.converter.convert()

        self.assertTrue(result)
        self.converter.file_handler.read_text.assert_called_once_with(self.config.input_file)
        self.converter.markdown_processor.convert_markdown_to_html.assert_called_once()
        self.converter.html_document_builder.build_document.assert_called_once()
        self.converter.file_handler.write_text.assert_called_once()

    def test_convert_with_css(self):
        self.config.css_files = [Path("style.css")]
        self.converter.file_handler.read_text.return_value = "# Test"
        self.converter.markdown_processor.convert_markdown_to_html.return_value = "<h1>Test</h1>"
        self.converter.css_embedder.load_css_files.return_value = "body { color: red; }"
        self.converter.media_embedder.embed_media_in_html.return_value = ("<h1>Test</h1>", 0, {})
        self.converter.html_document_builder.extract_title_from_html.return_value = "Title"
        self.converter.html_document_builder.build_document.return_value = "<html>...</html>"

        result = self.converter.convert()

        self.assertTrue(result)
        self.converter.css_embedder.load_css_files.assert_called_once_with(self.config.css_files)
        self.assertEqual(self.converter.stats.css_files_embedded, 1)

    def test_convert_conversion_error(self):
        self.converter.file_handler.read_text.side_effect = ConversionError("Read error")

        # We need to suppress error logging to keep test output clean or just let it happen
        with self.assertLogs(self.logger, level='ERROR') as cm:
            result = self.converter.convert()

        self.assertFalse(result)
        self.assertIn("変換失敗: Read error", cm.output[0])

    def test_convert_unexpected_error(self):
        self.converter.file_handler.read_text.side_effect = Exception("Unexpected")

        with self.assertLogs(self.logger, level='ERROR') as cm:
            result = self.converter.convert()

        self.assertFalse(result)
        self.assertIn("予期しないエラー: Unexpected", cm.output[0])

    def test_convert_size_limit_error(self):
        self.converter.file_handler.read_text.return_value = "# Test"
        self.converter.markdown_processor.convert_markdown_to_html.return_value = "<h1>Test</h1>"
        self.converter.media_embedder.embed_media_in_html.return_value = ("<h1>Test</h1>", 0, {})
        self.converter.html_document_builder.extract_title_from_html.return_value = "Title"

        # Build a large document > 30MB
        large_content = "A" * (31 * 1024 * 1024)
        self.converter.html_document_builder.build_document.return_value = large_content

        with self.assertLogs(self.logger, level='ERROR') as cm:
            result = self.converter.convert()

        self.assertFalse(result)
        self.assertIn("出力サイズが 30MB を超えています", cm.output[0])

    def test_convert_size_limit_force(self):
        self.config.force = True
        self.converter.file_handler.read_text.return_value = "# Test"
        self.converter.markdown_processor.convert_markdown_to_html.return_value = "<h1>Test</h1>"
        self.converter.media_embedder.embed_media_in_html.return_value = ("<h1>Test</h1>", 0, {})
        self.converter.html_document_builder.extract_title_from_html.return_value = "Title"

        large_content = "A" * (31 * 1024 * 1024)
        self.converter.html_document_builder.build_document.return_value = large_content

        result = self.converter.convert()

        self.assertTrue(result)
        self.converter.file_handler.write_text.assert_called_once()

    def test_convert_size_warning(self):
        self.converter.file_handler.read_text.return_value = "# Test"
        self.converter.markdown_processor.convert_markdown_to_html.return_value = "<h1>Test</h1>"
        # Include an asset to trigger detailed size breakdown in warning
        self.converter.media_embedder.embed_media_in_html.return_value = ("<h1>Test</h1>", 1, {"img1": "data..."})
        self.converter.html_document_builder.extract_title_from_html.return_value = "Title"

        # Build a document > 20MB but < 30MB
        content = "A" * (21 * 1024 * 1024)
        self.converter.html_document_builder.build_document.return_value = content

        with self.assertLogs(self.logger, level='WARNING') as cm:
            result = self.converter.convert()

        self.assertTrue(result)
        self.assertTrue(any("出力サイズが 20MB を超えています" in msg for msg in cm.output))

if __name__ == '__main__':
    unittest.main()
