import re
from src.processors.base_parser import BaseComponentParser

class Parser(BaseComponentParser):
    PATTERN = r"@\[(?:textfield|textfiled):\s*(.+?)\]"

    def process(self, markdown_content: str) -> str:
        pattern = re.compile(self.PATTERN)
        def replacer(match: re.Match) -> str:
            content = match.group(1).strip()
            size_match = re.match(r"size:\s*(\d+)(?:\s*\((.*?)\))?", content)
            if size_match:
                size = size_match.group(1)
                placeholder = size_match.group(2)
                if placeholder is None:
                    placeholder = ""
                placeholder = placeholder.strip()
                size_attr = f' size="{size}"'
            else:
                placeholder = content
                size_attr = ""
            safe_placeholder = self.escape_html(placeholder)
            component_id = self.get_next_id("textfield")
            return f'<situ-textfield-input id="{component_id}" placeholder="{safe_placeholder}"{size_attr}></situ-textfield-input>'
        return pattern.sub(replacer, markdown_content)
