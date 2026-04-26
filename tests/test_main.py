import sys
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile

import src.main as main_module
from src.config import ConversionConfig

class TestMain(unittest.TestCase):
    @patch("src.main.MarkdownToHTMLConverter")
    @patch("src.main.configure_logging")
    @patch("sys.argv", ["main.py", "test.md", "-o", "output.html"])
    def test_main_success(self, mock_configure_logging, mock_converter_class):
        # Setup mocks
        mock_logger = MagicMock()
        mock_configure_logging.return_value = mock_logger

        mock_converter = MagicMock()
        mock_converter.convert.return_value = True
        mock_converter_class.return_value = mock_converter

        # Call main
        exit_code = main_module.main()

        # Assertions
        self.assertEqual(exit_code, 0)
        mock_converter_class.assert_called_once()
        mock_converter.convert.assert_called_once()

    @patch("src.main.MarkdownToHTMLConverter")
    @patch("src.main.configure_logging")
    @patch("sys.argv", ["main.py", "test.md"])
    def test_main_failure(self, mock_configure_logging, mock_converter_class):
        # Setup mocks
        mock_logger = MagicMock()
        mock_configure_logging.return_value = mock_logger

        mock_converter = MagicMock()
        mock_converter.convert.return_value = False
        mock_converter_class.return_value = mock_converter

        # Call main
        exit_code = main_module.main()

        # Assertions
        self.assertEqual(exit_code, 1)

    @patch("builtins.print")
    def test_print_header(self, mock_print):
        config = ConversionConfig(
            input_file=Path("test.md"),
            output_file=Path("test.html"),
            css_files=[Path("style.css")],
            excluded_tags=["script", "iframe"],
            template_path=None
        )
        main_module.print_header(config)

        mock_print.assert_any_call("  CSSファイル:  style.css")
        mock_print.assert_any_call("  除外タグ:     script, iframe")

    def test_module_execution_subprocess(self):
        import runpy

        with patch("sys.argv", ["src/main.py", "-h"]):
            with self.assertRaises(SystemExit) as cm:
                runpy.run_module("src.main", run_name="__main__")
            self.assertEqual(cm.exception.code, 0)

    # Integration test without mocking the converter
    def test_main_integration(self):
        # Create a temporary directory for integration testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_file = temp_path / "integration_test.md"
            output_file = temp_path / "output.html"

            # Create a simple markdown file
            input_file.write_text("# Integration Test\n\nThis is a real integration test.", encoding="utf-8")

            # We don't mock the converter, we let it run on the real filesystem in our temp directory
            with patch("sys.argv", ["main.py", str(input_file), "-o", str(output_file)]):
                # Call main
                exit_code = main_module.main()

                # Assertions
                self.assertEqual(exit_code, 0)

                # Verify output file was actually created and has content
                self.assertTrue(output_file.exists())
                content = output_file.read_text(encoding="utf-8")

                # The html uses some different ids from markdown conversion but the text will exist
                self.assertIn("Integration Test", content)
                self.assertIn("This is a real integration test.", content)

if __name__ == "__main__":
    unittest.main()
