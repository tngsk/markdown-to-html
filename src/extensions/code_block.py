import re
from markdown.postprocessors import Postprocessor
from markdown.extensions import Extension

class CodeBlockPostprocessor(Postprocessor):
    def run(self, text):
        pattern = re.compile(
            r'(<pre><code(?:\s+class="([^"]*)")?>.*?</code></pre>)', re.DOTALL
        )

        def replacer(match: re.Match) -> str:
            original_block = match.group(1)
            lang_class = match.group(2) or ""

            language = ""
            if lang_class:
                lang_match = re.search(r"language-(\w+)", lang_class)
                if lang_match:
                    language = lang_match.group(1)

            return f'<mono-code-block language="{language}">\n{original_block}\n</mono-code-block>'

        return pattern.sub(replacer, text)

class CodeBlockExtension(Extension):
    def extendMarkdown(self, md):
        # markdown's RawHtmlPostprocessor has priority 30
        # By setting priority to 10, we ensure this runs AFTER raw HTML blocks (like fenced code)
        # are restored from their stash placeholders.
        md.postprocessors.register(CodeBlockPostprocessor(md), 'code_block', 10)

def makeExtension(**kwargs):
    return CodeBlockExtension(**kwargs)
