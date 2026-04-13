import unittest
from pathlib import Path

from handlers.mime import MIMETypeRegistry
from constants import DEFAULT_MIME_TYPE, MIME_TYPE_REGISTRY


class TestMIMETypeRegistry(unittest.TestCase):
    def test_init_default(self):
        registry = MIMETypeRegistry()
        self.assertEqual(registry.registry, MIME_TYPE_REGISTRY)
        # Ensure it's a copy
        self.assertIsNot(registry.registry, MIME_TYPE_REGISTRY)

    def test_init_custom(self):
        custom_registry = {".custom": "application/x-custom"}
        registry = MIMETypeRegistry(registry=custom_registry)
        self.assertEqual(registry.registry, custom_registry)

    def test_get_mime_type_known(self):
        registry = MIMETypeRegistry()
        file_path = Path("image.png")
        self.assertEqual(registry.get_mime_type(file_path), "image/png")

    def test_get_mime_type_case_insensitive(self):
        registry = MIMETypeRegistry()
        file_path = Path("image.JPG")
        self.assertEqual(registry.get_mime_type(file_path), "image/jpeg")

    def test_get_mime_type_unknown(self):
        registry = MIMETypeRegistry()
        file_path = Path("file.unknown")
        self.assertEqual(registry.get_mime_type(file_path), DEFAULT_MIME_TYPE)

    def test_get_mime_type_no_extension(self):
        registry = MIMETypeRegistry()
        file_path = Path("file")
        self.assertEqual(registry.get_mime_type(file_path), DEFAULT_MIME_TYPE)

if __name__ == '__main__':
    unittest.main()
