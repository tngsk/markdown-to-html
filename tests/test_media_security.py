import unittest
from unittest.mock import MagicMock
from pathlib import Path
import logging
import sys

# Mocking missing dependencies before they are imported by media.py
mock_pil = MagicMock()
sys.modules['PIL'] = mock_pil
sys.modules['PIL.Image'] = mock_pil.Image

from src.embedders.media import MediaEmbedder

class TestMediaEmbedderSecurity(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger("test_logger")
        self.file_handler = MagicMock()
        self.embedder = MediaEmbedder(self.logger, self.file_handler)
        self.markdown_dir = Path("/mock/markdown/dir").resolve()

    def test_path_traversal_prevention(self):
        # Create an HTML with a path traversal attempt in an img tag
        html_content = '<img src="../../etc/passwd" alt="secret">'

        # When embedding media
        result_html, media_count, asset_store = self.embedder.embed_media_in_html(
            html_content, self.markdown_dir
        )

        # Then media count should be 0 because it was skipped
        self.assertEqual(media_count, 0)

        # And the original src should be preserved (not embedded)
        self.assertIn('src="../../etc/passwd"', result_html)

        # And asset store should be empty
        self.assertEqual(len(asset_store), 0)

    def test_path_traversal_prevention_absolute_path(self):
        # Create an HTML with an absolute path
        html_content = '<img src="/etc/passwd" alt="secret">'

        # When embedding media
        result_html, media_count, asset_store = self.embedder.embed_media_in_html(
            html_content, self.markdown_dir
        )

        # Then media count should be 0 because it was skipped
        self.assertEqual(media_count, 0)

        # And the original src should be preserved
        self.assertIn('src="/etc/passwd"', result_html)

        # And asset store should be empty
        self.assertEqual(len(asset_store), 0)

if __name__ == '__main__':
    unittest.main()
