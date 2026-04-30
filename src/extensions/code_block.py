import re
import html
from markdown.postprocessors import Postprocessor
from markdown.extensions import Extension
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.lexers.special import TextLexer
from pygments.formatters import HtmlFormatter

class CodeBlockPostprocessor(Postprocessor):
    def run(self, text):
        pattern = re.compile(
            r'(<pre><code(?:\s+[^>]+)?>(.*?)</code></pre>)', re.DOTALL
        )

        def replacer(match: re.Match) -> str:
            original_block = match.group(1)
            code_content = match.group(2)

            # Markdown escapes the HTML content within the code block, so unescape it before Pygments
            raw_code = html.unescape(code_content)

            # Extract language
            language = ""
            lang_match = re.search(r'class="[^"]*language-([^"\s]+)[^"]*"', original_block)
            if lang_match:
                language = lang_match.group(1)

            # Extract theme
            theme = ""
            theme_match = re.search(r'theme="([^"]*)"', original_block)
            if theme_match:
                theme = theme_match.group(1)

            # Apply Pygments
            lexer = None
            if language:
                try:
                    lexer = get_lexer_by_name(language)
                except Exception:
                    pass

            if lexer is None:
                lexer = TextLexer()

            # Format the output without wrapping in full div/pre wrappers if possible, but HtmlFormatter
            # normally wraps in `<div class="highlight"><pre>...</pre></div>`. We use `nowrap=True`
            # to only get the highlighted `<span>` tags, and then wrap it manually to retain original
            # structure and theme attributes.
            formatter = HtmlFormatter(nowrap=True)
            highlighted_code = highlight(raw_code, lexer, formatter)

            # Manually reconstruct the inner <code> content, maintaining the <pre><code> structure
            # to be compatible with MonoCodeBlock's Light DOM strategy.
            # Pygments formatter adds a trailing newline, remove it if the original didn't have an extra one.
            highlighted_block = f'<pre><code class="language-{language} hljs">{highlighted_code}</code></pre>'

            theme_attr = f' theme="{theme}"' if theme else ""
            return f'<mono-code-block language="{language}"{theme_attr}>\n{highlighted_block}\n</mono-code-block>'

        return pattern.sub(replacer, text)

class CodeBlockExtension(Extension):
    def extendMarkdown(self, md):
        # markdown's RawHtmlPostprocessor has priority 30
        # By setting priority to 10, we ensure this runs AFTER raw HTML blocks (like fenced code)
        # are restored from their stash placeholders.
        md.postprocessors.register(CodeBlockPostprocessor(md), 'code_block', 10)

def makeExtension(**kwargs):
    return CodeBlockExtension(**kwargs)
