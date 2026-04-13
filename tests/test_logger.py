import unittest
import logging
import sys

from logger import configure_logging
from constants import LOG_DATE_FORMAT, LOG_FORMAT

class TestConfigureLogging(unittest.TestCase):

    def setUp(self):
        # Reset the logger before each test
        logger = logging.getLogger("markdown_converter")
        logger.handlers.clear()
        logger.setLevel(logging.NOTSET)

    def test_default_logging(self):
        logger = configure_logging(verbose=False)

        self.assertEqual(logger.name, "markdown_converter")
        self.assertEqual(logger.level, logging.INFO)
        self.assertEqual(len(logger.handlers), 1)

        handler = logger.handlers[0]
        self.assertIsInstance(handler, logging.StreamHandler)
        self.assertEqual(handler.stream, sys.stdout)
        self.assertEqual(handler.level, logging.INFO)

        formatter = handler.formatter
        self.assertIsNotNone(formatter)
        self.assertEqual(formatter._fmt, LOG_FORMAT)
        self.assertEqual(formatter.datefmt, LOG_DATE_FORMAT)

    def test_verbose_logging(self):
        logger = configure_logging(verbose=True)

        self.assertEqual(logger.level, logging.DEBUG)
        self.assertEqual(len(logger.handlers), 1)

        handler = logger.handlers[0]
        self.assertEqual(handler.level, logging.DEBUG)

    def test_handler_clear(self):
        # First configuration
        logger1 = configure_logging(verbose=False)
        self.assertEqual(len(logger1.handlers), 1)

        # Second configuration should clear the first handler and add a new one
        logger2 = configure_logging(verbose=True)
        self.assertEqual(len(logger2.handlers), 1)
        self.assertEqual(logger1, logger2)  # Same logger instance

if __name__ == '__main__':
    unittest.main()
