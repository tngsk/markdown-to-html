import unittest
from unittest.mock import MagicMock, patch
import sys
import logging

import importlib.util
if importlib.util.find_spec("markdown") is None:
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
            ("@[icon: search]", '<mono-icon name="search"></mono-icon>'),
            ("@[icon: search]()", '<mono-icon name="search"></mono-icon>'),
            ("@[icon: search](size: 24px)", '<mono-icon name="search" size="24px"></mono-icon>'),
            ("@[icon: search](size: 24px, color: red)", '<mono-icon name="search" size="24px" color="red"></mono-icon>'),
            ("@[icon: search](size: 24px, color: #FF0000, display: block)", '<mono-icon name="search" size="24px" color="#FF0000" display="block"></mono-icon>'),
            ("@[icon: search](size: 24px, color: rgba(255, 0, 0, 0.5), display: block)", '<mono-icon name="search" size="24px" color="rgba(255, 0, 0, 0.5)" display="block"></mono-icon>'),
            ("@[icon: search](color: blue)", '<mono-icon name="search" color="blue"></mono-icon>'),
            ("@[icon: search](display: inline)", '<mono-icon name="search" display="inline"></mono-icon>'),
            ('@[icon: "quotes" test]', '<mono-icon name="&quot;quotes&quot; test"></mono-icon>'),
            ('@[icon: "search"]', '<mono-icon name="search"></mono-icon>'),
            ("@[icon: 'search with space']", '<mono-icon name="search with space"></mono-icon>'),
            ('@[icon: "search with space"](size: 24px)', '<mono-icon name="search with space" size="24px"></mono-icon>'),
        ]

        for markdown_text, expected_html in cases:
            with self.subTest(markdown_text=markdown_text):
                result = self._get_parser("mono-icon").process(markdown_text)
                self.assertEqual(result, expected_html)

    def test_preprocess_sound(self):
        # Test basic and no-label replacements
        md_content = "Here is @[sound: UI1](src: test.mp3) and @[sound](src: test.wav)."
        result = self._get_parser("mono-sound").process(md_content)

        self.assertIn('<mono-sound id="sound-1" label="UI1" src="test.mp3"></mono-sound>', result)
        self.assertIn('<mono-sound id="sound-2" label="" src="test.wav"></mono-sound>', result)

    def test_preprocess_polls(self):
        # Test basic replacement
        md_content = "Some text @[poll: My Title](options: \"Option A, Option B\")"
        expected_html = 'Some text <mono-poll id="poll-1" title="My Title" options="Option A, Option B"></mono-poll>'
        result = self._get_parser("mono-poll").process(md_content)
        self.assertEqual(result, expected_html)

        # Test escaping
        md_content_escape = 'Another @[poll: Title "with quotes"](options: "Option <A>")'
        expected_html_escape = 'Another <mono-poll id="poll-1" title="Title &quot;with quotes&quot;" options="Option &lt;A&gt;"></mono-poll>'

        # We need to create a new processor to reset the counter
        processor2 = MarkdownProcessor(self.logger, self.file_handler)
        result_escape = self._get_parser("mono-poll", processor2).process(md_content_escape)
        self.assertEqual(result_escape, expected_html_escape)

    def test_preprocess_textfield(self):
        # Test standard format
        md_content = "Please enter @[textfield: Your Name]"
        expected_html = 'Please enter <mono-textfield-input placeholder="Your Name" label="Your Name" id="textfield-1"></mono-textfield-input>'
        result = self._get_parser("mono-textfield-input").process(md_content)
        self.assertEqual(result, expected_html)

        # Test size format
        md_content_size = "Input with size: @[textfield](size: 50, placeholder: Details)"
        expected_html_size = 'Input with size: <mono-textfield-input placeholder="Details" size="50" id="textfield-1"></mono-textfield-input>'
        processor2 = MarkdownProcessor(self.logger, self.file_handler)
        result_size = self._get_parser("mono-textfield-input", processor2).process(md_content_size)
        self.assertEqual(result_size, expected_html_size)

    def test_preprocess_textfield_size_without_placeholder(self):
        # Test size without placeholder
        md_content_size_no_placeholder = "Input with size no placeholder: @[textfield](size: 30)"
        expected_html_size_no_placeholder = 'Input with size no placeholder: <mono-textfield-input placeholder="" size="30" id="textfield-1"></mono-textfield-input>'
        processor = MarkdownProcessor(self.logger, self.file_handler)
        result_size_no_placeholder = self._get_parser("mono-textfield-input", processor).process(md_content_size_no_placeholder)
        self.assertEqual(result_size_no_placeholder, expected_html_size_no_placeholder)

    def test_preprocess_notebooks(self):
        md_content = "Notebook link: @[notebook-input](id: my-notebook-id)"
        expected_html = 'Notebook link: <mono-notebook id="my-notebook-id"></mono-notebook>'
        result = self._get_parser("mono-notebook").process(md_content)
        self.assertEqual(result, expected_html)

        md_content_title = "Notebook link: @[notebook: My Notes](id: my-notebook-id)"
        expected_html_title = 'Notebook link: <mono-notebook title="My Notes" id="my-notebook-id"></mono-notebook>'
        processor2 = MarkdownProcessor(self.logger, self.file_handler)
        result_title = self._get_parser("mono-notebook", processor2).process(md_content_title)
        self.assertEqual(result_title, expected_html_title)

        md_content_placeholder = "Notebook link: @[notebook](id: my-notebook-id, placeholder: Please write here)"
        expected_html_placeholder = 'Notebook link: <mono-notebook placeholder="Please write here" id="my-notebook-id"></mono-notebook>'
        processor3 = MarkdownProcessor(self.logger, self.file_handler)
        result_placeholder = self._get_parser("mono-notebook", processor3).process(md_content_placeholder)
        self.assertEqual(result_placeholder, expected_html_placeholder)

        md_content_both = "Notebook link: @[notebook: My Notes](id: my-notebook-id, placeholder: Please write here)"
        expected_html_both = 'Notebook link: <mono-notebook title="My Notes" placeholder="Please write here" id="my-notebook-id"></mono-notebook>'
        processor4 = MarkdownProcessor(self.logger, self.file_handler)
        result_both = self._get_parser("mono-notebook", processor4).process(md_content_both)
        self.assertEqual(result_both, expected_html_both)

    def test_preprocess_ab_tests(self):
        md_content = "Test: @[ab-test: My Test](src-a: file_a.md, src-b: file_b.md)"
        expected_html = 'Test: <mono-ab-test id="abtest-1" title="My Test" src-a="file_a.md" src-b="file_b.md"></mono-ab-test>'
        result = self._get_parser("mono-ab-test").process(md_content)
        self.assertEqual(result, expected_html)

    def test_preprocess_reactions(self):
        md_content = "React here: @[reaction](options: \"like, dislike\")"
        expected_html = 'React here: <mono-reaction id="reaction-1" options="like, dislike"></mono-reaction>'
        result = self._get_parser("mono-reaction").process(md_content)
        self.assertEqual(result, expected_html)

    def test_preprocess_session_join(self):
        md_content = "Join session: @[session-join: Room 101]"
        expected_html = 'Join session: <mono-session-join title="Room 101"></mono-session-join>'
        result = self._get_parser("mono-session-join").process(md_content)
        self.assertEqual(result, expected_html)

    def test_preprocess_group_assignment(self):
        md_content = "Groups: @[group-assignment: Project Alpha]"
        expected_html = 'Groups: <mono-group-assignment title="Project Alpha"></mono-group-assignment>'
        result = self._get_parser("mono-group-assignment").process(md_content)
        self.assertEqual(result, expected_html)

    def test_preprocess_spacer(self):
        md_content_single = "Text before @[spacer](width: 20px) text after."
        expected_html_single = 'Text before <mono-spacer width="20px" height="20px"></mono-spacer> text after.'
        result_single = self._get_parser("mono-spacer").process(md_content_single)
        self.assertEqual(result_single, expected_html_single)

        md_content_double = "Text before @[spacer](width: 10px, height: 20px) text after."
        expected_html_double = 'Text before <mono-spacer width="10px" height="20px"></mono-spacer> text after.'
        result_double = self._get_parser("mono-spacer").process(md_content_double)
        self.assertEqual(result_double, expected_html_double)

    def test_preprocess_hero(self):
        md_content = (
            "@[hero: Welcome!](image: \"bg.jpg\", mode: cover, bg-color: \"#000\", text-color: \"#fff\")\n"
            "This is a subtext\n"
            "@[/hero]"
        )
        expected_html = (
            '<mono-hero markdown="1" image="bg.jpg" mode="cover" bg-color="#000" text-color="#fff">\n'
            '<h1>Welcome!</h1>\n\n'
            'This is a subtext\n'
            '</mono-hero>'
        )
        result = self._get_parser("mono-hero").process(md_content)
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
            "@[/stack]\n"
            "@[/row]"
        )
        expected_html = (
            '<mono-layout type="row" class="center gap-md" markdown="1">\n'
            '<div class="column" markdown="1">\n'
            "A\n"
            "</div>\n"
            '<mono-layout type="stack" markdown="1">\n'
            '<div class="column" markdown="1">\n'
            "B\n"
            "</div>\n"
            "</mono-layout>\n"
            "</mono-layout>"
        )
        result = self._get_parser("mono-layout").process(md_content)
        self.assertEqual(result, expected_html)

    @patch('src.processors.markdown.markdown')
    def test_convert_markdown_to_html_success(self, mock_markdown):
        mock_markdown.markdown.side_effect = None
        mock_markdown.markdown.return_value = "<h1>Processed</h1>"

        md_content = "# Title\n@[poll: Title](options: \"A, B\")"
        result = self.processor.convert_markdown_to_html(md_content)

        self.assertEqual(result, "<h1>Processed</h1>")

        # Verify markdown.markdown was called with the preprocessed content
        expected_preprocessed = '# Title\n<mono-poll id="poll-1" title="Title" options="A, B"></mono-poll>'
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
        assert '<mono-icon name="outside">' in html_output

        # フェンスコードブロック内のアイコンは変換されない
        assert '<mono-icon name="inside_fenced">' not in html_output
        # Highlight.js might wrap parts of it in spans depending on the language
        # We just need to ensure the raw string `@` and `[` are present and the component wasn't parsed
        # Due to highlight.js, 'inside_fenced' gets split: 'inside<span class="hljs-emphasis">_fenced]</span>'
        assert 'inside' in html_output
        assert 'fenced' in html_output
        assert 'icon:' in html_output

        # インラインコードブロック内のアイコンは変換されない
        assert '<mono-icon name="inside_inline">' not in html_output
        assert '@[icon: inside_inline]' in html_output

    @patch('src.processors.markdown.markdown')
    def test_convert_markdown_to_html_error(self, mock_markdown):
        mock_markdown.markdown.side_effect = Exception("Markdown parsing failed")

        md_content = "# Title"
        with self.assertRaises(ConversionError) as context:
            self.processor.convert_markdown_to_html(md_content)

        self.assertIn("Markdown変換エラー", str(context.exception))

    def test_new_syntax_pattern_a(self):
        """Test the new Markdown syntax (Pattern A) separating specific args and styles"""
        # testfield with label, id, placeholder in [] and class in ()
        md_content = 'Input: @[textfield: "Name", id: "user-name", placeholder: "Enter name"](class: "gap-md center")'
        expected_html = 'Input: <mono-textfield-input placeholder="Enter name" label="Name" class="gap-md center" id="user-name"></mono-textfield-input>'
        result = self._get_parser("mono-textfield-input").process(md_content)
        self.assertEqual(result, expected_html)

        # icon with size, color in [], display in ()
        md_content2 = '@[icon: search, size: 24px, color: red](display: block)'
        expected_html2 = '<mono-icon name="search" size="24px" color="red" display="block"></mono-icon>'
        result2 = self._get_parser("mono-icon").process(md_content2)
        self.assertEqual(result2, expected_html2)
