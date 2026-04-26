import unittest
from unittest.mock import patch, mock_open
from pathlib import Path
import tomllib

from src.config import (
    ConversionError,
    FileProcessingError,
    ImageEmbeddingError,
    CSSEmbeddingError,
    ConversionConfig,
    ConversionStats
)

class TestCustomExceptions(unittest.TestCase):
    def test_exception_inheritance(self):
        """Test that custom exceptions inherit correctly."""
        self.assertTrue(issubclass(ConversionError, Exception))
        self.assertTrue(issubclass(FileProcessingError, ConversionError))
        self.assertTrue(issubclass(ImageEmbeddingError, ConversionError))
        self.assertTrue(issubclass(CSSEmbeddingError, ConversionError))

class TestConversionConfig(unittest.TestCase):
    def test_conversion_config_defaults(self):
        """Test ConversionConfig default values."""
        config = ConversionConfig(
            input_file=Path("test.md"),
            output_file=None,
            css_files=None
        )
        self.assertIsNone(config.template_path)
        self.assertFalse(config.verbose)
        self.assertIsNone(config.excluded_tags)
        self.assertFalse(config.force)
        self.assertFalse(config.enable_export)

    def test_post_init_success(self):
        """Test initialization when config.toml is loaded successfully."""
        mock_toml_data = {
            "security": {
                "connect-src": "wss://example.com"
            }
        }
        with patch('builtins.open', mock_open(read_data=b"dummy")):
            with patch('tomllib.load', return_value=mock_toml_data):
                config = ConversionConfig(
                    input_file=Path("test.md"),
                    output_file=None,
                    css_files=None
                )
                self.assertEqual(config.connect_src, "wss://example.com")

    def test_post_init_no_security_key(self):
        """Test initialization when config.toml doesn't have security key."""
        with patch('builtins.open', mock_open(read_data=b"dummy")):
            with patch('tomllib.load', return_value={}):
                config = ConversionConfig(
                    input_file=Path("test.md"),
                    output_file=None,
                    css_files=None
                )
                self.assertEqual(config.connect_src, "")

    def test_post_init_file_not_found(self):
        """Test exception handling during initialization (e.g. FileNotFoundError)."""
        with patch('builtins.open', side_effect=FileNotFoundError):
            config = ConversionConfig(
                input_file=Path("test.md"),
                output_file=None,
                css_files=None
            )
            # Default values should be preserved
            self.assertEqual(config.connect_src, "")

    def test_post_init_toml_decode_error(self):
        """Test exception handling during initialization (TOML decode error)."""
        with patch('builtins.open', mock_open(read_data=b"invalid toml")):
            with patch('tomllib.load', side_effect=tomllib.TOMLDecodeError("Error", "doc", 0)):
                config = ConversionConfig(
                    input_file=Path("test.md"),
                    output_file=None,
                    css_files=None
                )
                # Default values should be preserved
                self.assertEqual(config.connect_src, "")

    def test_resolve_output_file_provided(self):
        """Test resolving output file when explicitly provided."""
        config = ConversionConfig(
            input_file=Path("input.md"),
            output_file=Path("custom.html"),
            css_files=None
        )
        self.assertEqual(config.resolve_output_file(), Path("custom.html"))

    def test_resolve_output_file_not_provided(self):
        """Test resolving output file when not provided."""
        config = ConversionConfig(
            input_file=Path("input.md"),
            output_file=None,
            css_files=None
        )
        self.assertEqual(config.resolve_output_file(), Path("input.html"))

class TestConversionStats(unittest.TestCase):
    def test_default_initialization(self):
        """Test ConversionStats default values."""
        stats = ConversionStats()
        self.assertEqual(stats.images_embedded, 0)
        self.assertEqual(stats.css_files_embedded, 0)
        self.assertEqual(stats.output_file_size, 0)
        self.assertIsNone(stats.markdown_file)
        self.assertIsNone(stats.output_file)

    def test_custom_initialization(self):
        """Test ConversionStats custom values."""
        stats = ConversionStats(
            images_embedded=5,
            css_files_embedded=2,
            output_file_size=1024,
            markdown_file="test.md",
            output_file="out.html"
        )
        self.assertEqual(stats.images_embedded, 5)
        self.assertEqual(stats.css_files_embedded, 2)
        self.assertEqual(stats.output_file_size, 1024)
        self.assertEqual(stats.markdown_file, "test.md")
        self.assertEqual(stats.output_file, "out.html")

if __name__ == '__main__':
    unittest.main()
