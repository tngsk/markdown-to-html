import re
import html
import json
import subprocess
from pathlib import Path
from markdown.postprocessors import Postprocessor
from markdown.extensions import Extension
import logging

logger = logging.getLogger(__name__)

class CodeBlockPostprocessor(Postprocessor):
    def run(self, text):
        pattern = re.compile(
            r'(<pre><code(?:\s+[^>]+)?>(.*?)</code></pre>)', re.DOTALL
        )

        def replacer(match: re.Match) -> str:
            original_block = match.group(1)
            code_content = match.group(2)

            # Markdown escapes the HTML content within the code block, so unescape it before sending to highlight.js
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

            # Call Node.js script to highlight code
            highlighted_code = self._highlight_code(raw_code, language)

            # Manually reconstruct the inner <code> content, maintaining the <pre><code> structure
            # to be compatible with MonoCodeBlock's Light DOM strategy.
            highlighted_block = f'<pre><code class="language-{language} hljs">{highlighted_code}</code></pre>'

            theme_attr = f' theme="{theme}"' if theme else ""
            return f'<mono-code-block language="{language}"{theme_attr}>\n{highlighted_block}\n</mono-code-block>'

        return pattern.sub(replacer, text)

    def _highlight_code(self, code: str, language: str) -> str:
        """Call Node.js script to highlight the code."""
        script_path = Path(__file__).parent / "highlight_renderer.js"

        # If node script doesn't exist, fallback to raw code
        if not script_path.exists():
            logger.warning("highlight_renderer.js not found. Falling back to unhighlighted code.")
            return html.escape(code)

        try:
            input_data = json.dumps({"code": code, "language": language})

            result = subprocess.run(
                ["node", str(script_path)],
                input=input_data,
                text=True,
                capture_output=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Highlight.js rendering failed: {e.stderr}")
            return html.escape(code)
        except Exception as e:
            logger.error(f"Highlight.js process execution error: {e}")
            return html.escape(code)

class CodeBlockExtension(Extension):
    def extendMarkdown(self, md):
        md.postprocessors.register(CodeBlockPostprocessor(md), 'code_block', 10)

def makeExtension(**kwargs):
    return CodeBlockExtension(**kwargs)
