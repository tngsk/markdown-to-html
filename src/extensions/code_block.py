import re
from markdown.postprocessors import Postprocessor
from markdown.extensions import Extension

class CodeBlockPostprocessor(Postprocessor):
    def run(self, text):
        pattern = re.compile(
            r'(<pre><code(?:\s+[^>]+)?>.*?</code></pre>)', re.DOTALL
        )

        def replacer(match: re.Match) -> str:
            original_block = match.group(1)

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

            theme_attr = f' theme="{theme}"' if theme else ""
            return f'<mono-code-block language="{language}"{theme_attr}>\n{original_block}\n</mono-code-block>'

        return pattern.sub(replacer, text)

class CodeBlockExtension(Extension):
    def extendMarkdown(self, md):
        # markdown's RawHtmlPostprocessor has priority 30
        # By setting priority to 10, we ensure this runs AFTER raw HTML blocks (like fenced code)
        # are restored from their stash placeholders.
        md.postprocessors.register(CodeBlockPostprocessor(md), 'code_block', 10)

def makeExtension(**kwargs):
    return CodeBlockExtension(**kwargs)
