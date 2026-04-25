import re
from src.processors.base_parser import BaseComponentParser

class Parser(BaseComponentParser):
    PATTERN = r"@\[(?:textfield|textfiled)(?:\:\s*([^\]]+))?\](?:\(((?:[^()]*|\([^()]*\))*)\))?"

    def process(self, markdown_content: str) -> str:
        pattern = re.compile(self.PATTERN)
        def replacer(match: re.Match) -> str:
            label = match.group(1)
            args_str = match.group(2)
            args = self.parse_key_value_args(args_str)

            placeholder = args.get('placeholder', '')
            size = args.get('size', '')

            # Shorthand compatibility
            if label and not placeholder:
                placeholder = label.strip()

            size_attr = f' size="{self.escape_html(size)}"' if size else ""
            safe_placeholder = self.escape_html(placeholder)
            component_id = self.get_next_id("textfield")
            return f'<mono-textfield-input id="{component_id}" placeholder="{safe_placeholder}"{size_attr}{self.get_common_attributes(args)}></mono-textfield-input>'
        return pattern.sub(replacer, markdown_content)
