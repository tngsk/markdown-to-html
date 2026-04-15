import re

from src.processors.base_parser import BaseComponentParser


class Parser(BaseComponentParser):
    PATTERN = r"@\[notebook\]\((.+?)\)"

    def process(self, markdown_content: str) -> str:
        pattern = re.compile(self.PATTERN)

        def replacer(match: re.Match) -> str:
            input_id = match.group(1).strip()
            safe_id = self.escape_html(input_id)
            return f'<situ-notebook id="{safe_id}"></situ-notebook>'

        return pattern.sub(replacer, markdown_content)
