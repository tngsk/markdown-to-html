import re

from src.processors.base_parser import BaseComponentParser


class Parser(BaseComponentParser):
    PATTERN = r"@\[(?:notebook|notebook-input)(?::\s*([^\]]+))?\]\((.+?)\)"

    def process(self, markdown_content: str) -> str:
        pattern = re.compile(self.PATTERN)

        def replacer(match: re.Match) -> str:
            title = match.group(1)
            input_id = match.group(2).strip()
            safe_id = self.escape_html(input_id)

            if title:
                safe_title = self.escape_html(title.strip())
                return f'<situ-notebook id="{safe_id}" title="{safe_title}"></situ-notebook>'

            return f'<situ-notebook id="{safe_id}"></situ-notebook>'

        return pattern.sub(replacer, markdown_content)
