import unittest
from unittest.mock import MagicMock, patch
import sys
import logging

try:
    import markdown
except ImportError:
    # Fallback to mock if the dependency is missing in the test environment
    sys.modules['markdown'] = MagicMock()

from src.processors.markdown import MarkdownProcessor
from src.config import ConversionError
from src.constants import MARKDOWN_EXTENSIONS

class TestMarkdownProcessor(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger("test_logger")
        self.file_handler = MagicMock()
        self.processor = MarkdownProcessor(self.logger, self.file_handler)

    def test_preprocess_polls(self):
        # Test basic replacement
        md_content = "Some text @[poll: My Title](Option A, Option B)"
        expected_html = 'Some text <situ-poll id="poll-1" title="My Title" options="Option A, Option B"></situ-poll>'
        result = self.processor._preprocess_polls(md_content)
        self.assertEqual(result, expected_html)

        # Test escaping
        md_content_escape = 'Another @[poll: Title "with quotes"](Option <A>)'
        expected_html_escape = 'Another <situ-poll id="poll-1" title="Title &quot;with quotes&quot;" options="Option &lt;A&gt;"></situ-poll>'

        # We need to create a new processor to reset the counter
        processor2 = MarkdownProcessor(self.logger, self.file_handler)
        result_escape = processor2._preprocess_polls(md_content_escape)
        self.assertEqual(result_escape, expected_html_escape)

    def test_preprocess_textfield(self):
        # Test standard format
        md_content = "Please enter @[textfield: Your Name]"
        expected_html = 'Please enter <situ-textfield-input id="textfield-1" placeholder="Your Name"></situ-textfield-input>'
        result = self.processor._preprocess_textfield(md_content)
        self.assertEqual(result, expected_html)

        # Test size format
        md_content_size = "Input with size: @[textfield: size:50 (Details)]"
        expected_html_size = 'Input with size: <situ-textfield-input id="textfield-1" placeholder="Details" size="50"></situ-textfield-input>'
        processor2 = MarkdownProcessor(self.logger, self.file_handler)
        result_size = processor2._preprocess_textfield(md_content_size)
        self.assertEqual(result_size, expected_html_size)

        # Test typo 'textfiled'
        md_content_typo = "Typo @[textfiled: Description]"
        expected_html_typo = 'Typo <situ-textfield-input id="textfield-1" placeholder="Description"></situ-textfield-input>'
        processor3 = MarkdownProcessor(self.logger, self.file_handler)
        result_typo = processor3._preprocess_textfield(md_content_typo)
        self.assertEqual(result_typo, expected_html_typo)

    def test_preprocess_textfield_size_without_placeholder(self):
        # Test size without placeholder
        md_content_size_no_placeholder = "Input with size no placeholder: @[textfield: size:30]"
        expected_html_size_no_placeholder = 'Input with size no placeholder: <situ-textfield-input id="textfield-1" placeholder="" size="30"></situ-textfield-input>'
        processor = MarkdownProcessor(self.logger, self.file_handler)
        result_size_no_placeholder = processor._preprocess_textfield(md_content_size_no_placeholder)
        self.assertEqual(result_size_no_placeholder, expected_html_size_no_placeholder)

    def test_preprocess_notebooks(self):
        md_content = "Notebook link: @[notebook-input](my-notebook-id)"
        expected_html = 'Notebook link: <situ-notebook-input id="my-notebook-id"></situ-notebook-input>'
        result = self.processor._preprocess_notebooks(md_content)
        self.assertEqual(result, expected_html)

    def test_preprocess_ab_tests(self):
        md_content = "Test: @[ab-test: My Test](file_a.md, file_b.md)"
        expected_html = 'Test: <situ-ab-test id="abtest-1" title="My Test" src-a="file_a.md" src-b="file_b.md"></situ-ab-test>'
        result = self.processor._preprocess_ab_tests(md_content)
        self.assertEqual(result, expected_html)

    def test_preprocess_reactions(self):
        md_content = "React here: @[reaction: like, dislike]"
        expected_html = 'React here: <situ-reaction id="reaction-1" options="like, dislike"></situ-reaction>'
        result = self.processor._preprocess_reactions(md_content)
        self.assertEqual(result, expected_html)

    def test_preprocess_session_join(self):
        md_content = "Join session: @[session-join: Room 101]"
        expected_html = 'Join session: <situ-session-join title="Room 101"></situ-session-join>'
        result = self.processor._preprocess_session_join(md_content)
        self.assertEqual(result, expected_html)

    def test_preprocess_group_assignment(self):
        md_content = "Groups: @[group-assignment: Project Alpha]"
        expected_html = 'Groups: <situ-group-assignment title="Project Alpha"></situ-group-assignment>'
        result = self.processor._preprocess_group_assignment(md_content)
        self.assertEqual(result, expected_html)

    def test_preprocess_layout(self):
        md_content = (
            "@[row: center gap-md]\n"
            ":::column\n"
            "A\n"
            ":::\n"
            "@[stack]\n"
            ":::column\n"
            "B\n"
            ":::\n"
            "@[end]\n"
            "@[end]"
        )
        expected_html = (
            '<situ-layout type="row" class="center gap-md" markdown="1">\n'
            '<div class="column" markdown="1">\n'
            "A\n"
            "</div>\n"
            '<situ-layout type="stack" markdown="1">\n'
            '<div class="column" markdown="1">\n'
            "B\n"
            "</div>\n"
            "</situ-layout>\n"
            "</situ-layout>"
        )
        result = self.processor._preprocess_layout(md_content)
        self.assertEqual(result, expected_html)

    @patch('src.processors.markdown.markdown')
    def test_convert_markdown_to_html_success(self, mock_markdown):
        mock_markdown.markdown.side_effect = None
        mock_markdown.markdown.return_value = "<h1>Processed</h1>"

        md_content = "# Title\n@[poll: Title](A, B)"
        result = self.processor.convert_markdown_to_html(md_content)

        self.assertEqual(result, "<h1>Processed</h1>")

        # Verify markdown.markdown was called with the preprocessed content
        expected_preprocessed = '# Title\n<situ-poll id="poll-1" title="Title" options="A, B"></situ-poll>'
        mock_markdown.markdown.assert_any_call(expected_preprocessed, extensions=MARKDOWN_EXTENSIONS)

    @patch('src.processors.markdown.markdown')
    def test_convert_markdown_to_html_error(self, mock_markdown):
        mock_markdown.markdown.side_effect = Exception("Markdown parsing failed")

        md_content = "# Title"
        with self.assertRaises(ConversionError) as context:
            self.processor.convert_markdown_to_html(md_content)

        self.assertIn("Markdown変換エラー", str(context.exception))
