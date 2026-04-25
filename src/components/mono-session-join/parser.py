import re
from src.processors.base_parser import BaseComponentParser

class Parser(BaseComponentParser):
    # OPTIONS: title
    PATTERN = r"@\[session-join(?:\:\s*([^\]]+))?\](?:\(((?:[^()]*|\([^()]*\))*)\))?"

    def process(self, markdown_content: str) -> str:
        pattern = re.compile(self.PATTERN)
        def replacer(match: re.Match) -> str:
            title = match.group(1)
            if title:
                title = title.strip()
                if (title.startswith('"') and title.endswith('"')) or (title.startswith("'") and title.endswith("'")):
                    title = title[1:-1].strip()

            args_str = match.group(2)
            args = self.parse_key_value_args(args_str)
            if 'title' in args:
                title = args['title']

            safe_title = self.escape_html(title) if title else ""
            return f'<mono-session-join title="{safe_title}"{self.get_common_attributes(args)}></mono-session-join>'
        return pattern.sub(replacer, markdown_content)
