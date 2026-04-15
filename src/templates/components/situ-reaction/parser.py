import re
from src.processors.base_parser import BaseComponentParser

class Parser(BaseComponentParser):
    PATTERN = r"@\[reaction:\s*\"?(.*?)\"?\]"

    def process(self, markdown_content: str) -> str:
        pattern = re.compile(self.PATTERN)
        def replacer(match: re.Match) -> str:
            options = match.group(1).strip()
            safe_options = self.escape_html(options)
            component_id = self.get_next_id("reaction")
            return f'<situ-reaction id="{component_id}" options="{safe_options}"></situ-reaction>'
        return pattern.sub(replacer, markdown_content)
