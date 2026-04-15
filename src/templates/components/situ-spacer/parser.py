import re
from src.processors.base_parser import BaseComponentParser

class Parser(BaseComponentParser):
    PATTERN = r"@\[spacer(?:\:\s*([^\]]+))?\](?:\(((?:[^()]*|\([^()]*\))*)\))?"

    def process(self, markdown_content: str) -> str:
        pattern = re.compile(self.PATTERN)
        def replacer(match: re.Match) -> str:
            args_str = match.group(2)
            args = self.parse_key_value_args(args_str)

            width = args.get('width', '')
            height = args.get('height', width)

            safe_width = self.escape_html(width)
            safe_height = self.escape_html(height)
            return f'<situ-spacer width="{safe_width}" height="{safe_height}"></situ-spacer>'
        return pattern.sub(replacer, markdown_content)
