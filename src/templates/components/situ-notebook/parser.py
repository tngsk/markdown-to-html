import re

from src.processors.base_parser import BaseComponentParser


class Parser(BaseComponentParser):
    PATTERN = r"@\[(?:notebook|notebook-input)(?::\s*([^\]]+))?\]\(([^,)]+?)(?:,\s*([^)]+?))?\)"

    def process(self, markdown_content: str) -> str:
        pattern = re.compile(self.PATTERN)

        def replacer(match: re.Match) -> str:
            title = match.group(1)
            input_id = match.group(2).strip()
            placeholder = match.group(3)

            safe_id = self.escape_html(input_id)
            attrs = [f'id="{safe_id}"']

            if title:
                safe_title = self.escape_html(title.strip())
                attrs.append(f'title="{safe_title}"')

            if placeholder:
                safe_placeholder = self.escape_html(placeholder.strip())
                attrs.append(f'placeholder="{safe_placeholder}"')

            attrs_str = " ".join(attrs)
            return f'<situ-notebook {attrs_str}></situ-notebook>'

        return pattern.sub(replacer, markdown_content)
