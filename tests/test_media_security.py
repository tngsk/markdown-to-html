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

    def test_allowed_relative_path_within_cwd(self):
        # Create an HTML with a path traversal that resolves within cwd
        html_content = '<img src="../assets/img.png" alt="valid">'

        test_markdown_dir = (Path.cwd() / "tests" / "mock_markdown_dir").resolve()

        self.file_handler.read_binary.return_value = b"fakeimage"

        import unittest.mock
        with unittest.mock.patch.object(Path, 'exists') as mock_exists:
            mock_exists.return_value = True

            with unittest.mock.patch.object(self.embedder, 'encode_media_to_base64') as mock_encode:
                mock_encode.return_value = "base64data"

                result_html, media_count, asset_store = self.embedder.embed_media_in_html(
                    html_content, test_markdown_dir
                )

        # Then media count should be 1 because it was allowed
        self.assertEqual(media_count, 1)
        self.assertIn('asset-1', result_html)


if __name__ == '__main__':
    unittest.main()
