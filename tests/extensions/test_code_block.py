import unittest
import markdown

from src.extensions.code_block import CodeBlockExtension

class TestCodeBlockExtension(unittest.TestCase):
    def setUp(self):
        self.md = markdown.Markdown(extensions=["fenced_code", CodeBlockExtension()])

    def test_enhance_code_blocks(self):
        text = "```python\nprint(\"hello\")\n```"
        html = self.md.convert(text)
        expected = '<mono-code-block language="python">\n<pre><code class="language-python">print(&quot;hello&quot;)\n</code></pre>\n</mono-code-block>'
        self.assertEqual(html, expected)

    def test_enhance_code_blocks_no_lang(self):
        text = "```\nprint(\"hello\")\n```"
        html = self.md.convert(text)
        expected = '<mono-code-block language="">\n<pre><code>print(&quot;hello&quot;)\n</code></pre>\n</mono-code-block>'
        self.assertEqual(html, expected)
