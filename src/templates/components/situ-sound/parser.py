import re
from src.processors.base_parser import BaseComponentParser

class Parser(BaseComponentParser):
    PATTERN = r"@\[sound(?::\s*(.*?))?\]\((.+?)\)"

    def process(self, markdown_content: str) -> str:
        pattern = re.compile(self.PATTERN)
        def replacer(match: re.Match) -> str:
            label = match.group(1)
            src = match.group(2).strip()
            safe_label = self.escape_html(label) if label else ""
            safe_src = self.escape_html(src)
            component_id = self.get_next_id("sound")
            return f'<situ-sound id="{component_id}" label="{safe_label}" src="{safe_src}"></situ-sound>'
        return pattern.sub(replacer, markdown_content)
