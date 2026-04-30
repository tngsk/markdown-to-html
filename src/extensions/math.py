from markdown.inlinepatterns import InlineProcessor
from markdown.extensions import Extension
from xml.etree import ElementTree as etree

class MathInlineProcessor(InlineProcessor):
    def __init__(self, pattern, md, is_display=False):
        super().__init__(pattern, md)
        self.is_display = is_display

    def handleMatch(self, m, data):
        el = etree.Element('span')
        el.set('class', 'mono-math display' if self.is_display else 'mono-math inline')
        math_content = m.group(1)

        # nl2br uses <br /> which breaks display math spacing and syntax inside MathJax
        # By wrapping it inside an atomic string and replacing newlines, we can avoid standard <br /> insertion,
        # but markdown.util.AtomicString is the correct way to avoid ALL markdown processing (like nl2br, emphasis etc)
        # However, nl2br runs AFTER block/inline processors.
        # Using md.htmlStash is the standard way to protect HTML blocks completely.
        import markdown.util
        if self.is_display:
            el.text = markdown.util.AtomicString(f"\\[{math_content}\\]")
        else:
            el.text = markdown.util.AtomicString(f"\\({math_content}\\)")

        return el, m.start(0), m.end(0)

class MathExtension(Extension):
    def extendMarkdown(self, md):
        # We use (?s) to enable DOTALL (matching newlines) for display math
        display_math_pattern = r'(?s)\$\$(.*?)\$\$'
        md.inlinePatterns.register(MathInlineProcessor(display_math_pattern, md, True), 'math_display', 175)

        # Inline math shouldn't span lines, standard pattern is fine
        inline_math_pattern = r'\$([^\$]+)\$'
        md.inlinePatterns.register(MathInlineProcessor(inline_math_pattern, md, False), 'math_inline', 175)

def makeExtension(**kwargs):
    return MathExtension(**kwargs)
