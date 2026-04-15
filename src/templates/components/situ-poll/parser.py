import re
from src.processors.base_parser import BaseComponentParser

class Parser(BaseComponentParser):
    PATTERN = r"@\[poll:\s*(.+?)\]\((.+?)\)"

    def process(self, markdown_content: str) -> str:
        pattern = re.compile(self.PATTERN)
        def replacer(match: re.Match) -> str:
            title = match.group(1).strip()
            options = match.group(2).strip()
            safe_title = self.escape_html(title)
            safe_options = self.escape_html(options)
            component_id = self.get_next_id("poll")
            return f'<situ-poll id="{component_id}" title="{safe_title}" options="{safe_options}"></situ-poll>'
        return pattern.sub(replacer, markdown_content)
