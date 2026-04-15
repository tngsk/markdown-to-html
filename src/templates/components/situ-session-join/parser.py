import re
from src.processors.base_parser import BaseComponentParser

class Parser(BaseComponentParser):
    PATTERN = r"@\[session-join:\s*\"?(.*?)\"?\]"

    def process(self, markdown_content: str) -> str:
        pattern = re.compile(self.PATTERN)
        def replacer(match: re.Match) -> str:
            title = match.group(1).strip()
            safe_title = self.escape_html(title)
            return f'<situ-session-join title="{safe_title}"></situ-session-join>'
        return pattern.sub(replacer, markdown_content)
