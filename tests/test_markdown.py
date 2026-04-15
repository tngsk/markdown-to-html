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

    def _get_parser(self, component_name, processor=None):
        p = processor if processor else self.processor
        for parser in p.parsers:
            if parser.__class__.__module__.endswith(f"{component_name}.parser"):
                return parser
        return None

    def test_preprocess_icon(self):
        """アイコンコンポーネントの前処理をテスト"""
        cases = [
            ("@[icon: search]", '<situ-icon name="search"></situ-icon>'),
            ("@[icon: search]()", '<situ-icon name="search"></situ-icon>'),
            ("@[icon: search](size: 24px)", '<situ-icon name="search" size="24px"></situ-icon>'),
            ("@[icon: search](size: 24px, color: red)", '<situ-icon name="search" size="24px" color="red"></situ-icon>'),
            ("@[icon: search](size: 24px, color: #FF0000, display: block)", '<situ-icon name="search" size="24px" color="#FF0000" display="block"></situ-icon>'),
            ("@[icon: search](size: 24px, color: rgba(255, 0, 0, 0.5), display: block)", '<situ-icon name="search" size="24px" color="rgba(255, 0, 0, 0.5)" display="block"></situ-icon>'),
            ("@[icon: search](color: blue)", '<situ-icon name="search" color="blue"></situ-icon>'),
            ("@[icon: search](display: inline)", '<situ-icon name="search" display="inline"></situ-icon>'),
            ('@[icon: "quotes" test]', '<situ-icon name="&quot;quotes&quot; test"></situ-icon>'),
            ('@[icon: "search"]', '<situ-icon name="search"></situ-icon>'),
            ("@[icon: 'search with space']", '<situ-icon name="search with space"></situ-icon>'),
            ('@[icon: "search with space"](size: 24px)', '<situ-icon name="search with space" size="24px"></situ-icon>'),
        ]

        for markdown_text, expected_html in cases:
            with self.subTest(markdown_text=markdown_text):
                result = self._get_parser("situ-icon").process(markdown_text)
                self.assertEqual(result, expected_html)

    def test_preprocess_sound(self):
        # Test basic and no-label replacements
        md_content = "Here is @[sound: UI1](src: test.mp3) and @[sound](src: test.wav)."
        result = self._get_parser("situ-sound").process(md_content)

        self.assertIn('<situ-sound id="sound-1" label="UI1" src="test.mp3"></situ-sound>', result)
        self.assertIn('<situ-sound id="sound-2" label="" src="test.wav"></situ-sound>', result)

    def test_preprocess_polls(self):
        # Test basic replacement
        md_content = "Some text @[poll: My Title](options: \"Option A, Option B\")"
        expected_html = 'Some text <situ-poll id="poll-1" title="My Title" options="Option A, Option B"></situ-poll>'
        result = self._get_parser("situ-poll").process(md_content)
        self.assertEqual(result, expected_html)

        # Test escaping
        md_content_escape = 'Another @[poll: Title "with quotes"](options: "Option <A>")'
        expected_html_escape = 'Another <situ-poll id="poll-1" title="Title &quot;with quotes&quot;" options="Option &lt;A&gt;"></situ-poll>'

        # We need to create a new processor to reset the counter
        processor2 = MarkdownProcessor(self.logger, self.file_handler)
        result_escape = self._get_parser("situ-poll", processor2).process(md_content_escape)
        self.assertEqual(result_escape, expected_html_escape)

    def test_preprocess_textfield(self):
        # Test standard format
        md_content = "Please enter @[textfield: Your Name]"
        expected_html = 'Please enter <situ-textfield-input id="textfield-1" placeholder="Your Name"></situ-textfield-input>'
        result = self._get_parser("situ-textfield-input").process(md_content)
        self.assertEqual(result, expected_html)

        # Test size format
        md_content_size = "Input with size: @[textfield](size: 50, placeholder: Details)"
        expected_html_size = 'Input with size: <situ-textfield-input id="textfield-1" placeholder="Details" size="50"></situ-textfield-input>'
        processor2 = MarkdownProcessor(self.logger, self.file_handler)
        result_size = self._get_parser("situ-textfield-input", processor2).process(md_content_size)
        self.assertEqual(result_size, expected_html_size)

        # Test typo 'textfiled'
        md_content_typo = "Typo @[textfiled: Description]"
        expected_html_typo = 'Typo <situ-textfield-input id="textfield-1" placeholder="Description"></situ-textfield-input>'
        processor3 = MarkdownProcessor(self.logger, self.file_handler)
        result_typo = self._get_parser("situ-textfield-input", processor3).process(md_content_typo)
        self.assertEqual(result_typo, expected_html_typo)

    def test_preprocess_textfield_size_without_placeholder(self):
        # Test size without placeholder
        md_content_size_no_placeholder = "Input with size no placeholder: @[textfield](size: 30)"
        expected_html_size_no_placeholder = 'Input with size no placeholder: <situ-textfield-input id="textfield-1" placeholder="" size="30"></situ-textfield-input>'
        processor = MarkdownProcessor(self.logger, self.file_handler)
        result_size_no_placeholder = self._get_parser("situ-textfield-input", processor).process(md_content_size_no_placeholder)
        self.assertEqual(result_size_no_placeholder, expected_html_size_no_placeholder)

    def test_preprocess_notebooks(self):
        md_content = "Notebook link: @[notebook-input](id: my-notebook-id)"
        expected_html = 'Notebook link: <situ-notebook id="my-notebook-id"></situ-notebook>'
        result = self._get_parser("situ-notebook").process(md_content)
        self.assertEqual(result, expected_html)

        md_content_title = "Notebook link: @[notebook: My Notes](id: my-notebook-id)"
        expected_html_title = 'Notebook link: <situ-notebook id="my-notebook-id" title="My Notes"></situ-notebook>'
        processor2 = MarkdownProcessor(self.logger, self.file_handler)
        result_title = self._get_parser("situ-notebook", processor2).process(md_content_title)
        self.assertEqual(result_title, expected_html_title)

        md_content_placeholder = "Notebook link: @[notebook](id: my-notebook-id, placeholder: Please write here)"
        expected_html_placeholder = 'Notebook link: <situ-notebook id="my-notebook-id" placeholder="Please write here"></situ-notebook>'
        processor3 = MarkdownProcessor(self.logger, self.file_handler)
        result_placeholder = self._get_parser("situ-notebook", processor3).process(md_content_placeholder)
        self.assertEqual(result_placeholder, expected_html_placeholder)

        md_content_both = "Notebook link: @[notebook: My Notes](id: my-notebook-id, placeholder: Please write here)"
        expected_html_both = 'Notebook link: <situ-notebook id="my-notebook-id" title="My Notes" placeholder="Please write here"></situ-notebook>'
        processor4 = MarkdownProcessor(self.logger, self.file_handler)
        result_both = self._get_parser("situ-notebook", processor4).process(md_content_both)
        self.assertEqual(result_both, expected_html_both)

    def test_preprocess_ab_tests(self):
        md_content = "Test: @[ab-test: My Test](src-a: file_a.md, src-b: file_b.md)"
        expected_html = 'Test: <situ-ab-test id="abtest-1" title="My Test" src-a="file_a.md" src-b="file_b.md"></situ-ab-test>'
        result = self._get_parser("situ-ab-test").process(md_content)
        self.assertEqual(result, expected_html)

    def test_preprocess_reactions(self):
        md_content = "React here: @[reaction](options: \"like, dislike\")"
        expected_html = 'React here: <situ-reaction id="reaction-1" options="like, dislike"></situ-reaction>'
        result = self._get_parser("situ-reaction").process(md_content)
        self.assertEqual(result, expected_html)

    def test_preprocess_session_join(self):
        md_content = "Join session: @[session-join: Room 101]"
        expected_html = 'Join session: <situ-session-join title="Room 101"></situ-session-join>'
        result = self._get_parser("situ-session-join").process(md_content)
        self.assertEqual(result, expected_html)

    def test_preprocess_group_assignment(self):
        md_content = "Groups: @[group-assignment: Project Alpha]"
        expected_html = 'Groups: <situ-group-assignment title="Project Alpha"></situ-group-assignment>'
        result = self._get_parser("situ-group-assignment").process(md_content)
        self.assertEqual(result, expected_html)

    def test_preprocess_spacer(self):
        md_content_single = "Text before @[spacer](width: 20px) text after."
        expected_html_single = 'Text before <situ-spacer width="20px" height="20px"></situ-spacer> text after.'
        result_single = self._get_parser("situ-spacer").process(md_content_single)
        self.assertEqual(result_single, expected_html_single)

        md_content_double = "Text before @[spacer](width: 10px, height: 20px) text after."
        expected_html_double = 'Text before <situ-spacer width="10px" height="20px"></situ-spacer> text after.'
        result_double = self._get_parser("situ-spacer").process(md_content_double)
        self.assertEqual(result_double, expected_html_double)

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
        result = self._get_parser("situ-layout").process(md_content)
        self.assertEqual(result, expected_html)

    @patch('src.processors.markdown.markdown')
    def test_convert_markdown_to_html_success(self, mock_markdown):
        mock_markdown.markdown.side_effect = None
        mock_markdown.markdown.return_value = "<h1>Processed</h1>"

        md_content = "# Title\n@[poll: Title](options: \"A, B\")"
        result = self.processor.convert_markdown_to_html(md_content)

        self.assertEqual(result, "<h1>Processed</h1>")

        # Verify markdown.markdown was called with the preprocessed content
        expected_preprocessed = '# Title\n<situ-poll id="poll-1" title="Title" options="A, B"></situ-poll>'
        mock_markdown.markdown.assert_any_call(expected_preprocessed, extensions=MARKDOWN_EXTENSIONS)

    def test_code_blocks_protected(self):
        """コードブロック内のコンポーネント構文が変換されず保護されることをテスト"""
        markdown_content = """
@[icon: outside]

```markdown
@[icon: inside_fenced]
```

Inline `@[icon: inside_inline]` testing.
"""
        html_output = self.processor.convert_markdown_to_html(markdown_content)

        # 外側のアイコンは変換される
        assert '<situ-icon name="outside">' in html_output

        # フェンスコードブロック内のアイコンは変換されない
        assert '<situ-icon name="inside_fenced">' not in html_output
        assert '@[icon: inside_fenced]' in html_output

        # インラインコードブロック内のアイコンは変換されない
        assert '<situ-icon name="inside_inline">' not in html_output
        assert '@[icon: inside_inline]' in html_output

    @patch('src.processors.markdown.markdown')
    def test_convert_markdown_to_html_error(self, mock_markdown):
        mock_markdown.markdown.side_effect = Exception("Markdown parsing failed")

        md_content = "# Title"
        with self.assertRaises(ConversionError) as context:
            self.processor.convert_markdown_to_html(md_content)

        self.assertIn("Markdown変換エラー", str(context.exception))
