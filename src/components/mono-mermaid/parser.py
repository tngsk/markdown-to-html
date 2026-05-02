import re
import html
import subprocess
import tempfile
import logging
from pathlib import Path
from src.processors.base_parser import BaseComponentParser

logger = logging.getLogger(__name__)

class Parser(BaseComponentParser):
    # OPTIONS: theme, title
    START_PATTERN = r"@\[mermaid(?:(?:\:\s*)?([^\]]*))\](?:\(((?:[^()]*|\([^()]*\))*)\))?"
    END_PATTERN = r"@\[/mermaid\]"

    @property
    def block_level_tags(self) -> list[str]:
        return ["mono-mermaid"]

    def process(self, markdown_content: str) -> str:
        pattern = re.compile(f"({self.START_PATTERN})(.*?)({self.END_PATTERN})", re.DOTALL)

        def replacer(match: re.Match) -> str:
            start_tag = match.group(1)
            bracket_content = match.group(2)
            args_str = match.group(3)
            content = match.group(4).strip()
            end_tag = match.group(5)

            title, specific_args = self.parse_bracket_content(bracket_content)
            common_args = self.parse_key_value_args(args_str) if args_str else {}
            args = {**specific_args, **common_args}

            theme = args.get("theme", "default")
            svg_content = self._generate_svg(content, theme)
            if not svg_content:
                # If SVG generation fails, fallback to displaying the code
                safe_content = html.escape(content)
                return f'<div class="mermaid-error"><pre><code>{safe_content}</code></pre><p>Failed to render Mermaid diagram.</p></div>'

            attrs = []
            if title and title.strip():
                attrs.append(f'title="{html.escape(title.strip())}"')

            # Clean up the SVG a bit to embed smoothly (remove xml/doctype declarations if present)
            svg_content = re.sub(r'<\?xml.*?\?>', '', svg_content, flags=re.IGNORECASE).strip()
            svg_content = re.sub(r'<!DOCTYPE.*?>', '', svg_content, flags=re.IGNORECASE).strip()

            attrs_str = " ".join(attrs)
            common_attrs_str = self.get_common_attributes(args)

            result = f'<mono-mermaid {attrs_str}{common_attrs_str}>\n'
            result += f'{svg_content}\n'
            result += '</mono-mermaid>'

            return result

        return pattern.sub(replacer, markdown_content)

    def _generate_svg(self, mermaid_code: str, theme: str = "default") -> str:
        """
        Uses @mermaid-js/mermaid-cli (mmdc) to generate SVG from Mermaid code.
        """
        if not mermaid_code:
            return ""

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dir_path = Path(temp_dir)
                input_file = temp_dir_path / "input.mmd"
                output_file = temp_dir_path / "output.svg"

                input_file.write_text(mermaid_code, encoding="utf-8")

                # npx must be used to call mmdc from node_modules securely
                # Suppress output to avoid spamming the console
                cmd = ["npx", "mmdc", "-i", str(input_file), "-o", str(output_file)]
                if theme and theme != "default":
                    cmd.extend(["-t", theme])

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )

                if output_file.exists():
                    return output_file.read_text(encoding="utf-8")
                else:
                    logger.error("Mermaid CLI failed to generate output SVG file.")
                    return ""

        except subprocess.CalledProcessError as e:
            logger.error(f"Mermaid CLI execution failed: {e.stderr}")
            return ""
        except FileNotFoundError:
            logger.error("npx or mmdc command not found. Please ensure Node.js and @mermaid-js/mermaid-cli are installed.")
            return ""
        except Exception as e:
            logger.error(f"An unexpected error occurred during Mermaid SVG generation: {e}")
            return ""
