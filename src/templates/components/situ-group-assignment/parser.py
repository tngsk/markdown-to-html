import re
from src.processors.base_parser import BaseComponentParser

class Parser(BaseComponentParser):
    PATTERN = r"@\[group-assignment:\s*\"?(.*?)\"?\]"

    def process(self, markdown_content: str) -> str:
        pattern = re.compile(self.PATTERN)
        def replacer(match: re.Match) -> str:
            title = match.group(1).strip()
            safe_title = self.escape_html(title)
            return f'<situ-group-assignment title="{safe_title}"></situ-group-assignment>'
        return pattern.sub(replacer, markdown_content)
