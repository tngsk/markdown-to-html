import re
from src.processors.base_parser import BaseComponentParser

class Parser(BaseComponentParser):
    PATTERN = r"@\[spacer\]\((.+?)\)"

    def process(self, markdown_content: str) -> str:
        pattern = re.compile(self.PATTERN)
        def replacer(match: re.Match) -> str:
            args = match.group(1).split(",")
            width = args[0].strip()
            height = args[1].strip() if len(args) > 1 else width
            safe_width = self.escape_html(width)
            safe_height = self.escape_html(height)
            return f'<situ-spacer width="{safe_width}" height="{safe_height}"></situ-spacer>'
        return pattern.sub(replacer, markdown_content)
