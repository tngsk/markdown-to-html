import re
from src.processors.base_parser import BaseComponentParser

class Parser(BaseComponentParser):
    PATTERN = r"@\[ab-test:\s*(.+?)\]\((.+?),\s*(.+?)\)"

    def process(self, markdown_content: str) -> str:
        pattern = re.compile(self.PATTERN)
        def replacer(match: re.Match) -> str:
            title = match.group(1).strip()
            src_a = match.group(2).strip()
            src_b = match.group(3).strip()
            safe_title = self.escape_html(title)
            safe_src_a = self.escape_html(src_a)
            safe_src_b = self.escape_html(src_b)
            component_id = self.get_next_id("abtest")
            return f'<situ-ab-test id="{component_id}" title="{safe_title}" src-a="{safe_src_a}" src-b="{safe_src_b}"></situ-ab-test>'
        return pattern.sub(replacer, markdown_content)
