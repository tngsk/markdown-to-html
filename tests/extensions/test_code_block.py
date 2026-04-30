import unittest
import markdown

from src.extensions.code_block import CodeBlockExtension

class TestCodeBlockExtension(unittest.TestCase):
    def setUp(self):
        self.md = markdown.Markdown(extensions=["fenced_code", CodeBlockExtension()])

    def test_enhance_code_blocks(self):
        text = "```python\nprint(\"hello\")\n```"
        html = self.md.convert(text)
        self.assertIn('<mono-code-block language="python">', html)
        self.assertIn('<pre><code class="language-python hljs">', html)
        self.assertIn('<span class="nb">print</span>', html)

    def test_enhance_code_blocks_no_lang(self):
        text = "```\nprint(\"hello\")\n```"
        html = self.md.convert(text)
        self.assertIn('<mono-code-block language="">', html)
        self.assertIn('<pre><code class="language- hljs">', html)
        self.assertIn('print(&quot;hello&quot;)', html)
